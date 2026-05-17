# 3.5. Cơ Chế Tự Động Chỉnh Độ Nét

DaPlex sử dụng **MPEG-DASH** (Dynamic Adaptive Streaming over HTTP) làm giao thức truyền tải video chính. Cơ chế ABR (Adaptive Bitrate) cho phép trình phát tự động lựa chọn chất lượng video phù hợp với băng thông hiện tại của người xem trong thời gian thực — tránh hiện tượng buffering khi mạng yếu và tận dụng tối đa chất lượng khi mạng tốt.

Thư viện xử lý DASH phía client là **dash.js** (phiên bản 5.0.0), được tích hợp vào trình phát qua **vidstack** — một wrapper chuẩn hóa sự kiện và trạng thái trên nhiều provider khác nhau. Chuỗi từ file video đã encode đến màn hình người xem trải qua bốn bước: encode → lưu trữ → manifest → trình phát.

- [**3.5.1 — Cấu Trúc File DASH**](3.5.1-cau-truc-file-dash.md): Profile `isoff-on-demand`, SegmentBase, byte range request.
- [**3.5.2 — StreamManifest**](3.5.2-stream-manifest.md): Định dạng JSON trung gian, `HlsVideoTrack`, `HlsAudioTrack`.
- [**3.5.3 — Chuyển Đổi Manifest Sang DASH**](3.5.3-chuyen-doi-manifest-sang-dash.md): `generateParsedDash`, `generateParsedDashFromUrls`, Web Worker.
- [**3.5.4 — Cấu Hình dash.js và Thuật Toán BOLA**](3.5.4-cau-hinh-dashjs-va-bola.md): Cấu hình provider, ABR, BOLA.
- [**3.5.5 — Lựa Chọn Codec và AV1 Capability Detection**](3.5.5-lua-chon-codec-av1.md): `supportsMediaSource`, HLS fallback, AV1 detection.
- [**3.5.6 — Chọn Chất Lượng Thủ Công**](3.5.6-chon-chat-luong-thu-cong.md): Override ABR, persist settings.
- [**3.5.7 — Tóm Tắt Luồng**](3.5.7-tom-tat-luong.md): Sơ đồ luồng ABR đầu cuối.
