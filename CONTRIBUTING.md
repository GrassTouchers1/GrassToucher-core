# Quy định Đóng góp Mã Nguồn Mở (Contributing Guidelines)

Gói thuật toán **grasstoucher-core** là thư viện Python mã nguồn mở, được phát hành theo giấy phép **Apache License 2.0 (OSI-Approved)**.

---

## 📜 1. Tiêu chuẩn Mã Nguồn
- Tuân thủ chuẩn định dạng mã nguồn PEP 8.
- Mọi hàm thuật toán đồ thị và hàm hồi quy AI mới phải có Unit Test đi kèm trong thư mục `tests/`.
- Đóng gói chuẩn PEP 517 / PEP 621 (`pyproject.toml`).

---

## 🛠️ 2. Hướng dẫn Phát triển
1. **Clone & Cài đặt môi trường phát triển (Editable):**
   ```bash
   git clone https://github.com/GrassTouchers1/GrassToucher-core.git
   cd GrassToucher-core
   pip install -e .
   ```
2. **Kiểm thử:**
   ```bash
   pytest tests/
   ```

---

## 🐛 3. Hệ thống Quản lý Lỗi Phần mềm (Bug Tracker)
- 🔗 **Kho quản lý lỗi:** [https://github.com/GrassTouchers1/GrassToucher-core/issues](https://github.com/GrassTouchers1/GrassToucher-core/issues)
- Vui lòng sử dụng GitHub Issues để báo cáo lỗi thuật toán, sai lệch trọng số thủy văn hoặc ngoại lệ đồ thị.
