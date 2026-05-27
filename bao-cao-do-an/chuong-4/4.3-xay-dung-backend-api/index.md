# 4.3. Xây Dựng Backend API

Phần này trình bày kiến trúc và cách triển khai backend RESTful API của DaPlex — được xây dựng trên NestJS và Fastify với hệ thống module phân tầng, dual database MongoDB, và tích hợp BullMQ cho pipeline encode video. Hiểu rõ cấu trúc backend là nền tảng để nắm bắt cách toàn bộ nền tảng vận hành, từ xác thực người dùng đến quản lý media và thông báo real-time. Nội dung được tổ chức thành năm mục con đi sâu vào từng khía cạnh kỹ thuật quan trọng.

---

## Tổng Quan Kiến Trúc

DaPlex-API là backend RESTful API xây dựng bằng **NestJS 10.3.0** chạy trên **Fastify 4.25.1** thay cho Express mặc định. Lý do chọn Fastify thay Express là hiệu năng: Fastify xử lý request nhanh hơn khoảng 15–20% nhờ schema-based JSON serialization và một request pipeline gọn hơn — điều quan trọng với video platform nơi các endpoint stream manifest và thumbnail phải phục vụ hàng trăm request đồng thời. NestJS cung cấp lớp abstraction với decorator pattern, Dependency Injection container, và module system, trong khi Fastify đảm nhiệm HTTP layer bên dưới qua `NestFastifyApplication` adapter.

Toàn bộ API được đặt dưới prefix `/api`, với 17 resource module độc lập đăng ký thông qua `AppRoutingModule` sử dụng `RouterModule` của NestJS core. Mỗi resource module tương ứng với một domain nghiệp vụ — `AuthModule` (`/api/auth`), `MediaModule` (`/api/media`), `UsersModule` (`/api/users`)... — và tự quản lý schema, service, controller, và các dependency của riêng mình. Ngoài REST API, `AppSocketModule` tích hợp một WebSocket gateway (`WsAdminGateway`) phục vụ thông báo real-time cho admin dashboard, hoạt động song song với HTTP server trên cùng một cổng Fastify.

---

## Khởi Động Ứng Dụng và Bootstrap

File `src/main.ts` thực hiện toàn bộ quá trình cấu hình trước khi lắng nghe kết nối. Đầu tiên, `NestFactory.create()` nhận `AppModule` và `FastifyAdapter` với `trustProxy: process.env.TRUST_PROXY === 'true'` — flag này cần bật khi API đứng sau reverse proxy (Nginx, Cloudflare) để đọc đúng IP thực của client từ header `X-Forwarded-For`, quan trọng cho rate limiting chính xác. Logger level được đặt `info` trong development và `warn` trong production để tránh log quá nhiều khi tải cao.

**Swagger UI** chỉ được mount trong development (`NODE_ENV === 'development'`) tại endpoint `/docs`. Document được build từ `DocumentBuilder` với bearer auth scheme (JWT), mô tả toàn bộ controller thông qua decorator `@ApiOperation`, `@ApiOkResponse`, `@ApiTags` trong từng controller. Việc chỉ mount Swagger trong development tránh expose API schema ra production, đồng thời không tốn bộ nhớ để build document object trong môi trường live.

**`ValidationPipe` global** với `whitelist: true` tự động loại bỏ các property không khai báo trong DTO — bảo vệ chống mass assignment injection. `stopAtFirstError: true` dừng validate sau lỗi đầu tiên thay vì collect tất cả errors, giảm overhead. `exceptionFactory` tùy chỉnh serialize validation error thành JSON `{ code: number, message: string }` — `code` lấy từ `error.contexts` (được inject bởi custom validator decorators như `UsernameExistConstraint`) hoặc `-1` nếu không có, `message` lấy từ constraint message. Chuẩn hóa error format này đảm bảo frontend có thể phân biệt loại lỗi bằng numeric code thay vì parse message string.

**Fastify plugins** được register sau pipe: `fastify-multipart` cho phép parse `multipart/form-data` (dùng khi admin upload video/ảnh), `fastify-cookie` với `httpOnly: true`, `sameSite: 'strict'`, `domain` từ env để phát và parse cookie an toàn (refresh token). `useContainer(app.select(AppModule), { fallbackOnErrors: true })` kết nối NestJS DI container với `class-validator` — cho phép các custom constraint như `UsernameExistConstraint` nhận inject `UserModel` để query database khi validate DTO.

---

## Cấu Hình AppModule — Dual Database và BullMQ

`AppModule` khai báo ba connection quan trọng khởi động ứng dụng:

**Dual MongoDB**: hai `MongooseModule.forRootAsync()` với `connectionName` khác nhau (`DATABASE_A` và `DATABASE_B`). Connection A trỏ đến database chính chứa 16+ collection (User, Media, Role, Genre, Tag, Production, History, Playlist, Rating, Collection, MediaStorage, TVEpisode...), Connection B trỏ đến database phụ chứa `AuditLog` và `Notification`. Phân tách này giúp isolate workload audit và notification khỏi core business data — nếu cần scale riêng hoặc archive AuditLog, có thể migrate collection B mà không ảnh hưởng A. Cả hai connection đều bật `useBigInt64: true` để Mongoose xử lý Snowflake ID (64-bit integer) thay vì auto-cast sang Float64 gây mất precision.

**BullMQ global** được cấu hình từ `REDIS_QUEUE_URL` thông qua `parse-redis-url-simple` để extract host/port/password/database. Redis connection option bật `enableOfflineQueue: false` — khi Redis mất kết nối, job enqueue thất bại ngay lập tức với error thay vì queue trong memory và gửi khi reconnect, tránh accumulate job trong trường hợp Redis outage kéo dài.

**`ScheduleModule.forRoot()`** kích hoạt `@nestjs/schedule` để các service có thể dùng decorator `@Cron()` hay `@Interval()` cho tác vụ định kỳ — ví dụ cleanup expired drive sessions, refresh external storage tokens.

---

## Phân Tầng Resource Modules

Mười bảy resource module trong `src/resources/` được đăng ký theo route prefix tương ứng:

| Module | Prefix | Chức năng chính |
|---|---|---|
| `AuthModule` | `/api/auth` | Đăng nhập, đăng ký, refresh token, xác nhận email, khôi phục mật khẩu |
| `UsersModule` | `/api/users` | Hồ sơ người dùng, cài đặt, upload avatar/banner |
| `RolesModule` | `/api/roles` | Quản lý role RBAC, gán permission bitmask |
| `MediaModule` | `/api/media` | CRUD media, upload file nguồn, trigger encode, stream manifest |
| `HistoryModule` | `/api/history` | Lịch sử xem, cập nhật watch time |
| `PlaylistsModule` | `/api/playlists` | Tạo/quản lý playlist và playlist item |
| `RatingsModule` | `/api/ratings` | Đánh giá sao theo media |
| `CollectionModule` | `/api/collections` | Bộ sưu tập media do admin curate |
| `GenresModule` | `/api/genres` | Quản lý thể loại |
| `TagsModule` | `/api/tags` | Quản lý tag |
| `ProductionsModule` | `/api/productions` | Quản lý nhà sản xuất |
| `ExternalStoragesModule` | `/api/external-storages` | Cấu hình cloud storage providers |
| `NotificationModule` | `/api/notification` | Thông báo in-app, read/unread |
| `AuditLogModule` | `/api/audit-log` | Nhật ký thao tác admin |
| `MediaScannerModule` | `/api/media-scanner` | Tích hợp TMDB/TVDB scraper |
| `ChapterTypeModule` | `/api/chapter-types` | Quản lý kiểu chapter |
| `SettingsModule` | `/api/settings` | Cài đặt toàn hệ thống |

---

## Common Modules — Shared Infrastructure

Thư mục `src/common/modules/` chứa các module infrastructure dùng chung bởi nhiều resource module, tổ chức theo chức năng:

**Cache layer** gồm ba module Redis riêng biệt, mỗi module connect đến Redis instance độc lập để phân tách workload: `RedisCacheModule` (từ `REDIS_URL`) dùng cho primary cache như JWT payload cache, `Redis2ndCacheModule` (từ `REDIS_2ND_URL`) dùng cho rate limiting và secondary cache, `RedisPubSubModule` dùng cho pub/sub event (kết quả encode Transcoder gửi về API). Việc dùng ba connection Redis tách biệt cho phép scale và monitor từng loại workload độc lập.

**External storage modules** hỗ trợ đa provider: `CloudflareR2Module`, `S3Module` (tương thích S3 API — dùng cho Backblaze B2, AWS S3, MinIO), `AzureBlobModule`, `OnedriveModule`, `DropboxModule`, `GoogleDriveModule`, `ImageKitModule`, `ImgurModule`, `FilerModule` (local filesystem). Mỗi module inject `ConfigService` để đọc credentials từ env, và expose service với interface đồng nhất (`upload`, `delete`, `getPresignedUrl`...) để `MediaService` gọi mà không cần biết provider cụ thể.

**`HttpEmailModule`** wrap `@sendgrid/mail` để gửi email transactional (xác nhận email, reset mật khẩu) qua SendGrid API. Email template được định nghĩa trong SendGrid dashboard và tham chiếu bằng `SendgridTemplate` enum — không hardcode HTML trong codebase.

**`PermissionsModule`** cung cấp `PermissionsService` để verify bitmask permission của user trong các guard. Permission system dùng bitwise AND: `user.roles.find(role => role.permissions & UserPermission.MANAGE_MEDIA)` — mỗi role có một số 64-bit, mỗi bit là một permission flag.

---

## Hệ Thống ID Snowflake

DaPlex-API không dùng MongoDB ObjectId mặc định mà dùng **Snowflake ID** — 64-bit integer do Twitter thiết kế, bao gồm timestamp 41 bit, machine ID 10 bit, và sequence 12 bit. `createSnowFlakeId()` trong `src/utils/` sinh ID dạng `bigint` (native JS BigInt), lưu vào MongoDB dưới kiểu BSON Int64. Ưu điểm so với ObjectId: Snowflake ID có thứ tự thời gian tự nhiên (sort by `_id` = sort by created time mà không cần trường `createdAt` riêng), độ dài cố định 19 chữ số decimal thuận tiện cho URL, và không tiết lộ thông tin về server/process. Trong API response, Snowflake ID được serialize thành string để tránh mất precision khi JavaScript đọc JSON (JS Number chỉ chính xác đến 2^53).

<!-- FIGURE
  id: Hình 4.6
  title: Kiến trúc tổng thể DaPlex-API — NestJS modules, dual MongoDB, và BullMQ queues
  type: architecture-diagram
  description: >
    Sơ đồ kiến trúc DaPlex-API. Trên cùng là entry point main.ts (FastifyAdapter + ValidationPipe + CORS + fastify-multipart + fastify-cookie). Tầng giữa: AppModule chứa AppRoutingModule (17 resource modules, prefix /api) và AppSocketModule (WsAdminGateway). Bên trái AppModule: 3 Redis connections (REDIS_URL → RedisCacheModule, REDIS_2ND_URL → Redis2ndCacheModule, REDIS_QUEUE_URL → BullMQ + RedisPubSubModule, REDIS_IO_URL → Socket.IO adapter). Bên phải: Dual MongoDB (DATABASE_A → 16+ collections, DATABASE_B → AuditLog + Notification). Tầng dưới: Common Modules (external storage, email, permissions, rate-limit). Mũi tên từ 4 BullMQ queues (H264/H265/VP9/AV1 transcode + result queue) sang Transcoder service.
  nodes:
    - main.ts → FastifyAdapter (:3000)
    - main.ts → ValidationPipe (whitelist, stopAtFirstError, custom exceptionFactory)
    - main.ts → fastify-multipart + fastify-cookie
    - main.ts → Swagger UI (/docs, dev only)
    - AppModule → AppRoutingModule (17 modules under /api)
    - AppModule → AppSocketModule → WsAdminGateway (WebSocket)
    - AppModule → MongooseModule × 2 (DATABASE_A, DATABASE_B)
    - AppModule → BullModule (REDIS_QUEUE_URL)
    - AppModule → ScheduleModule
    - AppRoutingModule → AuthModule (/api/auth)
    - AppRoutingModule → MediaModule (/api/media)
    - AppRoutingModule → UsersModule (/api/users)
    - AppRoutingModule → HistoryModule/PlaylistsModule/RatingsModule/CollectionModule
    - AppRoutingModule → GenresModule/TagsModule/ProductionsModule/RolesModule
    - AppRoutingModule → NotificationModule/AuditLogModule/SettingsModule/MediaScannerModule
    - MediaModule → BullMQ Queue H264/H265/VP9/AV1
    - BullMQ Queue → DaPlex-Transcoder (consume encode jobs)
    - MediaModule → RedisPubSubModule (subscribe encode results)
    - Common Modules: RedisCacheModule/Redis2ndCacheModule/RedisPubSubModule/PermissionsModule/ExternalStorageModules/HttpEmailModule
  style: top-to-bottom; AppRoutingModule nền xanh nhạt; Common Modules nền xám nhạt; Redis connections nền đỏ nhạt; MongoDB connections nền xanh lá nhạt; BullMQ queues nền cam nhạt
  output:
    drawio: figures/hinh-4-6-kien-truc-tong-the-daplex-api-nestjs.drawio
    png: figures/hinh-4-6-kien-truc-tong-the-daplex-api-nestjs.png
-->
![Hình 4.6: Kiến trúc tổng thể DaPlex-API](pending)
*Hình 4.6: Kiến trúc DaPlex-API — NestJS + Fastify, 17 resource modules, dual MongoDB, 4 Redis connections, BullMQ transcode queues*

---

## Cấu Trúc Chi Tiết Các Phần

Phần 4.3 được chia thành năm mục phân tích chi tiết từng khía cạnh kỹ thuật của backend:

- **[4.3.1. Cấu trúc dự án NestJS](4.3.1-cau-truc-du-an-nestjs.md)** — Tổ chức thư mục `src/`, quy ước đặt tên module, schemas Mongoose, enums, decorators, utils, và cấu hình TypeScript cho backend.
- **[4.3.2. Module xác thực và phân quyền](4.3.2-module-xac-thuc.md)** — `AuthModule` với JWT access token + Redis refresh token, RBAC permission bitmask, `AuthGuard`, `RateLimitInterceptor`, email verification flow.
- **[4.3.3. Module quản lý media](4.3.3-module-quan-ly-media.md)** — `MediaModule` với upload file nguồn, enqueue encode job, `MediaConsumer` xử lý kết quả, stream manifest generation, phân quyền theo visibility.
- **[4.3.4. Tích hợp external storage](4.3.4-external-storage.md)** — Kiến trúc multi-provider storage (Cloudflare R2, S3, Azure Blob, OneDrive, local), `ExternalStoragesModule`, cơ chế presigned URL và callback.
- **[4.3.5. Hệ thống thông báo real-time](4.3.5-websocket-notification.md)** — `WsAdminGateway` với Socket.IO, room-based notification, header `X-Socket-ID` để loại trừ self-notification, `NotificationModule`.
