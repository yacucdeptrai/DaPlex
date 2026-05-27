# 4. Định Hướng Phát Triển

Dựa trên nền tảng kỹ thuật đã xây dựng và những hạn chế được xác định ở mục trước, phần này đề xuất các hướng phát triển cụ thể, có cơ sở kỹ thuật, và khả thi trong ngắn đến trung hạn. Các đề xuất được tổ chức theo nhóm: mở rộng khả năng mở rộng hệ thống, nâng cao hiệu suất encode, cải thiện trải nghiệm người dùng, và bổ sung tính năng mới.

---

## Mở Rộng Kiến Trúc Để Hỗ Trợ Multi-Instance

Hướng phát triển ưu tiên cao nhất là chuyển Transcoder service từ mô hình single-instance sang mô hình worker pool có thể scale ngang. BullMQ — thư viện hàng đợi hiện tại — hỗ trợ nhiều worker cùng consume từ một queue Redis mà không cần thay đổi giao diện publish. Điều này có nghĩa là việc thêm Transcoder worker thứ hai chỉ yêu cầu khởi động thêm một container với cùng cấu hình, không cần sửa code backend hay thay đổi cách admin upload video.

Để đảm bảo tính bền vững của hàng đợi, Redis cần được cấu hình với AOF persistence và Sentinel hoặc Cluster để tránh mất job khi Redis khởi động lại. Ngoài ra, có thể bổ sung Dead Letter Queue — một queue riêng lưu lại các job thất bại sau khi hết retry — để admin có thể xem và retry thủ công thay vì mất hoàn toàn. Những thay đổi này không đòi hỏi thay đổi kiến trúc lớn và có thể thực hiện trong một sprint ngắn.

---

## Tích Hợp Hardware Encoding Để Tăng Tốc AV1 Và H.265

Thời gian encode AV1 bằng software (`libaom-av1`) hiện tại là điểm nghẽn lớn nhất trong pipeline. Giải pháp thực tế nhất là tích hợp encoder AV1 phần cứng thế hệ mới: NVIDIA Ada Lovelace (RTX 40 series) và Intel Arc đều hỗ trợ AV1 NVENC/QSV, có thể tăng tốc encode AV1 lên 10–20 lần so với software.

Về mặt triển khai, FFmpeg đã hỗ trợ `av1_nvenc` và `av1_qsv` từ phiên bản 6.0 — Transcoder service chỉ cần phát hiện hardware khả dụng lúc khởi động (qua `ffmpeg -encoders`) và tự động chọn encoder phần cứng thay cho software fallback. Cần bổ sung logic kiểm tra quality preset phù hợp giữa software (`cpu-used=4`) và hardware (`preset=p4`), vì hai encoder dùng tham số khác nhau. Tính năng này sẽ giảm thời gian encode 4K AV1 từ vài giờ xuống còn vài phút trên phần cứng có GPU rời.

---

## Bổ Sung Priority Queue Cho Encode

Khi hệ thống có nhiều người dùng hoặc nhiều video chờ encode, khả năng ưu tiên một số job nhất định là tính năng vận hành quan trọng. BullMQ hỗ trợ `priority` field tích hợp sẵn — mỗi job có thể được gán số ưu tiên (số nhỏ hơn = ưu tiên cao hơn) khi publish vào queue.

Về giao diện, admin panel cần bổ sung nút "Ưu tiên encode" và hiển thị vị trí hiện tại trong hàng đợi. Ngoài ra, có thể triển khai tự động ưu tiên theo thời lượng: video ngắn (dưới 5 phút) được ưu tiên cao hơn video dài để giảm thời gian chờ cho phần lớn nội dung thông thường. Thay đổi này chỉ cần sửa logic publish job tại backend và bổ sung UI tại admin panel, không ảnh hưởng đến pipeline encode.

---

## Giảm Startup Time Với Low Latency DASH Và Manifest Pre-fetch

Startup time ~7 giây trên Slow 3G xuất phát từ hai nguyên nhân: (1) DASH manifest (MPD XML) phải được tải và parse trước khi request segment đầu tiên, và (2) segment đầu tiên phải tải xong trước khi video bắt đầu render.

Hướng giải quyết thứ nhất là triển khai manifest pre-fetch — khi người dùng hover vào thumbnail hoặc click vào poster, Angular gọi `prefetchManifest()` ngầm để tải manifest trước, giảm latency khi nhấn Play. Hướng giải quyết thứ hai là giảm segment duration từ 6 giây xuống 2–3 giây cho segment đầu tiên (initialization segment ngắn hơn), kỹ thuật này được YouTube và Netflix áp dụng để cải thiện startup. Low Latency DASH (LL-DASH) theo chuẩn ISO/IEC 23009-1:2022 cũng cho phép phát chunk-by-chunk trong cùng một segment, nhưng đòi hỏi thay đổi đáng kể ở cả pipeline CMAF packaging lẫn cấu hình DASH.js.

---

## Tích Hợp Whisper Để Tự Động Sinh Phụ Đề

OpenAI Whisper là mô hình nhận dạng giọng nói mã nguồn mở có khả năng phiên âm và dịch audio sang văn bản với độ chính xác cao trên nhiều ngôn ngữ, kể cả tiếng Việt. Tích hợp Whisper vào Transcoder pipeline sẽ cho phép tự động sinh phụ đề `.srt` sau khi encode hoàn thành, mà không cần upload thủ công.

Về mặt kỹ thuật, Transcoder có thể thêm một bước xử lý sau encode: trích xuất audio track từ video đã encode, gọi Whisper API (hoặc chạy model local với `whisper.cpp` cho môi trường không có internet), rồi lưu file `.vtt` vào storage và đăng ký vào database phụ đề. Whisper hỗ trợ nhiều model kích thước khác nhau (`tiny`, `base`, `small`, `medium`, `large`) — `small` hoặc `medium` là cân bằng tốt giữa độ chính xác và tốc độ cho môi trường self-hosted.

---

## Bảo Vệ Nội Dung Với CENC/Widevine

Với mục tiêu phục vụ nội dung có bản quyền thương mại trong tương lai, hệ thống cần triển khai Common Encryption (CENC) — chuẩn mã hóa MPEG DASH cho phép mã hóa segment video bằng AES-128-CTR. CENC được ba hệ thống DRM lớn (Widevine của Google, FairPlay của Apple, PlayReady của Microsoft) hỗ trợ cùng một lúc thông qua cơ chế multi-DRM.

Cụ thể trong pipeline DaPlex, MP4Box (công cụ đóng gói CMAF hiện tại) hỗ trợ CENC encryption thông qua tham số `--crypt`. Backend cần bổ sung Key Management Service (KMS) để tạo và lưu trữ encryption key, và tích hợp với một License Server (Shaka Packager + Shaka Server là giải pháp mã nguồn mở phổ biến) để cấp phát license cho client đã xác thực. Đây là hướng phát triển phức tạp nhất trong danh sách nhưng cần thiết nếu DaPlex muốn hướng đến thị trường doanh nghiệp.

---

## Hỗ Trợ Live Streaming Qua RTMP Ingest

Mở rộng DaPlex sang live streaming đòi hỏi bổ sung một thành phần mới: RTMP ingest server (ví dụ: nginx-rtmp-module hoặc SRS — Simple Realtime Server). Khi streamer gửi luồng RTMP từ OBS hoặc thiết bị phát, ingest server nhận và chuyển sang FFmpeg để encode real-time thành Low Latency HLS (LL-HLS) với segment duration 0.5–2 giây.

Backend NestJS cần bổ sung API quản lý stream key, và Angular frontend cần player mode riêng cho live — sử dụng LL-HLS thay vì DASH vì LL-HLS có hỗ trợ native trên Safari iOS mà không cần MSE. Kiến trúc backend hiện tại (NestJS + BullMQ) không thay đổi đáng kể vì live stream là luồng riêng biệt, không đi qua Transcoder queue. Đây là hướng phát triển có tác động cao về tính năng với mức độ thay đổi kiến trúc tương đối giới hạn.

---

## Tổng Kết Lộ Trình

Bảng dưới đây tóm tắt các hướng phát triển theo độ ưu tiên và mức độ phức tạp triển khai, giúp xác định thứ tự thực hiện hợp lý.

| Hướng phát triển | Ưu tiên | Độ phức tạp | Phụ thuộc |
|-----------------|---------|-------------|-----------|
| Multi-instance Transcoder + Redis HA | Cao | Thấp | BullMQ worker pool |
| Priority queue cho encode | Cao | Thấp | BullMQ priority field |
| Hardware encoding (NVENC/QSV) | Cao | Trung bình | GPU khả dụng |
| Manifest pre-fetch | Trung bình | Thấp | Angular service worker |
| Whisper auto-subtitle | Trung bình | Trung bình | Whisper model / API |
| Low Latency DASH | Trung bình | Cao | Pipeline CMAF thay đổi |
| Live streaming RTMP | Thấp | Cao | Ingest server mới |
| DRM / CENC Widevine | Thấp | Rất cao | License server bên thứ ba |
