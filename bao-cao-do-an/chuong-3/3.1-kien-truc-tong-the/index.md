# 3.1. Kiến Trúc Tổng Thể

Kiến trúc của DaPlex được thiết kế xoay quanh một nguyên tắc trung tâm: **phân tách trách nhiệm theo năng lực phần cứng**. Pipeline xử lý video — vốn là tác vụ nặng về CPU — không được phép cạnh tranh tài nguyên với API phục vụ hàng trăm request HTTP đồng thời. Trình phát video — vốn phát sinh lưu lượng mạng lớn — không được phép đi qua tầng ứng dụng nếu có thể offload sang cloud storage. Những ràng buộc thiết kế này dẫn đến một kiến trúc ba thành phần độc lập có thể triển khai và mở rộng riêng biệt: `DaPlex-API`, `DaPlex-Transcoder`, và `daplex-dune-v2` (Angular PWA).

Toàn bộ hệ thống được tổ chức trong một **umbrella repository dạng git submodule**, cho phép từng thành phần có vòng đời phát triển và triển khai độc lập trong khi vẫn duy trì một điểm kiểm soát version chung. Đây là lựa chọn khác biệt so với kiến trúc monorepo: mỗi submodule có `package.json`, `node_modules`, và cấu hình CI/CD riêng, phản ánh thực tế là Transcoder thường cần một máy chủ riêng với nhiều CPU hơn so với máy chủ API.

Mục này đi sâu vào ba khía cạnh kiến trúc: tổng quan toàn hệ thống, kiến trúc nội bộ của DaPlex-API, và kiến trúc pipeline xử lý của DaPlex-Transcoder.

---

## Các Thành Phần Chính

Hệ thống DaPlex bao gồm bốn thành phần kỹ thuật có thể phân vùng triển khai:

**DaPlex-API** là NestJS 10 service đóng vai trò trung tâm điều phối. Toàn bộ nghiệp vụ — xác thực, phân quyền, quản lý metadata, orchestrate encode job — được xử lý tại đây. API expose bề mặt dưới prefix `/api` với 17 resource module đăng ký qua `AppRoutingModule`. Fastify adapter thay thế Express mặc định của NestJS để đạt throughput cao hơn cho workload JSON-heavy.

**DaPlex-Transcoder** là NestJS 10 worker service chạy hoàn toàn tách biệt, không expose HTTP endpoint ra ngoài (ngoại trừ endpoint health check nội bộ). Transcoder lắng nghe BullMQ queue trên Redis, thực thi pipeline FFmpeg+MP4Box, và báo cáo kết quả ngược về API. Cơ chế phân tách này cho phép Transcoder chạy trên một máy chủ khác với cấu hình CPU cao hơn, trong khi API tiếp tục phục vụ trên VPS nhỏ.

**daplex-dune-v2** là Angular 21 PWA phục vụ cả người dùng thông thường lẫn giao diện quản trị. Frontend giao tiếp với DaPlex-API qua REST/HTTP và nhận cập nhật realtime qua WebSocket. Điểm đáng chú ý là frontend **không bao giờ nhận segment video từ API** — sau khi lấy MPD URL từ API, trình phát dash.js 5.0.0 kéo segment trực tiếp từ cloud storage provider, hoàn toàn bypass API server.

**Redis** đóng ba vai trò song song trong hệ thống: (1) backend cho BullMQ queue (`REDIS_QUEUE_URL`) chứa encode job; (2) application cache tầng thứ hai — `Redis2ndCacheModule` lưu dữ liệu user, rate limit counters; (3) Pub/Sub bus — `RedisPubSubModule` phát tín hiệu hủy job (`video-cancel` channel) từ API đến Transcoder đang chạy. Ba vai trò này được cấu hình trên các database index khác nhau và được import qua ba module NestJS riêng biệt để tránh coupling.

---

## Luồng Dữ Liệu Chính

Có ba luồng dữ liệu chính trong hệ thống, mỗi luồng phản ánh một trade-off thiết kế rõ ràng:

**Luồng phát video** (data plane): Client → API (`GET /api/media/:id/movie/streams`) → nhận MPD URL → dash.js tải segment trực tiếp từ cloud storage → hardware decoder. API hoàn toàn không tham gia vào data plane. Lưu lượng segment có thể đạt vài MB/giây cho một client 4K; việc offload hoàn toàn sang cloud storage/CDN là yếu tố quyết định cho phép một VPS nhỏ (~2 vCPU, 4 GB RAM) phục vụ hàng chục luồng đồng thời.

**Luồng encode** (async pipeline): Admin xác nhận upload session → API đẩy job vào BullMQ Redis queue → Transcoder consumer nhận job → tải file nguồn qua Rclone → FFmpeg encode → MP4Box package → upload segment lên cloud storage qua Rclone → gọi API để cập nhật `Media` document. Progress event được BullMQ relay ngược về API, API đẩy đến client qua WebSocket `WsAdminModule`.

**Luồng metadata** (control plane): Mọi thao tác CRUD trên nội dung, người dùng, vai trò, và cấu hình đều đi qua API REST. MongoDB lưu trạng thái bền vững; Redis2ndCache giảm latency cho các read-heavy operation (profile lookup, permission check). Access token HS256 5 phút + refresh token nanoid(32) 30 ngày (lưu trong Redis) bảo vệ toàn bộ control plane.

---

## Quan Hệ Giữa Các Thành Phần

<!-- FIGURE
  id: Hình 3.1
  title: Kiến trúc tổng thể hệ thống DaPlex — luồng dữ liệu và kênh giao tiếp
  type: architecture-diagram
  description: >
    Sơ đồ kiến trúc tổng thể thể hiện bốn thành phần chính của DaPlex và ba luồng dữ liệu.
    Thành phần: Angular PWA (daplex-dune-v2), DaPlex-API, DaPlex-Transcoder, Redis, MongoDB, Cloud Storage.
    Ba luồng: (1) Phát video: Client → API (MPD URL) → dash.js kéo segment thẳng từ Cloud Storage, bypass API;
    (2) Encode: API → Redis BullMQ → Transcoder → Cloud Storage; progress event ngược về API → WebSocket → Client;
    (3) Control: Client ↔ API ↔ MongoDB; token trong Redis2ndCache.
    Chú ý: Mũi tên segment video (đường nét đứt) đi thẳng từ Cloud Storage đến dash.js, không qua API.
  nodes:
    - Angular PWA →|REST HTTP Bearer JWT| DaPlex-API
    - Angular PWA →|WebSocket| WsAdminModule (trong DaPlex-API)
    - DaPlex-API →|CRUD| MongoDB (DATABASE_A + DATABASE_B)
    - DaPlex-API →|GET/SET cache, rate-limit| Redis (Redis2ndCacheModule)
    - DaPlex-API →|addJob H264/H265/VP9/AV1| Redis BullMQ (REDIS_QUEUE_URL)
    - DaPlex-API →|PUBLISH video-cancel| Redis PubSub (RedisPubSubModule)
    - Redis BullMQ →|job dispatch| DaPlex-Transcoder
    - DaPlex-Transcoder →|SUBSCRIBE video-cancel| Redis PubSub
    - DaPlex-Transcoder →|upload/download via Rclone| Cloud Storage
    - DaPlex-Transcoder →|PATCH Media status| DaPlex-API
    - DaPlex-Transcoder →|progress events| Redis BullMQ
    - Angular PWA (dash.js) →|segment download BYPASS API| Cloud Storage (đường nét đứt)
    - DaPlex-API →|MPD URL| Angular PWA
  style: >
    center-out, DaPlex-API ở trung tâm màu xanh lá; Angular PWA bên trái màu xanh dương;
    Transcoder bên dưới màu cam; Redis bên phải trên màu đỏ nhạt; MongoDB bên phải dưới màu xanh lam;
    Cloud Storage góc phải màu vàng; đường nét đứt cho luồng segment video
  output:
    drawio: figures/hinh-3-1-kien-truc-tong-the-he-thong-daplex-luong.drawio
    png: figures/hinh-3-1-kien-truc-tong-the-he-thong-daplex-luong.png
-->
![Hình 3.1: Kiến trúc tổng thể hệ thống DaPlex](pending)
*Hình 3.1: Ba luồng dữ liệu chính trong DaPlex — control plane (REST), async encode pipeline (BullMQ), và data plane streaming (bypass API)*

Hình 3.1 làm rõ điều quan trọng nhất trong kiến trúc DaPlex: **DaPlex-API là hub kiểm soát, không phải hub dữ liệu**. Mọi request HTTP đi qua API để xác thực và xử lý nghiệp vụ, nhưng dữ liệu video khối lượng lớn không bao giờ đi qua API. Sự phân tách này là nguồn gốc của khả năng mở rộng theo chiều ngang theo cách phi đối xứng: khi nhu cầu encode tăng, ta mở rộng Transcoder workers; khi catalog lớn lên, ta mở rộng MongoDB; khi người xem tăng, CDN của cloud storage provider xử lý — API chỉ cần đủ tài nguyên cho metadata throughput.

---

## Mục Tiêu Của Phần Này

Ba mục tiếp theo đi vào chi tiết từng lớp kiến trúc:

- [**3.1.1 — Kiến trúc hệ thống tổng quan**](3.1.1-kien-truc-he-thong.md): Mô tả quan hệ giữa bốn thành phần, chiến lược triển khai VPS đơn vs. phân tán, và quyết định chọn umbrella repo với git submodule.
- [**3.1.2 — Kiến trúc Backend API**](3.1.2-kien-truc-backend.md): Đi sâu vào cấu trúc module NestJS — từ `AppModule` root qua `AppRoutingModule` (17 resource modules) và `AppSocketModule`, đến tầng common modules (Redis, cache, storage adapters, scanner). Phân tích quyết định dùng Fastify và hai kết nối MongoDB (`DATABASE_A`, `DATABASE_B`).
- [**3.1.3 — Kiến trúc Transcoder**](3.1.3-kien-truc-transcoder.md): Mô tả ba module (`VideoModule`, `VideoCancelModule`, `TranscoderApiModule`), cơ chế chọn codec qua biến môi trường `VIDEO_CODEC`, pipeline encode nội bộ `VideoService`, và Winston structured logging.
