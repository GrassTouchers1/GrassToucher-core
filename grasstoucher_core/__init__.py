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
