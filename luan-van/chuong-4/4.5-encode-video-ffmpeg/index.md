# 4.5. Encode Video với FFmpeg

Phần này trình bày toàn bộ pipeline encode video trong DaPlex-Transcoder — từ lúc nhận file nguồn đến khi tạo ra các luồng CMAF sẵn sàng phát trên nhiều thiết bị. Hệ thống phối hợp bốn công cụ FFmpeg, MediaInfo, MP4Box, và rclone để encode đa codec, đóng gói CMAF single-file, và upload lên cloud storage. Phần này bao gồm tổng quan kiến trúc, chiến lược chất lượng, và các kỹ thuật encode chuyên biệt cho video, audio, CMAF packaging, split encoding, HDR, và thumbnail.

---

## Tổng Quan Hệ Thống Encode

Quá trình chuyển đổi file video nguồn thành các luồng stream phù hợp nhiều thiết bị trong DaPlex-Transcoder dựa trên sự phối hợp của bốn công cụ chính: **FFmpeg** thực hiện encode video/audio, **MediaInfo** phân tích metadata chi tiết của file, **MP4Box** (từ thư viện GPAC) đóng gói CMAF container và tạo DASH MPD + HLS m3u8, và **rclone** tải file kết quả lên cloud storage. Mỗi công cụ được gọi bằng `child_process.spawn()` trong Node.js — không dùng wrapper library, gọi trực tiếp binary với mảng argument được build thủ công. Cách này cho phép kiểm soát chính xác từng flag FFmpeg mà không bị giới hạn bởi API của thư viện bọc ngoài.

`VideoService` trong Transcoder tổ chức toàn bộ logic encode qua một chuỗi method private có quan hệ phân cấp rõ ràng. `transcode()` là orchestrator cấp cao nhất — gọi `encodeAudioByTrack()` cho từng audio track, `encodeByCodec()` cho từng codec video, rồi `saveManifestFile()` sau khi tất cả track của một codec hoàn thành. Trong `encodeAudio()` và `encodeByCodec()`, mỗi quality tier gọi `encodeMedia()` để chạy FFmpeg, rồi `prepareMediaFile()` để đóng gói qua MP4Box, rồi `uploadMedia()` để đẩy kết quả lên storage.

> Thiết kế phân cấp này làm cho mỗi method đủ nhỏ để test và debug độc lập.

Cấu hình encode có hai nguồn ưu tiên: admin có thể cấu hình tất cả FFmpeg parameters (`audioParams`, `videoH264Params`, `videoH265Params`, `videoVP9Params`, `videoAV1Params`) và quality list trực tiếp từ admin dashboard (lưu trong MongoDB `Setting` collection). Nếu không có cấu hình từ admin, Transcoder fallback về constants trong `config.ts`. Cơ chế override-từ-admin-dashboard này quan trọng với self-hosted platform — người triển khai có thể điều chỉnh quality preset mà không cần rebuild code, ví dụ giảm quality list xuống `[1080, 720, 480]` trên server CPU yếu để giảm thời gian encode.

---

## Bộ Codec và Chiến Lược Quality

DaPlex encode bốn codec video để tối ưu cho nhiều thiết bị và trình duyệt: H264 (AVC) cho compatibility tối đa, H265 (HEVC) cho bitrate thấp hơn ~40% ở cùng chất lượng, VP9 cho trình duyệt Chromium không hỗ trợ H265, và AV1 cho hiệu suất cao nhất trên trình duyệt hiện đại. H264 dùng encoder `libx264` (x264), H265 dùng `libx265` (x265), VP9 dùng `libvpx-vp9`, AV1 dùng `libsvtav1` (SVT-AV1 — nhanh hơn `libaom-av1` đáng kể ở preset thấp).

Default encode params từ `config.ts` định nghĩa chiến lược chất lượng cơ bản: H264 và H265 dùng `-crf 18` với `-preset slow` (Constant Rate Factor — encode đến target chất lượng thay vì target bitrate); VP9 dùng `-crf 24 -b:v 0` với constrained quality mode; AV1 dùng `-crf 20 -preset 4` (SVT-AV1 preset từ 0-13, càng nhỏ càng chậm và tốt hơn). Quality list H264 là `[2160, 1440, 1080, 720, 480, 360]` (tối đa 6 quality tier từ 4K đến 360p). Next-gen codecs (H265/VP9/AV1) chỉ encode `[2160, 1440]` — chỉ encode bản chất lượng cao vì H264 đã phủ toàn bộ range, next-gen dùng cho client có codec support.

Tham số GOP (Group of Pictures) được tính từ fps của video nguồn: `gopSize = fps * 2` — keyframe mỗi 2 giây, phù hợp với segment duration 6 giây của DASH (`2 keyframes/segment`). `-sc_threshold 0` tắt scene change detection để đảm bảo keyframe interval đều đặn — quan trọng cho DASH packaging vì segment boundaries phải trùng với keyframe. `-keyint_min = gopSize` đảm bảo không có keyframe ngắn hơn giữa các I-frame.

---

## Đóng Gói CMAF — MP4Box và DASH/HLS Output

Sau khi FFmpeg encode xong raw video/audio MP4, `prepareMediaFile()` gọi MP4Box với `createMP4BoxPackArgs()` để đóng gói thành **CMAF (Common Media Application Format)**. MP4Box tạo ra ba file: (1) file MP4 được đóng gói lại với `initRange` (initialization segment chứa codec info) và `indexRange` (segment index) là hai byte range trong cùng file — đây là định dạng CMAF "single file DASH"; (2) file `.mpd` là DASH manifest XML mô tả representation; (3) file `.m3u8` là HLS playlist tham chiếu các byte range trong MP4 file.

Kết quả quan trọng nhất là hai byte range: `initRange` (ví dụ `0-687`) là offset của initialization segment trong file MP4, `indexRange` (ví dụ `688-1023`) là offset của segment index. Trình phát DASH (Vidstack) dùng byte range request HTTP (`Range: bytes=0-687`) để lấy init segment, sau đó dùng segment index để tính offset của từng segment trong file mà không cần tải toàn bộ file. Thiết kế single-file CMAF này giảm số lượng file cần quản lý trên storage (một file MP4 thay vì hàng trăm segment file), đồng thời vẫn hỗ trợ đầy đủ adaptive streaming.

`StreamManifest` class (`src/utils/stream-manifest.util.ts`) là custom JSON builder tích hợp toàn bộ thông tin track từ DASH MPD và HLS m3u8. Sau khi MP4Box tạo file `.mpd` và `.m3u8`, `appendVideoPlaylist()` parse XML MPD bằng `fast-xml-parser`, extract `indexRange` và `initRange` từ `SegmentBase`, parse duration từ ISO 8601 string qua `luxon.Duration.fromISO()`, rồi thêm `HlsVideoTrack` object vào `manifest.videoTracks[]`. Tương tự, `appendAudioPlaylist()` thêm `HlsAudioTrack` vào `manifest.audioTracks[]`. Kết quả cuối cùng là một file JSON duy nhất (`manifest_N.json`) cho mỗi codec, chứa đầy đủ thông tin để Angular frontend reconstruct DASH manifest client-side — không cần server generate MPD động.

<!-- FIGURE
  id: Hình 4.13
  title: Pipeline encode FFmpeg-MP4Box-rclone — từ raw source đến CMAF trên cloud storage
  type: flowchart
  description: >
    Flowchart pipeline encode cho một codec và một quality tier. Input: encoded raw MP4 (từ FFmpeg). Bước 1: FFmpeg encode - createVideoEncodingArgs()/createAudioEncodingArgs() build args array → child_process.spawn('ffmpeg', args) → parseProgress() từ pipe:1 → log percent. Output: {quality}p.mp4 hoặc audio_{index}.mp4. Bước 2: prepareMediaFile - diskSpaceUtil.hasFreeSpace() check → MP4Box -dash 6000 -frag 6000 -rap -single-file → tạo 3 files: {quality}p.mp4 (CMAF), {quality}p.mpd (DASH MPD XML), {quality}p_1.m3u8 (HLS). Delete raw encoded file. Bước 3: StreamManifest.appendVideoPlaylist()/appendAudioPlaylist() - XMLParser parse MPD → extract initRange+indexRange → m3u8Parser parse segments → push HlsVideoTrack/HlsAudioTrack to manifest. Bước 4: rcloneHelper.uploadMedia() → rclone copyto {quality}p.mp4 {storageRemote}:{mediaId}/{streamId}/. Bước 5: videoResultQueue.add('add-stream-video'/'add-stream-audio', { streamId, fileName, codec, quality }). Bước 6 (sau tất cả quality): StreamManifest.saveFile(manifest_N.json) → rclone upload → videoResultQueue.add('add-stream-manifest').
  nodes:
    - FFmpeg -c:v libx264 -crf 18 -preset slow → {quality}.mp4 (raw)
    - MP4Box -dash 6000 -frag 6000 -rap -single-file → {quality}.mp4 (CMAF) + {quality}.mpd + {quality}_1.m3u8
    - XMLParser.parse(mpd) → initRange=0-N + indexRange=M-K
    - m3u8Parser.push(m3u8) → segments[{duration, byterange}]
    - StreamManifest.appendVideoPlaylist() → manifest.videoTracks.push({codec, initRange, indexRange, hlsSegment})
    - rcloneHelper.uploadMedia({quality}.mp4 → storage:mediaId/streamId/)
    - videoResultQueue.add('add-stream-video', {streamId, fileName, codec, quality})
    - [After all qualities]: manifest.saveFile(manifest_N.json) → upload → add-stream-manifest
  style: left-to-right; FFmpeg nền xanh nhạt; MP4Box nền cam nhạt; StreamManifest nền tím nhạt; rclone nền xanh lá nhạt; BullMQ publish nền đỏ nhạt
  output:
    drawio: figures/hinh-4-13-pipeline-encode-ffmpeg-mp4box-rclone.drawio
    png: figures/hinh-4-13-pipeline-encode-ffmpeg-mp4box-rclone.png
-->
![Hình 4.13: Pipeline encode FFmpeg-MP4Box-rclone](pending)
*Hình 4.13: Flowchart pipeline một quality tier — FFmpeg encode → MP4Box CMAF packaging → StreamManifest JSON builder → rclone upload → BullMQ result publish*

---

## Phần Chi Tiết Các Kỹ Thuật Encode

Phần 4.5 được chia thành năm mục phân tích kỹ thuật chuyên sâu từng khía cạnh của hệ thống encode:

- **[4.5.1. Tham số encode và chiến lược chất lượng](4.5.1-tham-so-encode.md)** — CRF strategy, codec-specific parameters, quality list override, hai encode mode (single-pass vs two-pass VP9), `resolveVideoFilters()` scaling và HDR tonemap, `resolveH264Params()` profile/level negotiation.
- **[4.5.2. Encode âm thanh đa kênh](4.5.2-encode-am-thanh.md)** — AAC (libfdk_aac VBR 5) và Opus (libopus VBR) dual encoding, surround downmix pan filter, extra audio tracks, `createAudioEncodingArgs()` argument pipeline.
- **[4.5.3. Đóng gói CMAF và StreamManifest](4.5.3-dong-goi-cmaf.md)** — MP4Box `-dash` command, single-file CMAF, DASH MPD structure, HLS byte-range playlist, StreamManifest JSON schema, dual-format compatibility (DASH + HLS).
- **[4.5.4. Split encoding mode](4.5.4-split-encoding.md)** — `SPLIT_ENCODING` flag, `splitAndEncodeVideo()` chia video thành segment 30 giây, encode song song qua nhiều CPU, concat bằng ffmpeg concat demuxer.
- **[4.5.5. HDR metadata và thumbnail sprite](4.5.5-hdr-thumbnail.md)** — `hdrMetadataHelper.getHdrMetadata()` detect HDR10/HDR10+/HLG, x265/libsvtav1 color metadata flags, `generateSprites()` hai size thumbnail grid, `thumbhash.util.ts` sinh placeholder hash.
