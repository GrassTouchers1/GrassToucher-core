# 🌐 GrassToucher Core – Adaptive Urban Flood Routing & AI Hydrology Engine

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![OSI Approved](https://img.shields.io/badge/OSI-Approved%20Open%20Source-brightgreen.svg)](https://opensource.org/licenses)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![OpenStreetMap](https://img.shields.io/badge/Data-OpenStreetMap-green.svg)](https://www.openstreetmap.org/)
[![Open-Meteo](https://img.shields.io/badge/Weather-Open--Meteo%20API-orange.svg)](https://open-meteo.com/)
[![Scikit-Learn](https://img.shields.io/badge/AI-Scikit--Learn-F7931E.svg?logo=scikit-learn)](https://scikit-learn.org/)

> **Thư viện lõi định tuyến thông minh thích ứng ngập lụt đô thị và mô hình AI dự báo mực nước dâng/rút.**  
> Dự án 100% Mã nguồn mở, độc lập và dễ dàng tích hợp vào bất kỳ hệ sinh thái giao thông đô thị nào.

---

## 💡 1. Giới thiệu & Tuyên ngôn Mã nguồn mở

Vào mùa mưa lũ tại các đô thị Việt Nam (như Hà Nội, TP.HCM), hiện tượng ngập cục bộ khiến các dịch vụ bản đồ thông thường (Google Maps, Apple Maps) trở nên kém hiệu quả do thiếu thông tin về độ sâu mực nước và không hỗ trợ né ngập theo ngưỡng an toàn từng loại phương tiện.

**GrassToucher Core** cung cấp giải pháp thuật toán mã nguồn mở toàn diện:
- **Đồ thị không gian mở:** Trích xuất mạng lưới đường bộ từ **OpenStreetMap (OSM)** thông qua **OSMnx** và **NetworkX**.
- **Thuật toán A\* có trọng số phạt ngập:** Tự động né các đoạn ngập sâu hoặc cấm đường đối với phương tiện vượt ngưỡng.
- **Học máy dự báo ngập 30/60 phút:** Sử dụng mô hình **Gradient Boosting** tích hợp lượng mưa mở theo thời gian thực từ **Open-Meteo API**.
- **100% Free & Open Source Software (FOSS):** Không sử dụng bất kỳ API trả phí, khóa bảo mật độc quyền hay dữ liệu đóng nào.

---

## 📐 2. Cơ sở Toán học & Thuật toán

### 2.1. Hàm trọng số cạnh thích ứng (Adaptive Edge Cost)

Đoạn đường $e$ có chiều dài $L(e)$ và mực nước ngập cục bộ $d(e)$ (cm). Chi phí di chuyển $C(e)$ được tính như sau:

$$C(e) = L(e) \times (1 + \alpha \cdot \text{penalty}(d(e), \text{limit}))$$

Trong đó:
- $\text{penalty} = 0$ nếu $d(e) < 5\text{ cm}$ (mực nước an toàn, không cản trở).
- $\text{penalty} = \frac{d(e) - 5}{\text{limit} - 5}$ nếu $5\text{ cm} \le d(e) < \text{limit}$ (chi phí tăng dần làm cho thuật toán ưu tiên đường vòng khô ráo).
- $C(e) = \infty$ (đoạn đường bị chặn hoàn toàn) nếu $d(e) \ge \text{limit}$.

**Ngưỡng an toàn phương tiện ($\text{limit}$):**
- Xe máy: $\text{limit} \approx 20\text{ cm}$.
- Ô tô: $\text{limit} = 20 \times 1.5 = 30\text{ cm}$.
- Hệ số phạt tối đa: $\alpha = 8.0$ (đoạn đường có thể bị tăng chi phí tới 9 lần trước khi bị chặn hẳn).

---

### 2.2. Khớp nối không gian (Spatial Snapping & Buffering)
- Sử dụng hệ tọa độ mét **UTM 48N (EPSG:32648)** để đảm bảo độ chuẩn xác khoảng cách thực địa tại Hà Nội.
- Điểm ngập được tạo vùng ảnh hưởng (Buffer) bán kính $60\text{ m}$.
- Chỉ mục không gian **R-Tree** (`geopandas`, `shapely.sindex`) cho phép quét và gán trọng số ngập lên hàng chục nghìn đoạn đường trong thời gian tính bằng mili-giây.

---

## 📦 3. Cài đặt & Sử dụng

### 3.1. Cài đặt thư viện
```bash
git clone https://github.com/GrassTouchers1/GrassToucher-core.git
cd GrassToucher-core

# Cài đặt dạng package phát triển
pip install -e .
```

### 3.2. Ví dụ code tìm đường Python:
```python
from grasstoucher_core import get_graph, calculate_routes

# 1. Nạp đồ thị bản đồ
graph = get_graph()

# 2. Danh sách các điểm ngập hiện tại
flood_sources = [
    {"lng": 105.7801, "lat": 21.0372, "depth_cm": 25.0, "threshold_cm": 20.0, "name": "Ngã tư Cầu Giấy"}
]

# 3. Tính toán lộ trình né ngập cho xe máy
result = calculate_routes(
    graph=graph,
    flood_sources=flood_sources,
    origin_lng=105.7820, origin_lat=21.0380,
    dest_lng=105.8120, dest_lat=21.0110,
    vehicle="motorbike",
    use_ai_prediction=True
)

print("Lộ trình né ngập an toàn:", result["safe"]["found"])
print("Khoảng cách (m):", result["safe"]["distance_m"])
print("Thời gian dự kiến (phút):", result["safe"]["duration_min"])
```

---

## 🧪 4. Chạy kiểm thử tự động
```bash
python -m unittest discover -s tests
```

---

## 📄 5. Giấy phép Bản quyền (License)
Dự án được phân phối dưới giấy phép **Apache License 2.0 (OSI-Approved)**. Xem chi tiết tại [LICENSE](LICENSE).
Mọi đóng góp tuân thủ theo [CONTRIBUTING.md](CONTRIBUTING.md).
