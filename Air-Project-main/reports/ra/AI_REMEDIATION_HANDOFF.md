# Bộ prompt điều phối sửa dự án — RA → Dev / DA / BA

Ngày: 11/11/2026 · Điều phối và nghiệm thu: AI-2 Research Analyst (RA).

**Cách dùng:** gửi nguyên phần **0 + prompt đúng vai** sang phiên làm việc của từng AI. Các AI phải trả xác nhận nhận việc trước khi sửa/chạy. Tài liệu này là gói bàn giao, **không phải bằng chứng rằng RA đã gọi hoặc giao việc trực tiếp cho các phiên AI khác**.

## 0. Ngữ cảnh chung — gửi cho cả ba AI

Bạn tham gia dự án `HTung0511/Air_Project_Test`, cùng bốn vai:

- AI-1 **BA:** quản lý yêu cầu, phạm vi và checklist.
- AI-2 **RA:** đánh giá methodology, điều phối và nghiệm thu bằng chứng.
- AI-3 **DA:** tái lập, kiểm chứng và phân tích bổ sung; không tự phê chuẩn methodology thay RA.
- AI-4 **Dev:** sửa mã, notebook, môi trường và viết kiểm thử kỹ thuật.

### Nguồn phải đọc trước

1. `Air-Project-main/README.md`: nguồn mô tả pipeline chính. README ở root chỉ là tên repository.
2. `Air-Project-main/reports/ra/final_review_report.md`: phạm vi RA đã cập nhật sau đính chính của nhóm.
3. `Air-Project-main/reports/ra/notebook_review.md` và `open_questions.md`: lịch sử vòng đánh giá ban đầu; không dùng các yêu cầu đã được rút/thu hẹp để mở lại công việc ngoài phạm vi.
4. Bộ DA tại PR #3, snapshot `0dfc71568d439b3b2e9dae9a9093f23bcf379969`:
   - [verification_results.md v1.1](https://github.com/HTung0511/Air_Project_Test/blob/0dfc71568d439b3b2e9dae9a9093f23bcf379969/Air-Project-main/reports/ra/verification_results.md)
   - [reproduction_log.md v1.1](https://github.com/HTung0511/Air_Project_Test/blob/0dfc71568d439b3b2e9dae9a9093f23bcf379969/Air-Project-main/reports/ra/reproduction_log.md)
   - [supplementary_analysis.md](https://github.com/HTung0511/Air_Project_Test/blob/0dfc71568d439b3b2e9dae9a9093f23bcf379969/Air-Project-main/reports/ra/supplementary_analysis.md), cùng CSV/script trong `evidence/`.
5. Nếu được cung cấp bài giữa kỳ `Giua_ky_INFO3020_O_nhiem_khong_khi_8_thanh_pho.pdf`, dùng làm bối cảnh EDA giữa kỳ. Nếu phiên của bạn không có file, đọc phần tóm tắt theo trang trong báo cáo RA; không giả nhận đã đọc PDF.

Không mặc định những file DA đã có trên nhánh của bạn: lấy đúng snapshot để tham khảo, ghi nguồn rõ ràng. Không chuyển nhánh/cherry-pick/merge thay đổi của người khác một cách tự động; thực hiện trên nhánh phiên của bạn được nền tảng cho phép. Trước khi áp dụng patch ngoài nhánh, kiểm tra diff và xin quyết định tích hợp nếu cần. Không tự merge các PR #1/#2/#3 hoặc đóng PR của vai khác.

### Phạm vi đã chốt — không hỏi lại từ đầu

- NB01–02: làm sạch 8 TP và bằng chứng làm sạch.
- NB03: EDA **ở đâu — khi nào — chất nào**.
- NB04: tích hợp khí tượng Open-Meteo/ERA5.
- NB05: liên hệ khí tượng–AQI, khử mùa, các giả thuyết và độ nhạy.
- NB06: **dự báo AQI ngày mai và cảnh báo AQI≥201**, không phải dự báo khí hậu tương lai. Việc bổ sung khí tượng/dự báo là yêu cầu giáo viên, không phải nhóm tự mở rộng sai phạm vi.
- Nhóm đã giải thích chọn 8 TP vì khoảng thời gian gần nhau và dữ liệu tương đối đầy đủ. Ghi nhận lý do này; không tự gọi là top-8 coverage hay mẫu đại diện toàn Ấn Độ. AQI từ Kaggle/CPCB, weather hiện tại từ Open-Meteo/ERA5.
- **Giữ nội suy ≤14 ngày cho nhánh làm sạch hồi cứu/EDA.** Đây là quyết định thiết kế của nhóm, không cần thay ngưỡng. Không đồng nhất lý do thực hành với chứng minh ngưỡng duy nhất/tối ưu khoa học.
- Bỏ chấm **Phần 4–5**: không đòi slide, template, biên bản vấn đáp, demo cá nhân hoặc hình thức báo cáo để đóng vòng sửa kỹ thuật. Nội dung giải thích phương pháp có thể bổ sung, không biến thành kiểm tra trình bày.
- Không dựng production system nếu không có yêu cầu. Dự báo offline vẫn phải tôn trọng thời gian.

### Hai lỗi kỹ thuật chính có căn cứ DA

- **F01 / P0:** preprocessing toàn chuỗi có dùng tương lai. `make_features(as_of=...)` cắt dữ liệu đã sạch; top-5 toàn chuỗi, cửa sổ centered, nội suy và flatline có thể thay đổi khi xuất hiện ngày sau. DA V05/V07 đo được sai khác; biến thể V07 giảm tác động nhưng giữ nhãn baseline và có wrapper riêng, chưa sửa mã nguồn chính.
- **F02 / P0:** NB04 gọi mạng trước đọc cache; trên Python 3.11, cell29 có lỗi f-string. API bị chặn là blocker môi trường, không chứng minh weather sai. V10/V11/NEW-003/NEW-004 ghi rõ phạm vi.

Các việc nội dung bổ sung: F03 giới hạn test/holdout/ngưỡng; F04 tỷ số PM2.5 và q/CI/family; F05 lý do chọn mẫu, missing và ngưỡng. F06 biến đích **đã đóng theo README**, không mở lại bài toán dự báo khí hậu. NEW-005 đã rút do shallow clone, không còn blocker.

### Quy tắc chung

- Không sửa raw/cache gốc hoặc ghi đè baseline để làm số khớp. Dùng output mới/scratch; ghi hash và đường dẫn.
- Không thay split/baseline/feature/threshold tùy tiện để tăng điểm test. Mọi thay đổi cần lý do, diff và đánh giá riêng.
- Không tự đánh “đạt” chỉ vì không thấy lỗi. Chưa kiểm được ghi **❓ Không đủ bằng chứng**, kèm lý do blocked nếu có.
- Mọi bảng tổng hợp dùng `Tiêu chí | Kết quả | Bằng chứng | Ghi chú`.
- Mọi kết quả mới phải gắn **commit mã đã chạy, environment, lệnh, exit code, artifact**; ảnh cũ hoặc câu “đã chạy thành công” không đủ.
- Vấn đề mới ghi `NEW-R2-001`… và gửi RA, không âm thầm bỏ qua hoặc mở rộng scope.

## 1. Prompt gửi AI-4 — Dev

**Bạn là AI-4 Dev. Mục tiêu: sửa F02 trước, sau đó F01, giữ nhánh EDA hiện hành ổn định. Không làm lại toàn bộ dự án.**

### DEV-01 — Sửa NB04 và môi trường chạy (F02)

1. Đọc `notebooks/04_weather_merge.ipynb`, `src/weather_utils.py`, `Requirements.txt` và V10/V11/NEW-003/NEW-004.
2. Đổi luồng thành **cache-first theo từng TP**. Cache hợp lệ: kiểm schema/biến bắt buộc, phạm vi thời gian, lưới giờ, duplicate và missing; không chỉ kiểm file có tồn tại.
3. Cache đầy đủ thì không gọi smoke-test/probe/API. Xác định BLH từ schema cache; không âm thầm bỏ BLH trong khi NB05/06 cần nó.
4. Cache thiếu/hỏng: nếu cho phép online thì tải đúng phần cần thiết; lỗi mạng phải báo rõ TP/file/biến. Chế độ offline phải thất bại rõ ràng khi thiếu cache, không bịa dữ liệu. Giữ provenance/timezone/đơn vị.
5. Sửa f-string cell29 tương thích phiên bản Python hỗ trợ, không chỉ né chạy cell lỗi. Ghi phiên bản Python, ghim dependency đã kiểm được; không đoán environment tác giả.
6. Kiểm thử ít nhất: cache đủ + mạng bị vô hiệu hóa; thiếu một cache offline; thiếu cột BLH; duplicate/thiếu giờ; đường đi online bằng mock nếu không gọi được API thật. Không báo mock là kiểm API thật.
7. NB04 phải chạy trọn, output mới ghi ở bản sao/scratch. Chốt tolerance có lý do cho weather quanh biên round; không nâng tolerance rộng để che sai đơn vị/ngày.

### DEV-02 — Tách preprocessing dự báo khỏi hồi cứu (F01)

1. Giữ nguyên ngưỡng 14 ngày và nhánh EDA/cleaning lịch sử, không ghi đè các CSV baseline đã kiểm.
2. Tạo đường đi dự báo từ raw có contract rõ: một mẫu `(City,t)` dự đoán `AQI(t+1)`; feature chỉ dùng thông tin có sẵn đến hết `t`.
3. Không đưa ô nội suy hai đầu mút vào feature dự báo. Nếu dùng forward-fill thì giới hạn quá khứ đã chốt; imputer/scaler chỉ fit train. Không backward-fill từ ngày sau.
4. Xử lý flatline và suspect bằng chính sách causal rõ ràng: không chọn top-5 toàn chuỗi/cửa sổ centered để thay feature đã công bố tại t. Có thể dùng raw hợp lệ + quy tắc causal hoặc chỉ gắn cờ; nêu lựa chọn trước khi triển khai và xin RA nếu làm thay đổi mạnh định nghĩa bài toán.
5. Phân biệt “dựng feature as-of t” với bảng feature đã phát hành trong quá khứ: nếu cho phép cập nhật lịch sử quan sát trong phạm vi ≤t thì ghi rõ chính sách; tuyệt đối không dùng ngày >t. Không tự hứa mô phỏng revision CPCB khi không có snapshot phát hành thực.
6. **Nhãn y là phần bắt buộc của thiết kế:** không nội suy AQI; không mặc định giữ nhãn đã bị loại bằng luật toàn chuỗi mà gọi pipeline là causal end-to-end. Nêu nhãn gốc nào hợp lệ, xử lý nghi lỗi thế nào, thời điểm đánh giá và tiêu chí giữ mẫu. Không tự xóa AQI chỉ vì PM2.5 nghi lỗi nếu không có căn cứ. Gửi RA protocol nhãn/mẫu trước khi khóa implementation.
7. Cập nhật NB06 dùng đường đi mới, giữ nguyên chia thời gian, L1–L3, các baseline và cơ chế chọn alpha/ngưỡng trên train/OOF. Nếu API thay đổi, đảm bảo notebook dùng thực sự, không chỉ thêm hàm chưa được gọi.
8. Thêm no-gas/empty guard và regression test cho NEW-002; kiểm đầu chuỗi ngắn, thiếu pollutant, biên flatline, suspect và khoảng thiếu.
9. Test chống leakage từ **raw**: cắt ở t, perturb dữ liệu sau t, đối chiếu feature tại t; phủ các ngày đã có vấn đề ở V05/V07 và ranh train/test. Kiểm riêng nhãn/mẫu và sự khác biệt do chính sách evaluation, không che chúng bằng cách chỉ so hàng giao nhau.

### Dev trả gì?

Tạo `reports/ra/round2/dev_change_log.md` và kiểm thử trong cấu trúc test phù hợp repo. Log có anchor `D01`… cho từng sửa, file/function, before/after, rationale, unit/integration tests, command/exit, tolerance, phần chưa làm và rollback/compatibility EDA. Ghi commit/PR cụ thể và output mới để DA lấy đúng bản.

**Cổng bàn giao:** Dev báo “sẵn sàng DA kiểm”, không tự báo “RA nghiệm thu đạt”. Gửi RA và DA danh sách F01/F02/NEW-002 đã xử lý, test đã chạy, test chưa chạy, thay đổi nhãn/mẫu. Không chờ DA đến cuối mới tiết lộ đổi split hoặc định nghĩa y.

## 2. Prompt gửi AI-3 — DA

**Bạn là AI-3 DA. Mục tiêu: kiểm chứng độc lập bản sửa của Dev và báo bằng chứng cho RA, không chỉ chạy lại script Dev rồi xác nhận.**

### Trước khi Dev bàn giao

- Xác nhận đã đọc V05/V07/V10/V11 và gói này.
- Chốt test protocol trước khi xem metric mới: split, baseline, metrics, paired comparisons, bootstrap khối lịch 14 ngày chung giữa TP, sensitivity 7/28 ngày khi cần. Test cũ đã mở, không gọi là test chưa từng nhìn.
- Chuẩn bị baseline từ đúng commit cũ và ghi environment/hash. Không chạy toàn bộ phân tích bổ sung cũ nếu không phục vụ sửa F01/F02.

### Sau khi Dev bàn giao đúng commit

**DA-01 / F02:** chạy NB04 nguyên bản đã sửa trên bản sao, không sửa nóng notebook cho qua. Test offline với cache đầy đủ và mạng tắt; negative tests cache thiếu/schema sai. Xác nhận đọc BLH, 24 giờ/ngày, timezone, u/v, mưa, merged 14056×54, khóa không trùng, 40 cột AQ không đổi, weather không thiếu. So baseline với tolerance đã khóa, báo actual max diff và downstream effects. API thật không truy cập được thì chỉ đánh blocked phần API, không đánh fail cache hay pass API bằng mock.

**DA-02 / F01:** kiểm từ raw, không chỉ `make_features(as_of)` trên bảng sạch. Chạy cắt ngày và future perturb, các boundary test, rồi walk-forward toàn khoảng nếu chi phí phù hợp. Báo số ô/dòng khác theo feature/TP/split; kiểm timestamp và đường đi dữ liệu. Xem mã notebook thực sự gọi pipeline mới. Unit test pass là bằng chứng kỹ thuật, chưa thay kiểm tra thực nghiệm.

**DA-03 / nhãn và mẫu:** đối chiếu protocol Dev/RA đã thống nhất. Báo cohort cũ/mới, dòng thêm/bỏ theo TP/mùa/split và nguyên nhân. Đánh giá **cùng nhãn/cùng mẫu** để tách ảnh hưởng feature nếu so được; báo thêm kết quả theo protocol nhãn mới. Nếu không cùng estimand thì nói rõ không so trực tiếp. Không chỉ giữ y baseline rồi kết luận causal end-to-end. Không điền nhãn AQI để tăng coverage.

**DA-04 / regression:** chạy 01→06 trên scratch bằng environment mới; kiểm nhánh EDA có đổi hay không và giải thích mọi diff. Với NB06 báo MAE/RMSE/R², TP/FP/FN/TN, recall/precision/F1, ngưỡng201 và ngưỡng F2 chọn train/OOF, paired CI test và holdout. Giữ kết quả âm; không bắt mô hình phải hơn baseline ở mọi ngưỡng hoặc holdout mới được xem sửa đúng. Không tune lại bằng test để cứu số.

**DA-05 / nội dung:** cung cấp bảng V16/V18/V19 cần cho BA sửa ratio, q/CI và family15. Chỉ sửa/tái tính benchmark S05 nếu nhóm muốn dùng nó để chứng minh tối ưu ngưỡng; không mở thành dự án nghiên cứu ngưỡng mới.

### DA trả gì?

Trong `reports/ra/round2/`:

- `reproduction_log.md`: code commit Dev, scripts commit, baseline commit, environment, hash, lệnh, exit code, runtime, mạng/mock/offline, artifact.
- `verification_results.md`: anchor `R2-V01`…; map từng yêu cầu Dev/RA; expected/actual, pass/partial/fail/blocked, link CSV/diff/script và nhận xét giới hạn. Kết luận kỹ thuật nào chỉ dựa test của Dev phải nói rõ.
- `supplementary_analysis.md`: chỉ tạo nếu có phân tích bổ sung cần thiết, anchor `R2-S01`…; không nhồi kết quả không liên quan.
- `evidence/`: CSV nhỏ, script, diff; không đẩy dataset/output notebook lớn không cần thiết.

Không sửa v1.1 DA đã bàn giao; vòng 2 là hồ sơ mới. Phát hiện mới ghi `NEW-R2-*` và chủ động gửi RA. Kết thúc bằng “đã kiểm chứng trên commit …; các mục còn blocked …; đề nghị RA xét đóng …”, không tự nghiệm thu methodology.

## 3. Prompt gửi AI-1 — BA

**Bạn là AI-1 BA. Mục tiêu: cập nhật yêu cầu/checklist và phần giải thích cho khớp phạm vi hiện tại; không đặt thêm bài toán ngoài README, không sửa mã thay Dev.**

### BA-01 — Khóa phạm vi, tránh scope creep

- Ghi rõ khí tượng–AQI và dự báo AQI ngày mai/cảnh báo≥201 là yêu cầu bổ sung của giáo viên theo thông tin nhóm cung cấp.
- Đóng câu hỏi dự báo khí hậu: không yêu cầu thêm mô hình nhiệt độ/mưa/gió. Không tự mở lại PM2.5 cùng ngày hoặc AQI theo giờ nếu không có yêu cầu mới được xác nhận.
- Ghi Phần4/5 là **tạm ngoài phạm vi vòng sửa**, không tính thiếu slide/vấn đáp thành fail; cũng không ghi các phần này đã đạt.
- Giữ lý do chọn 8 TP và ngưỡng14 ngày; phân biệt lựa chọn thực hành với chứng minh đại diện/tối ưu. Không nói mọi TP ngoài mẫu đều kém hơn khi V17 có ví dụ coverage tương đương.

### BA-02 — Sửa checklist và nội dung phương pháp có căn cứ

Đọc V01/V08/V14/V16/V17/V18/V19/V26; tài liệu giữa kỳ đã giải thích nhiều điểm, không ghi “nhóm chưa có” khi chỉ chưa thấy file trong clone.

- 54 ID thực tế so với câu “50”; mẫu số P3 và trọng số phải tự nhất quán. Không tự quy đổi thành điểm mới khi chưa chốt với chủ yêu cầu.
- 2169 **ô**, không 2069 ngày; summary False=8 Xylene đã bỏ +3 cặp cột thật, không phải đúng3 trên toàn bảng.
- 2,82 là median5 tỷ số TP; hai median gộp137,1/42,0 cho3,26. Chỉ sửa chỗ thực sự ghép sai; slide giữa kỳ trang11 đã ghi đúng median5 TP.
- 32/48 có q_BH<0,05; 33/48 có CI95% chưa hiệu chỉnh loại0. Family Bonferroni là15 so sánh trong notebook được kiểm, không3 trên toàn bảng.
- Không gán chắc MAR/MNAR từ thiếu100%/block_ratio; không coi tương quan khí tượng là nhân quả hoặc PM2.5–AQI là đóng góp định lượng.
- Giới hạn Delhi51% theo cửa sổ; kết luận theo nhóm thay xếp hạng đầy đủ; kết quả test/holdout/ngưỡng khác nhau là thông tin cần trình bày, không lý do bác việc thêm dự báo.
- Làm rõ kế hoạch split giữa kỳ khác implementation hiện tại, không tự kết luận sai. Log notebook07 cũ nên dẫn notebook01 hiện hành, ghi rõ snapshot nếu giữ lịch sử.

### BA-03 — Phân công nội dung và trạng thái kỹ thuật

Tạo bảng yêu cầu sửa với owner, đầu vào/bằng chứng, điều kiện đóng, phụ thuộc Dev→DA→RA. F01/F02 không được đóng bằng sửa lời văn. F03–F05 chủ yếu là nội dung cần bổ sung, không mặc định bắt nhóm tái phân tích. Cập nhật kết quả sau DA vòng2, không sửa số trước để dự đoán mã mới sẽ tốt hơn.

### BA trả gì?

Tạo `reports/ra/round2/ba_requirements_update.md` gồm anchor `B01`…: yêu cầu trước/sau, nguồn xác nhận của nhóm, CK/F liên quan, owner, điều kiện đóng, các sửa checklist đề xuất/thực hiện và các quyết định còn chờ.

Nếu sửa source of truth checklist, xác định bản canonical trước (repo có thể có bản root/docs sao chép); không tạo thêm bản khác mà không giải thích. Commit/PR có diff rõ ràng; không ghi đè đánh giá RA/DA hoặc coi chỉnh checklist là tự động biến kết quả thành đạt. Gửi RA phê duyệt sự nhất quán yêu cầu.

## 4. Giao thức xác nhận và báo hoàn thành — bắt buộc cho cả ba AI

### Tin nhắn 1 — xác nhận nhận việc, trước khi triển khai

```text
ACK — [BA / DA / Dev]
Đã đọc: [đường dẫn, commit/snapshot; phần không truy cập được ghi rõ]
Nhánh phiên hiện tại và HEAD: [giá trị thực]
Tôi hiểu mục tiêu: [...]
Nhận các mã: [DEV-01/DEV-02, DA-01… hoặc BA-01…]
Không làm ngoài phạm vi: [EDA14 ngày, không dự báo khí hậu, không chấm slide/vấn đáp…]
Kế hoạch và phụ thuộc: [...]
Quyết định cần RA trước khi triển khai: [chỉ điểm mới ảnh hưởng thiết kế, không hỏi lại nội dung đã chốt]
```

### Tin nhắn 2 — bàn giao có bằng chứng

```text
HANDOFF — [vai]
Code commit đã sửa/đã chạy: [...]
Commit tài liệu/script/bằng chứng: [...]
PR hoặc link file: [...]
Các mã hoàn thành: [...]
Các mã partial/blocked/chưa làm và nguyên nhân: [...]
Lệnh + exit code + môi trường: [file log/anchor]
Nhãn/mẫu/split/baseline có đổi không: [không / có và giải thích]
Artifact: [đường dẫn CSV/diff/tests, anchor D/R2-V/B]
Vấn đề mới cần RA: [...]
Đề nghị RA xét đóng: [...]
```

Không dùng các ô `[...]` như dữ liệu thực; đây là template để AI điền bằng kết quả thật. Nếu không thể push/đọc PR, báo blocker, không bịa URL/commit.

### Thứ tự phối hợp và quyền đóng

1. **BA và Dev nhận việc song song.** BA xác nhận scope; Dev xử lý cache/environment và gửi protocol causal/nhãn. DA chuẩn bị protocol kiểm.
2. **RA duyệt các quyết định methodology còn mới**, nhất là nhãn và cohort. Dev triển khai, chạy unit/integration tests, gửi commit chính xác.
3. **DA kiểm commit Dev**, trả hồ sơ vòng2. Dev sửa tiếp nếu test fail, mỗi lần DA ghi commit mới; không dùng kết quả của commit cũ để đóng bản sửa mới.
4. **BA cập nhật mô tả/checklist** dựa trên số cuối đã kiểm; RA xem cả diff yêu cầu và hồ sơ DA.
5. **RA quyết định đóng từng F/NEW** bằng bằng chứng. Ghi kết luận ở `reports/ra/round2/ra_acceptance.md` (RA tạo sau), mọi kết luận kỹ thuật phải dẫn `verification_results.md#R2-V…` hoặc `supplementary_analysis.md#R2-S…` của DA vòng2.

Trạng thái thống nhất: `Chưa nhận → ACK → Đang làm → Chờ DA/RA → Đóng` hoặc `Blocked`. “Dev đã sửa” không đồng nghĩa “DA đã xác minh”, và “DA đã tái lập” không tự đồng nghĩa “RA đã nghiệm thu”. Không AI nào tự merge thay cả nhóm.
