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
Mô hình AI dự báo mực nước ngập đô thị bằng Scikit-Learn Gradient Boosting.
Dự báo mực nước sau 30 phút và 60 phút.
"""
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import joblib
import numpy as np

from ..weather import get_rainfall_summary

log = logging.getLogger("grasstoucher.ai")

MODELS_DIR = Path(__file__).resolve().parent / "models"
MODEL_30_PATH = MODELS_DIR / "model_30m.joblib"
MODEL_60_PATH = MODELS_DIR / "model_60m.joblib"


def get_point_slope_factor(point_name: str, threshold_cm: float = 20.0) -> float:
    """
    Xác định hệ số độ dốc / trũng địa hình (slope/depression factor):
    - Hầm chui: ~2.2
    - Vùng trũng ngoại thành, ven sông: ~1.8 - 2.0
    - Điểm trũng nội đô: ~1.4 - 1.6
    - Cốt nền cao (Tây Hồ, Hoàn Kiếm): ~0.85 - 1.0
    """
    name_lower = point_name.lower()
    if any(k in name_lower for k in ["hầm", "ham chui", "ngã tư hầm"]):
        return 2.2
    if any(k in name_lower for k in ["sông", "đê", "ven sông", "thanh oai", "thường tín", "phú minh", "chương mỹ"]):
        return 1.9
    if any(k in name_lower for k in ["nguyễn khuyến", "thái hà", "hoa bằng", "bùi xương trạch", "định công", "triều khúc"]):
        return 1.6
    if any(k in name_lower for k in ["hoàn kiếm", "tây hồ", "tràng tiền", "phố cổ"]):
        return 0.85
    if threshold_cm <= 15:
        return 1.5
    return 1.2


class WaterPredictionEngine:
    def __init__(self, model_30m_path: Optional[Path] = None, model_60m_path: Optional[Path] = None):
        self.model_30m_path = model_30m_path or MODEL_30_PATH
        self.model_60m_path = model_60m_path or MODEL_60_PATH
        self.model_30m = None
        self.model_60m = None
        self._load_models()

    def _load_models(self):
        if self.model_30m_path.exists():
            try:
                self.model_30m = joblib.load(self.model_30m_path)
            except Exception as e:
                log.warning("Không thể tải model 30m: %s", e)
        if self.model_60m_path.exists():
            try:
                self.model_60m = joblib.load(self.model_60m_path)
            except Exception as e:
                log.warning("Không thể tải model 60m: %s", e)

    def predict(
        self,
        current_depth_cm: float,
        point_name: str = "",
        threshold_cm: float = 20.0,
        rain_1h: Optional[float] = None,
        rain_3h: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Dự báo mực nước sau 30 phút và 60 phút.
        """
        if rain_1h is None or rain_3h is None:
            r1, r3 = get_rainfall_summary()
            rain_1h = rain_1h if rain_1h is not None else r1
            rain_3h = rain_3h if rain_3h is not None else r3

        slope_factor = get_point_slope_factor(point_name, threshold_cm)
        features = np.array([[float(current_depth_cm), float(rain_1h), float(rain_3h), float(slope_factor)]])

        # Dự báo 30 phút
        if self.model_30m is not None:
            pred_30 = float(self.model_30m.predict(features)[0])
        else:
            # Thuật toán hồi quy quy tắc fallback nếu chưa tải model
            pred_30 = current_depth_cm + (rain_1h * 0.4 * slope_factor) - (current_depth_cm * 0.15)
        pred_30 = max(0.0, round(pred_30, 1))

        # Dự báo 60 phút
        if self.model_60m is not None:
            pred_60 = float(self.model_60m.predict(features)[0])
        else:
            pred_60 = current_depth_cm + (rain_3h * 0.6 * slope_factor) - (current_depth_cm * 0.3)
        pred_60 = max(0.0, round(pred_60, 1))

        diff_30 = pred_30 - current_depth_cm
        trend_30 = "rising" if diff_30 > 1.5 else ("falling" if diff_30 < -1.5 else "stable")

        diff_60 = pred_60 - current_depth_cm
        trend_60 = "rising" if diff_60 > 1.5 else ("falling" if diff_60 < -1.5 else "stable")

        has_trained_models = (self.model_30m is not None) and (self.model_60m is not None)
        return {
            "current_depth_cm": current_depth_cm,
            "is_demo_model": True,
            "model_type": "GradientBoostingRegressor (Demo/Trained-on-Simulation)" if has_trained_models else "Rule-Based Hydrological Fallback",
            "training_data_type": "synthetic_hydrological_simulation" if has_trained_models else "heuristic_fallback",
            "data_type": "simulated_prediction",
            "rainfall_context": {
                "rain_1h_mm": rain_1h,
                "rain_3h_mm": rain_3h,
                "slope_factor": slope_factor
            },
            "forecast_30m": {
                "predicted_depth_cm": pred_30,
                "change_cm": round(diff_30, 1),
                "trend": trend_30,
                "risk_level": "danger" if pred_30 >= threshold_cm else ("warning" if pred_30 >= 10 else "safe")
            },
            "forecast_60m": {
                "predicted_depth_cm": pred_60,
                "change_cm": round(diff_60, 1),
                "trend": trend_60,
                "risk_level": "danger" if pred_60 >= threshold_cm else ("warning" if pred_60 >= 10 else "safe")
            }
        }


_engine_instance = None


def get_prediction_engine() -> WaterPredictionEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = WaterPredictionEngine()
    return _engine_instance
