# Bảng trích cho BA: V16, V18, V19 (DA-05)

Phiên bản 1.0 · 11/11/2026 · Người lập: AI-3 DA · Người nhận: AI-1 BA (qua RA).

Đây là **trích xuất số vòng 1** từ bằng chứng DA v1.1 (commit `0dfc715`), tính trên dữ liệu baseline. Nó không phải kết quả kiểm bản sửa vòng 2. Ba phần dưới đây thuộc EDA và tương quan (NB03, NB05); bản sửa F01/F02 của Dev nhắm vào đường dự báo, nên các số này chỉ cần tính lại nếu Dev đổi bảng sạch hồi cứu hoặc bảng thời tiết ngày. DA sẽ kiểm điều đó ở T1.5 và T2.7 của [giao thức](da_verification_protocol.md).

Script: [`r2_ba_extract.py`](evidence/scripts/r2_ba_extract.py). Script đọc các file CSV v1.1, tính lại mọi con số dẫn xuất (trung vị của 5 tỉ số, tỉ số của hai trung vị gộp, các số đếm 32/33/24, bảng chéo, số đếm kết luận) và dừng nếu lệch file nguồn. Lệnh: `python r2_ba_extract.py ../../../evidence <thư mục out>`, exit 0.

## Tóm tắt

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| Tỉ số PM2.5 "2,8 lần" | 2,82 [2,42; 3,17] là **trung vị của 5 tỉ số**, mỗi tỉ số tính riêng một thành phố | [BA01](#BA01); [V16](../verification_results.md#V16) | 5 thành phố có từ 100 ngày nặng trở lên: Delhi, Gurugram, Lucknow, Jaipur, Amritsar. Khoảng của 5 tỉ số: 2,06–3,13. |
| "137 so với 42 µg/m³" | 137,1 và 42,0 là hai trung vị **gộp cả 8 thành phố**; tỉ số của chúng là **3,26** | [BA01](#BA01); [V16](../verification_results.md#V16) | Hai phép tính khác tập và khác cách gộp. Không ghép "2,8 lần" với "137 so với 42" trong cùng một câu. |
| "32/48" | 32/48 hệ số có **q (Benjamini–Hochberg) < 0,05** | [BA02](#BA02); [V18](../verification_results.md#V18) | Đây là tiêu chí theo q, không phải theo khoảng tin cậy. |
| Khoảng tin cậy 95% loại trừ 0 | **33/48**, khoảng **chưa hiệu chỉnh** | [BA02](#BA02); [V18](../verification_results.md#V18) | Ô duy nhất khác nhau giữa hai tiêu chí: Bengaluru – mưa, rho −0,087 [−0,170; −0,003], p 0,039, q 0,057. |
| Họ phép thử của Bonferroni | **15** phép (3 giả thuyết × 5 thành phố), mức mỗi phép 0,05/15, khoảng tin cậy 99,67% | [BA03](#BA03); [V19](../verification_results.md#V19) | Notebook NB05 dùng 15. Checklist và phụ lục ghi "3 phép, α = 0,05/3". |
| Kết quả 15 phép | 3 ủng hộ, 1 ngược chiều, 11 chưa đủ bằng chứng | [BA03](#BA03); [V19](../verification_results.md#V19) | Với họ 3 mỗi thành phố (khoảng 98,33%), cả 15 kết luận giữ nguyên. |

<a id="BA01"></a>
## BA01 — Tỉ số PM2.5 ngày nặng so với ngày còn lại (V16)

Cửa sổ 14/06/2017–01/07/2020. Ngày nặng là ngày có AQI ≥ 201. Tỉ số = trung vị PM2.5 của ngày nặng chia trung vị PM2.5 của ngày còn lại. Khoảng tin cậy: bootstrap khối 14 ngày.

| Thành phố | Ngày có AQI | Ngày nặng | PM2.5: n nặng / n còn lại | Trung vị ngày nặng (µg/m³) | Trung vị ngày còn lại (µg/m³) | Tỉ số | CI 95% của tỉ số | Có trong "5 thành phố" |
|---|---|---|---|---|---|---|---|---|
| Delhi | 1.105 | 564 | 564/541 | 140,96 | 47,17 | 2,99 | [2,49; 3,63] | có |
| Gurugram | 1.070 | 495 | 495/575 | 139,72 | 56,54 | 2,47 | [2,14; 2,93] | có |
| Lucknow | 1.111 | 516 | 516/595 | 155,12 | 49,51 | 3,13 | [2,48; 3,60] | có |
| Jaipur | 1.093 | 121 | 121/972 | 98,10 | 47,55 | 2,06 | [1,88; 2,29] | có |
| Bengaluru | 1.108 | 2 | 2/1094 | 78,97 | 29,41 | 2,68 | — | không (dưới 100 ngày nặng) |
| Amritsar | 1.029 | 117 | 115/840 | 118,60 | 42,00 | 2,82 | [2,48; 3,28] | có |
| Chennai | 1.110 | 34 | 34/1076 | 103,37 | 39,76 | 2,60 | — | không (dưới 100 ngày nặng) |
| Hyderabad | 1.108 | 1 | 1/1107 | 78,69 | 37,72 | 2,09 | — | không (dưới 100 ngày nặng) |

Hai con số tổng hợp, tính từ bảng trên và từ file tóm tắt:

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| Trung vị của 5 tỉ số theo thành phố | 2,82 [2,42; 3,17] | [V16_eda_pollutant_summary.csv](../evidence/V16_eda_pollutant_summary.csv), cột `trung_vi_cua_ratio_cac_TP_du_ngay_nang` | Giá trị giữa của 2,06; 2,47; 2,82; 2,99; 3,13 (là tỉ số của Amritsar). |
| Tỉ số của hai trung vị gộp 8 thành phố | 137,145 / 42,050 = 3,26 | cùng file, cột `median_gop_nang`, `median_gop_conlai`, `ratio_cua_2_median_gop` | 8.648 cặp (thành phố, ngày) có cả AQI và PM2.5. Mẫu số gộp (42,0) thấp hơn trung vị "ngày còn lại" của 4 trong 5 thành phố ở bảng trên, vì nhóm này gộp thêm ba thành phố ít ô nhiễm (29,4–39,8 µg/m³). |
| Các chất khác, cùng hai cách tính | NO2 1,66 và 1,91; CO 1,62 và 1,67; SO2 1,09 và 1,49; O3 1,06 và 1,14 | cùng file | Số trước là trung vị 5 tỉ số; số sau là tỉ số gộp. Hai cách luôn cho số khác nhau. |

Giới hạn cần giữ khi viết: tỉ số so nồng độ giữa hai nhóm ngày; nó không đo phần đóng góp của PM2.5 vào AQI. Ba thành phố có dưới 100 ngày nặng (Bengaluru 2, Hyderabad 1, Chennai 34) không có khoảng tin cậy và không nằm trong trung vị 2,82.

Bảng gọn: [R2_BA01_pm25_ratio_by_city.csv](evidence/R2_BA01_pm25_ratio_by_city.csv). Nguồn: [V16_eda_pollutant_by_city.csv](../evidence/V16_eda_pollutant_by_city.csv).

<a id="BA02"></a>
## BA02 — 48 hệ số tương quan thời tiết–AQI: q và khoảng tin cậy (V18)

Mỗi ô: Spearman rho sau khi bỏ chu kỳ mùa theo tháng, khoảng tin cậy 95% **chưa hiệu chỉnh** (bootstrap khối 14 ngày, B = 4.000), và q theo Benjamini–Hochberg trên 48 phép. Dấu ✗ đánh dấu ô có q ≥ 0,05. "q 0,001" là giá trị nhỏ nhất xuất hiện trong bảng: 24 ô có p chạm sàn 0,0005 của B = 4.000.

| Thành phố | nhiệt độ | độ ẩm | tốc độ gió | lớp biên | mưa | áp suất |
|---|---|---|---|---|---|---|
| Delhi | 0,23 [0,12; 0,34]; q 0,001 | −0,33 [−0,43; −0,22]; q 0,001 | −0,18 [−0,26; −0,10]; q 0,001 | 0,08 [−0,03; 0,19]; q 0,193 ✗ | −0,14 [−0,22; −0,06]; q 0,001 | −0,16 [−0,27; −0,05]; q 0,009 |
| Gurugram | 0,21 [0,11; 0,30]; q 0,001 | −0,28 [−0,37; −0,18]; q 0,001 | −0,11 [−0,19; −0,03]; q 0,021 | 0,09 [−0,01; 0,19]; q 0,105 ✗ | −0,16 [−0,23; −0,08]; q 0,001 | −0,10 [−0,20; 0,01]; q 0,105 ✗ |
| Lucknow | 0,23 [0,11; 0,34]; q 0,001 | −0,33 [−0,42; −0,22]; q 0,001 | −0,07 [−0,16; 0,01]; q 0,113 ✗ | 0,13 [0,03; 0,23]; q 0,016 | −0,17 [−0,24; −0,11]; q 0,001 | −0,20 [−0,30; −0,08]; q 0,006 |
| Jaipur | 0,32 [0,23; 0,41]; q 0,001 | −0,48 [−0,56; −0,40]; q 0,001 | 0,07 [−0,03; 0,16]; q 0,165 ✗ | 0,30 [0,21; 0,39]; q 0,001 | −0,27 [−0,33; −0,22]; q 0,001 | −0,16 [−0,27; −0,05]; q 0,006 |
| Bengaluru | 0,19 [0,08; 0,29]; q 0,003 | −0,31 [−0,41; −0,21]; q 0,001 | −0,26 [−0,36; −0,16]; q 0,001 | −0,05 [−0,17; 0,07]; q 0,421 ✗ | −0,09 [−0,17; −0,003]; q 0,057 ✗ | 0,09 [−0,01; 0,19]; q 0,105 ✗ |
| Amritsar | 0,23 [0,15; 0,31]; q 0,001 | −0,26 [−0,35; −0,15]; q 0,001 | −0,09 [−0,17; −0,02]; q 0,022 | 0,09 [−0,01; 0,18]; q 0,111 ✗ | −0,19 [−0,25; −0,12]; q 0,001 | −0,19 [−0,28; −0,11]; q 0,001 |
| Chennai | −0,10 [−0,22; 0,01]; q 0,105 ✗ | −0,14 [−0,24; −0,04]; q 0,015 | −0,07 [−0,16; 0,01]; q 0,113 ✗ | −0,04 [−0,14; 0,06]; q 0,453 ✗ | −0,19 [−0,29; −0,09]; q 0,001 | −0,05 [−0,14; 0,04]; q 0,289 ✗ |
| Hyderabad | 0,10 [−0,03; 0,22]; q 0,133 ✗ | −0,37 [−0,47; −0,27]; q 0,001 | −0,26 [−0,35; −0,16]; q 0,001 | −0,01 [−0,13; 0,11]; q 0,849 ✗ | −0,17 [−0,25; −0,09]; q 0,001 | −0,01 [−0,11; 0,09]; q 0,852 ✗ |

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| q < 0,05 | 32/48 | cột `q_BH<0.05` | Theo biến (trên 8 thành phố): độ ẩm 8, mưa 7, nhiệt độ 6, gió 5, áp suất 4, lớp biên 2. |
| Khoảng 95% chưa hiệu chỉnh loại trừ 0 | 33/48 | cột `CI95_loai_0` | 32 ô chung với hàng trên, cộng Bengaluru – mưa. |
| q < 0,05 nhưng khoảng 95% chứa 0 | 0/48 | bảng chéo trong log script | |
| Bonferroni trên 48 phép | 24/48 | cột `p_Bonferroni48<0.05` | Để tham khảo; notebook không dùng. |
| Đổi dấu khi bỏ mùa | 18/48 | cột `doi_dau_khi_bo_mua` | Ví dụ Delhi – nhiệt độ: thô −0,52, sau khi bỏ mùa 0,23. |
| p bootstrap chạm sàn 0,0005 | 24/48 | cột `p_bootstrap` | Giới hạn độ phân giải của B = 4.000. |

Cách ghi đúng: "32/48 hệ số có q < 0,05 sau hiệu chỉnh Benjamini–Hochberg" hoặc "33/48 hệ số có khoảng tin cậy 95% chưa hiệu chỉnh loại trừ 0". Câu "32/48 có khoảng tin cậy loại trừ 0 sau hiệu chỉnh FDR" trộn hai tiêu chí; vòng 1 không tính khoảng tin cậy đã hiệu chỉnh FDR.

Bảng gọn 48 dòng: [R2_BA02_corr_48_q_ci.csv](evidence/R2_BA02_corr_48_q_ci.csv). Nguồn, có thêm các biến thể khối 7/28 ngày, bỏ mùa theo tuần, bỏ giai đoạn COVID: [V18_corr_48_coefficients.csv](../evidence/V18_corr_48_coefficients.csv), [V18_corr_sensitivity_summary.csv](../evidence/V18_corr_sensitivity_summary.csv).

<a id="BA03"></a>
## BA03 — 15 phép so sánh và họ phép thử (V19)

Hiệu ứng = trung vị AQI đã bỏ mùa của nhóm ngày bất lợi trừ nhóm thuận lợi, đơn vị điểm AQI. Khoảng tin cậy: bootstrap khối 14 ngày, B = 2.000, seed 0. Kết luận "ủng hộ" khi cả khoảng nằm trên 0; "ngược chiều dự đoán" khi cả khoảng nằm dưới 0.

| Thành phố | Giả thuyết | n bất lợi / thuận lợi | Hiệu ứng (điểm AQI) | CI 99,67% (họ 15) | Kết luận (họ 15) | CI 98,33% (họ 3) | Kết luận (họ 3) | CI 95% không hiệu chỉnh | Kết luận nếu không hiệu chỉnh |
|---|---|---|---|---|---|---|---|---|---|
| Delhi | H1 gió yếu | 371 / 367 | 30,0 | [9,6; 50,2] | ủng hộ | [13,5; 44,5] | ủng hộ | [16,7; 41,5] | ủng hộ |
| Delhi | H2 lớp biên thấp | 371 / 367 | −5,5 | [−35,5; 17,2] | chưa đủ bằng chứng | [−28,0; 13,8] | chưa đủ bằng chứng | [−24,0; 10,8] | chưa đủ bằng chứng |
| Delhi | H3 không mưa | 827 / 278 | 9,5 | [−2,2; 29,9] | chưa đủ bằng chứng | [0,0; 25,1] | chưa đủ bằng chứng | [1,5; 22,0] | ủng hộ |
| Lucknow | H1 gió yếu | 372 / 370 | 6,0 | [−7,9; 23,5] | chưa đủ bằng chứng | [−5,7; 19,1] | chưa đủ bằng chứng | [−3,2; 17,0] | chưa đủ bằng chứng |
| Lucknow | H2 lớp biên thấp | 372 / 370 | −10,5 | [−28,2; 4,0] | chưa đủ bằng chứng | [−23,7; 1,0] | chưa đủ bằng chứng | [−21,0; −0,5] | ngược chiều dự đoán |
| Lucknow | H3 không mưa | 792 / 319 | 11,5 | [−2,8; 24,2] | chưa đủ bằng chứng | [−1,0; 22,0] | chưa đủ bằng chứng | [1,0; 20,0] | ủng hộ |
| Gurugram | H1 gió yếu | 361 / 356 | 15,0 | [−5,5; 41,8] | chưa đủ bằng chứng | [−1,0; 34,0] | chưa đủ bằng chứng | [1,0; 31,0] | ủng hộ |
| Gurugram | H2 lớp biên thấp | 361 / 356 | −8,5 | [−39,8; 10,5] | chưa đủ bằng chứng | [−33,0; 8,5] | chưa đủ bằng chứng | [−29,0; 5,3] | chưa đủ bằng chứng |
| Gurugram | H3 không mưa | 811 / 259 | 12,0 | [−3,7; 34,2] | chưa đủ bằng chứng | [−0,3; 29,5] | chưa đủ bằng chứng | [2,0; 26,0] | ủng hộ |
| Jaipur | H1 gió yếu | 366 / 365 | −4,5 | [−16,5; 7,7] | chưa đủ bằng chứng | [−15,0; 5,5] | chưa đủ bằng chứng | [−12,2; 3,0] | chưa đủ bằng chứng |
| Jaipur | H2 lớp biên thấp | 366 / 365 | −25,0 | [−41,3; −11,0] | ngược chiều dự đoán | [−37,5; −13,4] | ngược chiều dự đoán | [−35,0; −15,5] | ngược chiều dự đoán |
| Jaipur | H3 không mưa | 869 / 224 | 17,2 | [7,0; 30,0] | ủng hộ | [8,0; 27,5] | ủng hộ | [9,8; 26,0] | ủng hộ |
| Amritsar | H1 gió yếu | 348 / 341 | 6,8 | [−3,2; 19,9] | chưa đủ bằng chứng | [−1,5; 17,0] | chưa đủ bằng chứng | [0,0; 15,0] | chưa đủ bằng chứng |
| Amritsar | H2 lớp biên thấp | 348 / 341 | −11,0 | [−26,4; 7,0] | chưa đủ bằng chứng | [−24,0; 2,8] | chưa đủ bằng chứng | [−22,0; 0,5] | chưa đủ bằng chứng |
| Amritsar | H3 không mưa | 750 / 279 | 16,0 | [3,5; 27,8] | ủng hộ | [5,2; 26,0] | ủng hộ | [7,2; 24,0] | ủng hộ |

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| Họ 15 (notebook): mức 0,05/15, khoảng 99,67% | 3 ủng hộ / 1 ngược chiều / 11 chưa đủ | cột `KL_family15` | Ủng hộ: Delhi H1, Jaipur H3, Amritsar H3. Ngược chiều: Jaipur H2. |
| Họ 3 mỗi thành phố (checklist): mức 0,05/3, khoảng 98,33% | 3 / 1 / 11 | cột `KL_family3` | 0/15 phép đổi kết luận so với họ 15. Delhi H3 có cận dưới đúng bằng 0,0 nên vẫn là "chưa đủ". |
| Không hiệu chỉnh: khoảng 95% | 7 / 2 / 6 | cột `KL_khong_hieu_chinh` | Chỉ để thấy tác động của hiệu chỉnh; không phải kết quả chính. |
| Mann–Whitney p < 0,05 | 11/15 | cột `p_MannWhitney` | Phép này coi các ngày là độc lập; DA không dùng để kết luận. |
| H2 (lớp biên thấp) | Hiệu ứng âm ở cả 5 thành phố, từ −5,5 đến −25,0 | bảng trên | Ngược chiều dự đoán; chỉ Jaipur có khoảng loại trừ 0. |

Cách ghi đúng: "Bonferroni trên 15 phép so sánh (3 giả thuyết × 5 thành phố), mức mỗi phép 0,05/15 ≈ 0,0033, khoảng tin cậy 99,67%". Việc chọn họ 15 hay họ 3 không làm đổi kết luận nào, nhưng tài liệu phải ghi đúng con số mà notebook dùng. Với B = 2.000, mỗi đuôi của khoảng 99,67% dựa trên khoảng 3 mẫu bootstrap, nên biên khoảng dao động theo seed; cả 15 kết luận giữ nguyên ở seed 0–9.

Bảng gọn: [R2_BA03_hypothesis_family15.csv](evidence/R2_BA03_hypothesis_family15.csv). Nguồn: [V19_hypothesis_tests_summary.csv](../evidence/V19_hypothesis_tests_summary.csv), [V19_hypothesis_tests_all_runs.csv](../evidence/V19_hypothesis_tests_all_runs.csv), [V19_hypothesis_tests_drop_covid.csv](../evidence/V19_hypothesis_tests_drop_covid.csv).

## S05 (sai số nội suy)

DA không tính lại S05 ở vòng 2. Theo gói giao việc, chỉ làm lại nếu nhóm dùng S05 để khẳng định 14 ngày là ngưỡng tối ưu. Số vòng 1 chỉ cho thấy sai số nội suy PM2.5 tăng dần theo độ dài khoảng trống (23% trung vị ở 1 ngày, 37% ở 14 ngày); nó không chứng minh 14 ngày là tối ưu. Nguồn: [S05](../supplementary_analysis.md#S05).
