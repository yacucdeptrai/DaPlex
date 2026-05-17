# 3. Hạn Chế

Bên cạnh những kết quả đạt được, DaPlex vẫn tồn tại một số hạn chế kỹ thuật và phạm vi chưa được giải quyết trong khuôn khổ luận văn. Việc nhìn nhận thẳng thắn những giới hạn này là cần thiết để đánh giá đúng phạm vi ứng dụng thực tế của hệ thống và làm cơ sở cho các hướng phát triển tiếp theo.

---

## Hạn Chế Về Khả Năng Mở Rộng

Kiến trúc hiện tại của DaPlex được thiết kế cho môi trường single-server: một instance backend NestJS, một instance Transcoder, một Redis broker, và storage được mount qua rclone.

> Thiết kế này đơn giản và dễ triển khai nhưng tạo ra nhiều single point of failure — nếu Transcoder service dừng hoặc Redis không phản hồi, toàn bộ hàng đợi encode bị treo và người dùng không nhận được thông báo trạng thái cụ thể.

Hệ thống chưa hỗ trợ horizontal scaling: không thể chạy nhiều instance Transcoder song song để phân chia tải encode, và không có cơ chế load balancing tại tầng API. Trong các kịch bản có nhiều người dùng đồng thời hoặc cần encode nhiều video cùng lúc, đây là giới hạn nghiêm trọng.

Redis được dùng làm message broker duy nhất cho BullMQ job queue — nếu Redis khởi động lại hoặc mất kết nối, các job đang chờ trong queue có thể bị mất nếu Redis không được cấu hình persistence (AOF/RDB). Trong môi trường production thực tế, điều này đòi hỏi phải cấu hình Redis Sentinel hoặc Cluster, một yêu cầu vận hành không được đề cập trong phạm vi luận văn.

---

## Hạn Chế Về Hiệu Suất Encode

Pipeline encode của DaPlex xử lý video tuần tự theo hàng đợi FIFO (First In, First Out) không có ưu tiên — một video dài 3 giờ sẽ chiếm Transcoder service và chặn tất cả video ngắn hơn phía sau. Hệ thống chưa có cơ chế priority queue, phân chia tải theo kích thước file, hay encode song song nhiều luồng. Ngoài ra, với video 4K nguồn và cấu hình encode đủ bốn codec (H.264 + H.265 + VP9 + AV1), thời gian encode có thể lên đến nhiều giờ trên phần cứng thông thường — trong thời gian này, người dùng không thể xem video và chỉ thấy trạng thái "đang xử lý" mà không biết còn bao lâu. Hệ thống chưa cung cấp ước tính thời gian hoàn thành hay progress realtime chi tiết hơn mức "đang encode".

Codec AV1 đặc biệt chậm trong giai đoạn software encode — với encoder `libaom-av1` mặc định, encode AV1 có thể chậm hơn H.264 tới 10–20 lần ở cùng chất lượng. Hệ thống chưa tận dụng hardware encoding (NVENC cho NVIDIA, AMF cho AMD, VideoToolbox cho Apple Silicon) để tăng tốc, do phụ thuộc vào FFmpeg binary không kèm hardware encoder trong cấu hình mặc định.

---

## Hạn Chế Về Bảo Vệ Nội Dung

DaPlex không triển khai bất kỳ hình thức DRM (Digital Rights Management) nào. Toàn bộ nội dung video được phát dưới dạng file DASH/HLS không mã hóa — bất kỳ người dùng nào có token hợp lệ đều có thể dùng DevTools để lấy URL trực tiếp của segment video và tải xuống bằng wget hay curl. Đối với nội dung cá nhân hoặc nội bộ tổ chức, điều này có thể chấp nhận được; nhưng với nội dung có bản quyền thương mại, thiếu DRM là giới hạn căn bản. Các hệ thống DRM phổ biến (Widevine, FairPlay, PlayReady) đòi hỏi tích hợp với dịch vụ cấp phát key của bên thứ ba và thay đổi đáng kể pipeline đóng gói CMAF, vượt ngoài phạm vi của dự án hiện tại.

---

## Hạn Chế Về Trải Nghiệm Người Dùng

**Không có cảnh báo quality vượt băng thông:** Khi người dùng chọn thủ công một tier chất lượng cao hơn khả năng băng thông hiện tại (TC_MAN_003), hệ thống không hiển thị cảnh báo hay gợi ý. Buffer tích lũy chậm dần nhưng người dùng không biết lý do — trải nghiệm kém hơn so với Netflix hay YouTube, nơi player hiển thị thông báo "Chất lượng đã được giảm do tốc độ mạng thấp".

**Không hỗ trợ xem offline:** Hệ thống không có tính năng tải về và xem offline. Toàn bộ nội dung yêu cầu kết nối mạng liên tục — người dùng di chuyển vào vùng không có sóng sẽ bị gián đoạn ngay. Đây là hạn chế đặc biệt rõ ràng so với các ứng dụng mobile như Netflix hay Spotify cho phép download nội dung để xem/nghe offline.

**Startup time chậm trên mạng yếu:** Trên Slow 3G (400 kbps), startup time đo được khoảng 6–7 giây — dài hơn nhiều so với ngưỡng 3 giây mà Google PageSpeed khuyến nghị cho trải nghiệm phát video web. Nguyên nhân là DASH manifest phải tải toàn bộ MPD XML trước khi bắt đầu buffer segment đầu tiên, và trên mạng chậm với RTT cao (~200ms), mỗi round-trip là chi phí đáng kể. Hệ thống chưa triển khai Low Latency DASH hay pre-fetching manifest để giảm startup time trên mạng yếu.

---

## Hạn Chế Về Tính Năng

**Không hỗ trợ live streaming:** DaPlex là hệ thống VoD (Video on Demand) thuần túy — không có tính năng phát trực tiếp (live stream). Việc mở rộng sang live streaming đòi hỏi thay đổi căn bản ở cả pipeline ingest (nhận luồng RTMP/SRT thay vì file) lẫn phân phối (Low Latency HLS/DASH với segment duration rất ngắn).

**Nguồn metadata giới hạn:** Hệ thống chỉ tích hợp hai nguồn metadata: TMDB (phim và series quốc tế) và TVDB (series TV). Nội dung nội bộ, tài liệu đào tạo, hay video không thuộc cơ sở dữ liệu hai nguồn này phải được nhập metadata thủ công — không có giao diện bulk import metadata từ file CSV hay API bên ngoài.

**Quản lý phụ đề còn hạn chế:** Phụ đề hiện tại chỉ hỗ trợ upload thủ công file .srt/.vtt và gán vào media qua admin panel. Hệ thống chưa có tính năng tự động nhận dạng ngôn ngữ hay tích hợp dịch vụ phụ đề tự động (như OpenAI Whisper) để sinh phụ đề từ audio. Ngoài ra, chưa hỗ trợ phụ đề đồ họa (PGS/VOBSUB từ Blu-ray) vì định dạng này cần render frame-by-frame thay vì render text.

**Không có hàng đợi encode ưu tiên:** Tất cả job encode được xử lý theo thứ tự nộp vào (FIFO) mà không có cơ chế ưu tiên theo người dùng, kích thước file, hay loại nội dung. Một admin không thể đẩy một video lên đầu hàng đợi khi cần phát ngay.
