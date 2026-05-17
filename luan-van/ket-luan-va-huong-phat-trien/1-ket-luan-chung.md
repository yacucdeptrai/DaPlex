# 1. Kết Luận Chung

Luận văn đặt ra mục tiêu xây dựng một hệ thống phát video trực tuyến tự lưu trữ (self-hosted VoD) có khả năng tự động chuyển đổi chất lượng video theo điều kiện mạng thực tế, hỗ trợ nhiều codec thế hệ mới, và cung cấp đầy đủ tính năng quản lý nội dung dành cho cả người dùng cá nhân lẫn quản trị viên. Sau quá trình thiết kế, triển khai và kiểm thử, hệ thống DaPlex đã hoàn thành các mục tiêu đề ra với 117 ca kiểm thử đạt 100% trên ba nhóm: kiểm thử chức năng, kiểm thử ABR, và kiểm thử môi trường mạng.

---

## Mục Tiêu Đã Hoàn Thành

Hệ thống DaPlex được xây dựng dựa trên kiến trúc ba tầng: Angular 21 frontend, NestJS 10 backend, và NestJS 10 Transcoder service. Ba thành phần này giao tiếp qua REST API và hàng đợi BullMQ/Redis, cho phép tách biệt rõ ràng giữa luồng xử lý đồng bộ (phục vụ người dùng) và luồng xử lý bất đồng bộ (mã hóa video nền). Kiến trúc này đã được kiểm chứng qua thực tế vận hành — hệ thống có thể nhận, xử lý và phát video mà không gián đoạn luồng phục vụ người dùng dù transcoding đang chạy song song.

Về phía mã hóa video, pipeline FFmpeg trong Transcoder service hỗ trợ bốn codec: H.264, H.265, VP9 và AV1 — với logic phân tầng chất lượng tĩnh (`calculateQuality()`) chỉ tạo các tier nhỏ hơn hoặc bằng độ phân giải nguồn, loại bỏ hoàn toàn hiện tượng upscale lãng phí tài nguyên. AV1 đã được tích hợp theo chuẩn CMAF, cung cấp hiệu suất nén vượt trội so với H.264 trên cùng chất lượng hình ảnh — kết quả kiểm thử TC_NET_002 và TC_NET_015 xác nhận AV1 hoạt động ổn định trên Chrome 124+ và 5G SA với CPU decode thấp hơn H.264 đáng kể.

Về phía phát video, hệ thống triển khai DASH.js với thuật toán BOLA (Buffer Occupancy based Lyapunov Algorithm) — một giải thuật ABR dựa trên trạng thái buffer thay vì ước lượng throughput thuần túy. Kết quả kiểm thử cho thấy BOLA duy trì chất lượng ổn định hơn và ít rebuffering hơn so với throughput-based ABR trong các tình huống băng thông biến động cao: tại 4G LTE thực tế (~25 Mbps), BOLA ổn định ở 720p–1080p với dưới 2 lần stall trong 3 phút; tại Slow 3G mô phỏng (400 kbps), hệ thống vẫn phát được 360p với startup khoảng 6–7 giây mà không crash hay mất kết nối.

---

## Kết Quả Kiểm Thử Tổng Hợp

Ba chương kiểm thử (Chương 5) bao phủ toàn bộ các tính năng và điều kiện vận hành quan trọng. Tổng cộng 117 ca kiểm thử thuộc ba nhóm đều đạt kết quả mong đợi.

**Kiểm thử chức năng (59 TC):** Toàn bộ luồng xác thực (đăng nhập, đăng ký, khôi phục mật khẩu, JWT rotation), phân quyền RBAC, quản lý media (upload chunked, scan metadata TMDB/TVDB, cấu hình codec), xem video (ABR tự động, chọn thủ công, phụ đề, chương), lịch sử xem hai tầng (localStorage + API), playlist, đánh giá và hồ sơ người dùng đều hoạt động đúng. Bốn trường hợp biên được phát hiện và xử lý trong quá trình kiểm thử: `QueueUploadService` vượt progress 100% khi retry, `AddToPlaylistComponent` không xử lý trạng thái 0 playlist, `RatingsService` chia cho 0 khi xóa rating cuối, và thumbnail ThumbHash chưa hiển thị placeholder tức thì.

**Kiểm thử ABR (26 TC):** Xác nhận ba đặc tính cốt lõi — (1) quality tier được tạo chính xác không upscale; (2) BOLA ổn định khi bandwidth dao động, không stall khi mất mạng ngắn dưới 3 giây nhờ buffer tích lũy; (3) audio track giữ nguyên khi video ABR switch (`autoSwitchBitrate.audio: false`). Một hạn chế được ghi nhận: khi người dùng chọn thủ công quality vượt băng thông (TC_MAN_003), hệ thống không hiển thị cảnh báo — buffer tích lũy chậm nhưng không stall.

**Kiểm thử môi trường mạng (32 TC):** Hệ thống hoạt động trên toàn bộ 13 môi trường kiểm thử từ LAN Gigabit (> 940 Mbps, startup ~0.8s, 2160p) đến Slow 3G DevTools (400 kbps, startup ~7s, 360p). Kết quả đáng chú ý: 5G SA (~8ms RTT) có startup gần bằng WiFi 5 GHz gần router (~1.5s vs ~1.0s) nhờ latency thấp — xác nhận RTT ảnh hưởng trực tiếp đến thời gian lấy DASH manifest và segment đầu tiên. 4G+ LTE-A với carrier aggregation (~60 Mbps) đạt 1080p–1440p, lấp đầy khoảng trống giữa 4G LTE (~25 Mbps) và 5G NSA (~300 Mbps). Cơ chế fallback từ 5G NSA về 4G LTE không gây stall nhờ buffer BOLA đủ dày (ít nhất 15–20 giây đệm).

---

## Đánh Giá Chung

DaPlex giải quyết được bài toán cốt lõi đặt ra: một hệ thống VoD tự lưu trữ có thể encode, lưu trữ và phát video chất lượng cao trên nhiều thiết bị và điều kiện mạng khác nhau mà không phụ thuộc vào dịch vụ đám mây bên thứ ba. Kiến trúc module hóa rõ ràng (frontend / backend / transcoder tách biệt), cơ chế ABR dựa trên buffer, và pipeline encode đa codec tạo nên nền tảng kỹ thuật vững chắc cho một hệ thống VoD cá nhân hoặc tổ chức nhỏ.

Tuy nhiên, hệ thống vẫn có những giới hạn về khả năng mở rộng và một số tính năng chưa được triển khai trong phạm vi luận văn — những điểm này được phân tích chi tiết trong mục Hạn Chế và Định Hướng Phát Triển.
