"""
GrassToucher Core - Đồ thị đường bộ và Khớp nối Không gian GIS.
Nạp đồ thị OSMnx, xây dựng chỉ mục không gian R-Tree, chiếu điểm ngập lên các đoạn đường.
"""
import logging
import math
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import geopandas as gpd
import numpy as np
import osmnx as ox
from shapely.geometry import Point

from . import config

log = logging.getLogger("grasstoucher.graph")
_lock = threading.Lock()
_graph = None


class GraphNotReady(Exception):
    pass


class RoadGraph:
    def __init__(self, G):
        self.G = G
        ids = list(G.nodes)
        self.node_ids = np.array(ids)
        self.node_lng = np.array([G.nodes[n]["x"] for n in ids])
        self.node_lat = np.array([G.nodes[n]["y"] for n in ids])

        edges = ox.graph_to_gdfs(G, nodes=False)
        self.edge_keys = [(int(u), int(v), int(k)) for u, v, k in edges.index]
        self.edges_m = edges.to_crs(config.METRIC_CRS)
        self.edges_m.sindex  # Dựng R-tree spatial index trước

    def nearest_node(self, lng: float, lat: float) -> Tuple[int, float]:
        """Tìm nút giao gần nhất và khoảng cách (m)."""
        k = math.cos(math.radians(lat))
        d2 = ((self.node_lng - lng) * k) ** 2 + (self.node_lat - lat) ** 2
        i = int(d2.argmin())
        return int(self.node_ids[i]), math.sqrt(float(d2[i])) * 111_320

    def snap_to_edge(self, lng: float, lat: float) -> Dict[str, Any]:
        """
        Tìm cạnh gần nhất và vị trí tiếp cận thực tế trên mặt đường:
        - Sử dụng R-tree spatial index trong hệ toạ độ mét UTM 48N.
        - Chiếu điểm lên cạnh để lấy toạ độ tiếp cận chính xác.
        """
        try:
            pt_m = gpd.GeoSeries([Point(lng, lat)], crs=4326).to_crs(config.METRIC_CRS)[0]
            for r in (50, 150, 400, 1000, 2500):
                hits = list(self.edges_m.sindex.query(pt_m.buffer(r), predicate="intersects"))
                if hits:
                    break
            else:
                n, d = self.nearest_node(lng, lat)
                node_x = self.G.nodes[n]["x"]
                node_y = self.G.nodes[n]["y"]
                return {
                    "u": n, "v": n, "key": 0, "closer_node": n, "dist_m": d,
                    "proj_pt": [round(node_x, 6), round(node_y, 6)],
                    "ratio": 0.0, "name": "Nút giao",
                }

            sub = self.edges_m.iloc[hits]
            dists = sub.distance(pt_m)
            best_idx = dists.idxmin()
            best_dist = float(dists[best_idx])
            geom_m = sub.loc[best_idx, "geometry"]

            proj_dist = geom_m.project(pt_m)
            ratio = float(proj_dist / max(geom_m.length, 1e-6))
            ratio = max(0.0, min(1.0, ratio))

            proj_pt_m = geom_m.interpolate(proj_dist)
            proj_pt_wgs = gpd.GeoSeries([proj_pt_m], crs=config.METRIC_CRS).to_crs(4326)[0]

            u, v, key = self.edge_keys[int(hits[dists.index.get_loc(best_idx)])]
            closer_node = u if ratio < 0.5 else v
            street_name = sub.loc[best_idx].get("name", "Đoạn đường")
            if isinstance(street_name, list):
                street_name = street_name[0] if street_name else "Đoạn đường"

            return {
                "u": u, "v": v, "key": key,
                "closer_node": closer_node,
                "dist_m": best_dist,
                "proj_pt": [round(proj_pt_wgs.x, 6), round(proj_pt_wgs.y, 6)],
                "ratio": round(ratio, 3),
                "name": str(street_name or "Đoạn đường"),
            }
        except Exception:
            n, d = self.nearest_node(lng, lat)
            node_x = self.G.nodes[n]["x"]
            node_y = self.G.nodes[n]["y"]
            return {
                "u": n, "v": n, "key": 0, "closer_node": n, "dist_m": d,
                "proj_pt": [round(node_x, 6), round(node_y, 6)],
                "ratio": 0.0, "name": "Nút giao",
            }

    def flood_edges(self, sources: List[Dict[str, Any]]) -> Dict[Tuple[int, int, int], Dict[str, Any]]:
        """
        sources: [{lng, lat, depth_cm, threshold_cm, name, kind, source_id}, ...]
        Trả về {(u, v, key): thông tin ngập} cho các đoạn đường nằm trong bán kính ngập.
        """
        usable = [s for s in sources if s.get("depth_cm") is not None and float(s["depth_cm"]) >= config.PENALTY_START_CM]
        result = {}
        if not usable:
            return result

        pts = gpd.GeoSeries(
            gpd.points_from_xy([s["lng"] for s in usable], [s["lat"] for s in usable]),
            crs=4326,
        ).to_crs(config.METRIC_CRS)

        for s, pt in zip(usable, pts):
            hits = self.edges_m.sindex.query(pt.buffer(config.FLOOD_RADIUS_M), predicate="intersects")
            for i in hits:
                key = self.edge_keys[int(i)]
                cur = result.get(key)
                depth = float(s["depth_cm"])
                if cur is None or depth > cur["depth_cm"]:
                    result[key] = {
                        "depth_cm": depth,
                        "threshold_cm": float(s.get("threshold_cm", 20.0)),
                        "name": s.get("name", "Điểm ngập"),
                        "kind": s.get("kind", "point"),
                        "source_id": s.get("source_id"),
                    }
        return result


def get_graph(graph_path: Optional[Path] = None) -> RoadGraph:
    """Nạp đồ thị một lần vào RAM, các lần sau tái sử dụng."""
    global _graph
    if _graph is None:
        with _lock:
            if _graph is None:
                path = graph_path or config.GRAPH_PATH
                if not Path(path).exists():
                    raise GraphNotReady(
                        f"Chưa có file đồ thị tại: {path}. Hãy chạy: python scripts/download_graph.py"
                    )
                log.info("Đang nạp đồ thị đường từ %s ...", path)
                _graph = RoadGraph(ox.load_graphml(path))
                log.info("Nạp xong: %d nút, %d đoạn", len(_graph.G.nodes), len(_graph.G.edges))
    return _graph
