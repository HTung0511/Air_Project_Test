# Protocol nhãn, mẫu và đặc trưng của đường dự báo — Dev, vòng sửa 2 (F01)

Ngày 12/11/2026 · Vai trò: AI-4 Dev · Căn cứ: [gói giao việc](../AI_REMEDIATION_HANDOFF.md) mục DEV-02; [RA-DEC-02](https://github.com/HTung0511/Air_Project_Test/blob/fa34b692efa8d605e39efa13def732fb15e56379/Air-Project-main/reports/ra/round2/RA_DECISIONS_02.md) mục 2–4; [RA-DEC-03](https://github.com/HTung0511/Air_Project_Test/blob/8c1a2fb176cc3b26cd612d34a731f0b44e5095d0/Air-Project-main/reports/ra/round2/RA_DECISIONS_03.md) mục 3 và AM-03.

**Trạng thái.** Thiết kế đã được RA duyệt ở RA-DEC-02. Tài liệu này mô tả **bản cài đặt** của thiết kế đó trong `src/forecast_utils.py` và các con số Dev đo được ở commit mã `a9757af`. Bản cài đặt và các con số **đang chờ DA kiểm**; chưa được RA nghiệm thu. Commit, lệnh chạy lại và bằng chứng: [`dev_change_log.md`](dev_change_log.md).

Tài liệu chỉ nói về đường **dự báo** (NB06). Đường làm sạch hồi cứu cho EDA (NB01–NB03, NB05, `pipeline.py`, `model_utils.py`) giữ nguyên: nội suy khoảng thiếu ≤ 14 ngày, luật nghi lỗi, số 0 treo toàn chuỗi.

## 1. Vì sao tách hai đường

Bảng sạch `air_quality_8cities.csv` được dựng bằng cách nhìn **cả chuỗi**: nội suy tuyến tính dùng giá trị hai đầu khoảng thiếu, luật nghi lỗi chọn top-5 toàn chuỗi và so với cửa sổ 15 ngày lấy tâm, số 0 treo bị xoá cả chuỗi kể cả hai ngày đầu. Lấy đặc trưng của ngày *t* từ bảng đó là để dữ liệu sau *t* lọt vào (DA V05, V07). Phép thử `make_features(as_of=t)` cũ không bắt được vì nó cắt bảng **đã** làm sạch.

Đường dự báo đi thẳng từ `data/raw/city_day.csv`. Mỗi hàng của ngày *t* được dựng chỉ từ các dòng raw và thời tiết có ngày ≤ *t*.

## 2. Đơn vị mẫu, nhãn, điều kiện giữ mẫu, chia tập

| Mục | Quy định | Nơi cài đặt |
|---|---|---|
| Một mẫu | một cặp (thành phố, ngày *t*), khoá `(City, Date)` | `build_forecast_dataset` |
| Nhãn | `y = AQI_raw(t+1)`, với *t*+1 là **ngày lịch kế tiếp**; ghép theo ngày, không dịch theo dòng | `attach_target` |
| Xử lý nhãn | không nội suy, không điền, không cắt ở 500, không xoá theo luật nghi lỗi | `attach_target` (chỉ là phép ghép với raw) |
| Giữ mẫu khi | raw có AQI ở **cả** *t* và *t*+1; `Date ≥ 14/06/2017`; `Date_target ≤ 01/07/2020` | `build_forecast_dataset` |
| Chia tập | theo `Date_target`: train đến 30/06/2019; test 01/07/2019–29/02/2020; giai đoạn 03–07/2020 từ 01/03/2020 | `attach_target` |
| Thứ tự dòng | `Date_target` tăng dần; trong cùng ngày theo tên thành phố dạng chuỗi. Giống đường cũ; `TimeSeriesSplit` cắt theo thứ tự này | `build_forecast_dataset` |

Tên tập trong mã là `train`, `test`, `lockdown`. `lockdown` chính là tập mà RA và DA gọi là holdout (03–07/2020); tên được giữ như mã gốc để không đổi các ô khác của NB06.

Nhãn là "AQI như được ghi trong raw của snapshot hiện có". Nó không phải số đo đã kiểm định tại trạm. Dùng raw cũng không mô phỏng việc CPCB sửa số liệu về sau, vì không có bản phát hành theo ngày.

### Kiểm raw trước khi dùng (`prepare_raw`)

Vi phạm thì dừng bằng `ValueError` có số lượng, ngày và quy tắc. Không dòng nào bị bỏ, không số nào bị thay.

| Kiểm tra | Hành vi |
|---|---|
| Thiếu cột trong `City, Date, AQI, PM2.5, NO2, CO, SO2, O3` | dừng, nêu cột thiếu |
| Khoá `(City, Date)` trùng | dừng, nêu số dòng và ví dụ |
| `Date` có giờ khác 00:00 | dừng |
| AQI có mặt nhưng không hữu hạn hoặc ≤ 0; nồng độ có mặt nhưng không hữu hạn hoặc < 0; ô không đọc được thành số | dừng, liệt kê (thành phố, ngày, cột, giá trị, quy tắc) |
| AQI > 500 | **hợp lệ**, giữ nguyên |
| Thiếu ngày lịch trong một thành phố | **được hỗ trợ**: chèn dòng NaN cho ngày thiếu, để mọi phép lùi ngày, ghép nhãn và forward-fill đều tính theo ngày lịch. Số ngày chèn được báo ở `attrs["n_inserted_days"]` |
| Bảng thời tiết thiếu cột, trùng khoá, hoặc không phủ một dòng raw | dừng (`_features`); không tự điền thời tiết |
| Khoảng chung của raw khác 14/06/2017–01/07/2020 | `build_forecast_dataset()` dừng, trừ khi truyền `start`, `end` |

Về ngày lịch thiếu (RA-DEC-03 mục 3, DA-Q2): Dev chọn **contract 1, hỗ trợ khoảng trống**. Raw hiện có không thiếu ngày nào (0 ngày được chèn); hành vi này được kiểm bằng raw tổng hợp.

Kết quả trên raw hiện có (8 thành phố, 14.056 dòng): 0 khoá trùng, 0 ngày lịch thiếu, 0 ô vi phạm. AQI có 13.239 giá trị, từ 20 đến 891, trong đó 93 giá trị > 500.

### Tập mẫu đo được

| Tập | Cặp trong khoảng | Thiếu AQI(*t*) | Có AQI(*t*), thiếu AQI(*t*+1) | Giữ | Ngày nặng (y ≥ 201) | Nhãn > 500 |
|---|---|---|---|---|---|---|
| train | 5.968 | 164 | 58 | 5.746 | 1.436 | 31 |
| test | 1.952 | 3 | 2 | 1.947 | 389 | 10 |
| 03–07/2020 | 984 | 7 | 2 | 975 | 18 | 0 |
| Cộng | 8.904 | 174 | 62 | 8.668 | 1.843 | 41 |

Chỉ đánh giá được những ngày có nhãn. Đây là giới hạn về độ phủ: 236 trên 8.904 cặp không vào mẫu.

**So với đường hồi cứu (8.663 mẫu = 5.741 / 1.947 / 975): thêm 5 mẫu, đều ở train; không mất mẫu nào; khoá và nhãn của test và 03–07/2020 giữ nguyên.** Số 5 là kết quả của phép trừ hai tập khoá, không phải giả định.

| Thành phố | Ngày *t* | AQI raw(*t*) → AQI raw(*t*+1) | Bảng sạch hồi cứu đã xoá |
|---|---|---|---|
| Bengaluru | 08/07/2017 | 108 → 112 | AQI(*t*) |
| Gurugram | 08/07/2017 | 372 → 529 | AQI(*t*+1), tức nhãn |
| Gurugram | 29/07/2017 | 248 → 482 | AQI(*t*+1), tức nhãn |
| Jaipur | 05/02/2018 | 153 → 305 | AQI(*t*+1), tức nhãn |
| Jaipur | 06/02/2018 | 305 → 291 | AQI(*t*) |

Cả 5 ô AQI bị xoá đều mang cờ `suspect_sensor_error` của nhánh hồi cứu. Giữ chúng không có nghĩa là khẳng định chúng đúng.

## 3. Đặc trưng as-of *t*

Mọi phép lùi ngày là theo ngày lịch, trong từng thành phố. Không đặc trưng nào của mức 1–3 đọc dòng có ngày > *t*.

| Mức | Cột | Công thức | Dữ liệu dùng |
|---|---|---|---|
| nền | thành phố | one-hot trong `Pipeline`, Delhi là mức tham chiếu | — |
| nền | `doy_sin`, `doy_cos` | sin, cos của ngày trong năm của **ngày được dự đoán** | lịch, biết trước |
| 1 | `aqi_0`, `aqi_1`, `aqi_2` | log AQI raw của *t*, *t*−1, *t*−2 | raw ≤ *t* |
| 1 | `aqi_wk` | log của trung bình AQI raw các ngày *t*−7…*t*−1; cần ít nhất 3 ngày có số | raw ≤ *t*−1 |
| 2 | `pm25_0`, `no2_0`, `co_0`, `so2_0`, `o3_0` | `log1p` của giá trị as-of (mục 4) | raw ≤ *t* |
| 3 | `temp_mean`, `humidity_mean`, `wind_speed_mean`, `wind_u`, `wind_v`, `blh_mean` | giá trị của ngày *t* | thời tiết ngày *t* |
| 3 | `pressure_dev` | áp suất ngày *t* trừ trung bình áp suất *t*−30…*t*−1 (cần ít nhất 10 ngày) | thời tiết ≤ *t* |
| 3 | `d_pressure` | áp suất ngày *t* trừ ngày *t*−1 | thời tiết ≤ *t* |
| 3 | `precip_log` | `log1p` của tổng mưa ngày *t* | thời tiết ngày *t* |

AQI **không** được forward-fill và không áp quy tắc số 0 treo. AQI các ngày trước bị thiếu thì đặc trưng là NaN: trong mẫu có 63 ô `aqi_1`, 93 ô `aqi_2` và 23 ô `aqi_wk` như vậy.

Kịch bản "cận trên" (mức 4) thêm 9 cột `*_next` là thời tiết của ngày *t*+1. Các cột này được gắn ở `attach_target`, cùng chỗ với nhãn, tách khỏi bảng đặc trưng. Mức 4 không phải mô hình dùng được; nó chỉ cho biết trần.

Công thức của AQI, thời tiết và lịch giống hệt `model_utils.make_features`. Khác biệt nằm ở **nguồn** (raw thay cho bảng sạch) và ở cách xử lý chất ô nhiễm.

### Điểm vào

| Việc cần làm | Gọi | Ghi chú |
|---|---|---|
| Bảng đặc trưng, **không nhãn, chưa lọc mẫu**, mọi dòng (thành phố, ngày) của raw | `forecast_utils.make_forecast_features(raw=None, weather=None, as_of=None)` | Không truyền gì thì đọc `data/raw/city_day.csv` và file thời tiết của thư mục dự án đang chạy. Nhận được DataFrame. Dùng được trên raw đã bị cắt hoặc sửa. `as_of` cắt raw và thời tiết trước khi tính |
| Gắn nhãn, split, thời tiết ngày mai | `forecast_utils.attach_target(feat, raw)` | Tương lai chỉ đi vào đây |
| Bảng mẫu của NB06 | `forecast_utils.build_forecast_dataset()` | Từ chối raw có khoảng chung khác phạm vi đã chốt, trừ khi truyền `start`, `end` |
| Bảng giữ mẫu | `forecast_utils.retention(ds)` | |
| Che và điền thực tế | `forecast_utils.masking_summary(ds)`, `masked_cells(ds, raw)` | |
| So với đường hồi cứu | `cohort_diff`, `feature_diff`, `compare_paths` | Chỉ để đối chiếu |
| Phép thử cắt và làm nhiễu | `asof_check(cuts)`, `perturb_after(raw, weather, cut)` | |

**Khi thử với file raw đã cắt ở ngày *t*:** dùng `make_forecast_features()`. Hàm này không lọc theo nhãn, nên hàng của ngày *t* vẫn có mặt dù chưa có AQI(*t*+1). `build_forecast_dataset()` và NB06 sẽ dừng với lỗi "khoảng chung của raw … khác phạm vi đã chốt", vì cắt raw làm khoảng chung ngắn lại; đó là từ chối có chủ đích, không phải lỗi của đặc trưng.

File thời tiết được đọc là `data/processed/weather_daily_8cities.csv`, hoặc file mà biến môi trường `AIR_WEATHER_DAILY` chỉ tới (xem `src/data_paths.py`).

Mỗi đặc trưng chất ô nhiễm có hai cột chẩn đoán, không đưa vào mô hình: `<tên>_lag` (0, 1, 2 = số ngày lùi của nguồn; −1 = không có nguồn) và `<tên>_flat` (True nếu số 0 của chính ngày *t* bị che).

## 4. Số 0 treo và forward-fill, theo snapshot as-of *t*

Áp cho đúng 5 cột `PM2.5, NO2, CO, SO2, O3` (`FLATLINE_COLS`). Không áp cho AQI và thời tiết. Ngưỡng 3 ngày (`FLATLINE_MIN_RUN`) và giới hạn điền 2 ngày (`FFILL_LIMIT`) lấy nguyên từ nhánh hồi cứu.

Với mỗi ngày *t*, hàm `asof_pollutant` xét lần lượt ngày *t*, *t*−1, *t*−2 và lấy giá trị hợp lệ đầu tiên. Giá trị của ngày *s* ≤ *t* hợp lệ khi nó có mặt và **không** phải số 0 thuộc một chuỗi 0 mà, tính đến hết *t*, đã dài từ 3 ngày.

1. Chuỗi 0 là các ngày lịch liên tiếp có giá trị quan sát đúng bằng 0. Chuỗi không nối qua ô NaN, qua ngày lịch thiếu, hay qua thành phố khác.
2. Ngày thứ nhất và thứ hai của một chuỗi 0 **giữ số 0**. Lúc đó chưa thể biết chuỗi sẽ kéo dài.
3. Từ ngày thứ ba, khi dựng hàng của ngày đó, cả chuỗi đã quan sát trong prefix ≤ *t* bị che. Số 0 đã che không làm nguồn điền.
4. **Hàng đã dựng cho ngày *t*−1, *t*−2 không bị sửa ngược.** Bảng mẫu gồm mỗi hàng đúng với prefix của chính nó; không lấy snapshot cuối rồi cập nhật lại lịch sử.
5. Một số 0 chưa bị che vẫn là nguồn điền hợp lệ cho ô NaN ngay sau nó, trong giới hạn 2 ngày.
6. Không nội suy, không backward-fill. Phần còn thiếu để NaN, do imputer chỉ fit trên train điền, kèm cột báo thiếu.

Ví dụ viết tay (A, B là số dương; kết quả là giá trị trước `log1p`):

| Raw theo ngày | Giá trị as-of từng ngày | Điều được thể hiện |
|---|---|---|
| A, 0, 0, 0, B | A, 0, 0, NaN, B | ngày 1–2 giữ 0; ngày 3 che cả chuỗi nên không còn nguồn |
| A, 0, 0, 0, 0, B | A, 0, 0, NaN, NaN, B | ngày 3 và 4 đều bị che |
| A, 0, 0, NaN, 0, B | A, 0, 0, 0, 0, B | chuỗi không nối qua NaN; ô NaN được điền từ số 0 hợp lệ |
| A, 0, 0, 0, NaN, NaN, B | A, 0, 0, NaN, NaN, NaN, B | số 0 đã che không làm nguồn điền |
| A, NaN, NaN, NaN, B | A, A, A, NaN, B | điền tối đa 2 ngày; không lấy B, không nội suy |
| 0, 0, 0, 0, 1,11 (đầu chuỗi) | 0, 0, NaN, NaN, 1,11 | không cần giá trị nào đứng trước |

Tám ví dụ loại này là test (`tests/test_forecast_flatline.py::test_handwritten_snapshot_examples_from_the_ra_decisions`). Ngoài ra `asof_pollutant` được so với hai trọng tài viết độc lập: một hàm áp chính `utils.flag_flatline_zeros` của nhánh làm sạch lên từng prefix, và một vòng lặp thuần Python.

### Che và điền thực tế trên dữ liệu hiện có

Trong raw của 8 thành phố chỉ CO có số 0: 396 ô từ 14/06/2017.

| Phạm vi | Ô CO bằng 0 | Bị che (ngày thứ 3 trở đi) | Giữ số 0 (ngày 1–2) |
|---|---|---|---|
| Mọi (thành phố, ngày) từ 14/06/2017 | 396 | 295 | 101 |
| Các hàng của tập mẫu | 331 | 252 | 79 |

Cả 252 ô bị che thuộc train (Amritsar 116, Delhi 65, Jaipur 54, Gurugram 6, Hyderabad 6, Chennai 5). Không ô nào của PM2.5, NO2, SO2, O3 bị che. Từng ô nằm trong `nb06_masked_cells.csv` của mỗi lần chạy NB06.

Nguồn giá trị của từng đặc trưng (số mẫu):

| Đặc trưng | Tập | Giá trị ngày *t* | Điền từ *t*−1 | Điền từ *t*−2 | Không có nguồn |
|---|---|---|---|---|---|
| `pm25_0` | train | 5.656 | 6 | 5 | 79 |
| `no2_0` | train | 5.736 | 5 | 1 | 4 |
| `co_0` | train | 5.461 | 6 | 4 | 275 |
| `so2_0` | train | 5.446 | 31 | 18 | 251 |
| `so2_0` | test | 1.946 | 1 | 0 | 0 |
| `o3_0` | train | 5.585 | 11 | 6 | 144 |
| `o3_0` | test | 1.929 | 3 | 3 | 12 |
| `o3_0` | 03–07/2020 | 972 | 1 | 1 | 1 |

Các tổ hợp không có trong bảng dùng giá trị của ngày *t* cho mọi mẫu. 81 mẫu train dùng CO = 0: 79 là số 0 của chính ngày *t*, 2 là ngày thiếu CO được điền từ một số 0 đơn lẻ trước đó (Amritsar 20–21/06/2018).

## 5. Không dùng luật nghi lỗi hồi cứu

Đường dự báo không gọi `pipeline.investigate`, không đọc `reports/suspect_points_8cities.csv` và không đọc cờ `suspect_sensor_error`. Giá trị raw hợp lệ được giữ nguyên, kể cả các điểm mà nhánh hồi cứu coi là nghi lỗi.

Trong khoảng chung, nhánh hồi cứu đã đặt NaN 10 ô: 4 ô AQI (Bengaluru 08/07/2017; Gurugram 09/07 và 30/07/2017; Jaipur 06/02/2018) và 6 ô PM2.5 (Bengaluru 07/07 và 08/07/2017; Gurugram 09/07, 30/07 và 29/08/2017; Jaipur 06/02/2018). Đường dự báo giữ nguyên giá trị raw ở 9 ô. Ô thứ mười, PM2.5 của Bengaluru ngày 07/07/2017, không có số đo trong raw nên vẫn là NaN. Bảng từng ô: `dev_evidence/pytest/suspect_cells_in_window_kept_raw.csv`.

## 6. Tiền xử lý chỉ học trên train

Imputer (trung vị, kèm cột báo thiếu), scaler, one-hot thành phố và mô hình nằm trong một `Pipeline` (`model_utils.make_pipe`, không đổi). Pipeline được fit trên train, hoặc trên phần train của từng lần chia khi chọn tham số.

| Lựa chọn | Cách chọn | Dữ liệu dùng |
|---|---|---|
| Alpha của Ridge | lưới 0,1; 1; 10; 30; 100; 300; `TimeSeriesSplit` 4 lần, bỏ 16 dòng giữa hai phần; MAE trung bình nhỏ nhất, hoà thì lấy alpha nhỏ hơn | train |
| Ngưỡng cảnh báo | F2 lớn nhất trên dự đoán ngoài mẫu của chính các lần chia đó; lưới 80…300 bước 1; hoà thì lấy ngưỡng nhỏ hơn | train |
| Test và 03–07/2020 | chỉ để báo cáo | không dùng để chọn gì |

Chia tập, ba mức đặc trưng, ba baseline và cách chọn alpha, ngưỡng **không đổi** so với NB06 gốc. Alpha chọn được vẫn là 10 / 0,1 / 30 cho mức 1 / 2 / 3. Ngưỡng F2 đổi từ 169 / 165 / 166 thành 170 / 166 / 167; ngưỡng của "ngày mai = hôm nay" vẫn là 160.

## 7. Bằng chứng không dùng tương lai

Mọi phép thử đi từ **raw**, không từ bảng đã làm sạch.

| Phép thử | Phạm vi | Kết quả Dev đo |
|---|---|---|
| Cắt raw và thời tiết ở *t*, dựng lại, so hàng của ngày *t* | mọi ngày của khoảng chung: 1.114 ngày cắt, 8.912 hàng, 31 cột mỗi hàng, 276.272 ô | 0 ô khác |
| Cắt ở *t* và làm nhiễu mọi giá trị sau *t* (nhân hệ số, đặt 0, đặt NaN; thời tiết đổi) | 47 ngày cắt, gồm các ngày của DA V05/V07 và hai bên các ranh chia tập | 0 ô khác |
| Cùng phép thử, chạy trong NB06 | 23 ngày cắt, 8 thành phố | 0 ô khác |
| Luật số 0 treo hồi cứu qua cùng phép thử | đối chứng | **trượt**, đúng như mong đợi |
| Đổi AQI(*t*+1) | nhãn và điều kiện giữ mẫu đổi; đặc trưng của *t* không đổi | đạt |
| Sửa đặc trưng của test và 03–07/2020 | tham số imputer, scaler đã fit trên train không đổi | đạt |

So là so chính xác, NaN bằng NaN, không dung sai. 31 cột gồm AQI, 20 đặc trưng mức 3 và 10 cột chẩn đoán. Nhãn và điều kiện giữ mẫu được kiểm riêng: việc AQI(*t*+1) xuất hiện làm một hàng đủ điều kiện là đúng thiết kế, không phải rò rỉ.

Phép thử cắt từng ngày (1.114 lần dựng lại) chạy trong khoảng 40 giây trên máy đã kiểm, nên không cần dùng tập mốc thay thế.

**Đầu vào bị từ chối.** Khi làm nhiễu tương lai, các giá trị sau làm `prepare_raw` hoặc `_features` dừng theo đúng contract ở mục 2, và đó không phải bằng chứng về rò rỉ: AQI bằng 0 hoặc âm; nồng độ âm; thời tiết NaN hoặc thiếu dòng cho một ngày có trong raw. Các kiểu sau là đầu vào hợp lệ: AQI và nồng độ thành NaN; nồng độ thành 0; nhân với số dương; hoán vị; thời tiết cộng hằng số.

## 8. Ba phép so bắt buộc (RA-DEC-02 mục 2)

Ba biến thể đều chạy qua cùng một hàm (`forecast_utils.run_protocol`): alpha và ngưỡng chọn trên train của chính biến thể đó, không lựa chọn nào nhìn test.

| Tên ở NB06 | Mã | Tập train | RA-DEC-02 | Giao thức DA, mục 8 |
|---|---|---|---|---|
| A | cũ (bảng sạch hồi cứu) | 5.741, tập mẫu hồi cứu | vế "mã cũ" của phép so 2 | vế "mã cũ" của B |
| B | mới (từ raw) | 5.741, bỏ các mẫu chỉ có ở raw theo hiệu hai tập khoá | phép so 2 (B − A) và 3 (C − B) | vế "mã mới" của B; thiết kế C |
| C | mới (từ raw) | 5.746, tập mẫu raw | phép so 1; là kết quả chính của NB06 | thiết kế A |

Test (1.947) và 03–07/2020 (975) có **cùng khoá và cùng nhãn** ở cả ba biến thể, nên mọi hiệu dưới đây là so cặp trên cùng outcome. Không có khoá chung nào khác nhãn, và không có khoá test hay 03–07/2020 nào chỉ thuộc một bên (thiết kế D của DA rỗng).

| | A | B | C |
|---|---|---|---|
| Alpha mức 1 / 2 / 3 | 10 / 0,1 / 30 | 10 / 0,1 / 30 | 10 / 0,1 / 30 |
| Ngưỡng F2 mức 1 / 2 / 3 | 169 / 165 / 166 | 170 / 165 / 166 | 170 / 166 / 167 |
| MAE test mức 1 | 22,9373 | 22,9354 | 22,9299 |
| MAE test mức 2 | 20,9189 | 20,9207 | 20,9216 |
| MAE test mức 3 | 19,5190 | 19,5192 | 19,5285 |
| MAE 03–07/2020 mức 3 | 13,7834 | 13,7879 | 13,7737 |
| Mức 3 ở ngưỡng 201: TP / FP / FN | 346 / 40 / 43 | 346 / 40 / 43 | 346 / 40 / 43 |
| Mức 3 ở ngưỡng F2: TP / FP / FN | 377 / 113 / 12 | 378 / 113 / 11 | 377 / 107 / 12 |

"Ngày mai = hôm nay" giống nhau ở cả ba: MAE test 23,4664; MAE 03–07/2020 14,8031; ngưỡng F2 160.

Hiệu MAE mức 3, so cặp, khoảng 95% bootstrap theo khối 14 ngày:

| Phép so | Ý nghĩa | Test | 03–07/2020 |
|---|---|---|---|
| B − A | đổi cách dựng đặc trưng, giữ nguyên mẫu và nhãn | +0,0002 (−0,0069; +0,0071) | +0,0045 (−0,0031; +0,0128) |
| C − B | thêm 5 mẫu train | +0,0093 (−0,0033; +0,0213) | −0,0142 (−0,0317; +0,0013) |
| C − A | tổng cộng | +0,0095 (−0,0052; +0,0237) | −0,0097 (−0,0277; +0,0041) |

Cả 18 khoảng (ba phép so, hai tập, ba mức) đều chứa 0. Trên các khoá chung, đặc trưng của hai đường khác nhau ở 63 ô, tất cả thuộc train: `co_0` 35, `aqi_wk` 22, `aqi_2` 4, `aqi_1` 2. Đặc trưng của test và 03–07/2020 trùng nhau.

Đọc kết quả: trên dữ liệu này, bỏ phần rò rỉ không làm đổi sai số ở mức đo được. Điều đó **không** biến đường cũ thành hợp lệ; nó chỉ nói rằng các con số đã báo trước đây không được lợi đáng kể từ rò rỉ.

## 9. Giới hạn

- Raw là một snapshot tải một lần. Đường dự báo đúng theo nghĩa "không đọc dòng có ngày sau *t*", không theo nghĩa "chỉ dùng số liệu đã được công bố vào ngày *t*".
- Giữ các điểm nghi lỗi chưa được xác minh là một lựa chọn minh bạch, không phải lời khẳng định các điểm đó đúng. Chưa có phân tích độ nhạy riêng cho các điểm này ngoài phép so B và C.
- Ngày thiếu AQI không vào mẫu. Nếu AQI hay thiếu vào ngày nặng thì sai số trông tốt hơn thực tế. Chưa kiểm được.
- Thời tiết là tái phân tích ERA5 đến hết ngày *t*, không phải dự báo có vào sáng ngày *t*.
- Test và 03–07/2020 đã được mở từ trước ở NB06 gốc và ở vòng kiểm 1. Các con số trên không phải xác nhận ngoài mẫu mới.

## 10. Kiểm lại

```bash
cd Air-Project-main
python -m pytest tests/test_forecast_flatline.py tests/test_forecast_leakage.py tests/test_forecast_cohort.py -q
python tools/run_chain.py --work <thư mục ngoài dự án> --name nb06 --notebooks 06 --weather baseline
```

Lệnh thứ hai chạy NB06 trong một bản sao và ghi `outputs/nb06/` của bản sao đó: khoá mẫu, bảng giữ mẫu, khoá thêm bớt, ô bị che, dự đoán theo khoá, các con số chưa làm tròn và bảng so A/B/C. Bản Dev đã chạy: `dev_evidence/chains/nb06_only/nb06_outputs/`.
