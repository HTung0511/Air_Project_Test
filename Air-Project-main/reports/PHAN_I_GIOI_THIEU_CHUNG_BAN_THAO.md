# BÁO CÁO MÔN HỌC KHOA HỌC DỮ LIỆU

**Tên đề tài:** Phân tích ô nhiễm không khí theo thời gian tại tám thành phố ở Ấn Độ

**Học phần:** Khoa học dữ liệu — Mã học phần: [Cần bổ sung]  
**Lớp:** [Cần bổ sung]  
**Giảng viên hướng dẫn:** [Cần bổ sung]  
**Nhóm thực hiện:** [Cần bổ sung — 4 thành viên, theo Metadata.json: Dương Minh Tuấn, Trần Hoàng Tùng, Phạm Tuấn Mạnh, Lưu Văn Lịch; cần đối chiếu danh sách nộp chính thức]  
**Thời gian thực hiện:** [Cần bổ sung]  
**Repository nộp chính thức:** [Cần bổ sung — đối chiếu URL Git nhóm] — *Bản hiện tại là bản sao thử nghiệm (Test) cá nhân được clone từ repository nhóm, dùng để hoàn thiện báo cáo; không mô tả các bản sửa chỉ có ở Test như chức năng đã triển khai của nhóm.*

> **Căn cứ biên soạn Phần I:** (1) PDF rubric/matrice nội dung kiểm tra học phần Khoa học dữ liệu (trang 6–7: yêu cầu Phần 1 Giới thiệu chung); (2) `GOI_BO_SUNG_BAO_CAO.md` trên `main` — ghi chú diễn giải và hạn chế; (3) `Data_dictionary.md`, `Metadata.json`, `reports/cleaning_log_8cities.md` và `reports/cleaning_summary_8cities.csv` — căn cứ số liệu và phương pháp thực tế; (4) `Canh_bao_o_nhiem_truoc_mot_ngay_Pro_v5.html` — sản phẩm minh họa/phát lại kết quả trên dữ liệu lịch sử. Slide giữa kỳ và mẫu báo cáo TTNT chỉ tham khảo hình thức, không thay thế bảng nguồn.

---

## MỞ ĐẦU

Báo cáo này trình bày kết quả đồ án môn Khoa học dữ liệu với đề tài **Phân tích ô nhiễm không khí theo thời gian tại tám thành phố ở Ấn Độ**. Dữ liệu chính là chuỗi quan trắc theo ngày từ Central Pollution Control Board (CPCB) Ấn Độ, được chia sẻ lại qua Kaggle (`city_day.csv`, 01/01/2015–01/07/2020), kết hợp nguồn thứ hai là dữ liệu thời tiết tái phân tích ERA5 qua Open-Meteo Historical Weather API (25/12/2014–01/07/2020, theo giờ, gộp theo ngày). Trên 8 thành phố được lựa chọn, báo cáo thực hiện trọn vòng đời khoa học dữ liệu: thu thập và tiền xử lý, phân tích khám phá (EDA) và trực quan hóa — gồm Data Storytelling — mô hình hóa và đánh giá, cùng thảo luận về đạo đức dữ liệu và sử dụng kết quả có trách nhiệm.

Trọng tâm của báo cáo là **phân tích mô tả theo thời gian**: ô nhiễm nặng ở đâu, khi nào và do chất nào, với thời tiết được xem xét như một nhóm biến giải thích có liên quan (không đưa thời tiết vào tên đề tài theo thống nhất). Bài toán **dự báo chỉ số chất lượng không khí (AQI) ngày kế tiếp** được đặt ở vị trí **phần mở rộng**, phục vụ minh họa khả năng vận dụng mô hình vào kịch bản cảnh báo, không lấn át trọng tâm phân tích.

Báo cáo được tổ chức theo đúng cấu trúc đã chốt, đối chiếu rubric học phần (Phần 1: Tổng quan & Đặt bài toán; Phần 2: Thu thập & Tiền xử lý; Phần 3: EDA, Trực quan & Mô hình hóa; Phần 4: Đạo đức dữ liệu & Báo cáo). **Phần II** tập trung giải thích phương pháp; **Phần III** trình bày kết quả, tránh lặp lại. Các số liệu, ngưỡng và hạn chế được trích từ `cleaning_log_8cities.md`, `Data_dictionary.md` và `Metadata.json`; những nội dung chưa có bảng nguồn được đánh dấu `[Cần bổ sung]` thay vì suy đoán.

Sản phẩm đi kèm là tệp HTML `Canh_bao_o_nhiem_truoc_mot_ngay_Pro_v5.html` — được gọi thống nhất trong báo cáo là **ứng dụng minh họa/phát lại kết quả trên dữ liệu lịch sử** (giai đoạn kiểm thử 01/07/2019–29/02/2020), chưa khẳng định dự báo trực tuyến vận hành. Các cải tiến đề xuất trên bản sao thử nghiệm (ví dụ: quy trình đọc cache, đường dựng đặc trưng) là hướng phát triển, chưa phải chức năng đã nghiệm thu của bản nộp chính thức.

---

## PHẦN I. GIỚI THIỆU CHUNG

### 1.1. Lý do chọn đề tài

Ô nhiễm không khí là vấn đề môi trường — sức khỏe cộng đồng có tính thời sự cao, đặc biệt tại các đô thị có mật độ dân cư lớn và hoạt động giao thông, công nghiệp, đốt phụ phẩm nông nghiệp diễn ra theo mùa. Ấn Độ là quốc gia có hệ thống quan trắc quốc gia do CPCB vận hành, với dữ liệu theo ngày được công bố và chia sẻ lại trên Kaggle (bộ `Air Quality Data in India`, 2015–2020). Sự sẵn có của chuỗi thời gian dài, đa thành phố, đa chất ô nhiễm, cùng khả năng bổ sung biến thời tiết từ nguồn mở ERA5/Open-Meteo, tạo điều kiện thuận lợi để thực hành trọn vòng đời khoa học dữ liệu: từ làm sạch dữ liệu khuyết và nhiễu cảm biến, đến EDA theo không gian–thời gian–thành phần chất, phân tích tương quan có kiểm soát mùa vụ, và thử nghiệm mô hình dự báo ngắn hạn.

Về mặt học thuật, đề tài cho phép vận dụng đồng thời các kỹ thuật cốt lõi của học phần: xử lý dữ liệu khuyết theo khối thời gian, phát hiện ngoại lai theo tháng, trực quan hóa chuỗi thời gian và phân bố, kỹ thuật đặc trưng trễ (lag) và biến mùa vụ, mô hình hồi quy có chuẩn hóa (Ridge) so sánh với các baseline quán tính, cùng đánh giá bằng bootstrap theo khối thời gian. Về mặt thực tiễn, việc hiểu “ở đâu — khi nào — do chất nào” và mối liên quan giữa điều kiện khí tượng (gió, mưa, độ ẩm, chiều cao lớp biên khí quyển) với AQI có ý nghĩa tham khảo cho truyền thông nguy cơ và lập kế hoạch phân tích hồi cứu, dù báo cáo không nhằm thay thế hệ thống cảnh báo nghiệp vụ.

Lựa chọn tám thành phố — **Delhi, Gurugram, Lucknow, Jaipur, Bengaluru, Amritsar, Chennai, Hyderabad** — được thực hiện theo tiêu chí của nhóm: **khoảng thời gian quan sát tương đối đồng nhất và độ phủ dữ liệu AQI tương đối đầy đủ hơn các phương án khác được cân nhắc, phục vụ khả năng so sánh trong bộ dữ liệu** (`GOI_BO_SUNG_BAO_CAO.md` §1; `Metadata.json` §selected_cities_for_deep_analysis). Đây là **lựa chọn phục vụ so sánh nội bộ bộ dữ liệu, không phải bằng chứng rằng tám thành phố đại diện cho toàn bộ Ấn Độ hay là tám thành phố ô nhiễm nhất**; báo cáo không suy diễn vượt quá phạm vi mẫu.

Cuối cùng, việc bổ sung thời tiết như một hợp phần phân tích — dù không đưa vào tên đề tài — phản ánh bản chất liên ngành của bài toán chất lượng không khí: nồng độ chất ô nhiễm không chỉ do phát thải mà còn chịu ảnh hưởng của điều kiện khuếch tán và rửa trôi khí quyển, cần được xem xét thận trọng, có kiểm soát yếu tố mùa vụ và không suy diễn nhân quả vượt quá dữ liệu quan sát.

### 1.2. Mục tiêu nghiên cứu và câu hỏi phân tích

**Mục tiêu chung** là mô tả, so sánh và diễn giải có kiểm chứng thực trạng ô nhiễm không khí theo thời gian tại tám thành phố nêu trên, trên cơ sở dữ liệu CPCB đã được làm sạch thống nhất, có bổ sung biến thời tiết ERA5 để phân tích liên quan và thử nghiệm mở rộng dự báo AQI ngày kế tiếp ở mức minh họa.

**Mục tiêu cụ thể:**

1. **Chuẩn hóa dữ liệu phục vụ phân tích hồi cứu:** xây dựng pipeline làm sạch thống nhất cho 8 thành phố (xử lý chuỗi số 0 treo ≥3 ngày, nội suy tuyến tính chỉ cho khoảng thiếu ≤14 ngày, không nội suy AQI, đánh dấu ngoại lai IQR theo tháng và điểm nghi lỗi cảm biến), giữ nguyên số dòng (14.056 dòng) và lưu vết bằng các cờ `_was_missing`, `_is_outlier` để truy vết.
2. **Trả lời ba câu hỏi mô tả cốt lõi bằng EDA có kiểm tra độ nhạy:** (a) Ô nhiễm nặng tập trung ở đâu? (b) Khi nào trong năm/chu kỳ quan sát? (c) Do chất nào đóng góp chính vào AQI? Mỗi phát hiện gắn với biểu đồ có tiêu đề kết luận, nguồn và cỡ mẫu.
3. **Phân tích mối liên quan thời tiết–AQI có kiểm soát mùa vụ:** so sánh tương quan thô với tương quan sau khi khử chu kỳ mùa (dùng anomaly theo trung vị City×Month), kiểm định theo nhóm giả thuyết đã nêu trước với hiệu chỉnh đa kiểm định (Bonferroni/FDR), diễn giải theo từng thành phố và không suy diễn nhân quả.
4. **Thử nghiệm mở rộng dự báo AQI ngày mai ở mức minh họa:** bài toán hồi quy (MAE, R²) và bài toán cảnh báo nhị phân (AQI ≥201, Precision/Recall), huấn luyện Ridge trên log(AQI) với đặc trưng lịch sử AQI, nồng độ chất hôm nay và thời tiết đến hết hôm nay; so sánh với 3 baseline (trong đó có persistence — sao chép AQI hôm nay), chia tập theo thời gian, chẩn đoán phần dư và bootstrap theo khối 14 ngày.

**Câu hỏi phân tích** được phát biểu tường minh để dẫn dắt Phần II–III:

- **CQ1 (Không gian):** Trong khoảng chung 14/06/2017–01/07/2020, mức độ và tần suất ngày ô nhiễm nặng (AQI ≥201, ngưỡng Poor theo thang CPCB) phân bố như thế nào giữa 8 thành phố? Thứ hạng có vững khi thay đổi cách tổng hợp hay khi loại giai đoạn phong tỏa COVID-19?
- **CQ2 (Thời gian):** Biến động theo tháng/mùa và theo năm có hình thái gì? Tỷ số mùa (ví dụ: mùa ô nhiễm cao so với mùa mưa) khác nhau ra sao giữa các thành phố, và cần lưu ý gì khi diễn giải trung vị tỷ số trên 5 thành phố so với tỷ số gộp 8 thành phố?
- **CQ3 (Thành phần):** Chất ô nhiễm nào có tương quan mạnh nhất với AQI, và mối quan hệ PM2.5–AQI (Spearman ≈0,91 trong EDA) cần được diễn giải như thế nào khi AQI được tính theo nguyên tắc max chỉ số con?
- **CQ4 (Thời tiết):** Sau khi khử mùa vụ, các biến gió, mưa, độ ẩm, áp suất, chiều cao lớp biên (BLH) còn “đi cùng” với AQI ngày hôm sau ở mức nào? Ba giả thuyết nêu trước (gió yếu/BLH thấp/không mưa đi cùng AQI cao) được ủng hộ ở bao nhiêu kiểm định sau hiệu chỉnh?
- **CQ5 (Dự báo — mở rộng):** Với đặc trưng chỉ đến hết hôm nay, mô hình Ridge cải thiện MAE và Precision/Recall cho cảnh báo ≥201 ra sao so với baseline? Việc bổ sung thời tiết đóng góp bao nhiêu, và kịch bản “dùng thời tiết ngày mai” chỉ nên được gọi là **cận trên (dự báo hoàn hảo)**?

Về **dạng bài toán**, báo cáo thực hiện: (i) phân tích mô tả và trực quan hóa; (ii) phân tích tương quan có kiểm định; (iii) hồi quy dự báo AQI (biến liên tục) và (iv) phân loại nhị phân cho cảnh báo AQI ≥201 (đánh giá bằng Precision/Recall, ngưỡng vận hành được chọn trên tập huấn luyện).

### 1.3. Phạm vi thực hiện

**Phạm vi không gian và thời gian:**

- Không gian: 8 thành phố nêu trên. Mỗi thành phố là trung bình các trạm trong địa giới hành chính theo dữ liệu CPCB; không có dữ liệu cấp trạm riêng lẻ.
- Thời gian: nguồn gốc 01/01/2015–01/07/2020, nhưng **độ dài chuỗi khác nhau giữa các thành phố**: Delhi, Bengaluru, Chennai, Lucknow từ 01/2015; Gurugram từ 27/11/2015; Amritsar từ 27/02/2017; Jaipur từ 14/06/2017 (`Data_dictionary.md` §2). Để so sánh giữa các thành phố, báo cáo sử dụng **khoảng chung 14/06/2017–01/07/2020**; khi so sánh theo năm, chỉ dùng tháng 1–6 nhằm tránh lệch mùa và loại nửa cuối 2020 có phong tỏa COVID-19 (theo `CHECKLIST_KIEM_CHUNG.md` CK-5.6). Dữ liệu kết thúc 01/07/2020 nên có chứa giai đoạn phong tỏa — được ghi nhận như một yếu tố nhiễu cần thận trọng khi diễn giải xu hướng.

**Phạm vi dữ liệu và biến:**

- Dữ liệu chính: `city_day.csv` (Kaggle/rohanrao/air-quality-data-in-india, nguồn gốc CPCB), 29.531 dòng, 26 thành phố; sau khi chọn 8 thành phố còn **14.056 dòng** (mỗi dòng là một cặp City–Date, không trùng khóa, không đứt ngày trong chuỗi mỗi thành phố). 16 cột gốc gồm 11 chất (PM2.5, PM10, NO, NO2, NOx, NH3, CO, SO2, O3, Benzene, Toluene; Xylene đã bỏ), AQI và AQI_Bucket.
- Dữ liệu thứ hai: thời tiết ERA5 qua Open-Meteo, 8 điểm tọa độ trung tâm thành phố, theo giờ, gộp thành ngày với 14 cột: `temp_mean/min/max`, `humidity_mean`, `pressure_mean`, `wind_speed_mean/max`, `wind_u/v`, `wind_dir_8` (mô tả), `precip_sum`, `rain_day`, `blh_mean/min`. **Đây là dữ liệu mô hình trên lưới 0,25° (~25 km), không phải số đo tại trạm**; Delhi và Gurugram ở hai ô lưới sát nhau nên thời tiết theo ngày gần như trùng nhau (tương quan 0,95–0,999, `Data_dictionary.md` §3). Thời tiết không có giá trị thiếu.
- Biến sử dụng: các cột chất có độ thiếu <60% trong thành phố mới được dùng làm biến mô hình; PM10 Lucknow (thiếu 100%), Chennai (84,5%) và NH3 Gurugram (92,9%) không dùng làm biến theo quy ước này. AQI là biến kết quả, **không nội suy**.

**Phạm vi phương pháp:**

- Làm sạch: chuỗi 0 liên tiếp ≥3 ngày → NaN (2.169 ô); nội suy tuyến tính theo thời gian chỉ cho khoảng thiếu ≤14 ngày (3.329 ô), giữ cờ `_was_missing`; khoảng dài hơn giữ NaN; ngoại lai IQR×1,5 theo tháng chỉ đánh dấu; 24 ngày nghi lỗi cảm biến (top 5 PM2.5/AQI mỗi thành phố) → NaN, lưu vết trong `suspect_points_8cities.csv`. Quy tắc nội suy ≤14 ngày là **quy ước thực hành cho phân tích hồi cứu, không phải ngưỡng tối ưu duy nhất**; nội suy có thể làm trơn biến động và ảnh hưởng thống kê đợt ngắn hạn (`GOI_BO_SUNG_BAO_CAO.md` §1).
- EDA: thống kê mô tả, phân bố AQI, tỷ lệ ngày ≥201, heatmap City×Month, xu hướng City×Year, quan hệ PM2.5–AQI, kiểm tra độ nhạy (bootstrap, đổi khoảng chung, bỏ COVID).
- Thời tiết: tương quan Spearman thô vs. khử mùa (anomaly = giá trị − trung vị City×Month), kiểm định 3 giả thuyết nêu trước có hiệu chỉnh Bonferroni/FDR; không suy diễn nhân quả.
- Mô hình: Ridge (chính) trên log(AQI) với 3 mức đặc trưng (L1: lịch sử AQI + mùa; L2: + chất ô nhiễm hôm nay; L3: + thời tiết đến hết hôm nay) so với 3 baseline; L4 (“cận trên: dự báo hoàn hảo” nếu dùng thời tiết ngày mai) chỉ để tham chiếu. Chia tập theo thời gian; scaler/imputer chỉ fit trên train; đánh giá MAE/R² và Precision/Recall cho cảnh báo, kèm chẩn đoán phần dư và bootstrap theo khối 14 ngày.

**Những gì ngoài phạm vi:**

- Không suy diễn nhân quả thời tiết “gây” ô nhiễm; chỉ nói “có liên quan/đi cùng”.
- Không khẳng định dự báo vận hành thời gian thực; mô hình hồi cứu có thể đã sử dụng quan sát xuất hiện sau thời điểm cần dự báo nếu không kiểm soát chặt — do đó HTML chỉ là phát lại trên dữ liệu lịch sử và báo cáo không tuyên bố “chống rò rỉ dữ liệu tuyệt đối”.
- Không thay thế tư vấn y tế hay quyết định quản lý; ngưỡng AQI ≥201 được dùng theo thang CPCB (Poor) cho mục đích phân tích.
- Không tối ưu ngưỡng nội suy/thời tiết mới trong phạm vi báo cáo này; các ngưỡng BA được giữ nguyên và chỉ đề xuất thay đổi khi có thí nghiệm so sánh.

### 1.4. Ý nghĩa và ứng dụng thực tế của sản phẩm

**Ý nghĩa khoa học:** Báo cáo cung cấp một nghiên cứu trường hợp (case study) có thể tái tạo về phân tích ô nhiễm không khí theo thời gian trên dữ liệu mở, minh họa cách xử lý các vấn đề điển hình của dữ liệu quan trắc: thiếu theo khối thời gian, chuỗi 0 treo do cảm biến, ngoại lai theo mùa, và khác biệt độ dài chuỗi giữa các địa phương. Việc tách bạch tương quan thô và tương quan khử mùa, cùng thực hành hiệu chỉnh đa kiểm định, góp phần rèn luyện tư duy phản biện về ý nghĩa thống kê và nguy cơ nhầm lẫn tương quan với nhân quả.

**Ý nghĩa xã hội và giáo dục:** Kết quả EDA giúp người đọc hình dung bức tranh so sánh giữa các thành phố và tính mùa vụ của ô nhiễm, từ đó nâng cao nhận thức về các giai đoạn nguy cơ cao. Ở cấp độ học phần, đồ án đáp ứng rubric về “Complete lifecycle: thu thập, làm sạch, EDA, trực quan hóa và mô hình hóa bằng Python (Pandas, Matplotlib, Seaborn, Scikit-learn)”, đồng thời thực hành Data Storytelling — mỗi phát hiện gắn với một biểu đồ có tiêu đề kết luận, nguồn và cỡ mẫu.

**Ứng dụng minh họa — tệp HTML:** Sản phẩm đi kèm `Canh_bao_o_nhiem_truoc_mot_ngay_Pro_v5.html` là **ứng dụng minh họa/phát lại kết quả trên dữ liệu lịch sử** (giai đoạn kiểm thử 01/07/2019–29/02/2020), cho phép:

- Chọn một cặp (thành phố, ngày) để xem ngữ cảnh hôm nay, mức AQI thực tế ngày mai, và cách mô hình Ridge điều chỉnh dự báo qua ba mức đặc trưng;
- Quan sát toàn cảnh dự báo cả giai đoạn kiểm thử: đường AQI thực tế ngày mai vs. dự báo, cùng các điểm báo đúng/báo nhầm/bỏ sót theo ngưỡng cảnh báo;
- Thử đổi ngưỡng cảnh báo (ví dụ: ngưỡng chuẩn 201 so với ngưỡng ưu tiên không bỏ sót) để cảm nhận đánh đổi Precision–Recall;
- Đọc diễn giải hệ số hồi quy và sai số MAE kèm khoảng tin cậy bootstrap theo khối 14 ngày.

Báo cáo thống nhất cách gọi **“giai đoạn kiểm thử (01/07/2019–29/02/2020)”** thay cho “mùa đông” khi nói về cửa sổ test của mô hình, nhằm tránh nhầm lẫn với định nghĩa mùa khí hậu. Ứng dụng **chưa khẳng định khả năng dự báo trực tuyến** (không dùng API thời tiết trực tiếp, không có đánh giá vận hành ngoài mẫu lịch sử), và **không sử dụng tuyên bố “chống rò rỉ dữ liệu tuyệt đối”**; các hạn chế về rò rỉ tương lai trong khâu nội suy và tạo đặc trưng được trình bày ở Phần III (Những hạn chế).

Về triển khai, **bản chính của nhóm chưa tích hợp các bản sửa đề xuất trên bản sao thử nghiệm** (ví dụ: đọc cache offline, đường dựng đặc trưng từ dữ liệu gốc). Do đó báo cáo không mô tả các bản sửa đó như chức năng đã có; chúng được ghi nhận ở mục Hướng phát triển. Kiểm chứng F01/F02 và PR #4 (Dev) **chưa được merge/nghiệm thu** tại thời điểm khóa báo cáo, nên báo cáo **không tuyên bố đã loại bỏ hoàn toàn leakage** và không trộn số liệu trước sửa với số của ứng viên Dev.

### 1.5. Quy trình thực hiện và phân công nhiệm vụ

**Quy trình khoa học dữ liệu áp dụng** tuân theo vòng đời chuẩn, được cụ thể hóa thành 6 notebook chạy tuần tự trong thư mục `notebooks/` (chi tiết trong `README.md` §4 và `reports/cleaning_log_8cities.md`):

1. **Thu thập dữ liệu:** tải `city_day.csv` từ Kaggle (nguồn gốc CPCB) và dữ liệu thời tiết theo giờ từ Open-Meteo (ERA5) qua `src/weather_utils.py`; lưu bản gốc không chỉnh sửa tại `data/raw/` và `data/raw/weather/*.gz`; ghi provenance trong `Metadata.json` và `Data_dictionary.md`.
2. **Làm sạch và biến đổi:** `01_cleaning.ipynb` + `02_cleaning_evidence.ipynb` thực hiện pipeline thống nhất cho 8 thành phố (bỏ Xylene, xử lý 0 treo, nội suy ≤14 ngày, giữ NaN khoảng dài, không nội suy AQI, gắn cờ ngoại lai và nghi lỗi cảm biến), xuất `data/processed/air_quality_8cities.csv` (14.056×40) và các báo cáo `cleaning_summary_8cities.csv`, `suspect_points_8cities.csv`, `cleaning_log_8cities.md`.
3. **Hợp nhất thời tiết:** `04_weather_merge.ipynb` chuẩn hóa múi giờ Asia/Kolkata, gộp 24 giờ thành ngày, tính `wind_u/v`, `precip_sum`, `rain_day`, `blh_mean/min`, ghép trái theo (City, Date) thành `air_quality_8cities_weather.csv` (14.056×54), giữ nguyên bảng không thời tiết để EDA không bị ảnh hưởng.
4. **EDA và trực quan hóa (Data Storytelling):** `03_eda.ipynb` thực hiện ba cụm phân tích — Ở đâu (tỷ lệ ngày ≥201 theo thành phố), Khi nào (heatmap City×Month, xu hướng City×Year), Chất nào (quan hệ PM2.5–AQI, phân bố AQI) — kèm kiểm tra độ nhạy và ghi chú confounder (vị trí trạm, Diwali, đốt rơm Punjab, cách tính AQI).
5. **Mô hình hóa và đánh giá:** `05_weather_correlation.ipynb` (tương quan thô vs. khử mùa, 3 giả thuyết, hiệu chỉnh đa kiểm định) và `06_predict_aqi.ipynb` (Ridge trên log(AQI) với L1→L3, 3 baseline, chia theo thời gian, bootstrap theo khối, chẩn đoán phần dư, diễn giải hệ số). Mọi scaler/imputer/encoder chỉ fit trên train; thời tiết ngày mai (nếu thử) được gắn nhãn “Cận trên: dự báo hoàn hảo”.
6. **Trình bày sản phẩm và báo cáo:** tổng hợp biểu đồ vào `reports/figures/` (15 hình: 6 EDA + 4 corr + 5 model), hoàn thiện báo cáo theo cấu trúc rubric, và minh họa bằng tệp HTML phát lại trên dữ liệu lịch sử.

Các công cụ chính: **Python** (pandas, numpy, matplotlib, seaborn, scipy, scikit-learn, statsmodels), **Jupyter Notebook**, **Git** quản lý phiên bản. Mỗi notebook có thể chạy lại bằng *Kernel → Restart & Run All* từ thư mục `notebooks/` sau khi cài `Requirements.txt`; thứ tự 01→06 phải được tôn trọng do phụ thuộc dữ liệu.

**Phân công nhiệm vụ** được ghi nhận theo nhóm 4 thành viên; do yêu cầu không bịa đặt thông tin hành chính, bảng dưới đây để trống tên cụ thể và cần được điền khớp với biên bản phân công chính thức của nhóm nộp:

| Thành viên | Phụ trách chính | Sản phẩm liên đới |
|---|---|---|
| [Cần bổ sung — Thành viên 1] | Thu thập & làm sạch 2 thành phố đầu, chuẩn hóa pipeline | `01_cleaning.ipynb`, `src/pipeline.py`, `src/utils.py` |
| [Cần bổ sung — Thành viên 2] | EDA & trực quan hóa (Ở đâu/Khi nào/Chất nào), Data Storytelling | `03_eda.ipynb`, `reports/figures/eda_*.png` |
| [Cần bổ sung — Thành viên 3] | Hợp nhất thời tiết & phân tích tương quan khử mùa | `04_weather_merge.ipynb`, `05_weather_correlation.ipynb`, `src/weather_utils.py`, `src/corr_utils.py` |
| [Cần bổ sung — Thành viên 4] | Mô hình hóa & đánh giá, ứng dụng minh họa HTML | `06_predict_aqi.ipynb`, `src/model_utils.py`, `Canh_bao_o_nhiem_truoc_mot_ngay_Pro_v5.html` |
| Tất cả | Viết báo cáo, rà soát đạo đức dữ liệu & thuyết trình | Báo cáo PDF/MD, slide bảo vệ |

> **Lưu ý về trạng thái triển khai:** Repository hiện tại là **bản Test cá nhân clone từ nhóm**; các cải tiến trên nhánh Dev (PR #4) chưa được merge/nghiệm thu, các kiểm chứng F01/F02 chưa đóng. Do đó báo cáo không mô tả bản sửa chỉ có ở Test như chức năng nhóm đã triển khai, không tuyên bố đã loại bỏ hoàn toàn leakage, và không trộn số liệu trước sửa với số của ứng viên Dev. Trước bất kỳ tác vụ nặng nào (chạy lại DA/Dev), nhóm sẽ báo quy mô, thời gian và xin phép theo nguyên tắc đã thống nhất.

---

**Tài liệu tham khảo cho Phần I** (trích dẫn đầy đủ ở cuối báo cáo):

- Central Pollution Control Board (CPCB), Government of India — nguồn gốc dữ liệu quan trắc; Kaggle: Rohan Rao, *Air Quality Data in India* (city_day.csv).
- Open-Meteo Historical Weather API, dữ liệu tái phân tích ERA5 (ECMWF/Copernicus), giấy phép CC BY 4.0 — *Weather data by Open-Meteo.com*.
- Rubric học phần Khoa học dữ liệu (INFO3020) — cấu trúc báo cáo và ma trận đánh giá CLO.
- `GOI_BO_SUNG_BAO_CAO.md`, `Data_dictionary.md`, `Metadata.json`, `reports/cleaning_log_8cities.md` — căn cứ số liệu, ngưỡng và hạn chế.

*Các thông tin hành chính còn thiếu (mã học phần, lớp, giảng viên, danh sách nhóm chính thức, URL repo nhóm, thời gian thực hiện) được đánh dấu `[Cần bổ sung]` và sẽ được điền sau khi đối chiếu với hồ sơ nộp của nhóm.*
