# Bản sửa đổi giao thức kiểm chứng DA — v1.1 (amendment)

Ngày: 12/11/2026 · Người lập: AI-3 DA (phiên `arena/05796171-air-project-test`) · RA duyệt: AI-2 RA (RA-DEC-03).

**Tài liệu này là bản sửa đổi (amendment) bổ sung cho Giao thức kiểm chứng vòng 2 v1.0, KHÔNG thay thế v1.0.** Giao thức gốc giữ nguyên:

- Protocol v1.0: SHA `e0eef8cccce7a09cbdbcb7de3cbdde9b35b2ab61` (file `da_verification_protocol.md`), khóa trước khi có bản sửa, chưa có anchor `R2-V…` nào đánh đạt.
- Thời điểm khóa và các điều kiện đạt (T1.1–T2.7, DA-01…DA-05) **giữ nguyên**, không đổi để phù hợp bất kỳ kết quả Dev nào.
- Mọi số dưới đây mang nhãn rõ: `CLAIM-DEV` = Dev tự đo (chưa DA xác minh); `AUDIT-RA` = RA kiểm trên snapshot (không phải kết quả Dev); `CHƯA-KIỂM` = DA chưa chạy.

Nguồn SHAs đã xác nhận trên remote (phiên này đã fetch):
- Dev code để DA kiểm: `a9757af398ddac2f8536e8019e4eb6b5900b4f75` (PR #4, nhánh `arena/5cb21c04-air-project-test`, HEAD `ce78795227b184d9ab0c9a2d38e9d0185169c501`).
- DA protocol v1.0: `e0eef8cccce7a09cbdbcb7de3cbdde9b35b2ab61`.
- DA prep snapshot: `13e93ae12c483f01a573ee51ef9562a315e45068` (47 evidence files).
- RA-DEC-02 / RA-DEC-03: có trong phiên làm việc này (`416dd7bd…`).

---

## AM-01 — Theo dõi đúng đường I/O và output scratch (tương ứng T1.8)

Theo RA-DEC-03 §4 AM-01. DA phân biệt rõ hai đường:

- **Output Dev mới** nằm ở `outputs/nb04/` và `outputs/nb06/` trong bản sao dự án (không commit, không ghi đè `data/processed/`).
- **Baseline đã commit** nằm ở `data/processed/weather_daily_8cities.csv` (SHA `45f3579a…` theo Dev) và `data/raw/`.

GateA đo: NB05/NB06 trong chuỗi `--weather nb04` phải thật sự đọc file do NB04 vừa sinh (kỳ vọng SHA `2c906e61…` theo Dev), không đọc baseline. Nếu downstream đọc baseline đã commit → **trượt (❌)** bất kể metric. DA ghi path + SHA mỗi lần đọc từ `provenance.jsonl` / `chain_summary.json`, không chỉ dựa vào hash.

## AM-02 — So metric chưa làm tròn, không fail do định dạng (tương ứng DA-04)

Theo RA-DEC-03 §4 AM-02. Ưu tiên bảng biến/dataframe hoặc export numeric chưa làm tròn để so `1e-6`. Với số chỉ hiển thị (làm tròn 1–4 chữ số) dùng nửa đơn vị chữ số cuối + epsilon, ghi rõ là kiểm presentation rounding. Counts/key/nhãn/threshold so chính xác tuyệt đối. Giữ đối chiếu dung sai gốc; không chạy lại baseline chỉ để đổi cách gọi "khớp".

## AM-03 — Tách feature-only, eligibility và invalid-input (tương ứng T2.2/T2.3/T2.5)

Theo RA-DEC-03 §4 AM-03. So feature tại khóa định trước, **không chỉ intersection các mẫu còn nhãn** sau khi cắt/perturb raw (tránh mất hàng `t` khi builder chỉ trả hàng có `y`). Expected `y`/eligibility đổi khi `AQI(t+1)` đổi là hợp lệ, không gọi là leakage. Phải có ít nhất một mutation tương lai vẫn hợp lệ trong miền dữ liệu để kiểm feature (không xem mọi reject là no-leakage). (Áp dụng ở GateB/F01, không phải GateA.)

## AM-04 — Chốt deviations thành amendment minh bạch, không tự nới tolerance

Theo RA-DEC-03 §4 AM-04. Tie tính bằng số nguyên: chấp nhận nếu assert precision đầu vào và đúng 24 giờ trước tính. Hai phía round tại tie cho T1.4 ở 5 mean; T1.5 chỉ 3 cột temp/pressure/wind, điều kiện tie và `0,01+epsilon` giữ nguyên. Reject-gap ghi thành amendment chính thức (mục dưới). Trước đây chỉ là deviation đề xuất.

### AM-04.1 — Reject raw thiếu ngày lịch (từ RA-DEC-03 §3 DA-Q2)

Trong vòng sửa này, DA chấp nhận theo một trong hai contract Dev công bố **trước phép thử**: (1) hỗ trợ gap qua lag/target/ffill theo lịch không shift nhầm; hoặc (2) chỉ hỗ trợ chuỗi ngày liên tục: validate và dừng lỗi rõ TP/ngày thiếu trước khi tạo feature/mẫu sai. Cách (2) được đánh "đạt xử lý đầu vào ngoài contract bằng từ chối rõ ràng", **không gọi là đạt hỗ trợ gap**. KeyError ngoài ý muốn / lỗi im lặng / nối sai run / shift nhầm ngày → vẫn fail. NaN trên dòng ngày hợp lệ là tình huống khác, không dùng contract reject-gap để bỏ kiểm NaN. (Áp dụng GateB/F01.)

---

## Phụ lục A — Tách rõ kích thước dữ liệu (hiệu đính mô tả cũ "daily 16.128×54")

Đo trực tiếp trên snapshot `a9757af` (phiên này đã extract sang scratch). Bốn lớp, KHÔNG gộp:

| Lớp | File | Số hàng | Số cột | Ghi chú |
|---|---|---|---|---|
| Hourly cache (thô) | `data/raw/weather/openmeteo_*_hourly.csv.gz` | 8 TP × **48.384** = 387.072 hàng giờ | 11 | 2014-12-25 → 2020-07-01; đầu vào NB04, không đổi |
| Daily weather | `data/processed/weather_daily_8cities.csv` | **16.128** (8×2.016 ngày) | **16** | City,Date + 14 biến thời tiết; đầu vào NB05/NB06 |
| Merged AQ+weather | `data/processed/air_quality_8cities_weather.csv` | **14.056** (8×1.757 ngày) | **54** | Bảng sạch hồi cứu (EDA/nhánh cũ), 2017-06-14 → 2020-07-01 |
| Raw AQ (nhãn/nguồn) | `data/raw/city_day.csv` | 29.531 | 16 | 2015-01-01 → 2020-07-01; NB06 đọc trực tiếp làm nhãn `AQI_raw(t+1)` |

Hiệu đính: bảng **16.128 hàng là daily weather (16 cột)**, không phải 54; bảng **54 cột là merged (14.056 hàng)**. Con số "225.792 ô" trong Dev (D03) = 8 TP × 28.224 ô = 8 × (16.128 hàng × 14 cột số) — khớp daily weather 16 cột × 16.128 × 8.

## Phụ lục B — Các claim metric đã tiếp xúc (CHƯA PHẢI KẾT QUẢ DA)

Nhãn: `CLAIM-DEV` (Dev tự đo, phiên này ĐÃ ĐỌC qua `dev_change_log.md` @ `ce78795`) / `AUDIT-RA` (RA kiểm snapshot, phiên này ĐÃ ĐỌC qua RA-DEC-03). **Không dùng để kết luận F01/F02; tiêu chí không đổi để khớp số này.**

- `CLAIM-DEV` 211 tests (210 pass / 1 skip-API-thật ❓), 21 bước exit 0, 5 chuỗi notebook offline.
- `CLAIM-DEV` F02: NB04 chạy trọn 16/16 ô mã, 0 lần gọi `requests.get`, 8 cache không đổi SHA; 8 kiểu hỏng dừng rõ, không ghi output.
- `CLAIM-DEV` F02 T1.5: 852 ô khác trên 225.792 (temp_mean 335 / pressure_mean 348 / wind_speed_mean 169), lệch max 0,01, 0 ô ngoài dung sai, 11 cột còn lại 0 khác.
- `CLAIM-DEV` F01: NB06 from-raw; leakage 0 ô khác trên 1.114 ngày cắt (276.272 ô) + 47 ngày cắt kèm nhiễu; cohort 8.668 (5.746/1.947/975, +5 train vs cũ).
- `CLAIM-DEV` 181 số snapshot trong half-unit chữ số cuối; 18/18 khoảng 95% của hiệu MAE chứa 0.
- `CLAIM-DEV` Mở: NEW-R2-001 (2 ô PM2.5 raw thiếu vốn), NEW-R2-002 (3 số H1 đổi khi dùng weather mới) — DA chưa đánh giá, không tự đóng.
- `AUDIT-RA` 47 artifact khớp SHA256; 327 dòng baseline vs v11 trong dung sai từng dòng; 8.668 khóa cohort khớp (stdlib); 3 ca as-of nhỏ phù hợp. RA **không** chạy pipeline/model hay chứng nhận code Dev.

## Phụ lục C — Kế hoạch gate (phiên này)

- **GateA (F02, ĐÃ DUYỆT, đang chạy):** T1.1 (lock 3.11.2 + pip check), T1.2 (ast.parse NB04), T1.3 (NB04 offline từ 8 cache, exit 0, 0 mạng, cache không đổi), T1.6 (8 negative cases dừng rõ), T1.8 (NB05/NB06 đọc output NB04, không baseline). Dừng sau GateA.
- **GateB (F01):** CHƯA duyệt. Cần phép đo nhỏ + ngân sách trình user (fixture 14 hàng, rebuild cohort, walk-forward cắt 1.114 ngày hoặc tập thay thế, perturb 47 ngày).
- **GateC (regression cuối):** CHƯA duyệt. Chỉ sau GateA+B đạt và user duyệt; chạy NB01→06 ×1 lần trên SHA ứng viên + metric A–D/CI.

DA không sửa mã Dev; nếu GateA phát hiện lỗi, lưu counterexample ngắn rồi báo, không chạy tiếp tác vụ nặng. Không merge/đóng PR.
