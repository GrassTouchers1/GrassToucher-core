# Quy định Đóng góp Mã Nguồn Mở (Contributing Guidelines)

Dự án **GrassToucher Core** là phần mềm mã nguồn mở tự do được phát hành theo giấy phép **Apache License 2.0 (OSI-Approved)**. Chúng tôi luôn hoan nghênh và đánh giá cao mọi sự đóng góp từ cộng đồng nhà phát triển, nhà nghiên cứu thủy văn và sinh viên yêu thích công nghệ mở!

---

## 📜 1. Nguyên tắc Mã Nguồn Mở (FOSS Principles)
- **100% Công nghệ mở:** Mọi thư viện bổ sung phải có giấy phép tương thích mã nguồn mở (MIT, Apache 2.0, BSD, GPL, LGPL). Tuyệt đối không tích hợp thư viện độc quyền hoặc phụ thuộc API thương mại đóng.
- **Minh bạch & Tái sử dụng:** Mã nguồn phải được viết rõ ràng, có docstrings, chú thích công thức toán học/thủy văn đầy đủ.

---

## 🛠️ 2. Quy trình Đóng góp (Workflow)

1. **Fork** repository này về tài khoản GitHub của bạn.
2. Tạo nhánh tính năng mới:
   ```bash
   git checkout -b feature/ten-tinh-nang-moi
   ```
3. Cài đặt môi trường phát triển:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Trên Windows: .\venv\Scripts\activate
   pip install -e .
   ```
4. Viết code và viết Unit Test bổ sung trong thư mục `tests/`.
5. Đảm bảo mọi kiểm thử đều vượt qua:
   ```bash
   python -m unittest discover -s tests
   ```
6. Commit thay đổi với thông điệp rõ ràng theo chuẩn Conventional Commits:
   ```bash
   git commit -m "feat(routing): cai thien toc do tinh toan A* tren do thi lon"
   ```
7. Đẩy lên remote và tạo **Pull Request (PR)** vào nhánh `main` của repository gốc.

---

## ⚖️ 3. Quy tắc Ứng xử (Code of Conduct)
Chúng tôi cam kết xây dựng một môi trường đóng góp mã nguồn mở thân thiện, tôn trọng và hòa nhập cho tất cả mọi người. Mọi hành vi thiếu văn hóa hoặc vi phạm tiêu chuẩn cộng đồng sẽ bị từ chối.
