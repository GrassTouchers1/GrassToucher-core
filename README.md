# 🌐 NORTHSTAR Core – Multi-Hazard Disaster Intelligence & Evacuation Engine (GrassToucher Core v0.4.0)

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![OSI Approved](https://img.shields.io/badge/OSI-Approved%20Open%20Source-brightgreen.svg)](https://opensource.org/licenses)
[![Changelog](https://img.shields.io/badge/Changelog-Keep%20a%20Changelog-orange.svg)](CHANGELOG.md)
[![Building from Source](https://img.shields.io/badge/Build-From%20Source-blue.svg)](INSTALL.md)
[![Release](https://img.shields.io/badge/Release-v1.0.0-green.svg)](https://github.com/GrassTouchers1/GrassToucher-core/releases)
[![Bug Tracker](https://img.shields.io/badge/Bug%20Tracker-GitHub%20Issues-red.svg)](https://github.com/GrassTouchers1/GrassToucher-core/issues)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![OpenStreetMap](https://img.shields.io/badge/Data-OpenStreetMap-green.svg)](https://www.openstreetmap.org/)
[![Open-Meteo](https://img.shields.io/badge/Weather-Open--Meteo%20API-orange.svg)](https://open-meteo.com/)
[![Scikit-Learn](https://img.shields.io/badge/AI-Scikit--Learn-F7931E.svg?logo=scikit-learn)](https://scikit-learn.org/)
[![Tests: 8/8 Passing](https://img.shields.io/badge/Tests-8%2F8%20Passing-brightgreen.svg)](https://docs.python.org/3/library/unittest.html)

> **Thư viện lõi định tuyến thông minh thích ứng đa thiên tai, cứu hộ sơ tán khẩn cấp và mô hình AI thủy văn học máy.**  
> Đóng gói độc lập theo chuẩn Python Package (Zero-DB Architecture) phục vụ cả hệ thống điều phối tác chiến **NORTHSTAR COMMAND** và ứng dụng cứu trợ dân sự **NORTHSTAR CITIZEN**.

---

## 💡 1. Giới thiệu & Tuyên ngôn Mã nguồn mở

Vào mùa mưa bão tại Việt Nam, các hiện tượng ngập lụt đô thị, sạt lở đất đá và lũ lụt diện rộng gây cô lập nghiêm trọng hạ tầng giao thông.

**NORTHSTAR Core** cung cấp giải pháp thuật toán mã nguồn mở toàn diện:
- **Đồ thị không gian mở:** Trích xuất mạng lưới đường bộ từ **OpenStreetMap (OSM)** thông qua **OSMnx** và **NetworkX**.
- **Thuật toán A\* Đa phương tiện né ngập:** Tự động né các cung đường ngập sâu >20cm (đối với xe máy) và >30cm (đối với xe cơ giới, cứu thương, xe tải cứu trợ 4x4).
- **Thuật toán Định tuyến Sơ tán Khẩn cấp (Multi-target Dijkstra):** Tự động tìm đường thoát nạn ngắn nhất và an toàn nhất từ tọa độ nạn nhân tới điểm trú ẩn an toàn (`evacuation shelter`) gần nhất theo phương thức đi bộ hoặc xe cơ giới.
- **Học máy dự báo ngập 30/60 phút:** Sử dụng mô hình **Gradient Boosting** tích hợp lượng mưa mở theo thời gian thực từ **Open-Meteo API** kèm cơ chế in-memory caching 5 phút tối ưu hiệu năng.
- **Tính toán Lộ trình Tác chiến bàn giao:** Đóng gói thông tin lộ trình khô ráo, an toàn hỗ trợ các lực lượng cứu hộ cơ động (PCCC 114, Cấp cứu 115, Đoàn xe 4x4) tiếp cận hiện trường nhanh nhất.
- **100% Free & Open Source Software (FOSS):** Không sử dụng bất kỳ API trả phí hay cơ sở dữ liệu đóng nào.

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
- Ô tô / Xe tải nhẹ: $\text{limit} = 20 \times 1.5 = 30\text{ cm}$.
- Xe cứu hộ đặc chủng / Xe tải 4x4: $\text{limit} \approx 50\text{ cm}$.
- Hệ số phạt tối đa: $\alpha = 8.0$ (đoạn đường có thể bị tăng chi phí tới 9 lần trước khi bị chặn hẳn).

---

### 2.2. Khớp nối không gian & Chỉ mục R-Tree (Spatial Snapping & Buffering)
- Sử dụng hệ tọa độ mét **UTM 48N (EPSG:32648)** để đảm bảo độ chuẩn xác khoảng cách thực địa tại Việt Nam.
- Điểm ngập được tạo vùng ảnh hưởng (Buffer) bán kính $60\text{ m}$.
- Chỉ mục không gian **R-Tree** (`geopandas`, `shapely.sindex`) cho phép quét và gán trọng số ngập lên hàng chục nghìn đoạn đường trong thời gian tính bằng mili-giây.

---

## 📦 3. Cài đặt & Sử dụng

### 3.1. Cài đặt thư viện
```bash
git clone -b dev https://github.com/GrassTouchers1/GrassToucher-core.git
cd GrassToucher-core

# Cài đặt dạng package phát triển (Editable mode)
pip install -e .
```

### 3.2. Ví dụ code tìm đường Python (A* Né ngập)
```python
from grasstoucher_core import get_graph, calculate_routes

# 1. Nạp đồ thị bản đồ
graph = get_graph()

# 2. Danh sách các điểm ngập hiện tại
flood_sources = [
    {"lng": 105.7801, "lat": 21.0372, "depth_cm": 25.0, "threshold_cm": 20.0, "name": "Ngã tư Cầu Giấy"}
]

# 3. Tính toán lộ trình né ngập cho xe máy / ô tô
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

### 3.3. Ví dụ định tuyến sơ tán khẩn cấp (Emergency Evacuation Routing)
```python
from grasstoucher_core import get_graph, find_evacuation_route

graph = get_graph()

# Danh sách nơi trú ẩn an toàn
shelters = [
    {"id": 1, "name": "Nhà văn hóa Dịch Vọng", "lng": 105.792, "lat": 21.037},
    {"id": 2, "name": "Trường ĐH Quốc gia Hà Nội", "lng": 105.782, "lat": 21.038}
]

# Danh sách vùng thiên tai đang diễn ra
hazard_sources = [
    {"lng": 105.7801, "lat": 21.0372, "hazard_type": "flood", "severity": "danger", "depth_cm": 45.0}
]

# Tìm đường thoát hiểm gần nhất bằng phương thức đi bộ
evac_result = find_evacuation_route(
    graph=graph,
    origin_lng=105.7810, origin_lat=21.0365,
    shelters=shelters,
    hazard_sources=hazard_sources,
    mode="walk"
)

if evac_result["found"]:
    print(f"Điểm sơ tán tối ưu: {evac_result['shelter']['name']}")
    print(f"Khoảng cách đi bộ: {evac_result['distance_m']} m")
    print(f"Thời gian thoát hiểm: {evac_result['duration_min']} phút")
```

---

## 🧪 4. Chạy kiểm thử tự động
```bash
python -m unittest discover -s tests
```
**Kết quả thực tế:**
```text
Ran 8 tests in 2.454s
OK
```

---

## 🌍 5. Danh mục Nguồn Dữ liệu Mở & Tính Pháp lý (Open Data Compliance)

Hệ thống **NORTHSTAR** được thiết kế dựa trên nguyên tắc **100% Minh bạch Khoa học & Dữ liệu Mở Hợp pháp (Open Data & Open Source)**. Dự án hoàn toàn không sử dụng dữ liệu thương mại đóng, tuân thủ nghiêm ngặt các công ước và giấy phép bản quyền:

| STT | Nguồn dữ liệu | Cơ quan / Tổ chức phát hành | Giấy phép / Cơ sở pháp lý | Vai trò kỹ thuật trong NorthStar |
|---|---|---|---|---|
| **1** | [OpenStreetMap (OSM)](https://www.openstreetmap.org) | OpenStreetMap Foundation | **Open Database License (ODbL) 1.0** (Open Data) | Xương sống hình học mạng lưới đường bộ, nút giao thông. Trích xuất đồ thị (Graph) qua OSMnx/NetworkX cho thuật toán tìm đường né ngập $A^*$ và sơ tán Dijkstra. |
| **2** | [Copernicus Data Space](https://dataspace.copernicus.eu) (Sentinel-1 SAR) | European Space Agency (ESA) & European Commission (EC) | **EU Copernicus Full, Free & Open Access Policy** (Regulation EU No 377/2014) | Viễn thám radar khẩu độ tổng hợp băng C xuyên mây bão 24/7, bóc tách vết ngập nước (Water Inundation Mask) để tự động khoanh vùng rủi ro đa thiên tai (Multi-Hazard Zones). |
| **3** | [Copernicus GloFAS](https://global-flood.emergency.copernicus.eu/) | Trung tâm Khí tượng Châu Âu (ECMWF) & Copernicus Emergency Management Service | **Copernicus Open Access License** | Dự báo lưu lượng dòng chảy và cảnh báo ngập lụt sớm trên các lưu vực sông Hồng và sông Mê Kông theo chuẩn mở quốc tế. |
| **4** | [NASA GPM IMERG](https://gpm.nasa.gov/data) | Cơ quan Hàng không Vũ trụ Mỹ (NASA) | **NASA Open Data Policy** | Giám sát cường độ mưa vệ tinh toàn cầu gần thời gian thực phục vụ cảnh báo sớm nguy cơ lũ quét và lũ thượng nguồn. |
| **5** | [Open-Meteo Weather API](https://open-meteo.com) | Open-Meteo Inc. | **Creative Commons Attribution 4.0 (CC-BY 4.0)** | Lượng mưa thực tế theo giờ (mm/h) tại các tọa độ trạm quan trắc nạp vào mô hình máy học Gradient Boosting dự báo mực nước dâng sau 30/60 phút. |

---

## 📄 6. Tuyên Bố Giấy Phép & Tuân Thủ Chuẩn Mã Nguồn Mở (OSI & PoF Compliance)

Toàn bộ gói thuật toán lõi được phát triển và kiểm định theo chuẩn mở:
- ⚖️ **Giấy phép phần mềm:** [Apache License 2.0](LICENSE) (OSI-Approved, `SPDX-License-Identifier: Apache-2.0` gắn trên từng tệp mã nguồn).
- 📋 **Báo cáo kiểm định bản quyền:** [docs/LICENSE_AUDIT.md](docs/LICENSE_AUDIT.md).
- 📦 **Hướng dẫn dịch & cài đặt từ mã nguồn sạch:** [INSTALL.md](INSTALL.md).
- 📝 **Lịch sử phiên bản phát hành:** [CHANGELOG.md](CHANGELOG.md) (Chuẩn Keep a Changelog v1.1.0 & Semantic Versioning v2.0.0).
- 🤝 **Quy chuẩn đóng góp:** [CONTRIBUTING.md](CONTRIBUTING.md).
- 🐛 **Hệ thống Quản lý Lỗi (Bug Tracker):** Tiếp nhận tại [GitHub Issues](https://github.com/GrassTouchers1/GrassToucher-core/issues) với Issue Templates chuẩn trong `.github/ISSUE_TEMPLATE/`.
- 🏷️ **Bản phát hành chính thức dự thi:** [Release v1.0.0](https://github.com/GrassTouchers1/GrassToucher-core/releases/tag/v1.0.0).
