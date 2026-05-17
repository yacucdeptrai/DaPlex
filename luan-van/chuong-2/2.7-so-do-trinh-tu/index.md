# 2.7. Sơ Đồ Tuần Tự

Sơ đồ tuần tự (Sequence Diagram) mô tả tương tác giữa các đối tượng (objects/components) theo trục thời gian — mỗi đường thẳng đứng đại diện cho một lifeline của một thành phần, và các mũi tên ngang biểu thị message trao đổi theo thứ tự thời gian từ trên xuống dưới. Phương pháp này phù hợp để thể hiện luồng request-response qua nhiều lớp component và các tương tác bất đồng bộ.

Hai luồng đã được mô tả bằng Sequence Diagram ở các mục trước:
- **Hình 2.2** (mục 2.3.1): Luồng đăng ký, xác thực email, đăng nhập và tự động gia hạn phiên — thể hiện tương tác giữa Angular PWA, DaPlex-API, MongoDB, và Email Service
- **Hình 2.3** (mục 2.3.2): Luồng upload file nguồn và kích hoạt encode — thể hiện tương tác giữa Admin Angular, DaPlex-API, Redis BullMQ, DaPlex-Transcoder, và Cloud Storage

Mục này bổ sung thêm hai sequence diagram cho các luồng còn lại:

---

## Mục lục

- [2.7.1. Sơ đồ tuần tự — Phát video với ABR](2.7.1-phat-video-abr.md)
- [2.7.2. Sơ đồ tuần tự — Cấp phát và kiểm tra phân quyền](2.7.2-phan-quyen-rbac.md)
