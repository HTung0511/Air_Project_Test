# Ghi chú lời nói thuyết trình & Checklist trước buổi chiếu (Y07 · Y35 · Y37 · Y42)

Tài liệu này đi kèm bản **Demo tương tác Dự báo AQI ngày hôm sau (t → t+1) cho 8 thành phố Ấn Độ**. Theo nguyên tắc thiết kế (Y07, Y35), phần lời dẫn và checklist được tách thành tài liệu riêng để màn hình trình chiếu chính luôn thoáng, ít chữ và không bị lộ ghi chú khi chiếu lên máy chiếu.

---

## 1. Kịch bản kể chuyện tuần tự 3 ca + Chọn ngày tự do (Y07 · Y37)

> **Lưu ý phương pháp:** Các ca dưới đây là **ví dụ minh họa có thật** trích xuất từ artifact đã đối soát (`R2_B04_baseline_predictions.csv` tại commit `13e93ae`), **không đại diện cho toàn bộ tập dữ liệu**. Hiệu năng tổng thể phải xem trên toàn tập Test (`n = 1.947`) và Holdout (`n = 975`).

### Mở đầu (30 giây) — Giới thiệu bài toán & Mini Map Ấn Độ
- **Thao tác:** Chỉ vào **Mini Map Ấn Độ 8 thành phố** và thanh **Timeline `t → t+1`** ở chế độ **Tập Test (đích 01/07/2019 – 29/02/2020)**, bật chế độ **Ẩn thực tế `t+1` trước khi mở đối chiếu**.
- **Lời nói gợi ý (2–3 câu):**
  > *"Bài toán của nhóm là đứng ở cuối ngày hôm nay `t`, dùng lịch sử AQI, nồng độ chất ô nhiễm và khí tượng ERA5 đến hết ngày `t` để dự báo AQI ngày mai `t+1` và phát cảnh báo sớm ngày ô nhiễm nặng (`AQI thực tế ≥ 201`) cho 8 thành phố Ấn Độ. Do AQI có tính quán tính rất mạnh, mọi kết quả của mô hình Ridge L3 đều phải đối chiếu trực tiếp với baseline 'Ngày mai = hôm nay' (`AQI(t)`)."*

---

### Ca 1: Báo đúng (True Positive) — Mô hình bắt sớm đợt bùng phát ô nhiễm nặng
- **Ca chọn nhanh:** **Gurugram · Đầu vào `t = 19/11/2019` → Ngày đích `t+1 = 20/11/2019`** (Tập Test).
- **Số liệu kiểm chứng:**
  - `AQI(t)` hôm nay = **148,0** (mức Trung bình; thấp hơn cả ngưỡng F2 `160` lẫn ngưỡng `201` → Baseline **không phát cảnh báo**).
  - Dự báo `Ridge L3 (t+1)` = **219,35** (`219,346148`, vượt cả ngưỡng ưu tiên recall `166` lẫn ngưỡng `201` → Mô hình **phát cảnh báo**).
  - Thực tế `AQI(t+1)` (sau khi bấm *Mở kết quả thực tế*) = **223,0** (`≥ 201`, ngày ô nhiễm nặng).
- **Lời nói gợi ý (2–3 câu):**
  > *"Tại Gurugram ngày 19/11/2019, AQI hôm nay mới ở mức 148 nên nếu tin rằng 'ngày mai giống hôm nay' thì baseline không cảnh báo. Nhờ kết hợp nồng độ chất ô nhiễm và điều kiện khí tượng ngày `t`, Ridge L3 dự báo AQI ngày mai tăng lên 219,35 và phát cảnh báo sớm; khi mở thực tế ngày 20/11, AQI vọt lên 223 — mô hình Báo đúng trong khi baseline Bỏ sót."*

---

### Ca 2: Bỏ sót & Quy tắc chính xác sát ngưỡng (False Negative / Near-Threshold)
- **Ca chọn nhanh:** **Amritsar · Đầu vào `t = 03/01/2020` → Ngày đích `t+1 = 04/01/2020`** (Tập Test).
- **Số liệu kiểm chứng:**
  - `AQI(t)` hôm nay = **160,0** (đúng bằng ngưỡng F2 `160,0` của baseline).
  - Dự báo `Ridge L3 (t+1)` gốc = **165,973826** (nhỏ hơn ngưỡng vận hành F2 `166,000000` đúng `0,026174` điểm!).
  - Thực tế `AQI(t+1)` = **221,0** (`≥ 201`, ngày ô nhiễm nặng) → Kết quả của Ridge L3: **Bỏ sót (FN)**.
- **Lời nói gợi ý (2–3 câu):**
  > *"Ca Amritsar ngày 03/01/2020 minh họa cả tình huống Bỏ sót lẫn nguyên tắc kỹ thuật không làm tròn trước khi xét ngưỡng: dự báo gốc của Ridge L3 là `165,973826`, nếu làm tròn hiển thị thành `166` người xem sẽ tưởng mô hình có báo, nhưng so trên giá trị gốc `165,973826 < 166` nên hệ thống không phát cảnh báo. Ngày hôm sau AQI thực tế tăng vọt lên 221, đây là một trong 12 ca Bỏ sót của Ridge L3 trên tổng số 389 cặp ngày nặng của tập Test."*

---

### Ca 3: Báo nhầm khi ô nhiễm giảm nhanh (False Positive)
- **Ca chọn nhanh:** **Delhi · Đầu vào `t = 18/10/2019` → Ngày đích `t+1 = 19/10/2019`** (Tập Test) hoặc **Lucknow · `t = 15/12/2019 → t+1 = 16/12/2019`**.
- **Số liệu kiểm chứng (Delhi 18/10 → 19/10/2019):**
  - `AQI(t)` hôm nay = **265,0** (đang ô nhiễm nặng).
  - Dự báo `Ridge L3 (t+1)` = **232,73** (`232,730306 ≥ 166` và `≥ 201` → Phát cảnh báo).
  - Thực tế `AQI(t+1)` = **170,0** (`< 201`, đã giảm xuống mức Trung bình) → Kết quả: **Báo nhầm (FP)**.
- **Lời nói gợi ý (2–3 câu):**
  > *"Ngược lại, khi chọn ngưỡng ưu tiên recall (`166` cho Ridge L3, chọn bằng F2 trên out-of-fold của tập train) để giảm tối đa số lần bỏ sót, mô hình chấp nhận đánh đổi bằng các ca Báo nhầm khi không khí thực tế hôm sau bất ngờ thông thoáng hơn dự kiến. Trên toàn tập Test, ở chế độ F2, Ridge L3 đạt cùng mức recall cao như baseline (`96,9%` so với `96,1%`, chênh lệch chưa tách khỏi 0) nhưng giảm số lần báo nhầm từ `143` xuống `113` ca (precision tăng `+4,6` điểm %)."*

---

### Bước 4: Mời khán giả / giảng viên chọn thành phố & ngày tự do + Chuyển sang Holdout & Lớp Chi Tiết
- **Thao tác:**
  1. Bấm trực tiếp vào bất kỳ chấm thành phố nào trên **Mini Map Ấn Độ** (hoặc cụm phóng to **Delhi – Gurugram**), kéo thanh **Timeline** sang ngày bất kỳ (bao gồm cả ngày khuyết dữ liệu tại Amritsar như `t+1 = 26/08/2019` hoặc ngày vượt thang `> 500` tại Delhi `t+1 = 03/11/2019` với `AQI = 659`).
  2. Chuyển công tắc giai đoạn sang **Holdout (đích 01/03/2020 – 01/07/2020)**.
  3. Bấm mở **Ngăn Chi Tiết & Kiểm Chứng (Lớp 2)** để xem sơ đồ pipeline, bậc thang MAE L1→L3, ma trận 2×2 và hạn chế F01.
- **Lời nói gợi ý cho Holdout & Lớp Chi Tiết (2–3 câu):**
  > *"Trên tập Test mùa đông (`n = 1.947`), Ridge L3 giảm MAE từ `23,47` xuống `19,52` điểm (`ΔMAE = -3,95`, KTC 95% `[-5,40; -2,56]`). Tuy nhiên khi đối chiếu sang giai đoạn Holdout giữ lại cuối (`01/03 – 01/07/2020`, `n = 975`, chỉ có `18` cặp ngày nặng), MAE của L3 là `13,78` so với `14,80` của baseline (`ΔMAE = -1,02`, KTC 95% `[-2,70; +0,48]` theo báo cáo RA/DA hoặc `[-2,80; +0,50]` theo biến thể script — đều chứa 0), nghĩa là **chưa đủ bằng chứng về lợi thế trên holdout**."*

---

## 2. Checklist kiểm tra trước buổi trình chiếu (Y35)

> *Lưu ý: Danh sách dưới đây dùng để người thuyết trình tự kiểm tra thực tế trên máy tính và máy chiếu tại phòng thi/báo cáo; việc đánh dấu không thay thế cho kiểm thử thiết bị thực tế.*

- [ ] **Kiểm tra chạy Offline thực tế:** Ngắt thử Wi-Fi sau khi mở trang (hoặc chạy bản `npm run preview` / `dist/index.html`), xác nhận bản đồ SVG Ấn Độ 8 thành phố, dữ liệu 2.922 cặp dự báo và biểu đồ lịch sử hiển thị đầy đủ không cần mạng.
- [ ] **Kiểm tra độ phân giải & tương phản trên máy chiếu:** Cắm cáp HDMI/VGA vào máy chiếu, kiểm tra ở độ phân giải `1280×720` và `1920×1080` xem hai làn của **Thước quyết định AQI** và 8 chấm trên **Mini Map Ấn Độ** có rõ chữ, không bị chồng lấn nhãn `Delhi` – `Gurugram` hay không.
- [ ] **Kiểm tra trạng thái khởi động chống lộ đáp án (Anti-spoiler):** Đảm bảo chế độ **"Ẩn thực tế `t+1` trước khi đối chiếu"** đang bật và bản đồ đang để ở chế độ **"AQI quan sát ngày đầu vào `t`"** để màu bản đồ không tiết lộ kết quả ngày mai trước lời nói.
- [ ] **Kiểm tra thao tác bàn phím & giữ ngữ cảnh:** Thử phím mũi tên `←` / `→` để lướt ngày, phím `Space` / `Enter` để mở thực tế `t+1`, và mở/đóng **Lớp Chi Tiết** để xác nhận thành phố và ngày đang chọn được giữ nguyên.
- [ ] **Chuẩn bị sẵn câu trả lời vấn đáp về hạn chế:** Nắm vững 4 điểm trung thực khoa học:
  1. **Trạng thái F01 (Leakage):** `as_of` trong notebook hiện cắt bảng đã làm sạch hồi cứu (nội suy `≤ 14` ngày), chưa chứng minh nhân quả từ raw end-to-end (dù thử nghiệm walk-forward V07 cho thấy 0 dòng test/holdout đổi đặc trưng và MAE test chỉ chênh `19,517` vs `19,519`).
  2. **Đóng góp của thời tiết:** Giảm MAE thêm `1,40` điểm (`L3` so với `L2`), nhưng ở bài toán cảnh báo ngưỡng `201`, lợi thế chủ yếu đến từ chất ô nhiễm và lịch sử AQI (`L2`), phần thêm riêng của thời tiết chưa tách khỏi 0.
  3. **Giới hạn cỡ mẫu theo nhóm thành phố:** Quy ước `< 30` ngày nặng — nhóm Nam Ấn (`Bengaluru, Chennai, Hyderabad`) chỉ có tổng cộng `10` cặp ngày nặng trong Test nên không đủ cỡ mẫu để kết luận về recall/precision.
  4. **Không diễn giải nhân quả:** `Ridge L1`, `L2`, `L3` là ba mô hình được fit riêng trên thang `log(AQI)`; chênh lệch dự báo giữa chúng không phải là tác động nhân quả của thời tiết hay chất ô nhiễm.
