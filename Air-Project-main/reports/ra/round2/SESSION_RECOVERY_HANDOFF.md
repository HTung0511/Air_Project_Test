# HANDOFF khôi phục phiên — RA / DA / Dev

Ngày 11/11/2026. Mục đích: thay phiên quá tải bằng phiên mới mà không chạy lại dự án từ đầu. Đây là bản đồ tiếp nhận, KHÔNG phải nghiệm thu kỹ thuật.

## 1. Tình trạng được biết

- Người dùng báo phiên Dev sập, không thể chat lại; phiên DA cũng quá tải. Không suy nguyên nhân từ độ lớn diff.
- Remote vẫn có hồ sơ Dev và DA. Chỉ phần đã push được xác nhận; công việc chưa push trong workspace cũ không rõ. Không xóa phiên cũ trước khi kiểm checkpoint/file còn truy cập được.
- Không cần merge main để bàn giao. Không merge/close PR trong quy trình khôi phục.
- Dev đã tự ghi trạng thái sẵn sàng DA kiểm trên PR #4. DA chưa xác minh bản sửa; RA chưa nghiệm thu; F01/F02 vẫn mở.

## 2. Nguồn chuẩn, ghim commit

Repo: https://github.com/HTung0511/Air_Project_Test

| Vai trò | Nhánh / PR | Snapshot cần đọc |
|---|---|---|
| RA | `arena/8afd3d48-air-project-test`, PR #2 | `8c1a2fb` chứa RA_DECISIONS_03; dùng file tại commit đó, không đoán theo main |
| DA cũ | `arena/b5aacef3-air-project-test`, PR #3 | `13e93ae12c483f01a573ee51ef9562a315e45068` — preparation; remote được kiểm lại ngày11/11 |
| Protocol DA gốc | Nhánh DA | `e0eef8cccce7a09cbdbcb7de3cbdde9b35b2ab61` |
| Code Dev | `arena/5cb21c04-air-project-test`, PR #4 | `a9757af398ddac2f8536e8019e4eb6b5900b4f75` — đối tượng kiểm |
| Tài liệu/bằng chứng Dev | Cùng PR #4 | `ce78795227b184d9ab0c9a2d38e9d0185169c501` — HEAD remote lần kiểm trước |

Link PR Dev: https://github.com/HTung0511/Air_Project_Test/pull/4

Tài liệu dưới `Air-Project-main/reports/ra/round2/`:
- RA: `RA_DECISIONS_01.md`, `RA_DECISIONS_02.md`, **`RA_DECISIONS_03.md`**. DEC03 chứa các điều kiện mới nhất, không có nghĩa được bỏ DEC02.
- DA: `da_verification_protocol.md`, `reproduction_log.md`, `verification_results.md`, `evidence/` (xác minh tên bằng git tree nếu khác; không quét/in toàn thư mục).
- Dev: `dev_change_log.md`, `dev_label_feature_protocol.md`, `dev_evidence/`.
- Báo cáo RA tổng thể: `reports/ra/final_review_report.md`; chỉ đọc khi cần scope/issue cũ.

Đọc từ commit bằng git show/fetch có giới hạn; không cần checkout hoặc merge các nhánh khác. Phiên mới chỉ ghi/commit/push trên nhánh Arena cấp cho chính phiên đó. Không tự chuyển sang nhánh cũ để ghi.

## 3. Điều đã xác nhận và điều chưa xác nhận

RA đã kiểm snapshot DA: không thay code/data ngoài round2;47 artifact hiện diện khớp bytes/hash; kiểm nhỏ từ raw xác nhận8668 khóa/nhãn;327 phép so baseline nhất quán tolerance ghi trong CSV;3 ca nhỏ helper as-of phù hợp chính sách. RA KHÔNG chạy lại pipeline/model hoặc chứng nhận code Dev.

DA prep: chấp nhận có điều kiện, không yêu cầu làm lại baseline. Cần amendment AM-01…04 theo DEC03 trước kiểm Dev:
1. I/O theo dõi được cả output scratch và path/hash downstream, không bỏ sót vì root/dedup.
2. So metric full precision; số in đã round không ép1e-6.
3. Tách feature-only / nhãn / eligibility / invalid-input khi cắt hoặc perturb.
4. Ghi rõ deviation, rounding ties và contract reject-gap trước khi xem metric Dev.

Dev tự báo:211 tests (210 pass,1 skip),21 bước exit0,5 chuỗi notebook offline. Đây là CLAIM cần DA kiểm độc lập, không phải kết luận RA. PR có NEW-R2-001 (2 ô nghi lỗi vốn raw thiếu), NEW-R2-002 (3 số H1 đổi khi dùng weather mới); đọc mô tả trước khi đánh giá, không tự đóng.

Diff khoảng32k dòng thêm gồm evidence CSV/JSON/notebook/log; không phải32k dòng mã hay bằng chứng32k tác vụ đang chạy. Dev ghi diff mã riêng31 file từ cd719cf tới a9757af; dùng đối chiếu đúng base, không tính tài liệu RA kế thừa là code Dev.

## 4. Giữ nguyên scope và phương pháp

- Đánh giá kỹ thuật: runtime, reproducibility, leakage và kết quả. Người dùng đã loại phần Đạo đức dữ liệu & Báo cáo và Vấn đáp & Bảo vệ; không mở lại vì thiếu slide/báo cáo cuối.
- Weather và AQI ngày mai/caution≥201 là yêu cầu giảng viên. Không yêu cầu dự báo khí hậu/weather mới hoặc đổi mục tiêu sang PM2.5/hour.
- Giữ interpolation≤14 ngày cho EDA hồi cứu; không bắt tối ưu ngưỡng. Forecast phải causal riêng.
-8 TP là lựa chọn tác giả vì kỳ dữ liệu tương đối khớp/đầy đủ, nguồn Kaggle; không chứng nhận tính đại diện top8.
- DEC02: raw AQI(t+1), exact calendar next day, finite positive AQI(t)/(t+1); không cap500/interpolate nhãn; không global suspect mask cho forecast; split theo target-date. Flatline prefix≤t, FF≤2 ngày từ nguồn chưa mask; train-fit imputer. Xem DEC02 đầy đủ trước implement/test.
- DEC03 xác nhận ngày1/2 zero đã emit không sửa ngược; tại snapshot ngày3 mask run đã thấy. Có thể reject raw thiếu ngày bằng validation rõ TP/ngày, nhưng không gọi là hỗ trợ gap. NaN trên dòng hợp lệ vẫn phải xử lý.
- RA không chạy phân tích lớn thay DA; DA không tự thay quyết định phương pháp RA. BA cập nhật diễn giải/checklist sau kiểm chứng; không dùng văn bản để chữa runtime/leakage.

## 5. Ngân sách phiên mới — xin xác nhận trước tác vụ nặng

Yêu cầu mới của người dùng: TRƯỚC triển khai phải ước tính quy mô để người dùng quyết định có quá tải hay không. Không thể hứa thời gian chạy khi chưa đo.

Bước đầu chỉ metadata và đọc chọn lọc, không cài môi trường/chạy notebook/test đầy đủ. Báo:
- Số file/dung lượng input, output dự kiến; số hàng/cohort quan trọng.
- Số bước/models/folds/mutations, thời gian ước tính hoặc chưa biết, RAM/disk và rủi ro log.
- Phương án nhỏ trước và điểm dừng. Chờ người dùng đồng ý trước tác vụ lớn.

Quy ước nhẹ đề xuất (không là tiêu chí nghiệm thu mô hình):
- Mỗi lần đọc khoảng≤150 dòng; tránh diff/notebook JSON/log toàn bộ trong chat.
- Mỗi cập nhật chat≤20 dòng, đưa summary+path+SHA thay dump bảng.
- Log đầy đủ vào file; chat chỉ tail lỗi≤40 dòng. Không commit dataset sinh lớn/cache/venv hay output lặp nhiều lần; giữ evidence tối thiểu, hash/provenance. Không xóa bằng chứng cũ chỉ để giảm diff.
- Mỗi gate kết thúc ghi `DA_CHECKPOINT.md` ngắn, commit/push thay đổi phù hợp, trả SHA. Không chờ hết tất cả gate mới checkpoint.

## 6. Kế hoạch nối tiếp DA — không chạy lại từ đầu

0. Tiếp nhận repo/nhánh mới, kiểm status, các SHA remote và workspace; ghi cái chưa cứu được. Không trộn thay đổi chưa rõ nguồn.
1. Đọc handoff này+DEC02/03, protocol DA và2 tài liệu Dev theo từng phần; lập budget và ACK. Chưa rerun baseline.
2. Sửa amendment AM-01…04; kiểm có amendment/checkpoint mới hơn ở workspace DA cũ hay không trước khi viết trùng. Nếu không truy cập được thì ghi rõ. Nêu đã thấy metric nào của Dev qua PR/tài liệu; KHÔNG khẳng định mù số nếu đã thấy.
3. GateA F02 nhỏ: lock/cache offline, negative cases, output routing. Fail thì counterexample ngắn và checkpoint.
4. GateB F01 nhỏ: fixture, raw cohort, feature-only cutoff/perturb hợp lệ; fail thì báo trước khi train đầy đủ.
5. GateC chỉ sauA/B đạt và user đồng ý budget: chuỗi notebook cuối+metric A–D/CI theo protocol. Tái sử dụng đúng những thiết kế thực sự đồng nhất; không train D nếu chỉ là kiểm kê cohort. Không walk-forward lớn lặp lại vô ích.
6. Gửi RA bảng pass/fail/blocked theo SHA, anchors/log và issues mới. RA quyết định nghiệm thu; không tự merge/đóng F01/F02.

Nếu GateA/B phát hiện lỗi cần Dev: báo RA/người dùng, tạo prompt Dev sửa nhỏ ở phiên mới; không để DA tự sửa đối tượng kiểm rồi gọi là xác minh độc lập.

## 7. Prompt khởi động DA mới (copy kèm link handoff)

Bạn là DA tiếp nhận dự án Air_Project_Test từ phiên quá tải, không làm lại baseline. Đọc SESSION_RECOVERY_HANDOFF.md và các nguồn ghim SHA trong đó. Chỉ làm bước0–1 trước: kiểm metadata/trạng thái, đọc tài liệu chọn lọc và trả ACK≤20 dòng gồm vai trò, SHA code Dev và evidence, việc đã biết/chưa biết, budget dự kiến, điểm cần xin phép. Chưa cài môi trường, chưa chạy notebook/model/test lớn. Tiếp tục trên đúng nhánh Arena cấp cho phiên này, không merge PR. Hoàn thiện amendment RA-DEC-03 rồi dùng gateA→B→C sau khi được đồng ý; checkpoint/push mỗi gate. Không dump log/dataset vào chat. Mọi claim Dev phải được phân biệt với kết quả bạn tự kiểm. Nếu thiếu tài liệu hoặc amendment/checkpoint chưa push, nói rõ thay vì giả định đã có.

## 8. Prompt RA mới nếu cần chuyển cả phiên RA

Bạn là RA tiếp nhận, không thay DA chạy phân tích lớn. Đọc handoff này, RA-DEC02/03 và báo cáo RA theo vấn đề. F01/F02 chưa đóng; DA prep chấp nhận có điều kiện; Dev PR4 chỉ tự báo ready. Trước hết xác minh SHA và budget, không chạy lại dự án/merge PR. Chờ DA handoff độc lập rồi quyết định theo tiêu chí đã chốt; giữ scope và yêu cầu giảm tải của người dùng. Ghi checkpoint và bảng Tiêu chí | Kết quả | Bằng chứng | Ghi chú; phân biệt bằng chứng thực nghiệm, self-check và thiếu bằng chứng.
