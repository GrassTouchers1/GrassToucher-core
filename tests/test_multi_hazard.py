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
Unit tests cho Mô hình Trở kháng Đa thiên tai và Thuật toán Sơ tán khẩn cấp (Core).
"""
import unittest
from grasstoucher_core.routing import multi_hazard_edge_cost, edge_cost, find_evacuation_route
from grasstoucher_core.graph import get_graph


class TestMultiHazardRouting(unittest.TestCase):
    def test_multi_hazard_edge_cost_flood(self):
        # 1. Đoạn ngập nhẹ: cost tăng
        cost = multi_hazard_edge_cost(
            length=100.0,
            hazard_data={"depth_cm": 12.0, "threshold_cm": 20.0, "hazard_type": "flood"},
            vehicle="motorbike",
            mode="safe"
        )
        self.assertIsNotNone(cost)
        self.assertGreater(cost, 100.0)

        # 2. Đoạn ngập sâu vượt ngưỡng: chặn hoàn toàn (None)
        cost_blocked = multi_hazard_edge_cost(
            length=100.0,
            hazard_data={"depth_cm": 25.0, "threshold_cm": 20.0, "hazard_type": "flood"},
            vehicle="motorbike",
            mode="safe"
        )
        self.assertIsNone(cost_blocked)

    def test_multi_hazard_edge_cost_landslide(self):
        # Sạt lở nặng (critical): chặn hoàn toàn
        cost_crit = multi_hazard_edge_cost(
            length=100.0,
            hazard_data={"hazard_type": "landslide", "severity": "critical"},
            vehicle="car",
            mode="safe"
        )
        self.assertIsNone(cost_crit)

        # Sạt lở nhẹ/vừa (medium): phạt trở kháng rất cao
        cost_med = multi_hazard_edge_cost(
            length=100.0,
            hazard_data={"hazard_type": "landslide", "severity": "medium"},
            vehicle="car",
            mode="safe"
        )
        self.assertIsNotNone(cost_med)
        self.assertGreater(cost_med, 1000.0)

    def test_multi_hazard_edge_cost_storm_block(self):
        # Cây đổ / chướng ngại vật bão: chặn đường hoàn toàn
        cost = multi_hazard_edge_cost(
            length=100.0,
            hazard_data={"hazard_type": "storm_block", "name": "Cây đổ chắn đường"},
            vehicle="motorbike",
            mode="safe"
        )
        self.assertIsNone(cost)

    def test_evacuation_dijkstra(self):
        graph = get_graph()
        shelters = [
            {
                "id": 1,
                "name": "Trường THPT Yên Hòa (Điểm tập kết sơ tán)",
                "lng": 105.7940,
                "lat": 21.0210,
                "capacity": 500,
                "current_occupancy": 50,
                "status": "open"
            },
            {
                "id": 2,
                "name": "Nhà văn hóa Cầu Giấy (Trạm cứu hộ an toàn)",
                "lng": 105.7890,
                "lat": 21.0350,
                "capacity": 300,
                "current_occupancy": 30,
                "status": "open"
            }
        ]

        # Vị trí người dân cần sơ tán (Trần Duy Hưng)
        origin_lng, origin_lat = 105.8010, 21.0105

        res = find_evacuation_route(
            graph=graph,
            hazard_map={},
            origin_lng=origin_lng,
            origin_lat=origin_lat,
            shelters=shelters,
            vehicle="walk"
        )

        self.assertTrue(res["found"])
        self.assertEqual(res["mode"], "evacuation")
        self.assertIn("shelter", res)
        self.assertIn(res["shelter"]["id"], [1, 2])
        self.assertGreater(res["distance_m"], 0)
        self.assertGreater(res["duration_min"], 0)
        self.assertEqual(res["geometry"]["type"], "LineString")


if __name__ == "__main__":
    unittest.main()
