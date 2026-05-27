# AUDIT — Chương 5: Kiểm Thử

> Tạo theo quy trình PROMPT.md cập nhật.  
> Mọi kết quả được xác nhận bằng grep thực tế — không tự điền.

---

## 1. Danh Sách File — Đối Chiếu Cấu Trúc

| STT | Đường dẫn | Loại | Tồn tại? | Ghi chú |
|-----|-----------|------|----------|---------|
| 1 | `chuong-5/5.1-kiem-thu-chuc-nang.md` | file thẳng | ✅ | |
| 2 | `chuong-5/5.2-kiem-thu-abr.md` | file thẳng | ✅ | |
| 3 | `chuong-5/5.3-kiem-thu-moi-truong-mang.md` | file thẳng | ✅ | |

**Tổng: 3 file content. Tất cả tồn tại. ✅**

---

## 2. Kiểm Tra Đánh Số Hình — Toàn Chương 5

*Grep thực tế: `grep -rn "id: Hình 5\." chuong-5/`*

| ID hình | File chứa | Liên tục? | Trùng? |
|---------|-----------|-----------|--------|
| Hình 5.1 | `5.1-kiem-thu-chuc-nang.md` | ✅ | ❌ không trùng |
| Hình 5.2 | `5.2-kiem-thu-abr.md` | ✅ | ❌ không trùng |
| Hình 5.3 | `5.3-kiem-thu-moi-truong-mang.md` | ✅ | ❌ không trùng |

**Kết quả: 3 hình, Hình 5.1 → Hình 5.3, liên tục không bỏ số, không trùng. ✅**

---

## 3. Kiểm Tra FIGURE Block — 7 Trường Bắt Buộc

*Grep thực tế: `grep -n "id:\|title:\|type:\|description:\|nodes:\|style:\|output:" chuong-5/`*

| Hình | id | title | type | description | nodes | style | output |
|------|----|-------|------|-------------|-------|-------|--------|
| Hình 5.1 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Hình 5.2 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Hình 5.3 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**3/3 FIGURE block đủ 7 trường bắt buộc. ✅**

---

## 4. Kiểm Tra Số Test Case

*Grep thực tế đếm từng nhóm TC ID*

### 5.1 — Kiểm thử chức năng

| Nhóm | Dải ID | Số TC | Đúng? |
|------|--------|-------|-------|
| TC_AUTH | 001–013 | 13 | ✅ |
| TC_RBAC | 001–003 | 3 | ✅ |
| TC_MEDIA | 001–018 | 18 | ✅ |
| TC_WATCH | 001–010 | 10 | ✅ |
| TC_HIST | 001–005 | 5 | ✅ |
| TC_PL | 001–005 | 5 | ✅ |
| TC_RATE | 001–003 | 3 | ✅ |
| TC_PROF | 001–002 | 2 | ✅ |
| **Tổng** | | **59** | ✅ |

*Lỗi phát hiện và đã sửa: file ban đầu ghi "58 ca" — thực tế đếm được 59 (16+18+10+5+10=59). Đã cập nhật text, FIGURE title và caption.*

### 5.2 — Kiểm thử ABR

| Nhóm | Dải ID | Số TC | Đúng? |
|------|--------|-------|-------|
| TC_ABR | 001–006 | 6 | ✅ |
| TC_COD | 001–005 | 5 | ✅ |
| TC_BOLA | 001–010 | 10 | ✅ |
| TC_MAN | 001–005 | 5 | ✅ |
| **Tổng** | | **26** | ✅ |

*Lỗi phát hiện và đã sửa: file ban đầu ghi "31 ca" — do cộng thêm 5 TC cross-reference sang mục 5.3 (lỗi tích lũy từ phiên trước, khi 5.3 chưa hoàn chỉnh). Đã sửa thành 26 và xoá ghi chú chéo. TC_MAN_003 xuất hiện hai lần — lần hai là mention trong đoạn văn tổng hợp, không phải hàng TC trùng.*

### 5.3 — Kiểm thử môi trường mạng

| Nhóm | Dải ID | Số TC | Đúng? |
|------|--------|-------|-------|
| LAN | TC_NET_001–003 | 3 | ✅ |
| WiFi | TC_NET_004–010 | 7 | ✅ |
| Di động | TC_NET_011–024 | 14 | ✅ |
| Recovery | TC_NET_025–032 | 8 | ✅ |
| **Tổng** | | **32** | ✅ |

---

## 5. Kiểm Tra Nội Dung

| Hạng mục | Kết quả | Chi tiết |
|----------|---------|---------|
| `![...](pending)` trong draft | ✅ | 3 hình dùng `pending` — đúng theo quy ước draft phase |
| Không file nào có placeholder thực sự | ✅ | `...` trong 5.1 là code backtick ternary, không phải placeholder |
| Mọi `<!-- FIGURE -->` đủ 7 trường | ✅ | 3/3 block đủ id, title, type, description, nodes, style, output |
| Bảng test dùng đúng format | ✅ | Cột: Chức Năng \| Test Case ID \| Mô Tả \| Quy Trình \| Đánh Giá \| Kết Quả — không có cột Nhận Xét |
| `<br>` trong Quy Trình Kiểm Thử | ✅ | Tất cả bước đều dùng `<br>` |
| Không lặp Chức Năng ở các hàng liên tiếp | ✅ | Chỉ ghi tên nhóm ở hàng đầu của mỗi nhóm |
| Lỗi phát hiện và đã sửa | ✅ | 2 lỗi đếm TC (5.1: 58→59; 5.2: 31→26) |

---

## 6. Tổng Kết Chương

```
Chương 5 — Kiểm Thử
Tổng số file:        3  (3 content, không có index)
Tổng số hình:        3  (Hình 5.1 → Hình 5.3)
Tổng số test case:   117  (59 + 26 + 32)
Lỗi phát hiện:       2  (đã sửa hết)
Trạng thái:          ✅ SẴN SÀNG
```
