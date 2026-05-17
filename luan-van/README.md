# Luận Văn Tốt Nghiệp — DaPlex: Hệ Thống Xem Phim Trực Tuyến

> **Đề tài:** Xây dựng hệ thống xem phim trực tuyến với tính năng Adaptive Bitrate Streaming  
> **Công nghệ:** Angular · NestJS · MongoDB · Redis · FFmpeg · MPEG-DASH

---

## Mục Lục

### Mở Đầu
- [1. Lý do chọn đề tài](mo-dau/1-ly-do-chon-de-tai.md)
- [2. Tổng quan tình hình nghiên cứu](mo-dau/2-tong-quan-tinh-hinh-nghien-cuu/index.md)
  - [2.1. Xu hướng phát triển streaming tự quản lý](mo-dau/2-tong-quan-tinh-hinh-nghien-cuu/2.1-xu-huong-phat-trien-streaming.md)
  - [2.2. Các hệ thống self-hosted hiện có](mo-dau/2-tong-quan-tinh-hinh-nghien-cuu/2.2-cac-he-thong-self-hosted.md)
  - [2.3. Tình hình nghiên cứu về ABR Streaming](mo-dau/2-tong-quan-tinh-hinh-nghien-cuu/2.3-tinh-hinh-nghien-cuu-abr.md)
  - [2.4. Khoảng trống nghiên cứu](mo-dau/2-tong-quan-tinh-hinh-nghien-cuu/2.4-khoang-trong-nghien-cuu.md)
- [3. Mục tiêu nghiên cứu](mo-dau/3-muc-tieu-nghien-cuu/index.md)
  - [3.1. Mục tiêu tổng quát](mo-dau/3-muc-tieu-nghien-cuu/3.1-muc-tieu-tong-quat.md)
  - [3.2. Mục tiêu cụ thể](mo-dau/3-muc-tieu-nghien-cuu/3.2-muc-tieu-cu-the.md)
  - [3.3. Phạm vi và kết quả mong đợi](mo-dau/3-muc-tieu-nghien-cuu/3.3-pham-vi-ket-qua-mong-doi.md)
- [4. Đối tượng và phạm vi nghiên cứu](mo-dau/4-doi-tuong-pham-vi/index.md)
  - [4.1. Đối tượng nghiên cứu](mo-dau/4-doi-tuong-pham-vi/4.1-doi-tuong-nghien-cuu.md)
  - [4.2. Phạm vi nghiên cứu](mo-dau/4-doi-tuong-pham-vi/4.2-pham-vi-nghien-cuu.md)
- [5. Phương pháp thực hiện](mo-dau/5-phuong-phap-thuc-hien/index.md)
  - [5.1. Phương pháp nghiên cứu lý thuyết](mo-dau/5-phuong-phap-thuc-hien/5.1-phuong-phap-nghien-cuu-ly-thuyet.md)
  - [5.2. Phương pháp phát triển phần mềm](mo-dau/5-phuong-phap-thuc-hien/5.2-phuong-phap-phat-trien-phan-mem.md)
  - [5.3. Phương pháp triển khai và tích hợp](mo-dau/5-phuong-phap-thuc-hien/5.3-phuong-phap-trien-khai-tich-hop.md)
  - [5.4. Phương pháp kiểm thử và đánh giá](mo-dau/5-phuong-phap-thuc-hien/5.4-phuong-phap-kiem-thu-danh-gia.md)
- [6. Ý nghĩa khoa học và thực tiễn của đề tài](mo-dau/6-y-nghia-de-tai/index.md)
  - [6.1. Ý nghĩa khoa học](mo-dau/6-y-nghia-de-tai/6.1-y-nghia-khoa-hoc.md)
  - [6.2. Ý nghĩa thực tiễn](mo-dau/6-y-nghia-de-tai/6.2-y-nghia-thuc-tien.md)
- [7. Cấu trúc của đồ án](mo-dau/7-cau-truc-do-an.md)

---

### Chương 1: Tổng Quan Và Cơ Sở Lý Thuyết
- [1.1. Tổng quan hệ thống xem phim trực tuyến](chuong-1/1.1-tong-quan-he-thong-xem-phim/index.md)
  - [1.1.1. Định nghĩa và phân loại](chuong-1/1.1-tong-quan-he-thong-xem-phim/1.1.1-dinh-nghia-va-phan-loai.md)
  - [1.1.2. Mô hình hoạt động của hệ thống VoD](chuong-1/1.1-tong-quan-he-thong-xem-phim/1.1.2-mo-hinh-hoat-dong-vod.md)
  - [1.1.3. Các thành phần cơ bản của hệ thống streaming](chuong-1/1.1-tong-quan-he-thong-xem-phim/1.1.3-cac-thanh-phan-co-ban.md)
- [1.2. Một số nền tảng phổ biến](chuong-1/1.2-nen-tang-pho-bien.md)
- [1.3. Công nghệ truyền phát video](chuong-1/1.3-cong-nghe-truyen-phat-video.md)
- [1.4. Kỹ thuật Adaptive Bitrate Streaming](chuong-1/1.4-adaptive-bitrate-streaming.md)
- [1.5. Giao thức streaming phổ biến](chuong-1/1.5-giao-thuc-streaming.md)
- [1.6. Công nghệ sử dụng](chuong-1/1.6-cong-nghe-su-dung/index.md)
  - [1.6.1. Angular](chuong-1/1.6-cong-nghe-su-dung/1.6.1-angular.md)
  - [1.6.2. NestJS và Fastify](chuong-1/1.6-cong-nghe-su-dung/1.6.2-nestjs-fastify.md)
  - [1.6.3. MongoDB và Mongoose](chuong-1/1.6-cong-nghe-su-dung/1.6.3-mongodb-mongoose.md)
  - [1.6.4. Redis và BullMQ](chuong-1/1.6-cong-nghe-su-dung/1.6.4-redis-bullmq.md)
  - [1.6.5. FFmpeg](chuong-1/1.6-cong-nghe-su-dung/1.6.5-ffmpeg.md)
- [1.7. Bảo mật nội dung số](chuong-1/1.7-bao-mat-noi-dung-so.md)

---

### Chương 2: Phân Tích Hệ Thống
- [2.1. Khảo sát nhu cầu người dùng](chuong-2/2.1-khao-sat-nhu-cau.md)
- [2.2. Tác nhân hệ thống](chuong-2/2.2-tac-nhan-he-thong.md)
- [2.3. Yêu cầu chức năng](chuong-2/2.3-yeu-cau-chuc-nang/index.md)
  - [2.3.1. Yêu cầu chức năng — Người dùng thông thường](chuong-2/2.3-yeu-cau-chuc-nang/2.3.1-nguoi-dung.md)
  - [2.3.2. Yêu cầu chức năng — Quản trị viên](chuong-2/2.3-yeu-cau-chuc-nang/2.3.2-quan-tri-vien.md)
- [2.4. Yêu cầu phi chức năng](chuong-2/2.4-yeu-cau-phi-chuc-nang.md)
- [2.5. Biểu đồ Use Case](chuong-2/2.5-bieu-do-use-case/index.md)
  - [2.5.1. Biểu đồ Use Case tổng quan](chuong-2/2.5-bieu-do-use-case/2.5.1-tong-quan.md)
  - [2.5.2. Biểu đồ Use Case — Người dùng thông thường](chuong-2/2.5-bieu-do-use-case/2.5.2-nguoi-dung.md)
  - [2.5.3. Biểu đồ Use Case — Quản trị viên](chuong-2/2.5-bieu-do-use-case/2.5.3-quan-tri-vien.md)
- [2.6. Sơ đồ hoạt động](chuong-2/2.6-so-do-hoat-dong/index.md)
  - [2.6.1. Sơ đồ hoạt động — Đăng nhập và xác thực](chuong-2/2.6-so-do-hoat-dong/2.6.1-dang-nhap-xac-thuc.md)
  - [2.6.2. Sơ đồ hoạt động — Upload và encode video](chuong-2/2.6-so-do-hoat-dong/2.6.2-upload-encode.md)
- [2.7. Sơ đồ tuần tự](chuong-2/2.7-so-do-trinh-tu/index.md)
  - [2.7.1. Sơ đồ tuần tự — Phát video với ABR](chuong-2/2.7-so-do-trinh-tu/2.7.1-phat-video-abr.md)
  - [2.7.2. Sơ đồ tuần tự — Cấp phát và kiểm tra phân quyền RBAC](chuong-2/2.7-so-do-trinh-tu/2.7.2-phan-quyen-rbac.md)
- [2.8. Đặc tả Use Case](chuong-2/2.8-dac-ta-use-case/index.md)
  - [2.8.1. UC-U-02 — Đăng nhập và quản lý phiên](chuong-2/2.8-dac-ta-use-case/2.8.1-dang-nhap.md)
  - [2.8.2. UC-U-01, UC-U-03 — Đăng ký và khôi phục mật khẩu](chuong-2/2.8-dac-ta-use-case/2.8.2-dang-ky-khoi-phuc.md)
  - [2.8.3. UC-U-04, UC-U-05, UC-U-06 — Duyệt catalog, phát video, lịch sử](chuong-2/2.8-dac-ta-use-case/2.8.3-duyet-phat-lich-su.md)
  - [2.8.4. UC-U-07, UC-U-08, UC-U-09 — Playlist, đánh giá, hồ sơ](chuong-2/2.8-dac-ta-use-case/2.8.4-playlist-danh-gia-ho-so.md)
  - [2.8.5. UC-A-01, UC-A-03 đến UC-A-06 — Quản lý catalog và nội dung](chuong-2/2.8-dac-ta-use-case/2.8.5-quan-ly-catalog.md)
  - [2.8.6. UC-A-02 — Upload file nguồn và kích hoạt encode](chuong-2/2.8-dac-ta-use-case/2.8.6-upload-encode.md)
  - [2.8.7. UC-A-07 đến UC-A-10 — Vận hành hệ thống](chuong-2/2.8-dac-ta-use-case/2.8.7-van-hanh-he-thong.md)

---

### Chương 3: Thiết Kế Hệ Thống
- [3.1. Kiến trúc tổng thể](chuong-3/3.1-kien-truc-tong-the/index.md)
  - [3.1.1. Kiến trúc hệ thống tổng quan](chuong-3/3.1-kien-truc-tong-the/3.1.1-kien-truc-he-thong.md)
  - [3.1.2. Kiến trúc Backend API](chuong-3/3.1-kien-truc-tong-the/3.1.2-kien-truc-backend.md)
  - [3.1.3. Kiến trúc Transcoder](chuong-3/3.1-kien-truc-tong-the/3.1.3-kien-truc-transcoder.md)
- [3.2. Thiết kế cơ sở dữ liệu](chuong-3/3.2-thiet-ke-co-so-du-lieu.md)
- [3.3. ERD Diagram](chuong-3/3.3-erd-diagram.md)
- [3.4. Thiết kế giao diện](chuong-3/3.4-thiet-ke-giao-dien/index.md)
  - [3.4.1. Giao diện người dùng](chuong-3/3.4-thiet-ke-giao-dien/3.4.1-giao-dien-nguoi-dung.md)
  - [3.4.2. Giao diện quản trị viên](chuong-3/3.4-thiet-ke-giao-dien/3.4.2-giao-dien-admin.md)
- [3.5. Thiết kế cơ chế tự động chỉnh độ nét](chuong-3/3.5-co-che-tu-dong-chinh-do-net/index.md)
  - [3.5.1. Cấu trúc file DASH](chuong-3/3.5-co-che-tu-dong-chinh-do-net/3.5.1-cau-truc-file-dash.md)
  - [3.5.2. Stream Manifest](chuong-3/3.5-co-che-tu-dong-chinh-do-net/3.5.2-stream-manifest.md)
  - [3.5.3. Chuyển đổi Manifest sang DASH](chuong-3/3.5-co-che-tu-dong-chinh-do-net/3.5.3-chuyen-doi-manifest-sang-dash.md)
  - [3.5.4. Cấu hình dash.js và BOLA](chuong-3/3.5-co-che-tu-dong-chinh-do-net/3.5.4-cau-hinh-dashjs-va-bola.md)
  - [3.5.5. Lựa chọn codec AV1](chuong-3/3.5-co-che-tu-dong-chinh-do-net/3.5.5-lua-chon-codec-av1.md)
  - [3.5.6. Chọn chất lượng thủ công](chuong-3/3.5-co-che-tu-dong-chinh-do-net/3.5.6-chon-chat-luong-thu-cong.md)
  - [3.5.7. Tóm tắt luồng ABR](chuong-3/3.5-co-che-tu-dong-chinh-do-net/3.5.7-tom-tat-luong.md)
- [3.6. Thuật toán chọn độ nét (BOLA)](chuong-3/3.6-thuat-toan-chon-do-net/index.md)
  - [3.6.1. Lớp tĩnh — Thuật toán encode-time](chuong-3/3.6-thuat-toan-chon-do-net/3.6.1-lop-tinh-encode.md)
  - [3.6.2. Lớp động — Thuật toán BOLA](chuong-3/3.6-thuat-toan-chon-do-net/3.6.2-lop-dong-bola.md)
  - [3.6.3. Lựa chọn quality thủ công](chuong-3/3.6-thuat-toan-chon-do-net/3.6.3-lua-chon-thu-cong.md)
  - [3.6.4. Tổng hợp hai lớp thuật toán](chuong-3/3.6-thuat-toan-chon-do-net/3.6.4-tong-hop.md)

---

### Chương 4: Xây Dựng Và Triển Khai Hệ Thống
- [4.1. Môi trường phát triển](chuong-4/4.1-moi-truong-phat-trien.md)
- [4.2. Xây dựng frontend](chuong-4/4.2-xay-dung-frontend/index.md)
  - [4.2.1. Cấu trúc dự án Angular](chuong-4/4.2-xay-dung-frontend/4.2.1-cau-truc-du-an-angular.md)
  - [4.2.2. Module và routing](chuong-4/4.2-xay-dung-frontend/4.2.2-module-va-routing.md)
  - [4.2.3. Trình phát video](chuong-4/4.2-xay-dung-frontend/4.2.3-trinh-phat-video.md)
- [4.3. Xây dựng backend API](chuong-4/4.3-xay-dung-backend-api/index.md)
  - [4.3.1. Cấu trúc dự án NestJS](chuong-4/4.3-xay-dung-backend-api/4.3.1-cau-truc-du-an-nestjs.md)
  - [4.3.2. Module xác thực và phân quyền](chuong-4/4.3-xay-dung-backend-api/4.3.2-module-xac-thuc.md)
  - [4.3.3. Module quản lý media](chuong-4/4.3-xay-dung-backend-api/4.3.3-module-quan-ly-media.md)
  - [4.3.4. Tích hợp external storage](chuong-4/4.3-xay-dung-backend-api/4.3.4-external-storage.md)
  - [4.3.5. Hệ thống thông báo real-time](chuong-4/4.3-xay-dung-backend-api/4.3.5-websocket-notification.md)
- [4.4. Xây dựng DaPlex-Transcoder (Media Server)](chuong-4/4.4-xay-dung-transcoder.md)
- [4.5. Pipeline encode video đa codec với FFmpeg](chuong-4/4.5-encode-video-ffmpeg/index.md)
  - [4.5.1. Tham số encode và chiến lược chất lượng](chuong-4/4.5-encode-video-ffmpeg/4.5.1-tham-so-encode.md)
  - [4.5.2. Encode âm thanh đa kênh](chuong-4/4.5-encode-video-ffmpeg/4.5.2-encode-am-thanh.md)
  - [4.5.3. Đóng gói CMAF và StreamManifest](chuong-4/4.5-encode-video-ffmpeg/4.5.3-dong-goi-cmaf.md)
  - [4.5.4. Split encoding mode](chuong-4/4.5-encode-video-ffmpeg/4.5.4-split-encoding.md)
  - [4.5.5. HDR metadata và thumbnail sprite](chuong-4/4.5-encode-video-ffmpeg/4.5.5-hdr-thumbnail.md)
- [4.6. Tích hợp rclone — Lớp trừu tượng cloud storage](chuong-4/4.6-dash-packaging-rclone.md)
- [4.7. Adaptive Bitrate Streaming — Tái tạo manifest và phát video phía client](chuong-4/4.7-adaptive-bitrate-streaming.md)
- [4.8. Các chức năng chính đã hoàn thành](chuong-4/4.8-cac-chuc-nang-chinh.md)
- [4.9. Triển khai Cloud / VPS](chuong-4/4.9-trien-khai-cloud-vps.md)
- [4.10. Demo giao diện hệ thống](chuong-4/4.10-demo-giao-dien.md)

---

### Chương 5: Kiểm Thử
- [5.1. Kiểm thử chức năng](chuong-5/5.1-kiem-thu-chuc-nang.md)
- [5.2. Kiểm thử kỹ thuật ABR](chuong-5/5.2-kiem-thu-abr.md)
- [5.3. Kiểm thử nhiều môi trường mạng](chuong-5/5.3-kiem-thu-moi-truong-mang.md)

---

### Kết Luận Và Hướng Phát Triển
- [Tổng quan](ket-luan-va-huong-phat-trien/index.md)
  - [1. Kết luận chung](ket-luan-va-huong-phat-trien/1-ket-luan-chung.md)
  - [2. Đóng góp và điểm mới](ket-luan-va-huong-phat-trien/2-dong-gop-diem-moi.md)
  - [3. Hạn chế](ket-luan-va-huong-phat-trien/3-han-che.md)
  - [4. Định hướng phát triển](ket-luan-va-huong-phat-trien/4-dinh-huong-phat-trien.md)
