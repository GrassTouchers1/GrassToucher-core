# Changelog

Tất cả các thay đổi đáng chú ý của gói thư viện thuật toán **NORTHSTAR Core Engine (grasstoucher-core)** sẽ được ghi lại trong tệp này.

Định dạng dựa trên [Keep a Changelog](https://keepachangelog.com/vi/1.1.0/),
và dự án này tuân thủ [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-11-19 (Bản nộp chính thức Olympic Tin học Sinh viên - PMNM)

### Đã thêm (Added)
- **Thuật toán Định tuyến A* Thích ứng Thủy văn (Dynamic Hydrodynamic A* Routing)**: Tính toán hàm chi phí đường đi dựa trên:
  - Chiều dài thực tế của đoạn đường (từ đồ thị giao thông OpenStreetMap).
  - Độ sâu ngập lụt dự báo hoặc báo cáo từ trạm đo.
  - Ngưỡng chịu ngập của phương tiện di chuyển (xe máy: 25cm, ô tô: 40cm, xuồng cứu hộ: ngược lại cần nước sâu tối thiểu 20cm).
- **Mô hình Dự báo Mực nước AI (AI Water Level Prediction)**: Sử dụng mô hình hồi quy Gradient Boosting / Random Forest huấn luyện trên dữ liệu lượng mưa tích lũy và địa hình lưu vực.
- **Hệ thống Kiểm thử Tự động (Automated Test Suite)**: Bao gồm bộ test đơn vị và test tích hợp cho thuật toán đồ thị và mô hình AI.

### Đã thay đổi (Changed)
- **Đóng gói chuẩn PEP 517/PEP 621**: Cấu hình tệp `pyproject.toml` hiện đại, cho phép cài đặt phân phối bằng lệnh `pip install -e .` sạch 100%.
- **Thống nhất bản quyền**: Toàn bộ module lõi được cấp phép chính thức theo **Apache License 2.0 (OSI Approved)**.
- Gắn thẻ bản quyền mã nguồn chuẩn `SPDX-License-Identifier: Apache-2.0` trên từng tệp mã.

---

## [0.4.0] - 2026-11-15

### Đã thêm (Added)
- Xây dựng đồ thị mạng lưới đường giao thông từ OSMnx cho khu vực miền Bắc Việt Nam.
- Thiết lập cấu trúc dữ liệu `RoadGraph` lưu đệm đồ thị định tuyến.

---

## [0.1.0] - 2026-10-20

### Đã thêm (Added)
- Bản khởi tạo đầu tiên của thuật toán A* cơ bản trên đồ thị NetworkX.
