# -*- coding: utf-8 -*-
"""Sinh payload chèn 3 bảng native (từ điển biến, bảng ghép, bảng tỷ số) vào bản dàn trang.

Nguyên tắc: chỉ dùng số/mô tả đã có trong bản thảo, Data_dictionary.md và dữ liệu nguồn
(đã đối chiếu trực tiếp header + số dòng của 3 tệp CSV trong data/processed/).
Không tự điền đơn vị chưa đối chiếu; không thêm khoảng tin cậy chưa rõ loại.
"""
import json

DOC = "1vxuomPCYI7acP9ZBFy7miLHwqLAK652Oc4lDjUliBIA"

# ---------------------------------------------------------------- Bảng 2 (từ điển biến)
TITLE_A = ("Bảng 2. Từ điển biến thiết yếu của bảng phân tích: khóa, nồng độ, kết quả, "
           "thời tiết và cờ chất lượng")
NOTE_A = ("Đơn vị chép đúng theo Data_dictionary.md (mục 1 cho nồng độ, mục 3 cho thời tiết); "
          "dấu * có trong tệp nguồn nhưng không kèm chú giải, cần nhóm xác nhận trước khi nộp, "
          "không tự quy đổi đơn vị. Bảng chỉ giữ biến và nhóm biến thiết yếu cho các phân tích ở "
          "Phần 2 và Phần 3; danh sách đầy đủ 40 cột của air_quality_8cities.csv, 14 cột thời tiết "
          "và danh sách tệp nguồn xem Phụ lục A và Data_dictionary.md. Các cờ chất lượng là dấu vết "
          "xử lý, không phải số đo môi trường mới và không phải nhãn nguyên nhân đã kiểm chứng.")
DATA_A = [
    ["Tên biến / nhóm biến", "Ý nghĩa", "Đơn vị", "Vai trò trong nghiên cứu", "Lưu ý chất lượng"],
    ["City, Date", "Khóa thành phố–ngày của mỗi dòng", "text; ngày (YYYY-MM-DD)",
     "Khóa ghép hai nguồn; khung thời gian của chuỗi",
     "Tám thành phố, không đại diện cho toàn Ấn Độ; độ dài chuỗi khác nhau (Delhi, Bengaluru, Chennai, Lucknow từ 01/2015; Gurugram từ 11/2015; Amritsar từ 02/2017; Jaipur từ 06/2017)"],
    ["AQI", "Chỉ số chất lượng không khí tổng hợp, tính từ các chất thành phần theo thang CPCB",
     "— (chỉ số, không thứ nguyên)", "Biến mục tiêu của phân tích hồi cứu và của bài toán dự báo",
     "Lấy từ dữ liệu gốc, không nội suy; thiếu 15,9% ở dữ liệu gốc"],
    ["AQI_Bucket", "Nhãn phân loại mức AQI: Good, Satisfactory, Moderate, Poor, Very Poor, Severe",
     "text (nhãn)", "Xác định ngày nặng (Poor trở lên, AQI ≥201)",
     "Không nội suy; nhãn khớp thang CPCB"],
    ["PM2.5", "Bụi mịn đường kính ≤2,5 micromet", "µg/m³ *",
     "Biến giải thích chính; đầu vào của các mức đặc trưng mô hình",
     "Nội suy theo thời gian chỉ cho khoảng thiếu ≤14 ngày; điểm nghi lỗi cảm biến đặt NaN, không nội suy"],
    ["PM10", "Bụi đường kính ≤10 micromet", "µg/m³ *", "Biến giải thích",
     "Không dùng làm biến ở Lucknow (thiếu 100%) và Chennai (84,5%); có cờ kiểm tra logic PM2.5 > 1,2 × PM10"],
    ["NO, NO2, NH3, SO2, O3, Benzene, Toluene", "Nồng độ từng chất khí và hợp chất hữu cơ dễ bay hơi",
     "µg/m³ *", "Biến giải thích theo chất; so sánh tương quan với AQI",
     "NH3 không dùng làm biến ở Gurugram (thiếu 92,9%); đã bỏ Xylene (thiếu 61,3% ở dữ liệu gốc); giữ nguyên đơn vị gốc, chưa scale/encode"],
    ["NOx", "Tổng hợp các oxit nitơ", "ppb *", "Biến giải thích",
     "Khác đơn vị với nhóm µg/m³ nên không so sánh độ lớn trực tiếp giữa các chất"],
    ["CO", "Carbon monoxide", "mg/m³ *", "Biến giải thích",
     "Khác đơn vị nên không xếp hạng nồng độ chéo giữa các chất"],
    ["temp_mean, temp_min, temp_max, humidity_mean, pressure_mean",
     "Nhiệt độ không khí ở độ cao 2 m (trung bình, thấp nhất, cao nhất ngày), độ ẩm tương đối 2 m và áp suất bề mặt",
     "°C; %; hPa", "Biến bối cảnh và biến của các giả thuyết thời tiết (§3.2.4, §3.3)",
     "Dữ liệu mô hình ERA5 trên ô lưới 0,25°, không phải số đo tại trạm; áp suất phụ thuộc độ cao (Bengaluru thấp hơn các thành phố khác)"],
    ["wind_speed_mean, wind_speed_max, wind_u, wind_v, wind_dir_8",
     "Tốc độ gió ở 10 m (trung bình ngày, giá trị giờ lớn nhất), hai thành phần vector gió và hướng gió chính trong ngày",
     "m/s; wind_dir_8 là nhãn text 8 hướng", "Biến của giả thuyết khuếch tán và vận chuyển",
     "Hướng gió là đại lượng góc vòng tròn: dùng wind_u, wind_v làm biến số, wind_dir_8 chỉ để mô tả"],
    ["precip_sum, rain_day", "Tổng lượng mưa trong ngày và cờ ngày có mưa",
     "mm; bool (rain_day = True khi precip_sum ≥ 1 mm)", "Biến của giả thuyết rửa trôi",
     "precip_sum lệch phải rất mạnh (phần lớn ngày gần 0): dùng Spearman hoặc log1p khi tính tương quan, hồi quy"],
    ["blh_mean, blh_min", "Chiều cao lớp biên khí quyển trung bình ngày và thấp nhất trong ngày", "m",
     "Biến của giả thuyết nén và khuếch tán chất ô nhiễm",
     "Giá trị thấp nghĩa là chất ô nhiễm bị nén sát mặt đất; chưa scale, chưa tạo biến trễ"],
    ["<cột>_was_missing (12 cột), <cột>_is_outlier (11 cột)",
     "Cờ ô thiếu ở dữ liệu gốc hoặc chuỗi số 0 treo (flatline ≥3 ngày) đã chuyển thành NaN; cờ giá trị vượt IQR × 1,5 tính riêng theo tháng dương lịch",
     "bool", "Truy vết xử lý; phân biệt giá trị nội suy với giá trị bị đánh dấu ngoại lai",
     "Không phải số đo môi trường mới; is_outlier chỉ đánh dấu, không sửa hay xóa giá trị; không áp dụng cho AQI"],
    ["pm25_gt_pm10_flag, suspect_sensor_error",
     "Cờ kiểm tra logic PM2.5 > 1,2 × PM10 và cờ ngày bị nghi lỗi cảm biến", "bool",
     "Truy vết chất lượng; xác định 24 ngày nghi lỗi (41 ô)",
     "Chỉ đánh dấu; gọi là nghi lỗi vì chưa đối chiếu được với nguồn CPCB; không phải nhãn nguyên nhân"],
]

# ---------------------------------------------------------------- Bảng 5 (ghép dữ liệu)
TITLE_B = ("Bảng 5. Số dòng và số cột của hai nguồn dữ liệu và của bảng ghép "
           "(đọc riêng hai chiều, không phải phép cộng số dòng)")
NOTE_B = ("Đọc theo hai chiều riêng: 14.056 dòng của bảng ghép bằng số dòng của nguồn không khí vì "
          "phép ghép trái giữ phạm vi nguồn chính, không phải 14.056 + 16.128 dòng; các dòng thời tiết "
          "nằm ngoài phạm vi ngày của nguồn không khí không làm tăng kích thước bảng phân tích. "
          "54 cột = 40 cột không khí giữ nguyên + 14 cột thời tiết thêm vào; số cột không suy ra từ số dòng. "
          "Số dòng và số cột đối chiếu trực tiếp trên tệp CSV của phiên bản nhóm nộp "
          "(không tính dòng tiêu đề). Số dòng thời tiết 16.128 = 8 thành phố × 2.016 ngày.")
DATA_B = [
    ["Tệp / bước", "Số dòng", "Số cột", "Ghi chú"],
    ["data/processed/air_quality_8cities.csv — nguồn không khí tám thành phố sau làm sạch",
     "14.056", "40",
     "Mỗi dòng là một cặp City–Date, không trùng khóa; 40 cột gồm khóa, 11 nồng độ, AQI/AQI_Bucket và các cờ chất lượng"],
    ["data/processed/weather_daily_8cities.csv — nguồn thời tiết theo ngày",
     "16.128", "16",
     "8 thành phố × 2.016 ngày; có thêm các ngày từ 25/12/2014 để tạo biến trễ về sau; phạm vi ngày rộng hơn nguồn không khí; không có giá trị thiếu"],
    ["data/processed/air_quality_8cities_weather.csv — bảng ghép dùng cho phân tích",
     "14.056", "54",
     "Ghép trái theo City–Date: giữ nguyên 40 cột của nguồn không khí và thêm 14 cột thời tiết; 0 dòng thiếu thời tiết sau ghép"],
]

# ---------------------------------------------------------------- Bảng 7 (tỷ số)
TITLE_C = ("Bảng 7. Hai cách tổng hợp tỷ số PM2.5 giữa ngày AQI ≥201 và ngày còn lại "
           "(không phải tỷ số mùa)")
NOTE_C = ("Hai dòng trả lời hai cách tổng hợp khác nhau — trung vị của các tỷ số theo thành phố so với "
          "tỷ số của các trung vị gộp — nên không thay thế nhau và không phải hai lần tính lại cùng một "
          "đại lượng; nhãn phải đặt ngay cạnh số khi trình bày. Cả hai đều so nhóm ngày AQI ≥201 với nhóm "
          "ngày còn lại, không so mùa đông với mùa mưa. Hình 11 (eda_04_pm25_aqi.png) có hiển thị khoảng "
          "[2,42; 3,17] cạnh giá trị 2,82 nhưng không ghi loại khoảng, và §3.2.3 không nêu khoảng này, nên "
          "bảng chưa đưa khoảng đó vào: cần nhóm xác nhận loại khoảng (tin cậy hay phân vị) trước khi bổ sung. "
          "Nguồn số: §3.2.3 của báo cáo; đơn vị PM2.5 là µg/m³ nên tỷ số không thứ nguyên.")
DATA_C = [
    ["Chỉ tiêu", "Giá trị", "Cách tính", "Phạm vi và cỡ mẫu", "Lưu ý khi đọc"],
    ["Trung vị tỷ số PM2.5 theo từng thành phố đủ điều kiện", "2,82",
     "Tính tỷ số PM2.5 giữa nhóm ngày AQI ≥201 và nhóm ngày còn lại riêng cho từng thành phố, rồi lấy trung vị của các tỷ số đó",
     "5 thành phố đủ điều kiện (mỗi thành phố có ≥100 ngày AQI ≥201); khoảng chung 14/06/2017–01/07/2020",
     "“Năm thành phố” nghĩa là 5 thành phố, không phải phân tích theo năm lịch; tỷ số không thứ nguyên"],
    ["Tỷ số từ trung vị gộp của tám thành phố", "≈3,26 (= 137,1 / 42,0)",
     "Lấy trung vị PM2.5 gộp tám thành phố của nhóm ngày AQI ≥201 (137,1 µg/m³) chia cho trung vị gộp của nhóm ngày còn lại (42,0 µg/m³)",
     "Tám thành phố; cùng khoảng chung 14/06/2017–01/07/2020",
     "Gộp trước rồi mới lập tỷ số, khác với dòng trên; không diễn giải thành tỷ số giữa hai mùa"],
]

TABLES = [("A", 18068, 243, TITLE_A, NOTE_A, DATA_A),
          ("B", 45334, 218, TITLE_B, NOTE_B, DATA_B),
          ("C", 54197, 274, TITLE_C, NOTE_C, DATA_C)]


def text_batch(key, start, mlen, title, note):
    """delete marker -> chèn tiêu đề bảng -> chèn ghi chú (bảng sẽ chèn giữa hai khối)."""
    reqs = [
        {"deleteContentRange": {"range": {"startIndex": start, "endIndex": start + mlen}}},
        {"insertText": {"location": {"index": start}, "text": title}},
    ]
    note_at = start + len(title) + 1
    reqs.append({"insertText": {"location": {"index": note_at}, "text": note}})
    reqs.append({"updateTextStyle": {
        "range": {"startIndex": note_at, "endIndex": note_at + len(note)},
        "textStyle": {"italic": True, "fontSize": {"magnitude": 8.5, "unit": "PT"}},
        "fields": "italic,fontSize"}})
    reqs.append({"updateTextStyle": {
        "range": {"startIndex": start, "endIndex": start + len(title)},
        "textStyle": {"bold": True, "fontSize": {"magnitude": 10, "unit": "PT"}},
        "fields": "bold,fontSize"}})
    reqs.append({"updateParagraphStyle": {
        "range": {"startIndex": start, "endIndex": start + len(title) + 1},
        "paragraphStyle": {"alignment": "START", "spaceAbove": {"magnitude": 8, "unit": "PT"},
                           "spaceBelow": {"magnitude": 4, "unit": "PT"}, "keepWithNext": True},
        "fields": "alignment,spaceAbove,spaceBelow,keepWithNext"}})
    reqs.append({"updateParagraphStyle": {
        "range": {"startIndex": note_at, "endIndex": note_at + len(note) + 1},
        "paragraphStyle": {"alignment": "START", "spaceAbove": {"magnitude": 3, "unit": "PT"},
                           "spaceBelow": {"magnitude": 8, "unit": "PT"}},
        "fields": "alignment,spaceAbove,spaceBelow"}})
    return {"document_id": DOC, "requests": reqs}, note_at


if __name__ == "__main__":
    out = {}
    for key, start, mlen, title, note, data in TABLES:
        payload, table_index = text_batch(key, start, mlen, title, note)
        out[key] = {"text_batch": payload, "table_index": table_index,
                    "rows": len(data), "cols": len(data[0]), "table_data": data,
                    "title_len": len(title), "note_len": len(note)}
        print(f"# === {key}: marker [{start},{start+mlen}) | title_len={len(title)} | "
              f"note_len={len(note)} | TABLE_INDEX={table_index} | {len(data)}x{len(data[0])}")
        print(json.dumps(payload, ensure_ascii=False))
        print()
    json.dump(out, open("/home/user/Air_Project_Test/deliverables/layout_assets/tables_payload.json",
                        "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("saved tables_payload.json")
