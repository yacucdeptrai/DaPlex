# AUDIT — Chương 3: Thiết Kế Hệ Thống

> Tạo theo quy trình PROMPT.md cập nhật.  
> Mọi kết quả được xác nhận bằng grep/python thực tế — không tự điền.

---

## 1. Danh Sách File — Đối Chiếu Cấu Trúc

| STT | Đường dẫn | Loại | Tồn tại? | Ghi chú |
|-----|-----------|------|----------|---------|
| 1 | `chuong-3/3.1-kien-truc-tong-the/index.md` | index thư mục | ✅ | |
| 2 | `chuong-3/3.1-kien-truc-tong-the/3.1.1-kien-truc-he-thong.md` | file thẳng | ✅ | |
| 3 | `chuong-3/3.1-kien-truc-tong-the/3.1.2-kien-truc-backend.md` | file thẳng | ✅ | |
| 4 | `chuong-3/3.1-kien-truc-tong-the/3.1.3-kien-truc-transcoder.md` | file thẳng | ✅ | |
| 5 | `chuong-3/3.2-thiet-ke-co-so-du-lieu.md` | file thẳng | ✅ | |
| 6 | `chuong-3/3.3-erd-diagram.md` | file thẳng | ✅ | |
| 7 | `chuong-3/3.4-thiet-ke-giao-dien/index.md` | index thư mục | ✅ | |
| 8 | `chuong-3/3.4-thiet-ke-giao-dien/3.4.1-giao-dien-nguoi-dung.md` | file thẳng | ✅ | |
| 9 | `chuong-3/3.4-thiet-ke-giao-dien/3.4.2-giao-dien-admin.md` | file thẳng | ✅ | |
| 10 | `chuong-3/3.5-co-che-tu-dong-chinh-do-net/index.md` | index thư mục | ✅ | |
| 11 | `chuong-3/3.5-co-che-tu-dong-chinh-do-net/3.5.1-cau-truc-file-dash.md` | file thẳng | ✅ | |
| 12 | `chuong-3/3.5-co-che-tu-dong-chinh-do-net/3.5.2-stream-manifest.md` | file thẳng | ✅ | |
| 13 | `chuong-3/3.5-co-che-tu-dong-chinh-do-net/3.5.3-chuyen-doi-manifest-sang-dash.md` | file thẳng | ✅ | |
| 14 | `chuong-3/3.5-co-che-tu-dong-chinh-do-net/3.5.4-cau-hinh-dashjs-va-bola.md` | file thẳng | ✅ | |
| 15 | `chuong-3/3.5-co-che-tu-dong-chinh-do-net/3.5.5-lua-chon-codec-av1.md` | file thẳng | ✅ | |
| 16 | `chuong-3/3.5-co-che-tu-dong-chinh-do-net/3.5.6-chon-chat-luong-thu-cong.md` | file thẳng | ✅ | |
| 17 | `chuong-3/3.5-co-che-tu-dong-chinh-do-net/3.5.7-tom-tat-luong.md` | file thẳng | ✅ | |
| 18 | `chuong-3/3.6-thuat-toan-chon-do-net/index.md` | index thư mục | ✅ | |
| 19 | `chuong-3/3.6-thuat-toan-chon-do-net/3.6.1-lop-tinh-encode.md` | file thẳng | ✅ | |
| 20 | `chuong-3/3.6-thuat-toan-chon-do-net/3.6.2-lop-dong-bola.md` | file thẳng | ✅ | |
| 21 | `chuong-3/3.6-thuat-toan-chon-do-net/3.6.3-lua-chon-thu-cong.md` | file thẳng | ✅ | |
| 22 | `chuong-3/3.6-thuat-toan-chon-do-net/3.6.4-tong-hop.md` | file thẳng | ✅ | |

**Tổng: 22 file (18 content + 4 index). Tất cả tồn tại. ✅**

---

## 2. Kiểm Tra Đánh Số Hình — Toàn Chương 3

*Grep thực tế: `grep -rn "id: Hình 3\." chuong-3/`*

| ID hình | File chứa | Liên tục? | Trùng? |
|---------|-----------|-----------|--------|
| Hình 3.1 | `3.1-kien-truc-tong-the/index.md` | ✅ | ❌ không trùng |
| Hình 3.2 | `3.1-kien-truc-tong-the/3.1.1-kien-truc-he-thong.md` | ✅ | ❌ |
| Hình 3.3 | `3.1-kien-truc-tong-the/3.1.1-kien-truc-he-thong.md` | ✅ | ❌ |
| Hình 3.4 | `3.1-kien-truc-tong-the/3.1.2-kien-truc-backend.md` | ✅ | ❌ |
| Hình 3.5 | `3.1-kien-truc-tong-the/3.1.3-kien-truc-transcoder.md` | ✅ | ❌ |
| Hình 3.6 | `3.1-kien-truc-tong-the/3.1.3-kien-truc-transcoder.md` | ✅ | ❌ |
| Hình 3.7 | `3.2-thiet-ke-co-so-du-lieu.md` | ✅ | ❌ |
| Hình 3.8 | `3.3-erd-diagram.md` | ✅ | ❌ |
| Hình 3.9 | `3.3-erd-diagram.md` | ✅ | ❌ |
| Hình 3.10 | `3.3-erd-diagram.md` | ✅ | ❌ |
| Hình 3.11 | `3.3-erd-diagram.md` | ✅ | ❌ |
| Hình 3.12 | `3.3-erd-diagram.md` | ✅ | ❌ |
| Hình 3.13 | `3.3-erd-diagram.md` | ✅ | ❌ |
| Hình 3.14 | `3.3-erd-diagram.md` | ✅ | ❌ |
| Hình 3.15 | `3.3-erd-diagram.md` | ✅ | ❌ |
| Hình 3.16 | `3.3-erd-diagram.md` | ✅ | ❌ |
| Hình 3.17 | `3.4-thiet-ke-giao-dien/3.4.1-giao-dien-nguoi-dung.md` | ✅ | ❌ |
| Hình 3.18 | `3.4-thiet-ke-giao-dien/3.4.1-giao-dien-nguoi-dung.md` | ✅ | ❌ |
| Hình 3.19 | `3.4-thiet-ke-giao-dien/3.4.1-giao-dien-nguoi-dung.md` | ✅ | ❌ |
| Hình 3.20 | `3.4-thiet-ke-giao-dien/3.4.1-giao-dien-nguoi-dung.md` | ✅ | ❌ |
| Hình 3.21 | `3.4-thiet-ke-giao-dien/3.4.2-giao-dien-admin.md` | ✅ | ❌ |
| Hình 3.22 | `3.4-thiet-ke-giao-dien/3.4.2-giao-dien-admin.md` | ✅ | ❌ |
| Hình 3.23 | `3.4-thiet-ke-giao-dien/3.4.2-giao-dien-admin.md` | ✅ | ❌ |
| Hình 3.24 | `3.4-thiet-ke-giao-dien/3.4.2-giao-dien-admin.md` | ✅ | ❌ |
| Hình 3.25 | `3.5-co-che-tu-dong-chinh-do-net/3.5.7-tom-tat-luong.md` | ✅ | ❌ |
| Hình 3.26 | `3.6-thuat-toan-chon-do-net/3.6.4-tong-hop.md` | ✅ | ❌ |

**Kết quả: 26 hình, Hình 3.1 → Hình 3.26, liên tục không bỏ số, không trùng. ✅**

*Ghi chú: `3.5.1`–`3.5.6` và `3.6.1`–`3.6.3` không có hình riêng — các mục này là nội dung lý thuyết/kỹ thuật chi tiết; hình tổng hợp nằm ở `3.5.7-tom-tat-luong.md` (Hình 3.25) và `3.6.4-tong-hop.md` (Hình 3.26), không vi phạm. `3.4/index.md`, `3.5/index.md`, `3.6/index.md` là index thuần, không cần hình.*

---

## 3. Kiểm Tra Nội Dung

| Hạng mục | Kết quả | Chi tiết |
|----------|---------|---------|
| `![...](pending)` trong draft | ✅ | 26 hình dùng `pending` — đúng theo quy ước draft phase |
| Không file nào có "nội dung sẽ bổ sung" / placeholder | ✅ | Grep không tìm thấy |
| Mọi `<!-- FIGURE -->` đủ 7 trường bắt buộc | ✅ | Python script xác nhận 26/26 blocks đủ id, title, type, description, nodes, style, output |
| `index.md` của 3.1 link đủ 3 mục con | ✅ | Links đến 3.1.1, 3.1.2, 3.1.3 |
| `index.md` của 3.4 link đủ 2 mục con | ✅ | Links đến 3.4.1, 3.4.2 |
| `index.md` của 3.5 link đủ 7 mục con | ✅ | Links đến 3.5.1–3.5.7 |
| `index.md` của 3.6 link đủ 4 mục con | ✅ | Links đến 3.6.1–3.6.4 |
| Không file thẳng nào thiếu nội dung | ✅ | Tất cả file đầy đủ nội dung học thuật |
| Lỗi phát hiện | ✅ | Không có lỗi |

---

## 4. Tổng Kết Chương

```
Chương 3 — Thiết Kế Hệ Thống
Tổng số file:        22  (18 content + 4 index)
Tổng số hình:        26  (Hình 3.1 → Hình 3.26)
Lỗi phát hiện:       0
Trạng thái:          ✅ SẴN SÀNG
```
