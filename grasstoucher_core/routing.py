# Copyright 2026 GrassTouchers Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

"""
GrassToucher Core - Giải thuật Định tuyến A* Thích ứng Mực Nước Ngập.
100% Mã nguồn mở (OSI-Approved, Apache-2.0 License).

Hàm trọng số cạnh:
  cost(đoạn) = chiều dài × (1 + α · penalty)
    penalty = 0                       nếu độ sâu < 5 cm
            = (d - 5) / (ngưỡng - 5)  nếu 5 cm ≤ d < ngưỡng của xe
            = None (chặn hoàn toàn)   nếu d ≥ ngưỡng của xe
"""
import math
from typing import Dict, List, Optional, Tuple, Any
import networkx as nx

from . import config


def vehicle_limit(vehicle: str, threshold_cm: float) -> float:
    return threshold_cm * (config.CAR_LIMIT_FACTOR if vehicle == "car" else 1.0)


def flood_penalty(depth_cm: float, limit_cm: float) -> Optional[float]:
    """Trả về hệ số phạt từ 0 đến <1. None nghĩa là đường bị chặn hoàn toàn."""
    if depth_cm >= limit_cm:
        return None
    if depth_cm < config.PENALTY_START_CM:
        return 0.0
    return (depth_cm - config.PENALTY_START_CM) / (limit_cm - config.PENALTY_START_CM)


def multi_hazard_edge_cost(length: float, hazard_data: Any, vehicle: str, mode: str) -> Optional[float]:
    """
    Mô hình trở kháng đa thiên tai (Multi-Hazard Impedance Model):
    C(e) = L(e) * (1 + sum(alpha_h * factor_h))
    Hỗ trợ:
      - flood: ngập lụt đô thị theo mực nước và loại xe
      - landslide: sạt lở đất đồi núi/taluy
      - storm_block: cây đổ/chướng ngại vật do bão
      - general: vùng rủi ro thiên tai tổng hợp
    """
    if mode == "fastest" or hazard_data is None:
        return length

    hazards = hazard_data if isinstance(hazard_data, list) else [hazard_data]
    total_penalty = 0.0

    for h in hazards:
        if not isinstance(h, dict):
            continue

        # 1. Đoạn đường bị cấm/chặn hoàn toàn
        if h.get("passable") is False or h.get("blocked") is True:
            return None

        h_type = h.get("hazard_type") or h.get("type", "flood")

        # 2. Sạt lở đất
        if h_type == "landslide":
            sev = h.get("severity", "medium")
            if sev in ("high", "critical"):
                return None  # Cấm đường hoàn toàn khi sạt lở nặng
            total_penalty += getattr(config, "LANDSLIDE_PENALTY_ALPHA", 30.0)

        # 3. Tắc nghẽn bão / Cây đổ
        elif h_type in ("storm_block", "tree_fall"):
            return None

        # 4. Ngập lụt (Flood)
        elif "depth_cm" in h or h_type == "flood":
            depth = float(h.get("depth_cm", 0.0))
            threshold = float(h.get("threshold_cm", 20.0))
            pen = flood_penalty(depth, vehicle_limit(vehicle, threshold))
            if pen is None:
                return None  # Ngập vượt ngưỡng xe
            total_penalty += config.PENALTY_ALPHA * pen

        # 5. Rủi ro tổng quát
        else:
            risk = float(h.get("risk_score", 0.5))
            total_penalty += 10.0 * risk

    return length * (1.0 + total_penalty)


def edge_cost(length: float, flood: Optional[dict], vehicle: str, mode: str) -> Optional[float]:
    """Chi phí một đoạn đường (Tương thích ngược 100%)."""
    return multi_hazard_edge_cost(length, flood, vehicle, mode)


def best_edge(G, flood_map: dict, u: int, v: int, vehicle: str, mode: str) -> Tuple[Optional[int], Optional[float]]:
    """Trong các đoạn song song u->v, chọn đoạn có chi phí tối ưu nhất."""
    best_k, best_c = None, None
    best_has_geom = False
    for k, data in G[u][v].items():
        c = edge_cost(data.get("length", 0.0), flood_map.get((u, v, k)), vehicle, mode)
        if c is None:
            continue
        has_geom = ("geometry" in data and data["geometry"] is not None)
        if best_c is None or c < best_c:
            best_k, best_c, best_has_geom = k, c, has_geom
        elif math.isclose(c, best_c, rel_tol=1e-7, abs_tol=1e-7):
            if not best_has_geom and has_geom:
                best_k, best_c, best_has_geom = k, c, True

    # Trả về (None, None) nếu mọi cạnh song song đều bị chặn — tuyệt đối không rơi về cạnh bị chặn.
    return best_k, best_c


def _heuristic(G):
    def h(a, b):
        ya, xa = G.nodes[a]["y"], G.nodes[a]["x"]
        yb, xb = G.nodes[b]["y"], G.nodes[b]["x"]
        k = math.cos(math.radians((ya + yb) / 2))
        return math.hypot((xa - xb) * k, ya - yb) * 111_320  # mét
    return h


def find_path(G, flood_map: dict, origin: int, dest: int, vehicle: str, mode: str) -> List[int]:
    """A* giữa 2 nút giao. Ném NetworkXNoPath nếu không có đường đi."""
    def weight(u, v, key_dict):
        best = None
        for k, data in key_dict.items():
            c = edge_cost(data.get("length", 0.0), flood_map.get((u, v, k)), vehicle, mode)
            if c is not None and (best is None or c < best):
                best = c
        return best

    return nx.astar_path(G, origin, dest, heuristic=_heuristic(G), weight=weight)


def edge_coords(G, u: int, v: int, data: dict) -> List[List[float]]:
    """Toạ độ [lng, lat] của đoạn đường u -> v bảo toàn đường cong."""
    ux, uy = G.nodes[u]["x"], G.nodes[u]["y"]
    vx, vy = G.nodes[v]["x"], G.nodes[v]["y"]
    geom = data.get("geometry")
    if geom is None:
        return [[ux, uy], [vx, vy]]

    pts = [[float(x), float(y)] for x, y in geom.coords]
    if len(pts) < 2:
        return [[ux, uy], [vx, vy]]

    d_first = (pts[0][0] - ux) ** 2 + (pts[0][1] - uy) ** 2
    d_last = (pts[-1][0] - ux) ** 2 + (pts[-1][1] - uy) ** 2
    if d_first > d_last:
        pts = pts[::-1]

    pts[0] = [ux, uy]
    pts[-1] = [vx, vy]
    return pts


def describe_route(G, flood_map: dict, path: List[int], vehicle: str, mode: str) -> Dict[str, Any]:
    speed_m_per_min = config.SPEED_KMH[vehicle] * 1000 / 60
    if not path:
        return {
            "found": False, "mode": mode, "reason": "Không tìm thấy đường đi.",
            "distance_m": 0, "duration_min": 0.0, "cost": 0, "passable": True,
            "flood_warnings": [], "geometry": {"type": "LineString", "coordinates": []},
        }

    if len(path) == 1:
        single_pt = [round(G.nodes[path[0]]["x"], 6), round(G.nodes[path[0]]["y"], 6)]
        return {
            "found": True, "mode": mode, "distance_m": 0, "duration_min": 0.0, "cost": 0,
            "passable": True, "flood_warnings": [],
            "geometry": {"type": "LineString", "coordinates": [single_pt, single_pt]},
            "segments": [],
        }

    total_dist = 0.0
    total_cost = 0.0
    all_coords = []
    warnings = []
    segments = []
    passable = True

    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        k, c = best_edge(G, flood_map, u, v, vehicle, mode)
        if k is None or c is None:
            return {
                "found": False,
                "mode": mode,
                "reason": "Tuyến đường có đoạn bị thiên tai chặn hoàn toàn, không thể lưu thông an toàn.",
                "distance_m": round(total_dist),
                "duration_min": 0.0,
                "cost": round(total_cost, 1),
                "passable": False,
                "flood_warnings": [w["name"] for w in warnings],
                "geometry": {"type": "LineString", "coordinates": []},
                "segments": segments,
            }
        data = G[u][v][k]
        length = float(data.get("length", 0.0))
        total_dist += length
        total_cost += c

        raw_hazard = flood_map.get((u, v, k))
        hazards_on_edge = raw_hazard if isinstance(raw_hazard, list) else ([raw_hazard] if raw_hazard is not None else [])
        edge_passable = True
        edge_flooded = False
        for flood in hazards_on_edge:
            if not isinstance(flood, dict):
                continue
            h_type = flood.get("hazard_type") or flood.get("type", "flood")
            if flood.get("passable") is False or flood.get("blocked") is True or h_type in ("storm_block", "tree_fall"):
                edge_passable = False
                passable = False
                edge_flooded = True
                warnings.append({
                    "name": flood.get("name", "Vùng nguy cơ thiên tai"),
                    "depth_cm": 0.0,
                    "threshold_cm": 0.0,
                    "passable": False
                })
            elif h_type == "landslide" and flood.get("severity", "medium") in ("high", "critical"):
                edge_passable = False
                passable = False
                edge_flooded = True
                warnings.append({
                    "name": flood.get("name", "Sạt lở nghiêm trọng"),
                    "depth_cm": 0.0,
                    "threshold_cm": 0.0,
                    "passable": False
                })
            elif "depth_cm" in flood or h_type == "flood":
                depth = float(flood.get("depth_cm", 0.0))
                limit = vehicle_limit(vehicle, float(flood.get("threshold_cm", 20.0)))
                if depth >= limit:
                    edge_passable = False
                    passable = False
                if depth >= config.PENALTY_START_CM:
                    edge_flooded = True
                    warnings.append({
                        "name": flood.get("name", "Điểm ngập"),
                        "depth_cm": depth,
                        "threshold_cm": float(flood.get("threshold_cm", 20.0)),
                        "passable": edge_passable,
                    })
            else:
                edge_flooded = True
                warnings.append({
                    "name": flood.get("name", "Vùng cảnh báo thiên tai"),
                    "depth_cm": 0.0,
                    "threshold_cm": 0.0,
                    "passable": True,
                })

        coords = edge_coords(G, u, v, data)
        if not all_coords:
            all_coords.extend(coords)
        else:
            all_coords.extend(coords[1:])

        segments.append({
            "u": u, "v": v, "length_m": round(length, 1),
            "street": data.get("name") if isinstance(data.get("name"), str) else None,
            "flooded": edge_flooded,
            "passable": edge_passable,
        })

    duration_min = total_dist / speed_m_per_min

    # Loại bỏ cảnh báo trùng lặp
    seen = set()
    uniq_warnings = []
    for w in warnings:
        key = (w["name"], w["depth_cm"])
        if key not in seen:
            seen.add(key)
            uniq_warnings.append(w["name"])

    return {
        "found": True,
        "mode": mode,
        "distance_m": round(total_dist),
        "duration_min": round(duration_min, 1),
        "cost": round(total_cost, 1),
        "passable": passable,
        "flood_warnings": uniq_warnings,
        "geometry": {
            "type": "LineString",
            "coordinates": [[round(x, 6), round(y, 6)] for x, y in all_coords],
        },
        "segments": segments,
    }


def slice_coords_to_proj(coords_list: list, proj_coord: list, from_start: bool = True) -> list:
    """Cắt danh sách toạ độ cạnh từ đầu danh sách tới điểm chiếu proj_coord (hoặc ngược lại)."""
    if not coords_list:
        return [proj_coord]
    min_d, min_idx = float("inf"), 0
    px, py = proj_coord[0], proj_coord[1]
    for idx, c in enumerate(coords_list):
        d = (c[0] - px) ** 2 + (c[1] - py) ** 2
        if d < min_d:
            min_d, min_idx = d, idx
    if from_start:
        res = list(coords_list[:min_idx + 1])
        if not res or res[-1] != proj_coord:
            res.append(proj_coord)
        return res
    else:
        res = [proj_coord] + list(coords_list[min_idx:])
        return res


def calculate_routes(
    graph,
    flood_sources: List[Dict[str, Any]],
    origin_lng: float,
    origin_lat: float,
    dest_lng: float,
    dest_lat: float,
    vehicle: str = "motorbike",
    use_ai_prediction: bool = False
) -> Dict[str, Any]:
    """
    Tính toán đồng thời 2 lộ trình:
      1. Fastest (Ngắn nhất, không xét ngập)
      2. Safe (Né ngập có trọng số, tự động chuyển hướng an toàn)
    """
    snap_orig = graph.snap_to_edge(origin_lng, origin_lat)
    snap_dest = graph.snap_to_edge(dest_lng, dest_lat)

    if snap_orig["dist_m"] > config.MAX_SNAP_M or snap_dest["dist_m"] > config.MAX_SNAP_M:
        raise ValueError(
            f"Điểm chọn quá xa mạng lưới đường giao thông (>{config.MAX_SNAP_M}m)."
        )

    sources = list(flood_sources)
    if use_ai_prediction:
        try:
            from .ai.prediction_engine import get_prediction_engine
            ai_engine = get_prediction_engine()
            enhanced_sources = []
            for s in sources:
                d = float(s.get("depth_cm", 0.0))
                if d >= config.PENALTY_START_CM:
                    pred = ai_engine.predict(d, s.get("name", ""), float(s.get("threshold_cm", 20.0)))
                    p30 = pred["forecast_30m"]["predicted_depth_cm"]
                    s_copy = dict(s)
                    if p30 > d:
                        s_copy["depth_cm"] = p30
                        s_copy["name"] = s_copy["name"] + " (Dự báo +30p)"
                    enhanced_sources.append(s_copy)
                else:
                    enhanced_sources.append(s)
            sources = enhanced_sources
        except Exception:
            pass

    flood_map = graph.flood_edges(sources)

    # 1. Đường nhanh nhất (fastest)
    try:
        path_fastest = find_path(graph.G, flood_map, snap_orig["closer_node"], snap_dest["closer_node"], vehicle, "fastest")
        fastest_res = describe_route(graph.G, flood_map, path_fastest, vehicle, "fastest")
    except nx.NetworkXNoPath:
        fastest_res = {"found": False, "mode": "fastest", "reason": "Không tìm được đường đi."}

    # 2. Đường an toàn (safe)
    try:
        path_safe = find_path(graph.G, flood_map, snap_orig["closer_node"], snap_dest["closer_node"], vehicle, "safe")
        safe_res = describe_route(graph.G, flood_map, path_safe, vehicle, "safe")
    except nx.NetworkXNoPath:
        safe_res = {
            "found": False,
            "mode": "safe",
            "reason": "Mọi ngả đường đều ngập sâu vượt ngưỡng xe của bạn. Hãy chờ nước rút hoặc đổi phương tiện.",
        }

    same_route = False
    if fastest_res.get("found") and safe_res.get("found"):
        same_route = (path_fastest == path_safe)

    return {
        "vehicle": vehicle,
        "ai_prediction_applied": use_ai_prediction,
        "same_route": same_route,
        "fastest": fastest_res,
        "safe": safe_res,
        "flood_sources_used": len(sources),
        "affected_road_segments": len(flood_map),
        "snap_origin": snap_orig,
        "snap_destination": snap_dest,
    }


def find_evacuation_route(
    graph,
    hazard_map: dict,
    origin_lng: float,
    origin_lat: float,
    shelters: List[Dict[str, Any]],
    vehicle: str = "walk",
) -> Dict[str, Any]:
    """
    Thuật toán tìm đường sơ tán khẩn cấp tới điểm an toàn (Evacuation Dijkstra):
    Tìm lộ trình an toàn nhất và gần nhất từ vị trí người dân tới điểm sơ tán khả dụng.
    """
    if not shelters:
        return {"found": False, "reason": "Không có điểm sơ tán nào trong hệ thống."}

    snap_orig = graph.snap_to_edge(origin_lng, origin_lat)
    if snap_orig["dist_m"] > config.MAX_SNAP_M:
        return {"found": False, "reason": f"Vị trí quá xa mạng lưới đường bộ (>{config.MAX_SNAP_M}m)."}

    orig_node = snap_orig["closer_node"]

    shelter_node_map = {}
    shelter_snap_dist = {}
    target_nodes = set()
    for s in shelters:
        if s.get("status") == "closed":
            continue
        if s.get("capacity") and s.get("current_occupancy", 0) >= s["capacity"]:
            continue
        try:
            s_snap = graph.snap_to_edge(s["lng"], s["lat"])
            if s_snap["dist_m"] > config.MAX_SNAP_M:
                continue
            s_node = s_snap["closer_node"]
            if s_node not in shelter_snap_dist or s_snap["dist_m"] < shelter_snap_dist[s_node]:
                shelter_snap_dist[s_node] = s_snap["dist_m"]
                shelter_node_map[s_node] = s
            target_nodes.add(s_node)
        except Exception:
            continue

    if not target_nodes:
        return {"found": False, "reason": "Không có điểm sơ tán khả dụng nào còn chỗ tiếp nhận."}

    def weight_fn(u, v, key_dict):
        best = None
        for k, data in key_dict.items():
            c = multi_hazard_edge_cost(data.get("length", 0.0), hazard_map.get((u, v, k)), vehicle, "safe")
            if c is not None and (best is None or c < best):
                best = c
        return best

    try:
        dist_dict, path_dict = nx.multi_source_dijkstra(
            graph.G,
            sources={orig_node},
            target=None,
            weight=weight_fn
        )
    except Exception as e:
        return {"found": False, "reason": f"Lỗi thuật toán tìm kiếm: {e}"}

    reachable_shelters = [n for n in target_nodes if n in dist_dict]
    if not reachable_shelters:
        return {"found": False, "reason": "Tất cả các tuyến đường tới điểm sơ tán đã bị chia cắt bởi thiên tai."}

    best_shelter_node = min(reachable_shelters, key=lambda n: dist_dict[n])
    best_path = path_dict[best_shelter_node]
    chosen_shelter = shelter_node_map[best_shelter_node]

    desc = describe_route(graph.G, hazard_map, best_path, vehicle, "safe")
    if not desc.get("found") or not desc.get("passable", True):
        return {
            "found": False,
            "passable": False,
            "reason": desc.get("reason") or "Tuyến đường tới điểm sơ tán đã bị chia cắt bởi thiên tai.",
        }
    speed_kmh = config.SPEED_KMH.get(vehicle, 4.5)
    speed_m_min = speed_kmh * 1000 / 60
    duration_min = round(desc["distance_m"] / speed_m_min, 1)

    return {
        "found": True,
        "passable": True,
        "mode": "evacuation",
        "vehicle": vehicle,
        "shelter": chosen_shelter,
        "distance_m": desc["distance_m"],
        "duration_min": duration_min,
        "cost": desc["cost"],
        "geometry": desc["geometry"],
        "segments": desc["segments"],
        "flood_warnings": desc.get("flood_warnings", []),
        "safety_score": 1.0 if not desc.get("flood_warnings") else 0.85,
    }

