# 2.6. Sơ Đồ Hoạt Động

Sơ đồ hoạt động (Activity Diagram) mô tả luồng điều khiển của các tiến trình nghiệp vụ trong DaPlex theo góc nhìn hành động — tập trung vào *những gì xảy ra* và *theo thứ tự nào*, kể cả các nhánh điều kiện (decision) và luồng song song (fork/join). Khác với Biểu đồ Use Case (mục 2.5) mô tả *ai làm gì*, và Sơ đồ Tuần tự (mục 2.7) mô tả *component nào giao tiếp với nhau*, Activity Diagram phù hợp để mô tả logic điều khiển có nhiều điều kiện rẽ nhánh và các vòng lặp xử lý lỗi — điển hình là luồng xác thực người dùng và pipeline encode video.

Hai luồng được chọn để mô hình hóa là hai tiến trình có độ phức tạp điều khiển cao nhất của hệ thống:

---

## Mục lục

- [2.6.1. Sơ đồ hoạt động — Đăng nhập và xác thực](2.6.1-dang-nhap-xac-thuc.md)
- [2.6.2. Sơ đồ hoạt động — Upload và encode video](2.6.2-upload-encode.md)
