# 1.6. Công Nghệ Sử Dụng

DaPlex được xây dựng trên một stack công nghệ hiện đại, được lựa chọn có chủ đích để đáp ứng các yêu cầu đặc thù của hệ thống VoD tự lưu trữ: xử lý bất đồng bộ khối lượng lớn tác vụ encode chạy nền, phục vụ đồng thời nhiều yêu cầu streaming từ client, và cung cấp giao diện người dùng phản hồi nhanh tương đương ứng dụng native. Mỗi công nghệ trong stack được chọn dựa trên sự cân nhắc kỹ lưỡng giữa khả năng kỹ thuật, hệ sinh thái thư viện, và sự phù hợp với kiến trúc tổng thể của hệ thống. Phần này trình bày chi tiết từng công nghệ cốt lõi — từ framework frontend Angular cho đến bộ encode FFmpeg — bao gồm lý do lựa chọn, cơ chế hoạt động, và cách chúng tích hợp với nhau trong DaPlex.

---

## Mục lục

- [1.6.1. Angular](1.6.1-angular.md)
- [1.6.2. NestJS và Fastify](1.6.2-nestjs-fastify.md)
- [1.6.3. MongoDB và Mongoose](1.6.3-mongodb-mongoose.md)
- [1.6.4. Redis và BullMQ](1.6.4-redis-bullmq.md)
- [1.6.5. FFmpeg](1.6.5-ffmpeg.md)
