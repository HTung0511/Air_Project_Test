# Giao thức kiểm chứng vòng 2 của DA (khóa trước khi có bản sửa)

Phiên bản 1.0 · 11/11/2026 · Người lập: AI-3 DA · Người duyệt: AI-2 RA (chưa duyệt).

Căn cứ: `AI_REMEDIATION_HANDOFF.md` tại `cd719cf`; `RA_DECISIONS_01.md` tại `8c525ab`; `RA_DECISIONS_02.md` tại `fa34b69` (cả ba nằm trên nhánh `arena/8afd3d48-air-project-test`).

Tài liệu này là **cam kết về cách kiểm**, không phải kết quả. Chưa có anchor `R2-V…` nào được đánh đạt nhờ tài liệu này.

## 0. Trạng thái lúc khóa

- DA chưa thấy mã, log hay metric nào của Dev. Trên remote chưa có nhánh `arena/5cb21c04-air-project-test`.
- DA đã đọc các con số Dev dự kiến mà RA dẫn lại trong RA-DEC-02: 8.668 mẫu, 5.746/1.947/975, thêm 5 mẫu train, 6 ô PM2.5, 4 ô AQI, khoảng 50 ô CO. Các số này **không** là điều kiện đạt ở bất kỳ phép thử nào dưới đây.
- Tập test (01/07/2019–29/02/2020) và holdout (từ 01/03/2020) **đã được mở**: nhóm tác giả dùng ở NB06, DA dùng ở V21–V24 và S01–S06 vòng 1. Metric vòng 2 vì thế không phải xác nhận ngoài mẫu mới. Không lựa chọn nào trong giao thức này phụ thuộc vào kết quả test hay holdout vòng 2.
- SHA của giao thức là SHA commit đầu tiên chứa file này; DA ghi SHA đó vào `reproduction_log.md` và vào HANDOFF. Sửa giao thức sau khi khóa chỉ bằng mục "Sửa đổi" có ngày ở cuối file, không viết đè nội dung cũ.

## 1. Định danh mã và dữ liệu

| Đối tượng | Định danh | Cách lấy | Ghi chú |
|---|---|---|---|
| Mã và dữ liệu baseline | Tree git: `src` `848b2db7`, `data` `6e5d738d`, `notebooks` `f7e69545` | `git archive ccd0a63 Air-Project-main` ra scratch | Ba tree này giống nhau ở `b8aba4b`, `ccd0a63`, `0dfc715`, `fa34b69`. |
| Script DA vòng 1 | Commit `0dfc715`, thư mục `reports/ra/evidence/scripts/` | `git archive 0dfc715` ra scratch | Chạy trong scratch để không ghi đè bằng chứng v1.1. |
| Mã Dev | SHA 40 ký tự do Dev ghi trong HANDOFF | `git fetch origin <nhánh Dev>` rồi `git archive <SHA>` ra scratch | Không merge, không cherry-pick vào nhánh DA. Không nhận "bản mới nhất". |
| Script DA vòng 2 | Commit trên nhánh `arena/b5aacef3-air-project-test` | `reports/ra/round2/evidence/scripts/` | Mỗi kết quả ghi SHA script đã chạy. |

Trước khi chạy mã Dev, DA so blob của `data/raw/city_day.csv` và 8 file cache thời tiết ở commit Dev với baseline. Nếu khác, DA dừng và báo RA.

## 2. Môi trường

- Máy DA: Python 3.11.2, 2 CPU, không có mạng tới `archive-api.open-meteo.com`.
- **Môi trường baseline** (`.venv-da`): ghim đúng phiên bản vòng 1: numpy 2.4.6, pandas 3.1.1, scipy 1.17.1, scikit-learn 1.9.1, statsmodels 0.15.0, matplotlib 3.11.2, seaborn 0.13.2, nbclient 0.11.0, nbformat 5.11.1, ipykernel 7.4.0, requests 2.34.2, pillow 13.0.0.
- **Môi trường bản sửa** (`.venv-dev`): cài đúng file lock của Dev, không nới phiên bản. Nếu resolver hoặc wheel lỗi trên 3.11.2, DA gửi traceback cho RA và ghi blocked; không tự đổi phiên bản rồi báo đạt.
- Để tách ảnh hưởng môi trường khỏi ảnh hưởng bản sửa, mã baseline được chạy ở cả hai môi trường khi cài được. Chênh lệch giữa hai lần chạy mã baseline là ảnh hưởng môi trường.
- Mỗi kết quả ghi: SHA mã, môi trường (`pip freeze`), lệnh, exit code, đường dẫn artifact, SHA-256 của artifact.

## 3. Đại lượng dự báo, nhãn và tập mẫu

Theo RA-DEC-02 mục 2.

- Một mẫu là một cặp (thành phố, ngày t). Nhãn `y = AQI_raw(t+1)` đọc từ `data/raw/city_day.csv`, với t+1 là **ngày lịch kế tiếp**.
- **Tập mẫu mới `C_new`**: 8 thành phố; `Date ≥ 14/06/2017`; `Date_target ≤ 01/07/2020`; `AQI_raw(t)` và `AQI_raw(t+1)` đều có, hữu hạn và lớn hơn 0.
- **Tập mẫu cũ `C_old`**: kết quả của `model_utils.build_dataset()` trên mã và dữ liệu baseline.
- Khóa mẫu là `(City, Date)`.
- DA dựng `C_new` bằng script riêng đọc thẳng file raw, **không import** `src/` (cũ hay mới). Kết quả này là bản tham chiếu của DA, dùng để so với mã Dev.
- Nhãn raw được báo là "AQI ghi trong raw của snapshot hiện có". DA không gọi đó là ground truth trạm và không coi đó là mô phỏng việc phát hành số liệu theo thời gian thực.

Điều kiện đạt của DA-03 (khóa trước):

1. Tập khóa của Dev trùng **chính xác** `C_new` do DA dựng.
2. Mọi `y` của Dev bằng chính xác `AQI_raw` tại `(City, Date + 1 ngày)`. Không có nhãn nào được nội suy, điền, cắt ở 500 hay đổi giá trị.
3. Chia tập theo `Date_target` (mục 4), không theo `Date`.
4. Giá trị AQI không hợp lệ (thiếu, không hữu hạn, ≤ 0) được báo bằng số đếm và ngày; không có dòng nào bị loại ngoài ba điều kiện của `C_new`.
5. Bảng khóa thêm/bớt do Dev lưu trùng với diff `C_new` so với `C_old` do DA tính.

DA báo kèm: số hàng thêm và bớt theo thành phố, mùa (định nghĩa `eda_utils.season_of` của baseline) và split; AQI raw và AQI bảng sạch ở t và t+1 cho từng khóa thêm/bớt; số khóa chung có nhãn cũ khác nhãn mới.

## 4. Chia tập (giữ nguyên, theo ngày được dự đoán)

| Tập | `Date_target` |
|---|---|
| Train | đến hết 30/06/2019 |
| Test | 01/07/2019 – 29/02/2020 |
| Holdout | 01/03/2020 – 01/07/2020 |

Không đổi mốc, không thêm tập, không gộp holdout vào test.

## 5. Mô hình, chọn alpha, chọn ngưỡng

- Ba baseline, học trên train: trung bình theo thành phố; trung vị cùng thành phố cùng tháng của ngày được dự đoán; "ngày mai = hôm nay".
- Ridge L1, L2, L3 trên `log(y)`, đổi ngược bằng `exp`. Đây là nhóm mô hình **chính**.
- Ridge L4 (thời tiết ngày mai, cận trên) và HistGradientBoosting là **phụ**: báo nếu notebook của Dev còn giữ, không dùng để xét F01/F02.
- **Alpha**: lưới `[0,1; 1; 10; 30; 100; 300]`; `TimeSeriesSplit` 4 lần chia, bỏ 16 dòng giữa train và validation, trên train sắp theo `(Date_target, City)`; chọn alpha có MAE trung bình (điểm AQI) nhỏ nhất, hòa thì lấy alpha nhỏ hơn. Alpha mới được phép khác alpha cũ; DA báo cả hai.
- **Ngưỡng cảnh báo F2**: dự đoán out-of-fold của chính các lần chia trên; lưới 80…300 bước 1; chọn ngưỡng có F2 lớn nhất, hòa thì lấy ngưỡng nhỏ hơn. Ngưỡng của "ngày mai = hôm nay" chọn theo cùng cách trên `AQI(t)`.
- Test và holdout chỉ dùng để báo cáo. Không tune lại bằng test để lấy lại số cũ.
- Nếu Dev đổi lưới, cách chia CV hay tiêu chí chọn, DA ghi là thay đổi giao thức cần RA xét, và chạy thêm một lần theo đúng lưới và CV ở trên để so.

## 6. Chỉ số

- Hồi quy, trên test và holdout: n, số ngày nặng, MAE, RMSE, R² (`1 − SSE/SST` trên tập đánh giá), MAE riêng ngày nặng và ngày còn lại.
- Cảnh báo AQI ≥ 201, trên test và holdout: TP, FP, FN, TN, recall, precision, F1, ở ngưỡng 201 và ở ngưỡng F2.
- Holdout vòng 1 chỉ có 18 ngày nặng. Chỉ số cảnh báo trên holdout được báo bằng số đếm; khoảng tin cậy chỉ tính khi TP > 0 và được ghi là không ổn định.

## 7. So sánh cùng mẫu và khoảng tin cậy

- Hiệu được tính trên **cùng các dòng**.
- Bootstrap khối: khối 14 ngày lịch chung cho mọi thành phố, số khối tính từ ngày được dự đoán nhỏ nhất của tập đang đánh giá; B = 4.000; seed 0; khoảng phân vị 95%.
- Độ nhạy: lặp lại với khối 7 và 28 ngày.
- Danh sách so sánh cố định (không thêm sau khi thấy số):
  1. MAE, test và holdout: L1 − hôm nay; L2 − L1; L3 − L2; L3 − hôm nay.
  2. Cảnh báo, test: L3@201 so với hôm nay@201; L3@F2 so với hôm nay@F2; mỗi cặp cho recall, precision, F1.
  3. Mã mới so với mã cũ, test và holdout: MAE(mới) − MAE(cũ) cho hôm nay, L1, L2, L3; kèm số dòng đổi cờ cảnh báo.
- Cách diễn đạt: "tách khỏi 0" chỉ khi khoảng 95% không chứa 0; ngược lại ghi "chưa tách được". Các khoảng là theo từng phép so, không hiệu chỉnh đa so sánh; DA ghi rõ điều đó.

## 8. Bốn thiết kế so sánh

Theo RA-DEC-02 mục 2, phần "So sánh bắt buộc".

| Mã | Thiết kế | Tập train | Tập đánh giá | Trả lời câu hỏi |
|---|---|---|---|---|
| A | Mã mới, nhãn raw | Train của `C_new` | Test và holdout của `C_new` | Kết quả của đường dự báo mới. |
| B | Mã cũ so với mã mới | Khóa train thuộc `C_old ∩ C_new` | Khóa test/holdout thuộc `C_old ∩ C_new` có nhãn cũ bằng nhãn mới | Tác động của việc đổi tiền xử lý, giữ nguyên mẫu và nhãn. |
| C | Mã mới, bỏ các khóa train được thêm | Train của `C_new` trừ các khóa không có trong `C_old` (theo diff thật) | Như A | Tác động của việc mở rộng train. |
| D | Phần chênh nhãn | — | Khóa chung có nhãn cũ khác nhãn mới, và khóa test/holdout chỉ có ở một bên | Báo riêng; không gọi là so sánh cùng outcome. |

Mỗi thiết kế chọn alpha và ngưỡng theo mục 5 trên train của chính nó. Mỗi bảng ghi n và nguồn nhãn.

**Không có ngưỡng metric nào là điều kiện đạt của F01.** Metric kém đi không làm F01 trượt; metric tốt lên không làm F01 đạt. Kết quả âm tính được giữ nguyên trong hồ sơ.

## 9. Phép thử theo từng mã việc

Cách chạy chung: mọi phép thử chạy trên bản sao ở scratch. Dữ liệu raw, cache và baseline trong repo không bị ghi. Mỗi lần chạy có theo dõi I/O: danh sách file được mở để đọc và ghi, kèm SHA-256, và mọi lần thử mở kết nối mạng.

### 9.1. DA-01 / F02 — NB04 cache-first

| Mã | Phép thử | Điều kiện đạt (khóa trước) | Ghi chú |
|---|---|---|---|
| T1.1 | Cài file lock của Dev trên Python 3.11.2 | `pip install` exit 0; `pip check` không báo xung đột | Lưu `pip freeze`. |
| T1.2 | Cú pháp NB04 trên 3.11 | Mọi ô mã qua `ast.parse` | Thay cho lỗi f-string ở ô 29 vòng 1. |
| T1.3 | Chạy NB04 của Dev, không sửa, đủ 8 cache, mạng tắt | Exit 0; mọi ô mã được chạy; không ô nào cần mạng; 8 file cache giữ nguyên SHA-256 | Mạng tắt bằng chặn socket trong tiến trình, cộng với việc sandbox vốn không tới được Open-Meteo. |
| T1.4 | Kiểm nội dung bằng script riêng của DA đọc từ cache | 8 × 48.384 giờ; đủ 24 giờ mỗi ngày; BLH có và không trống; ngày tính theo giờ địa phương; u, v khớp công thức từ tốc độ và hướng; `rain_day` khớp quy tắc; bảng ngày 16.128 hàng; bảng gộp 14.056 × 54; khóa `(City, Date)` duy nhất; 40 cột chất lượng không khí trùng từng ô với bảng sạch; 0 ô thời tiết thiếu | Không dùng hàm của `weather_utils` để tính giá trị đối chiếu. |
| T1.5 | Sai lệch so với file đã commit | Xem quy tắc dung sai bên dưới | Báo số ô lệch, chênh lớn nhất, theo cột và thành phố. Không đòi đúng 852 ô. |
| T1.6 | Thử âm tính, mạng tắt | Mỗi ca: exit khác 0; thông báo lỗi nêu đúng vấn đề; không có file output "hoàn chỉnh" nào được ghi hoặc ghi đè | Các ca: thiếu 1 cache; thiếu cả 8; cache cụt 24 giờ cuối; thiếu cột BLH; đổi tên một cột bắt buộc; trùng giờ; file gzip hỏng; cache kết thúc sớm hơn khoảng yêu cầu. |
| T1.7 | Mock online và API thật | Mock: báo dưới nhãn "mock", không tính là đạt API. API thật: thử một lần, ghi exit code, ghi blocked nếu bị chặn | Không thử lại nhiều lần. |
| T1.8 | NB05 và NB06 đọc đúng output của NB04 trong cùng lần chạy | SHA-256 của file NB05/NB06 đọc bằng SHA-256 của file NB04 vừa ghi | Nếu downstream đọc CSV baseline đã commit thì phép thử toàn chuỗi **trượt**, bất kể metric. |

Quy tắc dung sai của T1.5 (theo RA-DEC-02 mục 5):

- `temp_mean`, `pressure_mean`, `wind_speed_mean`: một ô được lệch tới `0,01 + 1e-9` **chỉ khi** trung bình chưa làm tròn, do DA tự tính từ 24 giá trị giờ trong cache, cách biên làm tròn `x,xx5` không quá `1e-8` (tức `|100·m − (⌊100·m⌋ + 0,5)| ≤ 1e-6`).
- Mọi cột số khác: `1e-9`.
- Khóa, tên cột, kiểu, mặt nạ NaN, `rain_day`, `wind_dir_8`: so chính xác.
- Số đếm và ma trận nhầm lẫn: so chính xác, không áp dung sai.
- Ô lệch nằm ngoài các điều kiện trên: DA ghi trượt và gửi RA; không tự nới dung sai.

### 9.2. DA-02 / F01 — đặc trưng không dùng tương lai

Mọi phép thử tác động ở **mức file đầu vào**: DA tạo bản sao dự án với file raw (và đầu vào thời tiết mà bộ dựng đặc trưng đọc) đã bị cắt hoặc sửa, rồi chạy điểm vào của Dev không sửa. Tham số kiểu `as_of` của Dev, nếu có, chỉ là kiểm phụ: nó thử cái cờ, không thử dòng dữ liệu.

Phạm vi so: toàn bộ đặc trưng L1–L3, mặt nạ thiếu, và mọi cột nguồn gốc mà Dev xuất (ví dụ nguồn forward-fill). Đặc trưng `_next` của L4 dùng thời tiết t+1 theo thiết kế nên được loại khỏi yêu cầu này, nhưng phải bất biến trước dữ liệu sau t+1.

| Mã | Phép thử | Điều kiện đạt (khóa trước) | Ghi chú |
|---|---|---|---|
| T2.1 | Notebook thật sự gọi đường dự báo mới | (a) Đọc mã: ô dựng dữ liệu của NB06 gọi hàm mới. (b) Theo dõi I/O: file NB06 đọc là file của đường mới. (c) Bảng đặc trưng trong notebook trùng từng ô với bảng DA dựng qua điểm vào Dev công bố | Nếu NB06 còn đọc bảng sạch hồi cứu, DA nêu cột nào được dùng và dùng vào đâu. |
| T2.2 | Walk-forward cắt raw | Với **mỗi ngày t** từ 14/06/2017 đến 30/06/2020 (1.113 ngày): dựng lại từ dữ liệu cắt đến t, lấy các hàng `Date = t`, so với cùng hàng ở bản dựng đầy đủ. Đạt khi **0 ô khác**: mặt nạ NaN trùng, chênh số ≤ `1e-12` | Nếu một lần dựng lâu hơn 6 giây, dùng tập cắt thay thế đã định trước: 17 mốc cắt vòng 1; mọi ngày trong ±3 ngày quanh đầu và cuối mỗi chuỗi 0 và mỗi khoảng trống; hai ranh split; cộng mỗi 7 ngày một mốc. DA ghi rõ đã dùng tập nào. |
| T2.3 | Xáo trộn tương lai | Tại mỗi mốc t trong tập cố định, thay mọi giá trị sau t rồi dựng lại. Đạt khi **mọi hàng có `Date ≤ t`** giữ nguyên toàn bộ đặc trưng | Mốc: 17 mốc vòng 1; 29–30/06/2019; 28–29/02/2020; 20 ngày ngẫu nhiên seed 0. Kiểu thay: toàn NaN; toàn 0 (tạo chuỗi 0 vắt qua mốc); nhân 10; hoán vị trong từng thành phố (seed 0). Thời tiết sau t: cộng 10 đơn vị. |
| T2.4 | Ca biên tổng hợp | Trùng **bảng kỳ vọng do DA viết tay** từ RA-DEC-02 mục 4, không sinh từ mã Dev | Chuỗi 0 dài 1, 2, 3, 4 ngày ở: đầu chuỗi; giữa chuỗi; sát ô NaN; sát ngày lịch bị thiếu; chỗ chuyển thành phố; ranh 30/06–01/07/2019. Kiểm: ngày 1–2 giữ số 0; ngày 3 mask cả chuỗi trong prefix; số 0 đã mask không làm nguồn forward-fill; forward-fill tối đa 2 ngày; không backward-fill, không nội suy; không vắt qua thành phố; hàng ngày 1–2 không đổi khi thêm ngày 3–4. |
| T2.5 | Tham số tiền xử lý chỉ học trên train | Sửa giá trị đặc trưng ở test và holdout: tham số imputer, scaler, encoder và dự đoán trên train không đổi | Kèm đọc mã: không còn luật top-5 toàn chuỗi hay cửa sổ giữa 15 ngày trên đường dự báo. |
| T2.6 | Diff đặc trưng cũ so với mới | Không có điều kiện đạt; đây là bảng mô tả | Số ô và số hàng khác theo đặc trưng, thành phố, split, trên khóa chung; chênh lớn nhất. |
| T2.7 | Đường hồi cứu/EDA không đổi | Bảng sạch dựng lại từ mã Dev trùng file đã commit ở `1e-9`, ngoài phần Dev khai báo. `investigate` không lỗi với chuỗi không có khí (ca Jaipur, cắt 14/06/2017) | Đóng NEW-002 nếu đạt. |

Nhãn và điều kiện giữ mẫu được kiểm riêng (mục 3). Việc thêm `AQI(t+1)` làm một hàng đủ điều kiện đánh giá là hợp lệ; nó không được làm đổi đặc trưng của hàng t.

### 9.3. DA-04 — chạy lại 01→06 và metric

1. Chạy NB01→NB06 của Dev theo thứ tự trong một bản sao, môi trường bản sửa. Ghi exit code, số ô đã chạy, thời gian, I/O từng notebook.
2. Liệt kê mọi `assert` của NB06 trước và sau bản sửa. DA đọc từng assert bị đổi: không có assert chống rò rỉ nào bị xóa mà không có thay thế; không có assert luôn đúng; số đếm mới trong assert trùng số DA tự tính.
3. DA tính lại metric bằng script riêng theo mục 5–8, rồi so với số notebook in ra: số đếm so chính xác; MAE, RMSE, R² lệch không quá `1e-6`.
4. Báo đủ bốn thiết kế A–D và độ nhạy khối 7/28 ngày.

### 9.4. DA-05 — bảng cho BA

Trích V16, V18, V19 từ bằng chứng v1.1 vào `ba_evidence_extract.md`, có anchor và tên file nguồn. Đây là trích xuất số vòng 1 trên dữ liệu baseline, không phải kết quả kiểm vòng 2. S05 chỉ làm lại nếu nhóm dùng nó để khẳng định ngưỡng nội suy tối ưu.

## 10. Từ vựng trạng thái

| Ký hiệu | Nghĩa |
|---|---|
| ✅ đạt | Đã chạy; có lệnh, exit code, artifact; thỏa điều kiện khóa trước. |
| ⚠️ một phần | Đã chạy; thỏa một phần; phần còn lại được nêu rõ. |
| ❌ trượt | Đã chạy; không thỏa điều kiện khóa trước. |
| ⛔ blocked | Không chạy được vì lý do ngoài mã (mạng, môi trường); có log lỗi. |
| ❓ không đủ bằng chứng | Không có artifact để kết luận. |

DA không ghi F01 hay F02 là "đã đóng". DA chỉ ghi kết quả từng phép thử và đề nghị RA xét.

## 11. Những việc DA không làm

- Không sửa mã Dev trong bản sao rồi báo bản chính đạt. Nếu cần vá để chạy tiếp, DA ghi rõ bản vá, kết quả của bản chưa vá vẫn là kết quả chính thức.
- Không đổi split, baseline, tập đặc trưng, lưới alpha hay ngưỡng để metric đẹp hơn.
- Không điền nhãn AQI.
- Không sửa hồ sơ v1.1, dữ liệu raw, cache, bảng processed đã commit.
- Không merge hay đóng PR #1, #2, #3 hay PR của Dev.

## 12. Ghi nhận sai khác với giao thức

Mọi sai khác khi thực hiện được ghi vào `reproduction_log.md`: điều khoản bị lệch, lý do, làm gì thay thế, và việc đó xảy ra trước hay sau khi DA thấy kết quả liên quan.
