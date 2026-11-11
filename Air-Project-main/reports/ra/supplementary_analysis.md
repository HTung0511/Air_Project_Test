# Phân tích bổ sung — DA → RA

Ngày 11/11/2026 · phiên bản 1.0 · người chạy: AI-3 Data Analyst · commit `ccd0a63`
Đọc cùng [verification_results.md](verification_results.md) và [reproduction_log.md](reproduction_log.md).

Tài liệu này trả lời bốn câu hỏi mà phần kiểm chứng chính chưa phủ: kết quả có đổi khi đổi ngưỡng "ngày nặng" không; vì sao mô hình sai nhiều ở thành phố này và ít ở thành phố khác; kết luận có do một thành phố hay một mùa quyết định không; và nội suy sai bao nhiêu. DA báo số; RA quyết định ý nghĩa phương pháp.

**Giao thức chung, chốt trước khi chạy.** Dữ liệu là bảng sạch đã commit. Khoảng chung 14/06/2017–01/07/2020. Mô hình, alpha (L1 10; L2 0,1; L3 30) và cách chọn ngưỡng F2 giữ nguyên như NB06, tức đều chọn trên train. Không có lựa chọn nào dựa trên tập test. Khoảng tin cậy 95% bằng bootstrap theo khối lịch 14 ngày chung giữa các thành phố, B = 4.000, seed 0. "Hôm nay" là quy tắc "ngày mai = hôm nay". "L3" là Ridge với AQI các ngày trước, chất ô nhiễm hôm nay và thời tiết đến hôm nay. Hiệu MAE âm nghĩa là mô hình sai ít hơn.

**Giới hạn chung.** Tập test (01/07/2019–29/02/2020) đã được tác giả và DA dùng cho nhiều phép phân tích; các khoảng tin cậy dưới đây không hiệu chỉnh cho việc đó. Tập test chỉ có tháng 7 đến tháng 2, không có tháng 3–6.

## Tóm tắt

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| Đổi ngưỡng 201 → 151 | Ba thành phố đứng đầu giữ nguyên; thứ tự trong nhóm đổi; khoảng cách giữa nhóm cao và nhóm giữa thu hẹp mạnh. Mô hình vẫn hơn "hôm nay" về cảnh báo, ở cả test và holdout. | [S01](#S01), [S06](#S06) | Ở ngưỡng 301, mô hình **kém** "hôm nay" về recall. |
| Vì sao sai số khác nhau giữa các thành phố | Sai số tuyệt đối đi theo mức biến động ngày-qua-ngày của AQI (Spearman 0,98 trên 8 thành phố). Tính theo phần trăm của AQI trung bình thì Amritsar và Chennai mới là nơi mô hình sai nhiều nhất. | [S02](#S02) | 66% mức giảm sai số đến từ Delhi, Gurugram, Lucknow. |
| Một thành phố có quyết định kết luận không | Không. Bỏ bất kỳ thành phố nào, L3 vẫn hơn "hôm nay" (−3,4 đến −4,4). | [S03](#S03) | Mô hình không chuyển giao tốt sang thành phố chưa có trong train: kém "hôm nay" ở Bengaluru. |
| Một mùa có quyết định kết luận không | Không với mô hình. Với EDA: tỉ số PM2.5 trong cùng mùa thấp hơn (1,6–2,8) so với cả năm (2,1–3,1); tương quan độ ẩm gần 0 vào mùa đông ở Delhi và Gurugram. | [S04](#S04) | |
| Sai số nội suy | PM2.5: 23% trung vị cho khoảng 1 ngày, 37% cho 14 ngày. Từ 30 ngày trở lên, nội suy kém hơn việc điền trung vị cùng tháng. | [S05](#S05) | Ngưỡng 14 ngày của tác giả nằm ở phía còn có lợi. |
| Độ dài khối bootstrap | Kết luận chính (L3 hơn "hôm nay", thời tiết có ích) không đổi với khối 7, 14, 28 ngày. | [S06](#S06) | Holdout: chưa tách khỏi 0 ở cả ba độ dài khối. |

---

<a id="S01"></a>
## S01 — Ngưỡng "ngày nặng" 151 thay cho 201

**Vì sao làm.** Mọi kết luận về "ngày nặng" dùng ngưỡng AQI ≥ 201 (mức "Poor" của CPCB). Ngưỡng 151 nằm giữa dải 101–200 của CPCB và không phải một mốc phân loại của CPCB; nó được dùng ở đây như một ngưỡng cảnh báo sớm hơn. DA chạy thêm 101 và 301 để thấy xu hướng.
**Đại lượng ước lượng.** (a) Tỉ lệ ngày có AQI ≥ ngưỡng trên số ngày có AQI, từng thành phố, trong khoảng chung. (b) Recall và precision của cảnh báo "ngày mai AQI ≥ ngưỡng" trên tập test, và hiệu giữa L3 với "hôm nay" trên cùng mẫu.
**Mẫu.** EDA: 8.734 ngày có AQI. Mô hình: 1.947 cặp test. Sai số hồi quy (MAE) không phụ thuộc ngưỡng nên không lặp lại.
Script: `s01_threshold.py`, `v14_eda.py 151`.

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| Số ngày nặng | 2.792/8.734 = 32,0% ở ngưỡng 151; 1.850 = 21,2% ở ngưỡng 201 | [S01_threshold_eda.csv](evidence/S01_threshold_eda.csv) | Ở 101: 58,5%. Ở 301: 10,9%. |
| Tỉ lệ theo thành phố ở ngưỡng 151 | Delhi 719/1.105 = 65,1%; Gurugram 669/1.070 = 62,5%; Lucknow 663/1.111 = 59,7%; Jaipur 337/1.093 = 30,8%; Amritsar 204/1.029 = 19,8%; Chennai 107/1.110 = 9,6%; Hyderabad 69/1.108 = 6,2%; Bengaluru 24/1.108 = 2,2% | như trên | |
| Thứ hạng | Đổi ở cả ba cặp sát nhau: Gurugram lên trên Lucknow; Jaipur lên trên Amritsar; Hyderabad lên trên Bengaluru | như trên | Nhóm ba thành phố cao nhất giữ nguyên ở 100% số lần bootstrap, với cả ngưỡng 151 và 201. |
| Delhi đứng đầu | Xác suất bootstrap 83,0% ở ngưỡng 151; 94,8% ở 201; 56,4% ở 301 | như trên | CI của Delhi ở 151: [55,9; 73,6]. |
| Hiệu giữa các thành phố ở ngưỡng 151 (điểm %) | Delhi − Gurugram 2,5 [−2,9; 7,7]; Lucknow − Gurugram −2,8 [−7,9; 2,1]; Amritsar − Jaipur −11,0 [−17,1; −5,1]; Bengaluru − Hyderabad −4,1 [−6,9; −1,3] | [S01_V14_eda_block_bootstrap_rank_thr151.csv](evidence/S01_V14_eda_block_bootstrap_rank_thr151.csv) | Ở ngưỡng 201, Amritsar và Jaipur không tách được (0,3 [−3,4; 3,8]). Ở 151, Jaipur cao hơn rõ. Thứ hạng đầy đủ giữ ở 67% số lần, so với 19% ở ngưỡng 201. |
| Khoảng cách nhóm cao so với nhóm giữa | Delhi gấp Jaipur 2,1 lần ở ngưỡng 151; 4,6 lần ở 201; 27,6 lần ở 301; 1,2 lần ở 101 | S01_threshold_eda.csv | Câu "gấp 4,1–4,6 lần" trên hình `eda_01` chỉ đúng cho ngưỡng 201. |
| Số thành phố đủ 100 ngày nặng | 6 ở ngưỡng 151 (thêm Chennai); 5 ở 201; 3 ở 301; 8 ở 101 | như trên | Tập thành phố dùng cho các phân tích "ngày nặng" phụ thuộc ngưỡng. |
| Mùa | Ngày nặng rơi vào tháng 10–2: 64,3% ở ngưỡng 151; 73,2% ở 201; 87,5% ở 301. Tháng 11–12: 29,6%; 35,2%; 47,3% | như trên | Ngưỡng càng cao thì càng tập trung vào mùa đông. Tháng nhiều ngày nặng nhất vẫn là tháng 11 (ở ngưỡng 101 là tháng 1). |
| Tỉ số PM2.5 | Trung vị các thành phố 2,39 ở ngưỡng 151; 2,82 ở 201. Tỉ số hai trung vị gộp 2,74; 3,26 | như trên; [S01_V16_eda_pollutant_by_city_thr151.csv](evidence/S01_V16_eda_pollutant_by_city_thr151.csv) | Con số "2,8×" gắn với ngưỡng 201. |
| Cảnh báo trên test, ngưỡng 151 | 547 ngày nặng / 1.947. Hôm nay: recall 0,876, precision 0,871 (TP 479, FP 71, FN 68). L3: recall 0,898, precision 0,911 (TP 491, FP 48, FN 56) | [S01_threshold_alerts.csv](evidence/S01_threshold_alerts.csv) | |
| Hiệu L3 − hôm nay, ngưỡng 151 | Recall +0,022 [0,002; 0,046]; precision +0,040 [0,020; 0,069]; F1 +0,031 [0,019; 0,050] | như trên | Cả ba tách khỏi 0. |
| Ngưỡng F2 (chọn trên train), nhãn 151 | Hôm nay cắt ở 132: recall 0,931, precision 0,789. L3 cắt ở 137: recall 0,952, precision 0,831. Hiệu recall +0,022 [0,008; 0,040] | như trên | Ở nhãn 201, hiệu recall tại ngưỡng F2 là +0,008 [−0,010; 0,029], chưa tách khỏi 0. |
| **Kết quả âm**: nhãn 301 | L3 cắt ở 301: recall 0,678; hôm nay: 0,777. Hiệu −0,099 [−0,157; −0,049] | như trên | Mô hình bỏ sót nhiều ngày rất nặng hơn "hôm nay". Precision thì cao hơn (+0,118). F1 chưa tách khỏi 0. Phù hợp với độ chệch âm của mô hình trên ngày nặng ([V21](verification_results.md#V21)). |
| **Kết quả âm**: nhãn 101 | Hiệu recall +0,027 [−0,002; 0,048]; precision +0,005 [−0,012; 0,025] | như trên | Chưa tách khỏi 0. |

**Giới hạn.** Ngưỡng 151 không được tác giả định trước; mọi so sánh ở đây là hậu nghiệm. Bốn ngưỡng trên cùng một tập test nghĩa là có nhiều phép so sánh. Holdout ở ngưỡng 151 nằm ở [S06](#S06).

<a id="S02"></a>
## S02 — Vì sao mô hình sai nhiều ở thành phố này và ít ở thành phố khác

**Đại lượng.** Trên tập test, từng thành phố (239–244 ngày mỗi nơi): MAE của L3; MAE của "hôm nay"; AQI trung bình; mức thay đổi tuyệt đối trung bình giữa hai ngày liền nhau; MAE chia cho AQI trung bình; R² trong thành phố; độ chệch.
Script: `s02_city_season.py`.

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| MAE của L3 (điểm AQI) | Gurugram 30,1; Delhi 29,3; Amritsar 24,4; Lucknow 22,7; Chennai 17,0; Jaipur 15,2; Hyderabad 9,7; Bengaluru 7,9 | [S02_city_error_profile.csv](evidence/S02_city_error_profile.csv) | Chênh gần 4 lần giữa nơi cao nhất và thấp nhất. |
| MAE đi theo cái gì | Spearman giữa 8 thành phố: với mức thay đổi ngày-qua-ngày 0,98; với độ lệch chuẩn AQI 0,93; với AQI trung bình 0,86 | [S02_city_error_rank_correlation.csv](evidence/S02_city_error_rank_correlation.csv) | n = 8, chỉ mô tả. Thành phố có AQI cao thì AQI cũng dao động mạnh (Delhi đổi trung bình 36,7 điểm mỗi ngày; Bengaluru 8,7), nên khó đoán hơn theo điểm tuyệt đối. |
| MAE tính theo % AQI trung bình | Amritsar 21,1%; Chennai 18,2%; Gurugram 15,8%; Jaipur 13,6%; Delhi 12,5%; Lucknow 11,5%; Hyderabad 11,0%; Bengaluru 9,8% | S02_city_error_profile.csv | Thứ tự đổi hẳn: Delhi và Lucknow thuộc nhóm sai ít theo tỉ lệ. |
| R² trong từng thành phố | Lucknow 0,92; Delhi 0,89; Hyderabad 0,89; Gurugram 0,87; Amritsar 0,76; Jaipur 0,74; Bengaluru 0,70; Chennai 0,58 | như trên | R² chung 0,906 cao một phần vì khác biệt giữa các thành phố. Chennai có tự tương quan ngày-qua-ngày thấp nhất (0,71). |
| Mức giảm sai số so với "hôm nay" | Lucknow 22,1%; Delhi 20,2%; Gurugram 18,9%; Amritsar 15,9%; Hyderabad 14,9%; Chennai 12,4%; Bengaluru 9,1%; Jaipur 7,3% | như trên | Mô hình giúp nhiều nhất ở nơi AQI cao. |
| Ai đóng góp vào mức giảm chung | Delhi 23,5%, Gurugram 22,3%, Lucknow 20,5% (cộng 66,3%); Amritsar 14,4%; Chennai 7,7%; Hyderabad 5,4%; Jaipur 3,8%; Bengaluru 2,5% | [S02_city_contribution.csv](evidence/S02_city_contribution.csv) | Con số "−3,95" chung chủ yếu phản ánh ba thành phố ô nhiễm nặng. |
| Độ chệch trên ngày nặng | Delhi −17,3; Gurugram −16,7; Lucknow −17,7; Jaipur −40,8 (9 ngày); Amritsar −54,0 (29 ngày); Chennai −60,9 (10 ngày) | S02_city_error_profile.csv | Ở mọi thành phố mô hình đoán thấp ngày nặng. Nặng nhất ở nơi ngày nặng hiếm trong train (Chennai 24 ngày, Amritsar 84). |
| Sai số tập trung vào ít ngày | 10% ngày sai nhất chiếm 31–37% tổng sai số ở cả 8 thành phố | như trên | Sai số lớn nhất của L3: 218 điểm (Delhi). |
| Dữ liệu đầu vào | Amritsar thiếu PM2.5 ở 10,5% dòng train; Bengaluru 1,5%; các nơi khác 0% | như trên | Một yếu tố có thể liên quan đến sai số tương đối cao ở Amritsar. DA chưa kiểm quan hệ này. |

**Giới hạn.** Các tương quan giữa 8 thành phố là mô tả, không có khoảng tin cậy có nghĩa. Phân tích không tách được nguyên nhân (nguồn phát thải, địa hình, chất lượng trạm); nó chỉ cho thấy sai số tuyệt đối tỉ lệ với mức dao động của chính chuỗi AQI.

<a id="S03"></a>
## S03 — Bỏ lần lượt từng thành phố

**Giao thức.** (a) Bỏ một thành phố khỏi cả train và test, huấn luyện lại với alpha cũ. (b) Huấn luyện trên 7 thành phố, dự đoán thành phố bị bỏ. (c) Tính lại các số EDA gộp khi bỏ một thành phố.
Script: `s02_city_season.py`.

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| (a) L3 − hôm nay khi bỏ một thành phố | Từ −3,36 [−4,63; −2,11] (bỏ Gurugram) đến −4,44 [−6,13; −2,84] (bỏ Bengaluru). Gốc −3,95 | [S03_leave_one_city_out_model.csv](evidence/S03_leave_one_city_out_model.csv) | Cả 8 khoảng tin cậy loại trừ 0. Số "bỏ Gurugram −3,36" khớp phân tích độ nhạy của tác giả trong NB06. |
| (a) Thêm thời tiết (L3 − L2) | Từ −1,20 đến −1,63; cả 8 khoảng loại trừ 0 | như trên | |
| (a) Bỏ cả ba thành phố nặng | L3 − hôm nay −1,99 [−2,91; −1,12]; thời tiết −0,70 [−0,96; −0,45]; thêm chất ô nhiễm (L2 − L1) −0,54 [−1,25; 0,12] | như trên | 1.215 cặp test, 48 ngày nặng. Lợi ích vẫn còn nhưng bằng một nửa. Phần của chất ô nhiễm chưa tách khỏi 0. |
| (a) Chỉ ba thành phố nặng | −8,22 [−11,69; −4,88] | như trên | |
| (a) Chỉ ba thành phố phía nam | −1,16 [−2,18; −0,22]; thời tiết −0,28 [−0,45; −0,11] | như trên | Chỉ 10 ngày nặng trong test; không nói được gì về cảnh báo. |
| (b) **Kết quả âm**: dự đoán thành phố chưa có trong train | Bengaluru: MAE 10,07 so với "hôm nay" 8,68, hiệu +1,39 [0,26; 2,65] (kém hơn). Jaipur +2,12 [−0,26; 4,36]. Hyderabad +0,80 [−0,49; 2,14]. Delhi −3,00 [−6,67; 0,69], độ chệch −19,9 | [S03_train_without_city_predict_city.csv](evidence/S03_train_without_city_predict_city.csv) | Mô hình không dùng được ngay cho thành phố mới ở 4/8 trường hợp. |
| (b) Trường hợp vẫn hơn "hôm nay" | Lucknow −6,65 [−10,16; −3,38]; Gurugram −6,28 [−9,46; −3,37]; Amritsar −2,93 [−5,97; −0,16]; Chennai −2,11 [−4,30; −0,18] | như trên | |
| (c) Tỉ số PM2.5 (trung vị các thành phố) | 2,65–2,91 (gốc 2,82) | [S03_leave_one_city_out_eda.csv](evidence/S03_leave_one_city_out_eda.csv) | |
| (c) Spearman PM2.5–AQI; tỉ lệ ngày nặng rơi vào tháng 10–2 | 0,89–0,92; 72,4–74,9% | như trên | Không thành phố nào quyết định hai con số này. |
| (c) Ngày nặng nằm ở đâu | Delhi 30,5%; Lucknow 27,9%; Gurugram 26,8% của 1.850 ngày nặng | như trên | Ba thành phố giữ 85% số ngày nặng. Mọi thống kê gộp về "ngày nặng" thực chất mô tả ba thành phố này. |

**Giới hạn.** Ở (b), thành phố lạ nhận hệ số của mức tham chiếu trong mã hoá one-hot, nên một phần sai số là do thiếu hệ số chặn riêng, không hẳn do quan hệ khác nhau.

<a id="S04"></a>
## S04 — Bỏ lần lượt từng mùa

**Định nghĩa mùa.** Đông: tháng 12–2. Hè: 3–5. Mưa: 6–9. Sau mưa: 10–11.
**Giao thức.** (a) Giữ mô hình, bỏ một mùa khỏi test. (b) Bỏ một mùa khỏi train, đánh giá trên toàn bộ test. (c) Tỉ lệ ngày nặng, tỉ số PM2.5 và tương quan độ ẩm tính riêng từng mùa.
Script: `s02_city_season.py`.

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| (a) Test không có mùa đông | L3 − hôm nay −2,70 [−4,40; −1,24]; n = 1.222, 178 ngày nặng | [S04_leave_one_season_out_model.csv](evidence/S04_leave_one_season_out_model.csv) | Vẫn tách khỏi 0, nhỏ hơn gốc (−3,95). |
| (a) Test không có mùa mưa; không có mùa sau mưa | −5,63 [−6,90; −4,26]; −3,60 [−5,16; −2,07] | như trên | Test không có tháng 3–5 nên không có dòng "bỏ hè". |
| (b) Train thiếu một mùa | Thiếu đông −3,69 [−5,10; −2,37]; thiếu hè −3,91; thiếu mưa −3,83 [−5,50; −2,23]; thiếu sau mưa −3,76 | như trên | MAE của L3 từ 19,55 đến 19,77 (gốc 19,52). Không mùa nào trong train là thiết yếu. |
| (c) Ba thành phố cao nhất theo mùa | Luôn là Delhi, Lucknow, Gurugram ở cả 4 mùa và khi bỏ từng mùa | [S04_share_by_season.csv](evidence/S04_share_by_season.csv), [S04_heavy_days_by_season.csv](evidence/S04_heavy_days_by_season.csv) | |
| (c) Thứ tự trong nhóm theo mùa | Đông: Delhi 90,0%, Lucknow 86,7%, Gurugram 73,9%. Mưa: Gurugram 23,0%, Delhi 9,3%, Lucknow 5,5% | như trên | Gurugram đứng đầu vào mùa mưa. Thứ hạng cả năm che mất điều này. |
| (c) Ngoài tháng 10–2 | Delhi 25,0%; Gurugram 24,7%; Lucknow 20,2%; Amritsar 3,3%; Jaipur 2,8% | S04_share_by_season.csv | Ba thành phố nặng vẫn có một phần tư số ngày ở mức nặng ngoài mùa cao điểm. |
| (c) Tỉ số PM2.5 trong cùng mùa | Delhi 1,78 (hè), 1,82 (mưa). Gurugram 1,82; 2,53; 2,02; 2,10. Lucknow 1,79 (hè); 2,29 (sau mưa); 2,27 (đông). Jaipur 1,62; 1,80. Amritsar 2,82 (sau mưa) | [S04_pm25_ratio_by_season.csv](evidence/S04_pm25_ratio_by_season.csv) | Chỉ tính khi mỗi nhóm có ≥ 30 ngày. 10/12 tỉ số theo mùa thấp hơn tỉ số cả năm của chính thành phố đó (cả năm: 2,06–3,13). Một phần của "2,8×" là chênh lệch giữa các mùa. |
| (c) Tương quan độ ẩm–AQI (đã bỏ mùa theo tháng) riêng từng mùa | Delhi: hè −0,52; mưa −0,58; sau mưa −0,09; đông 0,00. Gurugram: −0,46; −0,41; −0,13; −0,07. Chennai: +0,08; +0,04; −0,54; −0,25. Amritsar sau mưa +0,07 | [S04_humidity_rho_by_season.csv](evidence/S04_humidity_rho_by_season.csv) | Câu "độ ẩm âm ở cả 8 thành phố" đúng cho cả năm ([V18](verification_results.md#V18)). Riêng mùa đông, mùa có nhiều ngày nặng nhất, quan hệ này gần 0 ở Delhi và Gurugram. |

**Giới hạn.** Các hệ số theo mùa ở dòng cuối chưa có khoảng tin cậy. Khoảng chung chỉ có 3 lần lặp của mỗi mùa.

<a id="S05"></a>
## S05 — Sai số nội suy đo bằng giả lập che khối

**Vì sao làm.** [V09](verification_results.md#V09) cho thấy đổi `max_gap` gần như không đổi kết quả mô hình, nhưng đó là vì mô hình bỏ các ô nội suy. Câu hỏi nội suy sai bao nhiêu cần đo riêng.
**Giao thức.** Lấy những đoạn có giá trị thật liên tục (không phải ô nội suy). Che L ngày liên tiếp, L ∈ {1, 3, 7, 14, 30, 60}. Nội suy tuyến tính giữa hai đầu mút thật, đúng cách `utils.impute_time_series` làm. So với giá trị thật. Mỗi tổ hợp (thành phố, chất, L) lấy ngẫu nhiên tối đa 300 vị trí, seed 0. Hai mốc so sánh: giữ giá trị cuối; trung vị cùng thành phố, cùng tháng.
**Chỉ số.** MAE; MAE chia cho trung vị của chất đó tại thành phố; độ chệch.
Script: `s05_interp_simulation.py`.

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| PM2.5, theo độ dài khoảng | MAE 13,8; 18,0; 20,5; 22,8; 24,9; 27,1 µg/m³ cho L = 1; 3; 7; 14; 30; 60. Tương ứng 23%; 29%; 33%; 37%; 40%; 43% trung vị | [S05_interp_sim_by_length.csv](evidence/S05_interp_sim_by_length.csv) | 2.400 khối giả lập cho mỗi L. |
| Độ chệch | 0,2–0,7 µg/m³ | như trên | Nội suy không lệch có hệ thống; sai số là do mất dao động. |
| PM2.5: so với giữ giá trị cuối | Nội suy tốt hơn ở cả 6 độ dài (13,8 so với 18,0 ở L = 1; 22,8 so với 27,6 ở L = 14) | như trên | |
| So với trung vị cùng tháng | PM2.5, PM10, NO: nội suy tốt hơn đến L = 14, **kém hơn** từ L = 30. SO2: kém hơn ở L = 60. CO, NO2, O3: nội suy tốt hơn ở mọi L | như trên | Ngưỡng 14 ngày nằm trước điểm đổi chiều của PM2.5. Log làm sạch ghi tác giả đã thôi nội suy 1.316 ô thuộc khoảng dài hơn 14 ngày; với PM2.5, đó là vùng nội suy kém hơn mốc đơn giản. |
| Các chất khác, MAE theo % trung vị ở L = 1 và L = 14 | NO2 16% → 29%; O3 15% → 27%; PM10 20% → 31%; SO2 24% → 36%; CO 37% → 49%; NO 40% → 64% | như trên | CO và NO khó nội suy nhất. |
| Theo thành phố (PM2.5, L = 14) | Gurugram 44%; Amritsar 42%; Lucknow 40%; Delhi 39%; Bengaluru 36%; Chennai 34%; Hyderabad 29%; Jaipur 29% | [S05_interp_sim_by_city.csv](evidence/S05_interp_sim_by_city.csv) | |
| Theo mùa (PM2.5, L = 14, µg/m³) | Sau mưa 35,1; đông 29,2; hè 18,4; mưa 14,8 | [S05_interp_sim_by_season.csv](evidence/S05_interp_sim_by_season.csv) | Nội suy sai nhiều nhất đúng vào mùa ô nhiễm cao. |
| Khoảng thật đã được nội suy | 3.329 ô: 62% thuộc khoảng dài 4–14 ngày | [S05_actual_interpolated_gap_lengths.csv](evidence/S05_actual_interpolated_gap_lengths.csv) | Sai số kỳ vọng của phần lớn ô nội suy vì vậy ở mức 30–37% trung vị (với PM2.5). |

**Giới hạn của giả lập.** Vị trí che là ngẫu nhiên trong những đoạn trạm đang đo đủ. Khoảng thiếu thật có thể trùng với sự cố hoặc đợt ô nhiễm bất thường, khi đó sai số thật có thể lớn hơn. Giả lập không dùng được cho cột gần như không có dữ liệu.

<a id="S06"></a>
## S06 — Độ dài khối bootstrap và holdout ở ngưỡng 151

**Giao thức.** (a) Tính lại bốn hiệu MAE chính với khối 7, 14, 28 ngày, trên test và holdout. (b) Cảnh báo trên holdout với nhãn 151 (94 ngày nặng) và 201 (18 ngày nặng); ngưỡng F2 lấy từ train.
Script: `s06_block_holdout.py`.

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| (a) Test: L3 − hôm nay (−3,95) | [−5,24; −2,73] với khối 7 ngày; [−5,40; −2,56] với 14; [−5,66; −2,28] với 28 | [S06_block_length_model.csv](evidence/S06_block_length_model.csv) | Khoảng rộng ra khi khối dài hơn; vẫn loại trừ 0. Số khối: 35, 18, 9. |
| (a) Test: thêm thời tiết (−1,40) và thêm chất ô nhiễm (−2,02) | Loại trừ 0 ở cả ba độ dài khối | như trên | |
| (a) Test: L1 − hôm nay (−0,53) | [−1,31; 0,22]; [−1,19; 0,08]; [−0,99; −0,10] | như trên | Kết luận **đổi** theo độ dài khối. Với 28 ngày chỉ còn 9 khối, khoảng tin cậy kém tin cậy. |
| (a) Holdout: L3 − hôm nay (−1,02) | [−2,59; 0,46]; [−2,70; 0,48]; [−2,55; 0,53] | như trên | Chưa tách khỏi 0 ở cả ba. Số khối: 18, 9, 5. |
| (a) Holdout: thêm thời tiết (−0,10); thêm chất ô nhiễm (−0,21) | Chưa tách khỏi 0 ở cả ba | như trên | Trên holdout, lợi ích của thời tiết không tái hiện. |
| (b) Holdout, nhãn 151, cắt ở 151 | Hôm nay: recall 0,532, precision 0,538 (TP 50, FP 43, FN 44). L3: recall 0,628, precision 0,621 (TP 59, FP 36, FN 35). Hiệu recall +0,096 [0,020; 0,167]; precision +0,083 [0,022; 0,180] | [S06_holdout_alerts_151_201.csv](evidence/S06_holdout_alerts_151_201.csv) | Với 94 ngày nặng, L3 tách khỏi "hôm nay" trên holdout. |
| (b) Holdout, nhãn 151, ngưỡng F2 | Cả hai: recall 0,798 (75/94). Hiệu recall 0,000 [−0,059; 0,043]; precision +0,032 [−0,043; 0,092] | như trên | Chưa tách khỏi 0. |
| (b) Holdout, nhãn 201 | Hôm nay bắt 5/18; L3 bắt 6/18. Ở ngưỡng F2 cả hai bắt 13/18 | như trên | Quá ít ngày nặng. |
| (b) Mức tuyệt đối trên holdout so với test | Recall ở nhãn 151: 0,53–0,63 trên holdout; 0,88–0,90 trên test | như trên; [S01](#S01) | Cả mô hình lẫn "hôm nay" đều kém đi nhiều trong giai đoạn tháng 3–7/2020. Giai đoạn này gồm phong toả (từ 25/03/2020) và các tháng vốn ít ô nhiễm; DA không tách được hai yếu tố. |

**Giới hạn.** Holdout chỉ có 4 tháng và 5–18 khối, nên mọi khoảng tin cậy trên holdout dựa vào rất ít khối độc lập.
