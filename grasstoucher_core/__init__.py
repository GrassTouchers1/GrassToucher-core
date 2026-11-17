"""
GrassToucher Core - Thư viện mã nguồn mở về định tuyến và mô hình ngập lụt đô thị.
Giấy phép: Apache License 2.0 (OSI-Approved).
"""
from .config import METRIC_CRS, FLOOD_RADIUS_M, PENALTY_ALPHA
from .graph import RoadGraph, get_graph, GraphNotReady
from .routing import (
    calculate_routes,
    find_path,
    describe_route,
    slice_coords_to_proj,
    multi_hazard_edge_cost,
    find_evacuation_route,
)
from .weather import (
    fetch_hanoi_weather,
    get_rainfall_summary,
    fetch_open_meteo_flood,
    get_glofas_basin_status,
    fetch_nasa_gpm_precipitation,
    get_osi_open_data_registry,
)
from .ai.prediction_engine import WaterPredictionEngine, get_prediction_engine

__version__ = "0.5.0"
__all__ = [
    "RoadGraph",
    "get_graph",
    "GraphNotReady",
    "calculate_routes",
    "find_path",
    "describe_route",
    "slice_coords_to_proj",
    "multi_hazard_edge_cost",
    "find_evacuation_route",
    "fetch_hanoi_weather",
    "get_rainfall_summary",
    "fetch_open_meteo_flood",
    "get_glofas_basin_status",
    "fetch_nasa_gpm_precipitation",
    "get_osi_open_data_registry",
    "WaterPredictionEngine",
    "get_prediction_engine",
    "METRIC_CRS",
    "FLOOD_RADIUS_M",
    "PENALTY_ALPHA",
]
