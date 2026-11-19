# HƯỚNG DẪN CÀI ĐẶT & ĐÓNG GÓI TỪ MÃ NGUỒN (BUILDING FROM SOURCE)
## GRASSTOUCHER CORE ENGINE (Thuật toán Thủy văn & Định tuyến A*)

> Tài liệu này hướng dẫn cách biên dịch, đóng gói và cài đặt thư viện thuật toán lõi `grasstoucher-core` từ mã nguồn gốc bằng các công cụ chuẩn mở PEP 517 / PEP 621.

---

## 1. YÊU CẦU MÔI TRƯỜNG

* **Python**: `>= 3.10`
* **pip**: `>= 22.0`
* **setuptools**: `>= 61.0` (Trình biên dịch/đóng gói mã nguồn mở chuẩn)

---

## 2. QUY TRÌNH BIÊN DỊCH VÀ CÀI ĐẶT

### Bước 2.1: Tải mã nguồn
```bash
git clone https://github.com/GrassTouchers1/GrassToucher-core.git
cd GrassToucher-core
```

### Bước 2.2: Khởi tạo môi trường ảo độc lập
```bash
python3 -m venv venv
# Linux / macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### Bước 2.3: Cài đặt ở chế độ Phát triển (Editable Mode)
```bash
pip install -e .
```

### Bước 2.4: Đóng gói thành phân phối bánh xe (Wheel) & bản mã nguồn nén (Source Distribution - Tarball)
```bash
pip install build
python -m build
```
Sau khi build, thư mục `dist/` sẽ chứa:
- `grasstoucher_core-1.0.0-py3-none-any.whl` (Chuẩn gói mở Python Wheel)
- `grasstoucher_core-1.0.0.tar.gz` (Chuẩn mã nguồn nén mở Tarball)

---

## 3. KIỂM THỬ ĐƠN VỊ (UNIT TESTS)

Để kiểm chứng thuật toán định tuyến và mô hình hồi quy AI hoạt động chính xác:
```bash
pip install pytest
pytest tests/
```
