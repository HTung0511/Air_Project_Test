# BÀN GIAO BA → RA | Research Analyst Brief
### Từ Checklist kiểm chứng (BA) sang Nhiệm vụ nghiên cứu (RA)

**Gốc:** `CHECKLIST_KIEM_CHUNG.md` (BA, 50 tiêu chí CK-1.1→CK-5.10, 10đ)  
**Nhánh Git:** `arena/ad184e76-air-project-test` — commit `deb8864`  
**Đề tài #6:** Ô nhiễm không khí Ấn Độ — `city_day.csv` (CPCB/Kaggle) + ERA5 (Open-Meteo) — 8 TP, 14.056 dòng  
**RA nhận gói này thì làm gì:** *Không phải tick checklist*, mà **đào sâu, phản biện, lấp lỗ hổng tri thức** để checklist có cơ sở khoa học.

---

## 1. Vứt kiểu gì cho RA là đúng?

> **Đừng vứt file thô.** BA gửi 3 lớp — RA nhận 1 gói duy nhất:

| Lớp | Cái gì | Ở đâu | RA làm gì với nó |
|---|---|---|---|
| **1. Source of truth** | `CHECKLIST_KIEM_CHUNG.md` (bản BA) | Git branch này — không sửa trực tiếp | Đọc để hiểu chuẩn Pass/Fail, nhưng **không tick** |
| **2. Research Brief (file này)** | `BAN_GIAO_BA-RA.md` — bản dịch BA→RA | Cùng branch + upload Drive (xem §6) | **Việc chính của RA diễn ra ở đây** |
| **3. Phụ lục dữ liệu** | `Metadata.json`, `Data_dictionary.md`, `reports/cleaning_log_8cities.md`, `cleaning_summary_8cities.csv` | `Air-Project-main/` | RA trích dẫn, không tự đi tìm lại |

**Quy tắc vàng:**
- BA **khóa ngưỡng** (ví dụ nội suy ≤14 ngày, AQI≥201, IQR theo tháng) — RA **không tự đổi**, chỉ **đề xuất có bằng chứng** và ghi vào `reports/cleaning_log_8cities.md` § Hạn chế.
- RA **trả về** 1 trong 2: (a) xác nhận ngưỡng BA là hợp lý + trích dẫn, hoặc (b) đề xuất đổi ngưỡng + thí nghiệm so sánh (sensitivity).
- Mọi trao đổi RA↔BA diễn ra bằng **comment trên Drive** hoặc **issue trên Git**, không qua chat rời rạc.

---

## 2. RA cần trả lời 5 câu hỏi nghiên cứu (map thẳng vào P1-P5 của BA)

| # | Câu hỏi BA đã đặt (đo được) | Nhiệm vụ RA — đào sâu | Checklist BA liên quan | Deliverable RA |
|---|---|---|---|---|
| **RQ1** | *Vì sao chọn Ấn Độ + 8 TP này?* | **Literature + bối cảnh:** Tìm 3–5 báo cáo CPCB/WHO về Delhi/Lucknow/Gurugram Top ô nhiễm TG; giải thích vì sao 8 TP được chọn theo độ phủ AQI (không phải ngẫu nhiên) → bias chọn mẫu | CK-1.1, 1.2, 4.5 | §2.1 trong `RA_REPORT.md`: 1 trang bối cảnh + bảng tiêu chí chọn 8/26 TP |
| **RQ2** | *Dữ liệu thiếu do đâu? Xử lý có đúng?* | **Cơ chế thiếu:** Phân loại MAR/MCAR/MNAR cho 5 cột thiếu nặng (PM10 Lucknow 100%, Chennai 84.5%, NH3 Gurugram 92.9%, PM10 Gurugram 52.4%, NH3 Lucknow 49.7%) + bằng chứng block_ratio; đánh giá rủi ro nếu đổi 14 ngày → 30/60 ngày | CK-2.5→2.14, 5.2 | Bảng `Cơ chế thiếu | Bằng chứng | Rủi ro nếu đổi ngưỡng` + chart missing pattern (reuse `02_cleaning_evidence.ipynb`) |
| **RQ3** | *Ô nhiễm nặng ở đâu/khi nào/do chất nào?* | **Xác thực EDA:** Kiểm lại 3 phát hiện lớn (Delhi 51% ngày nặng, mùa 11–12 cao gấp 3×, PM2.5 gấp 2.8× ngày thường) có robust không khi đổi khoảng chung/bỏ COVID; tìm confounder (trạm đo, Diwali, đốt rơm Punjab) | CK-3.1→3.8, 5.3→5.5 | §3 EDA validation: sensitivity table + ghi chú confounder cho từng chart |
| **RQ4** | *Thời tiết có “gây” ô nhiễm không?* | **Khử mùa + nhân quả:** Giải thích vì sao tương quan thô sai lệch, phải dùng anomaly (median City×Month); đánh giá 3 giả thuyết (gió yếu/BLH thấp/không mưa) với Bonferroni+FDR; **không** nói nhân quả | CK-3.8, 2.15, 3.11 | §4 Weather: bảng `corr thô vs khử mùa` + 4 chart `corr_*.png` đã có, bổ sung diễn giải |
| **RQ5** | *Dự đoán AQI ngày mai có khả thi?* | **Thiết kế mô hình:** So L1→L3 vs 3 baseline, vì sao Ridge trước cây, vì sao không dùng thời tiết ngày mai (cận trên giả), leakage `mask_interp/as_of`; đề xuất metric chính (MAE cho hồi quy, Precision/Recall cho cảnh báo ≥201) + chẩn đoán phần dư | CK-3.9→3.16, 5.1 | §5 Model card: bảng MAE/R²/Precision/Recall + residual plot + khuyến nghị ngưỡng cảnh báo |

> **Nếu RA chỉ có 2 ngày:** làm RQ2 + RQ3. Nếu đủ 1 tuần: làm cả 5.

---

## 3. Gói bàn giao gồm gì? (RA tải 1 lần là đủ)

```
Air-Project-main/
├── CHECKLIST_KIEM_CHUNG.md          ← BA source (khóa)
├── BAN_GIAO_BA-RA.md                ← file này (brief)
├── Metadata.json                    ← provenance 2 nguồn
├── Data_dictionary.md               ← 16 cột gốc + 40 cột sạch + 14 cột thời tiết
├── Reports/
│   ├── cleaning_log_8cities.md      ← 17 bước + 15 hạn chế — RA đọc trước tiên
│   ├── cleaning_summary_8cities.csv ← 105 dòng (8TP×13 cột) — RA dùng để tính lại
│   ├── suspect_points_8cities.csv   ← 93 điểm điều tra — RA phản biện luật 4 bằng chứng
│   └── figures/                     ← 15 chart (6 EDA +4 corr +5 model) — RA không vẽ lại, chỉ validate
├── Data/processed/
│   ├── air_quality_8cities.csv      ← 14.056×40 — RA chạy lại EDA nếu cần
│   └── air_quality_8cities_weather.csv ← 14.056×54 — RA chạy corr/model
└── src/*.py + notebooks/01→06       ← pipeline chuẩn — RA không sửa, chỉ đọc
```

**RA không cần:** `data/raw/weather/*.gz` (đã gộp), `data/interim/` (cũ, bỏ).

---

## 4. RA làm việc thế nào với checklist? (3 việc, không phải tick)

### Việc 1: Phản biện ngưỡng BA — mỗi ngưỡng 1 đoạn
Ví dụ cho CK-2.6 (nội suy ≤14 ngày):

> *BA chốt 14 ngày. RA kiểm: nếu đổi 14→30 ngày thì thêm 1.316 ô (đã từng bị lỗi pandas limit=14), MAE model thay đổi bao nhiêu? Có đáng để đổi không? Kết luận: giữ 14 ngày vì... (trích log).* 

RA làm tương tự cho: flatline ≥3 ngày, IQR×1.5 theo tháng, AQI≥201, train/test split.

### Việc 2: Lấp lỗ hổng tri thức — BA đã để sẵn 15 hạn chế
Trong `cleaning_log_8cities.md` §3 Hạn chế có sẵn 15 dòng rủi ro (ví dụ: Delhi/Gurugram thời tiết trùng 0.95–0.999, PM10 Chennai thiếu 84.5%, data là model ERA5 0.25° không phải đo trạm). RA chọn ≥5 cái quan trọng, viết **tác động tới kết luận + cách giảm thiểu**.

### Việc 3: Trích dẫn — mỗi phát hiện ≥1 nguồn ngoài
- RQ1: WHO Air Quality Database, CPCB Annual Report
- RQ2: Little & Rubin (MAR/MCAR), paper về flatline sensor
- RQ3: Paper về Diwali + stubble burning Punjab
- RQ4: Paper về BLH (boundary layer height) và AQI
- RQ5: Paper về persistence baseline cho AQI forecasting

RA không cần đọc hết, chỉ cần 1 nguồn/cluster để giám khảo thấy “có nghiên cứu”.

---

## 5. RA trả về cái gì? (Definition of Done)

RA xong khi có **1 file duy nhất** + **comment trên checklist**:

**File:** `reports/RA_REPORT.md` hoặc `docs/RA_FINDINGS.md` (≤10 trang), gồm:

1. **Tóm tắt 5 dòng** (mỗi RQ 1 dòng: xác nhận/bác + hệ quả)
2. **Bảng phản biện ngưỡng** (4 cột: Ngưỡng BA | Thí nghiệm RA | Kết quả | Khuyến nghị)
3. **Bảng bias/confounder** (3 cột: Bias | Tác động | Giảm thiểu) — bổ sung cho CK-4.5
4. **Trích dẫn** (≥5 nguồn, format APA, kèm URL + ngày truy cập)
5. **Khuyến nghị cho BA/Dev** (ví dụ: “Giữ 14 ngày, không đổi; nhưng Gurugram NH3 nên drop khỏi L2”)

**Comment:** RA comment trực tiếp vào `CHECKLIST_KIEM_CHUNG.md` trên Drive (dùng Google Drive API `create_comment`) ở các dòng CK-2.6, CK-3.8, CK-4.5 — để BA biết chỗ nào cần sửa ngưỡng/lời văn.

---

## 6. Cách “vứt” — thao tác cụ thể (30 giây)

### Option A: Git-only (đã xong)
```bash
git checkout arena/ad184e76-air-project-test
git log --oneline -2  # thấy deb8864
# RA clone cùng branch, đọc BAN_GIAO_BA-RA.md
```
> Đủ cho team dev. Không cần Drive.

### Option B: Drive cho RA không dùng Git (khuyến nghị)
1. Upload 2 file lên Drive: `CHECKLIST_KIEM_CHUNG.md` + `BAN_GIAO_BA-RA.md` (dùng `upload_file` với `target_mime_type='application/vnd.google-apps.document'` để RA comment được).
2. Tạo folder Drive `BA→RA | Air Project — Checklist 11/11/2026`, move 2 file vào.
3. `create_permission` cho RA (email) với role `commenter` (được comment, không được sửa), gửi kèm message:
   > “Gửi RA brief + checklist BA. Nhờ phản biện 5 RQ (§2), trả về RA_REPORT.md + comment trên checklist. Deadline: [điền].”
4. RA comment → BA nhận email → BA resolve comment sau khi sửa.

> Hiện tại Drive connector đã bật (`google_drive` enabled), có thể chạy `upload_file` ngay khi có file_path.

### Option C: Gửi link GitHub
Push branch lên remote rồi gửi URL:
```
https://github.com/HTung0511/Air_Project_Test/blob/arena/ad184e76-air-project-test/CHECKLIST_KIEM_CHUNG.md
https://github.com/HTung0511/Air_Project_Test/blob/arena/ad184e76-air-project-test/BAN_GIAO_BA-RA.md
```
RA xem trực tiếp, không cần tải.

---

## 7. Mẫu tin nhắn bàn giao (copy-paste)

> Chào RA,
>
> BA đã chốt checklist kiểm chứng đo được cho đồ án #6 (50 tiêu chí, 10đ, map vào pipeline 8TP). Gửi RA gói bàn giao:
> - **Research Brief:** `BAN_GIAO_BA-RA.md` (§2 có 5 RQ cần đào sâu)
> - **Checklist gốc:** `CHECKLIST_KIEM_CHUNG.md` (đừng sửa, chỉ comment)
> - **Data pack:** `Metadata.json` + `Data_dictionary.md` + `cleaning_log/summary/suspect_points`
>
> **Nhờ RA:** (1) phản biện ngưỡng 14 ngày/201/60%, (2) lấp 5 hạn chế, (3) trả `RA_REPORT.md` ≤10 trang + comment trên Drive.
> Branch: `arena/ad184e76-air-project-test`.
> Deadline: [điền].

---

## 8. Anti-pattern — đừng vứt kiểu này

| Kiểu vứt sai | Vì sao RA ngộp/bỏ qua |
|---|---|
| Gửi mỗi file 310 dòng, không brief | RA không biết bắt đầu từ đâu, không biết ưu tiên RQ nào |
| Gửi qua chat rời rạc, không folder | Mất provenance, không comment được, không trace |
| Cho RA sửa luôn checklist gốc | Mất khóa ngưỡng, BA không kiểm soát scope creep |
| Không ghi deadline/deliverable | RA nghiên cứu lan man, không trả về gì đo được |

---

> **BA đã xong phần “đặt thước đo”. RA nhận thước này để “kiểm thước có đúng khoa học không”.** Hai vai gặp nhau ở 5 RQ — mọi thứ khác là phụ.

— Hết brief. Đính file này + checklist gốc là đủ để RA bắt tay ngay.
