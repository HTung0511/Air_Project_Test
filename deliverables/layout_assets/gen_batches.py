# Sinh lô request batch_update cho Google Docs: chèn 20 hình + ghi chú giữ chỗ.
# Chỉ số gốc lấy từ find_text tại trạng thái T0; bù lũy kế D theo thứ tự tài liệu.
import json

RAW = ("https://raw.githubusercontent.com/HTung0511/Air_Project_Test/"
       "c4c75f65c7fb39f843d397bec0ef6c54fd15c29e/Air-Project-main/reports/figures/")
SRC = "Nguồn: %s, reports/figures/ tại HTung0511/Air_Project_Test, nhánh main, commit c4c75f6."

W = 450.0
ASPECT = {
    "so_do": 6.9686, "missing_after_cleaning_8cities": 2.2, "missing_pattern_lucknow_jaipur": 1.5,
    "fill_strategies_lucknow_jaipur": 3.25, "outliers_pm25_lucknow_jaipur": 1.8571,
    "eda_00_sample_size": 1.7778, "eda_01_poor_share_city": 1.7778, "eda_05_aqi_distribution": 1.6667,
    "eda_02_heatmap_city_month": 2.0833, "eda_03_trend_city_year": 1.875, "eda_04_pm25_aqi": 2.1739,
    "corr_01_raw_vs_adjusted": 2.5, "corr_02_hypothesis_tests": 1.6129, "corr_03_humidity_deciles": 2.6136,
    "corr_04_poor_share_by_humidity": 1.9792, "model_01_residual_diagnostics": 1.4375,
    "model_02_mae_by_model": 2.0408, "model_03_mae_by_city": 1.9, "model_04_precision_recall": 1.7857,
    "model_05_humidity_recheck": 2.3958,
}
URI = {k: (RAW + k + ".png") for k in ASPECT}
URI["so_do"] = "https://lh3.googleusercontent.com/d/1H4MHzXLcSVLr9DURzsAfeqL9bHWLLUr8"

CAP = {
 "so_do": ("Hình 1. Sơ đồ quy trình sáu nhóm công việc của đề tài: dữ liệu gốc → kiểm tra và làm sạch → "
           "bảng hồi cứu có cờ → EDA và tích hợp thời tiết → phân tích liên hệ → thực nghiệm dự báo → ứng dụng phát lại. "
           "Sơ đồ dàn trang vẽ lại từ §1.5, không chứa số liệu mới. Nhánh dự báo cần kiểm soát riêng thông tin theo thời điểm; "
           "không mặc định bảng hồi cứu là dữ liệu causal. "
           "Nguồn: sơ đồ dàn trang (tệp so_do_quy_trinh_AirProject25IT.png trên Drive của nhóm), không phải kết quả phân tích."),
 "missing_after_cleaning_8cities": ("Hình 2. Mức thiếu còn lại của từng biến theo thành phố sau khi làm sạch (% ngày thiếu, toàn kỳ 2015–01/07/2020; "
           "số ngày mỗi thành phố 1.114–2.009). Thiếu tập trung ở PM10 (Lucknow 100%, Chennai 85%, Gurugram 52%) và NH3 (Gurugram 93%, Lucknow 50%); "
           "các ô thiếu nặng được giữ nguyên thay vì tạo số cho khoảng dài. " + SRC % "missing_after_cleaning_8cities.png"),
 "missing_pattern_lucknow_jaipur": ("Hình 3. Mẫu hình thiếu dữ liệu TRƯỚC xử lý tại Lucknow và Jaipur (đen = thiếu): thiếu dạng khối ở PM10, NH3, NOx "
           "và thiếu toàn kỳ ở Xylene; đặt cạnh Hình 2 để đối chiếu trước–sau với cùng ý nghĩa màu. " + SRC % "missing_pattern_lucknow_jaipur.png"),
 "fill_strategies_lucknow_jaipur": ("Hình 4. Phân bố PM2.5 tại Lucknow và Jaipur dưới bốn chiến lược điền minh họa của Notebook 02: (A) bỏ dòng thiếu, "
           "(B) median toàn cục, (C) median theo tháng, (D) nội suy khoảng ≤1 ngày theo nhãn của hình. Quy tắc của pipeline chính là nội suy khoảng thiếu "
           "≤14 ngày (Data_dictionary.md); hình này chỉ so sánh chiến lược trên hai thành phố ví dụ. " + SRC % "fill_strategies_lucknow_jaipur.png"),
 "outliers_pm25_lucknow_jaipur": ("Hình 5. Chuỗi PM2.5 quan sát tại Lucknow (2015–2020) và Jaipur (06/2017–06/2020) với các điểm gắn cờ: chấm cam = vượt "
           "IQR×1,5 tính theo tháng dương lịch (giữ giá trị, chỉ đánh dấu); vòng đỏ = nghi lỗi theo ngữ cảnh (≥2,5× trung vị lân cận). " + SRC % "outliers_pm25_lucknow_jaipur.png"),
 "eda_00_sample_size": ("Hình 6. Số ngày có AQI hợp lệ của tám thành phố trong khoảng chung 14/06/2017–01/07/2020 (1.029–1.111 ngày mỗi thành phố; "
           "tổng n = 8.734 ngày có AQI) — mẫu số của các so sánh trong Phần III. " + SRC % "eda_00_sample_size.png"),
 "eda_01_poor_share_city": ("Hình 7. Tỷ lệ quan sát có AQI ≥201 (mức Poor trở lên) theo thành phố trong khoảng chung; giữ trục phần trăm và khoảng ngày "
           "từ hình gốc; n = 8.734 ngày có AQI, chỉ đọc theo nhóm. " + SRC % "eda_01_poor_share_city.png"),
 "eda_05_aqi_distribution": ("Hình 8. Phân phối AQI hằng ngày theo thành phố (hộp Q1–Q3, vạch đen: trung vị; đường đứt nét: ngưỡng Poor 201 điểm, thang CPCB); "
           "cho thấy khác biệt đuôi phân phối mà bảng xếp hạng không thể hiện; n = 8.734. " + SRC % "eda_05_aqi_distribution.png"),
 "eda_02_heatmap_city_month": ("Hình 9. Trung vị AQI theo thành phố–tháng dương lịch, gộp khoảng chung 14/06/2017–01/07/2020; thống kê trong mỗi ô là trung vị "
           "(không phải trung bình) và mỗi ô chỉ gồm khoảng 3 năm quan sát. " + SRC % "eda_02_heatmap_city_month.png"),
 "eda_03_trend_city_year": ("Hình 10. AQI trung bình của các tháng 1–6 theo năm (2015–2020; năm 2020 chỉ đến 30/6 và có phong tỏa từ 25/3/2020); bỏ 7 ô "
           "thành phố–năm có dưới 150 ngày; Amritsar (nét đứt) bắt đầu từ 2018; n = 13.220 ngày có AQI, 01/01/2015–01/07/2020. " + SRC % "eda_03_trend_city_year.png"),
 "eda_04_pm25_aqi": ("Hình 11. Trái: tương quan hạng Spearman cùng ngày giữa năm chất và AQI (PM2.5 0,91; NO2 0,52; CO 0,48; SO2 0,38; O3 0,34). Phải: trung vị "
           "tỷ số nồng độ giữa nhóm ngày AQI ≥201 và nhóm ngày còn lại của 5 thành phố có ≥100 ngày nặng (chấm = từng thành phố; đường đứt nét = bằng ngày thường); "
           "PM2.5 gấp 2,8 lần; đơn vị nồng độ theo Data_dictionary.md; n = 8.734, khoảng chung. " + SRC % "eda_04_pm25_aqi.png"),
 "corr_01_raw_vs_adjusted": ("Hình 12. Tương quan Spearman thời tiết–AQI thô (trái) và sau khi bỏ chu kỳ mùa bằng trung vị thành phố×tháng (phải), khoảng chung "
           "14/06/2017–01/07/2020; hai bảng dùng cùng thang hệ số để thấy đổi dấu/độ lớn. Ô in đậm: khoảng tin cậy 95% (bootstrap theo khối 14 ngày) loại trừ 0 "
           "sau hiệu chỉnh FDR; hàng đánh dấu * (Chennai, Bengaluru, Hyderabad) có dưới 100 ngày AQI ≥201 nên chỉ mô tả. Thời tiết: Open-Meteo (ERA5, dữ liệu mô hình); "
           "n = 8.734. " + SRC % "corr_01_raw_vs_adjusted.png"),
 "corr_02_hypothesis_tests": ("Hình 13. Chênh lệch trung vị AQI giữa điều kiện bất lợi và thuận lợi trong cùng thành phố–tháng cho 15 so sánh (5 thành phố × 3 giả thuyết); "
           "thanh = khoảng tin cậy bootstrap theo khối 14 ngày ở mức Bonferroni 99,67%; đường đứt nét tại 0. Màu cam: ủng hộ giả thuyết (3); đen: ngược chiều dự đoán (1); "
           "xám: chưa đủ bằng chứng (11). " + SRC % "corr_02_hypothesis_tests.png"),
 "corr_03_humidity_deciles": ("Hình 14. Lệch trung vị AQI so với ngày điển hình cùng tháng theo 10 nhóm độ ẩm (1 = khô nhất, 10 = ẩm nhất; mỗi nhóm = 1/10 số ngày của "
           "thành phố, xếp theo độ ẩm lệch so với trung vị cùng tháng) tại Delhi, Lucknow, Gurugram. " + SRC % "corr_03_humidity_deciles.png"),
 "corr_04_poor_share_by_humidity": ("Hình 15. Tỷ lệ ngày có AQI ≥201 theo ba nhóm độ ẩm (tertile tính trong từng thành phố–tháng, nên mỗi tháng đóng góp như nhau cho cả "
           "ba nhóm) tại năm thành phố; các nhãn tỷ lệ % giữ nguyên từ hình gốc. " + SRC % "corr_04_poor_share_by_humidity.png"),
 "model_01_residual_diagnostics": ("Hình 16. Chẩn đoán phần dư của mô hình OLS diễn giải trên tập train (mức 3, dòng đủ đặc trưng; n = 5.741 cặp, ngày được dự đoán "
           "15/06/2017–30/06/2019): phần dư theo giá trị khớp trước và sau biến đổi log mục tiêu, QQ-plot và trung vị tuần của phần dư. Tương quan giữa độ lớn phần dư và "
           "giá trị khớp giảm từ 0,23 xuống −0,03; Breusch–Pagan vẫn chỉ ra phương sai thay đổi nên dùng sai số chuẩn bền. " + SRC % "model_01_residual_diagnostics.png"),
 "model_02_mae_by_model": ("Hình 17. MAE trên tập test (điểm AQI; thấp hơn tốt hơn) của ba mô hình đối chứng và ba mức đặc trưng; cột kẻ sọc là kịch bản cận trên dùng thời tiết "
           "ngày mai, không phải cấu hình vận hành. Test = 01/07/2019–29/02/2020, n = 1.947 cặp thành phố–ngày. Lưu ý đối chiếu: hai cột đối chứng đầu trong hình (64,5 và 43,4) "
           "khác số nêu trong văn bản (§3.3.1: khoảng 60,5 và 55,8); nhóm cần kiểm lại bảng nguồn trước khi diễn giải. " + SRC % "model_02_mae_by_model.png"),
 "model_03_mae_by_city": ("Hình 18. MAE trên tập test theo thành phố, so sánh đối chứng 'ngày mai = hôm nay' với mức 3; thành phố xếp theo số ngày AQI ≥201 trong tập test "
           "(ghi trong nhãn); test = 01/07/2019–29/02/2020, n = 1.947 cặp. " + SRC % "model_03_mae_by_city.png"),
 "model_04_precision_recall": ("Hình 19. Đường precision–recall của cảnh báo AQI ≥201 trên tập test theo ngưỡng kích hoạt dự báo; điểm mở = ngưỡng 201 (định nghĩa ngày nặng), "
           "điểm đặc = ngưỡng chọn trên các lần validation của train (quy tắc F2, không chọn trên test); đường chấm ngang = tỷ lệ ngày nặng 0,20 (precision của đoán bừa). "
           + SRC % "model_04_precision_recall.png"),
 "model_05_humidity_recheck": ("Hình 20. Kiểm tra lại liên hệ độ ẩm–AQI theo hai giai đoạn train (06/2017–06/2019) và test (07/2019–02/2020): tỷ lệ ngày AQI ≥201 theo tertile "
           "độ ẩm tính trong từng giai đoạn; chỉ vẽ thành phố có ≥30 ngày nặng ở cả hai giai đoạn; n = 7.757 cặp, 14/06/2017–29/02/2020. " + SRC % "model_05_humidity_recheck.png"),
}

NOTE = {
 "overview": ("[CHỜ NGUỒN ẢNH ỨNG DỤNG — ẢNH TỔNG QUAN SẢN PHẨM] Vị trí này cần ảnh chụp thực tế tệp HTML "
   "Canh_bao_o_nhiem_truoc_mot_ngay_Pro_v5.html do nhóm cung cấp và phải được mô tả là phát lại kết quả trên dữ liệu lịch sử. "
   "Tại thời điểm dàn trang, tệp chưa có trong kho Git được xác nhận (HTung0511/Air_Project_Test, commit c4c75f6) lẫn Drive, nên chưa chèn ảnh; "
   "không thay bằng ảnh mô phỏng hay ảnh tạo bằng AI. Khi có tệp: chụp màn hình thấy rõ vùng chọn thành phố, ngày và kết quả, chèn tại đây; "
   "nếu trùng nội dung với ảnh tổng quan ở §3.4 thì chỉ giữ một ảnh và dẫn chiếu sang ảnh còn lại."),
 "dup_clean": ("Hình mức thiếu còn lại của tám thành phố sau làm sạch đã được chèn MỘT lần tại §2.2.8 (Hình 2) kèm hình mẫu hình thiếu trước xử lý (Hình 3); "
   "xem dẫn chiếu tại đó. Không lặp lại hình ở đây để tránh tăng số trang; các số liệu tương ứng đã có trong Bảng 3."),
 "app_block": ("[CHỜ NGUỒN ẢNH ỨNG DỤNG — 4 KHUNG HÌNH CỦA §3.4] Cần ảnh chụp thực tế tệp HTML Canh_bao_o_nhiem_truoc_mot_ngay_Pro_v5.html (phát lại lịch sử), gồm: "
   "(a) màn hình tổng quan ứng dụng; (b) ví dụ Delhi 24/01/2020 thấy dự báo, thực tế và hai ngưỡng; (c) đồ thị toàn kỳ và thanh kéo ngưỡng; "
   "(d) màn hình mẫu ít hoặc thông báo giới hạn. Tệp chưa có trong kho Git được xác nhận (commit c4c75f6) lẫn Drive tại thời điểm dàn trang; không dùng ảnh mô phỏng/AI. "
   "Không đặt ảnh ở hai ngưỡng khác nhau rồi so như hai mô hình độc lập; ảnh (c) phải ghi rõ 1.947 là tổng số cặp toàn test, không phải chiều dài ngày lịch của mỗi đường."),
}

MARK = [  # (key, S, E, kind, payload)
 ("overview", 10705, 10989, "note", NOTE["overview"]),
 ("so_do", 12787, 13135, "fig", "so_do"),
 ("missing_after_cleaning_8cities", 23625, 23955, "fig", "missing_after_cleaning_8cities"),
 ("missing_pattern_lucknow_jaipur", 23625, 23955, "fig2", "missing_pattern_lucknow_jaipur"),
 ("fill_strategies_lucknow_jaipur", 23956, 24187, "fig", "fill_strategies_lucknow_jaipur"),
 ("outliers_pm25_lucknow_jaipur", 23956, 24187, "fig2", "outliers_pm25_lucknow_jaipur"),
 ("dup_clean", 43629, 43895, "note", NOTE["dup_clean"]),
 ("eda_00_sample_size", 46386, 46581, "fig", "eda_00_sample_size"),
 ("eda_01_poor_share_city", 46582, 46751, "fig", "eda_01_poor_share_city"),
 ("eda_05_aqi_distribution", 46752, 46937, "fig", "eda_05_aqi_distribution"),
 ("eda_02_heatmap_city_month", 49144, 49376, "fig", "eda_02_heatmap_city_month"),
 ("eda_03_trend_city_year", 49377, 49558, "fig", "eda_03_trend_city_year"),
 ("eda_04_pm25_aqi", 51670, 51846, "fig", "eda_04_pm25_aqi"),
 ("corr_01_raw_vs_adjusted", 54678, 54864, "fig", "corr_01_raw_vs_adjusted"),
 ("corr_02_hypothesis_tests", 54865, 55077, "fig", "corr_02_hypothesis_tests"),
 ("corr_03_humidity_deciles", 55078, 55371, "fig", "corr_03_humidity_deciles"),
 ("corr_04_poor_share_by_humidity", 55078, 55371, "fig2", "corr_04_poor_share_by_humidity"),
 ("model_01_residual_diagnostics", 61492, 61691, "fig", "model_01_residual_diagnostics"),
 ("model_02_mae_by_model", 61692, 61877, "fig", "model_02_mae_by_model"),
 ("model_03_mae_by_city", 61878, 62104, "fig", "model_03_mae_by_city"),
 ("model_04_precision_recall", 62105, 62286, "fig", "model_04_precision_recall"),
 ("model_05_humidity_recheck", 62287, 62472, "fig", "model_05_humidity_recheck"),
 ("app16", 67932, 68192, "note", NOTE["app_block"]),
 ("app17", 68193, 68376, "del", None),
 ("app18", 68377, 68573, "del", None),
 ("app19", 68574, 68720, "del", None),
]

D = 0
chunks, cur, cur_keys = [], [], []
for key, S, E, kind, payload in MARK:
    span = E - S
    if kind in ("fig", "note", "del"):
        s = S + D
        reqs = [{"deleteContentRange": {"range": {"startIndex": s, "endIndex": s + span}}}]
        D -= span
    else:  # fig2: hình thứ hai của cùng một chỉ dẫn — chèn tiếp sau chú thích hình trước, không xóa lại
        reqs = []
        s = S + D
    if kind in ("fig", "fig2"):
        name = payload
        h = round(W / ASPECT[name], 1)
        reqs.append({"insertInlineImage": {"location": {"index": s},
                     "uri": URI[name],
                     "objectSize": {"width": {"magnitude": W, "unit": "PT"},
                                    "height": {"magnitude": h, "unit": "PT"}}}})
        D += 1
        cap = CAP[name]
        reqs.append({"insertText": {"location": {"index": s + 1}, "text": "\n" + cap}})
        D += 1 + len(cap)
        c0, c1 = s + 2, s + 2 + len(cap)
        reqs.append({"updateTextStyle": {"range": {"startIndex": c0, "endIndex": c1},
                     "textStyle": {"italic": True, "fontSize": {"magnitude": 9, "unit": "PT"}},
                     "fields": "italic,fontSize"}})
        reqs.append({"updateParagraphStyle": {"range": {"startIndex": s, "endIndex": s + 2},
                     "paragraphStyle": {"alignment": "CENTER"}, "fields": "alignment"}})
        reqs.append({"updateParagraphStyle": {"range": {"startIndex": c0, "endIndex": c1 + 1},
                     "paragraphStyle": {"alignment": "CENTER",
                                        "spaceAbove": {"magnitude": 4, "unit": "PT"},
                                        "spaceBelow": {"magnitude": 10, "unit": "PT"}},
                     "fields": "alignment,spaceAbove,spaceBelow"}})
    elif kind == "note":
        reqs.append({"insertText": {"location": {"index": s}, "text": payload}})
        D += len(payload)
        reqs.append({"updateTextStyle": {"range": {"startIndex": s, "endIndex": s + len(payload)},
                     "textStyle": {"italic": True, "fontSize": {"magnitude": 9.5, "unit": "PT"},
                                   "foregroundColor": {"color": {"rgbColor": {"red": 0.55, "green": 0.15, "blue": 0.10}}}},
                     "fields": "italic,fontSize,foregroundColor"}})
    cur += reqs
    cur_keys.append(key)
    if len(cur_keys) >= 4:
        chunks.append((list(cur_keys), cur))
        cur, cur_keys = [], []
if cur:
    chunks.append((list(cur_keys), cur))

for i, (keys, reqs) in enumerate(chunks, 1):
    print(f"===== CHUNK {i}: {keys} ({len(reqs)} requests) =====")
    print(json.dumps(reqs, ensure_ascii=False))
print("FINAL DELTA D =", D)
