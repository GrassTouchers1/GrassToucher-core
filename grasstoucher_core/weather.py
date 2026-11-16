"""
GrassToucher Core - Open-Meteo Weather Client
Truy xuất dữ liệu thời tiết & dự báo lượng mưa từ Open-Meteo API.
Giấy phép: GNU AGPL v3 (Mã nguồn mở, Hoàn toàn miễn phí, không yêu cầu API Key).
"""
import urllib.request
import json
import logging
from typing import Dict, Any, Tuple

log = logging.getLogger("grasstoucher.weather")

HANOI_LAT = 21.0285
HANOI_LNG = 105.8030

OPEN_METEO_URL = (
    f"https://api.open-meteo.com/v1/forecast?"
    f"latitude={HANOI_LAT}&longitude={HANOI_LNG}&"
    f"hourly=precipitation,rain,weather_code&"
    f"timezone=Asia%2FBangkok&forecast_days=1"
)


def fetch_hanoi_weather(timeout: int = 5) -> Dict[str, Any]:
    """
    Lấy dự báo lượng mưa theo từng giờ trong ngày của Hà Nội từ Open-Meteo.
    """
    try:
        req = urllib.request.Request(
            OPEN_METEO_URL,
            headers={"User-Agent": "GrassToucher-OpenSource-Research/1.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read().decode())

        hourly = data.get("hourly", {})
        times = hourly.get("time", [])[:24]
        precip = hourly.get("precipitation", [])[:24]

        return {
            "status": "ok",
            "city": "Hà Nội",
            "coordinates": {"lat": HANOI_LAT, "lng": HANOI_LNG},
            "hourly_forecast": [
                {"time": t, "precipitation_mm": float(p)}
                for t, p in zip(times, precip)
            ],
        }
    except Exception as e:
        log.warning("Không thể kết nối Open-Meteo API, sử dụng dữ liệu mặc định: %s", e)
        return {
            "status": "fallback",
            "city": "Hà Nội",
            "hourly_forecast": [
                {"time": f"2026-11-02T{h:02d}:00", "precipitation_mm": 5.2 if 14 <= h <= 18 else 0.0}
                for h in range(24)
            ],
        }


def get_rainfall_summary() -> Tuple[float, float]:
    """
    Trả về lượng mưa dự báo:
    - rain_1h: Lượng mưa trong 1 giờ tới (mm)
    - rain_3h: Tổng lượng mưa trong 3 giờ tới (mm)
    """
    try:
        w = fetch_hanoi_weather()
        forecast = w.get("hourly_forecast", [])
        if forecast:
            rain_1h = float(forecast[0].get("precipitation_mm", 0.0))
            rain_3h = sum(float(item.get("precipitation_mm", 0.0)) for item in forecast[:3])
            return rain_1h, rain_3h
    except Exception:
        pass
    return 0.0, 0.0
