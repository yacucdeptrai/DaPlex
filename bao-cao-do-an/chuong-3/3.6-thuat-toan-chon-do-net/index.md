# 3.6. Thuật Toán Chọn Độ Nét

Chương này mô tả hai lớp thuật toán quyết định chất lượng video trong DaPlex: lớp **tĩnh** xảy ra một lần tại thời điểm encode (Transcoder quyết định encode ở những độ phân giải nào), và lớp **động** xảy ra liên tục trong thời gian phát (dash.js BOLA quyết định độ phân giải nào được tải tiếp theo). Hai lớp này bổ sung cho nhau: lớp tĩnh xác định không gian lựa chọn, lớp động điều hướng trong không gian đó theo điều kiện mạng thực tế.

- [**3.6.1 — Lớp Tĩnh — Thuật Toán Chọn Độ Phân Giải Khi Encode**](3.6.1-lop-tinh-encode.md): `calculateQuality`, `validateSourceQuality`, tham số CRF per codec, HDR tonemapping, H.264 profile/level.
- [**3.6.2 — Lớp Động — Thuật Toán BOLA**](3.6.2-lop-dong-bola.md): Lyapunov optimization, công thức Score(i), ưu điểm so với throughput-based ABR, tắt ABR cho audio.
- [**3.6.3 — Lựa Chọn Quality Thủ Công**](3.6.3-lua-chon-thu-cong.md): Override ABR qua vidstack API, persist server/localStorage.
- [**3.6.4 — Tổng Hợp Hai Lớp Thuật Toán**](3.6.4-tong-hop.md): Sơ đồ tổng hợp encode-time và playback-time.
