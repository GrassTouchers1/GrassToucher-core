"""
Unit tests cho GrassToucher Core.
"""
import unittest
from grasstoucher_core.config import METRIC_CRS, FLOOD_RADIUS_M
from grasstoucher_core.weather import fetch_hanoi_weather
from grasstoucher_core.ai.prediction_engine import get_prediction_engine
from grasstoucher_core.routing import vehicle_limit, flood_penalty


class TestGrassToucherCore(unittest.TestCase):
    def test_vehicle_limit(self):
        self.assertEqual(vehicle_limit("motorbike", 20.0), 20.0)
        self.assertEqual(vehicle_limit("car", 20.0), 30.0)

    def test_flood_penalty(self):
        # Dưới 5cm -> 0
        self.assertEqual(flood_penalty(3.0, 20.0), 0.0)
        # Bằng hoặc vượt limit -> None (chặn)
        self.assertIsNone(flood_penalty(20.0, 20.0))
        self.assertIsNone(flood_penalty(25.0, 20.0))
        # Trong khoảng 5-20
        pen = flood_penalty(12.5, 20.0)
        self.assertGreater(pen, 0.0)
        self.assertLess(pen, 1.0)

    def test_ai_prediction_engine(self):
        engine = get_prediction_engine()
        res = engine.predict(current_depth_cm=15.0, point_name="Thái Hà", threshold_cm=20.0, rain_1h=10.0, rain_3h=25.0)
        self.assertIn("forecast_30m", res)
        self.assertIn("forecast_60m", res)
        self.assertGreaterEqual(res["forecast_30m"]["predicted_depth_cm"], 0.0)

    def test_weather_client(self):
        data = fetch_hanoi_weather()
        self.assertIn("hourly_forecast", data)
        self.assertEqual(data.get("city"), "Hà Nội")


if __name__ == "__main__":
    unittest.main()
