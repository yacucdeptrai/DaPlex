# 2. Đóng Góp Và Điểm Mới

Hệ thống DaPlex không đơn thuần là một máy chủ phát video — đây là nền tảng VoD tự lưu trữ tích hợp pipeline mã hóa đa codec, thuật toán ABR dựa trên trạng thái buffer, và kiến trúc phân tách rõ ràng giữa các tầng dịch vụ. So với các giải pháp phổ biến hiện có như Jellyfin, Plex hay các máy chủ HLS đơn giản, DaPlex đóng góp một số điểm kỹ thuật có giá trị thực tiễn được trình bày trong mục này.

---

## So Sánh Với Các Giải Pháp Hiện Có

Để làm nổi bật đóng góp của DaPlex, bảng dưới đây đối chiếu các đặc điểm kỹ thuật cốt lõi với ba đại diện tiêu biểu: Jellyfin (self-hosted mã nguồn mở), Plex (self-hosted thương mại), và một máy chủ HLS thuần túy (nginx + FFmpeg thủ công).

| Đặc điểm | DaPlex | Jellyfin | Plex | HLS thuần |
|----------|--------|----------|------|-----------|
| Codec hỗ trợ phát | H.264, H.265, VP9, AV1 | H.264, H.265, VP9 | H.264, H.265 | Phụ thuộc thủ công |
| Thuật toán ABR | BOLA (buffer-based) | Throughput-based | Throughput-based | Không có |
| Pipeline encode tự động | ✅ Đa tier, không upscale | ✅ Transcode on-demand | ✅ Transcode on-demand | ❌ Thủ công |
| Lọc tier theo nguồn | ✅ `calculateQuality()` | ❌ Encode cố định | ❌ Encode cố định | ❌ |
| Phát DASH + HLS song song | ✅ CMAF dual manifest | ✅ | ✅ | ❌ |
| Upload chunked có retry | ✅ `QueueUploadService` | ❌ | ❌ | ❌ |
| Watch history hai tầng | ✅ localStorage + API | ✅ | ✅ | ❌ |
| Quản lý lưu trữ ngoài | ✅ rclone abstraction | ✅ (hạn chế) | ✅ (Plex Pass) | ❌ |
| Tự lưu trữ hoàn toàn | ✅ | ✅ | ⚠️ (cần Plex.tv) | ✅ |
| Phân quyền RBAC | ✅ JWT + role | ✅ | ✅ | ❌ |

Jellyfin và Plex đều sử dụng mô hình transcode on-demand — chuyển đổi video ngay lúc phát theo thiết bị client yêu cầu — thay vì encode trước tất cả tier như DaPlex. Mô hình này tiết kiệm dung lượng lưu trữ nhưng đặt tải CPU cao tại thời điểm phát và không kiểm soát được chất lượng encode trước.

> DaPlex chọn hướng ngược lại — encode toàn bộ tier trước, lưu sẵn, phát từ file tĩnh — phù hợp cho môi trường có tài nguyên CPU hạn chế lúc phát nhưng chấp nhận chi phí encode một lần.

---

## Điểm Đóng Góp Kỹ Thuật

### 1. Lọc Tier Chất Lượng Tĩnh Theo Nguồn (`calculateQuality`)

Hàm `calculateQuality()` trong Transcoder service giải quyết một vấn đề thực tế thường bị bỏ qua trong các hệ thống encode đơn giản: không tạo tier có độ phân giải cao hơn nguồn. Khi nguồn là video 720p, hệ thống chỉ tạo các tier 720p, 480p, 360p — không upscale lên 1080p hay 4K. Logic lọc này áp dụng khác nhau theo codec: H.264 dùng danh sách `ENCODING_QUALITY = [2160, 1440, 1080, 720, 480, 360]` (đầy đủ 6 tier), trong khi H.265/VP9/AV1 dùng `NEXT_GEN_ENCODING_QUALITY = [2160, 1440]` (chỉ encode tier cao vì encode cost lớn hơn nhiều). Thiết kế này tránh lãng phí tài nguyên encode và dung lượng lưu trữ, đồng thời đảm bảo không có tier giả (upscaled) làm BOLA nhầm lẫn khi chọn chất lượng.

### 2. Chuỗi Fallback Codec Thông Minh

Hệ thống kiểm tra codec theo thứ tự ưu tiên AV1 → H.265 → H.264 tại phía client thông qua `MediaSource.isTypeSupported()`. Nếu trình duyệt không hỗ trợ AV1 (ví dụ: Safari trên iOS), client tự động chuyển sang codec tiếp theo trong chuỗi. Ngoài ra, toàn bộ pipeline DASH với Media Source Extensions có thể fallback về HLS native playback cho Safari iOS — trường hợp duy nhất không hỗ trợ MSE. Chuỗi fallback này được triển khai tại Angular `BaseVideoPlayerComponent` và hoàn toàn trong suốt với người dùng cuối.

### 3. BOLA Thay Vì Throughput-Based ABR

Phần lớn các hệ thống HLS/DASH tự triển khai hoặc dùng tham chiếu mặc định của hls.js đều dùng throughput-based ABR — ước lượng băng thông qua thời gian tải segment vừa xong, rồi chọn quality cho segment tiếp theo. Phương pháp này phản ứng nhanh nhưng không ổn định khi băng thông biến động: một spike ngắn có thể kéo quality lên rồi ngay lập tức phải hạ xuống, gây hiện tượng quality oscillation gây khó chịu cho người xem.

> DaPlex sử dụng BOLA — thuật toán được đề xuất bởi Spiteri et al. (2016) và tích hợp sẵn trong DASH.js — dựa trên hàm Lyapunov để chọn quality tối ưu dựa trên mức buffer hiện tại thay vì throughput ước lượng — vì buffer là tín hiệu trễ nhưng ít nhiễu hơn throughput: khi buffer cao, BOLA có thể upgrade quality; khi buffer thấp, BOLA hạ quality ngay lập tức.

Kết quả kiểm thử mục 5.2 xác nhận BOLA downgrade trong 2–3 segment khi bandwidth giảm từ 20 Mbps xuống 2 Mbps — nhanh hơn nhiều so với throughput-based và không gây stall.

### 4. Upload Chunked Có Retry Và Progress Tracking (`QueueUploadService`)

`QueueUploadService` triển khai giao thức upload phân mảnh với header `Content-Range: bytes start-end/total`, sử dụng `concatMap` của RxJS để đảm bảo các chunk được gửi tuần tự (không song song để tránh race condition trên server). Mỗi chunk có cơ chế retry tối đa 5 lần với delay 3 giây giữa các lần thử (`QUEUE_UPLOAD_RETRIES = 5`, `QUEUE_UPLOAD_RETRY_DELAY = 3000`), và progress được tính chính xác theo bytes thực sự được server xác nhận — không cộng dồn bytes của chunk đang retry.

> Tính năng này giải quyết trực tiếp vấn đề upload file lớn (vài GB) qua mạng không ổn định: nếu kết nối đứt giữa chừng, chỉ chunk hiện tại cần gửi lại, không upload từ đầu.

### 5. Watch History Hai Tầng Giảm Tải API

Thay vì ghi API call mỗi giây như nhiều hệ thống đơn giản, DaPlex triển khai watch history hai tầng: `interval(2000)` ghi vị trí xem vào localStorage mỗi 2 giây (không có network I/O), và `timer(5000, 60000)` gửi `PATCH /history/watch_time` sau 5 giây đầu rồi mỗi 60 giây sau đó. Thiết kế này giảm tải API server 30 lần so với ghi mỗi 2 giây, đồng thời vẫn đảm bảo vị trí xem không bị mất nếu trình duyệt đóng đột ngột (nhờ localStorage). Khi người dùng mở lại video, Angular đọc localStorage để phục hồi vị trí tức thì mà không cần đợi API response.

### 6. ThumbHash Placeholder Cho Thumbnail Tức Thì

Hệ thống tích hợp ThumbHash — một thuật toán mã hóa ảnh thu nhỏ cực nhỏ (20–30 byte) giúp hiển thị placeholder màu sắc chính xác ngay lập tức trong khi ảnh thật đang tải. Khi hover trên thanh seek, thumbnail sprite JPEG (~300KB mỗi file, 1 frame/10 giây) được tải bất đồng bộ — trong khoảng thời gian chờ đó, ThumbHash placeholder được decode client-side từ base64 và render như canvas, tạo cảm giác phản hồi tức thì. Đây là kỹ thuật tương tự BlurHash được dùng bởi các nền tảng lớn như Mastodon và Linear, nhưng được áp dụng vào ngữ cảnh thumbnail video — một trường hợp ứng dụng chưa phổ biến trong các hệ thống VoD tự lưu trữ.

### 7. Abstraction Lưu Trữ Qua Rclone

Backend DaPlex không trực tiếp thao tác với bất kỳ dịch vụ lưu trữ cụ thể nào — toàn bộ I/O file đi qua rclone, một công cụ quản lý lưu trữ đám mây hỗ trợ hơn 70 backend (S3, Google Drive, Backblaze B2, SFTP, WebDAV...). Người dùng cấu hình một hoặc nhiều `ExternalStorage` trong hệ thống, và DaPlex mount chúng như filesystem ảo thông qua `rclone mount`.

> Thiết kế này tách biệt hoàn toàn logic nghiệp vụ khỏi chi tiết lưu trữ — di chuyển từ S3 sang Google Drive hay SFTP không đòi hỏi thay đổi một dòng code backend.
