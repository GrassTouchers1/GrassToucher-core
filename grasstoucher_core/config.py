"""
GrassToucher Core - Cấu hình hệ thống tìm đường và mô hình thủy văn.
100% Mã nguồn mở (OSI-Approved, Apache-2.0 License).
"""
import os
from pathlib import Path

# Thư mục gốc của gói hoặc dữ liệu
PACKAGE_DIR = Path(__file__).resolve().parent
CORE_ROOT = PACKAGE_DIR.parent
DEFAULT_GRAPH_PATH = CORE_ROOT / "data" / "hanoi_drive.graphml"

GRAPH_PATH = Path(os.environ.get("GRASSTOUCHER_GRAPH_PATH", str(DEFAULT_GRAPH_PATH)))

# UTM 48N: Hệ toạ độ mét chuẩn cho khu vực Hà Nội (EPSG:32648)
METRIC_CRS = 32648

# --- Mực nước & Trọng số cản trở (Cost Penalty) ---
FLOOD_RADIUS_M = 60.0       # Điểm ngập ảnh hưởng tới các đoạn đường trong bán kính này (mét)
PENALTY_START_CM = 5.0      # Dưới 5 cm coi như không ngập
PENALTY_ALPHA = 8.0         # Càng sát ngưỡng chặn, chi phí đoạn đường càng tăng (tối đa 1 + 8 = 9 lần)
CAR_LIMIT_FACTOR = 1.5      # Ngưỡng ô tô = ngưỡng điểm ngập x 1.5 (xe máy 20 cm -> ô tô 30 cm)

# Mức ngập ước lượng từ báo cáo của người dân (cm)
LEVEL_DEPTH_CM = {"light": 10.0, "medium": 25.0, "heavy": 40.0}

# Tốc độ trung bình ước tính trong đô thị (km/h) để tính thời gian di chuyển
SPEED_KMH = {"motorbike": 25.0, "car": 30.0, "walk": 4.5}

# Hệ số cản trở đa thiên tai (Multi-Hazard Penalty Factors)
HAZARD_RADIUS_M = 100.0         # Bán kính vùng ảnh hưởng thiên tai (mét)
LANDSLIDE_PENALTY_ALPHA = 30.0  # Phạt đường sạt lở hoặc nguy cơ sạt lở
STORM_BLOCK_PENALTY_ALPHA = 50.0 # Phạt chướng ngại vật/cây đổ bão

MAX_SNAP_M = 2000.0         # Điểm xuất phát/đích cách đường gần nhất quá 2 km thì mới báo lỗi
