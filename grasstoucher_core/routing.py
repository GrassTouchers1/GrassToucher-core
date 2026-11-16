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


def edge_cost(length: float, flood: Optional[dict], vehicle: str, mode: str) -> Optional[float]:
    """Chi phí một đoạn đường. None nghĩa là không đi được."""
    if mode == "fastest" or flood is None:
        return length
    pen = flood_penalty(flood["depth_cm"], vehicle_limit(vehicle, flood["threshold_cm"]))
    if pen is None:
        return None
    return length * (1.0 + config.PENALTY_ALPHA * pen)


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

    if best_k is None and G[u][v]:
        best_k = min(G[u][v].keys(), key=lambda k: G[u][v][k].get("length", float("inf")))
        best_c = G[u][v][best_k].get("length", 0.0)

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
        data = G[u][v][k]
        length = float(data.get("length", 0.0))
        total_dist += length
        total_cost += (c if c is not None else length)

        flood = flood_map.get((u, v, k))
        edge_passable = True
        if flood is not None:
            depth = flood["depth_cm"]
            limit = vehicle_limit(vehicle, flood["threshold_cm"])
            if depth >= limit:
                edge_passable = False
                passable = False
            if depth >= config.PENALTY_START_CM:
                warnings.append({
                    "name": flood["name"],
                    "depth_cm": depth,
                    "threshold_cm": flood["threshold_cm"],
                    "passable": edge_passable,
                })

        coords = edge_coords(G, u, v, data)
        if not all_coords:
            all_coords.extend(coords)
        else:
            all_coords.extend(coords[1:])

        segments.append({
            "u": u, "v": v, "length_m": round(length, 1),
            "street": data.get("name") if isinstance(data.get("name"), str) else None,
            "flooded": flood is not None and flood["depth_cm"] >= config.PENALTY_START_CM,
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
