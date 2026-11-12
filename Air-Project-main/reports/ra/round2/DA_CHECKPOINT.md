# DA_CHECKPOINT — GateA (F02) · phiên `arena/05796171-air-project-test`

Ngày: 12/11/2026 · Vai trò: AI-3 DA · Trạng thái: **GateA xong, dừng trước GateB/GateC (chờ duyệt)**.
Không merge/đóng PR. Không sửa mã Dev. Mọi số dưới đây là kết quả DA tự đo trên snapshot `a9757af`, không phải claim Dev.

## 1. Nguồn và SHA (đã fetch/xác nhận)
| Đối tượng | SHA | Ghi chú |
|---|---|---|
| Mã Dev để DA kiểm (đối tượng) | `a9757af398ddac2f8536e8019e4eb6b5900b4f75` | snapshot extract sang /tmp/devroot |
| Dev doc/evidence (HEAD nhánh) | `ce78795227b184d9ab0c9a2d38e9d0185169c501` | branch `arena/5cb21c04` |
| Protocol v1.0 | `e0eef8cccce7a09cbdbcb7de3cbdde9b35b2ab61` | giữ nguyên, chưa sửa |
| DA prep snapshot | `13e93ae12c483f01a573ee51ef9562a315e45068` | 47 evidence files |
| Amendment v1.1 (DA viết) | `e7f339f370a7e3abb20c98c18d5888fa19eff79e` | đã push |
| Checkpoint này | (commit kế tiếp trên nhánh phiên) | |

## 2. Kết quả GateA — F02 (NB04 cache-first offline + routing)
| Mã | Điều kiện | Kết quả | Bằng chứng (scratch, không commit) |
|---|---|---|---|
| T1.1 | Lock 3.11.2 cài được, `pip check` sạch | ✅ đạt | `/tmp/da_venv_install.log` (exit 0, "No broken requirements found") |
| T1.2 | NB04 16/16 ô `ast.parse` trên 3.11.2 | ✅ đạt | 16/16 OK, 0 SyntaxError |
| T1.3 | NB04 chạy trọn offline từ 8 cache, 0 mạng, cache không đổi | ✅ đạt | chain: `04` ok 16/16, 5.1s, network_attempts=0; `data_files_changed_in_copy=[]` |
| T1.4 | Nội dung bảng tạo lại so bản commit | ✅ đạt | `nb04_vs_committed_cells.csv`: 852 ô lệch, chỉ 3 cột (temp/pressure/wind), max 0.01; 8 cache đọc (provenance kind="raw đã commit") |
| T1.5 | Dung sai đã duyệt | ✅ đạt | 852 ô lệch đều trong dung sai; 11 cột còn lại 0 khác |
| T1.6 | 8 cache hỏng → dừng rõ, không ghi output | ✅ đạt | `test_nb04_with_a_broken_cache_stops_clearly_and_writes_nothing` 8/8 pass |
| T1.7 | Mock online / API thật | ⛔ blocked | 1 skip: sandbox không tới được `archive-api.open-meteo.com` (SSL). Trùng item "API thật ❓" của Dev; chỉ mock được Dev tự test |
| T1.8 | NB05/NB06 đọc output NB04, không baseline | ✅ đạt | provenance + chain_summary: NB05,NB06 đọc `outputs/nb04/weather_daily_8cities.csv` SHA `2c906e61…` ("KHÔNG phải baseline") |

**Tổng GateA: 7 đạt / 0 trượt / 1 blocked (T1.7, do môi trường, không phải lỗi mã Dev).**

## 3. Thời gian & tài nguyên (thực tế, đo được)
- Venv install (66 gói, pip 23.0.1): **~39 s**.
- Chain `04,05,06 --weather nb04` (network blocked): **~61 s** (NB04 5.1s + NB05 17.2s + NB06 37.6s).
- Targeted pytest (test_weather_cache + broken-cache): **~32 s** (44 passed, 1 skipped).
- Scratch GateA: **44 MB** (`/tmp/da_gateA`). Peak RSS không đo chính xác (không có `/usr/bin/time`); sau chạy còn 2.4 GB free, không OOM.
- Sản phẩm NB04: `weather_daily_8cities.csv` SHA `2c906e617ec965fe…` (khớp claim Dev `2c906e61…`); baseline `45f3579a222c55c0…` (khớp `45f3579a…`).

## 4. Claim Dev/RA đã tiếp xúc (CHƯA phải kết quả DA)
- `CLAIM-DEV` 211 tests (210/1 skip-API), 21 bước exit0, F01 0-cell leakage, cohort 8.668, 181 số trong half-unit, 18/18 CI chứa 0, NEW-R2-001/002 mở.
- `AUDIT-RA` 47 artifact SHA256 khớp, 327 dòng baseline trong dung sai, 8.668 khóa cohort khớp, 3 ca as-of nhỏ phù hợp.
- GateA ở trên MỚI là kết quả DA tự đo (F02 I/O + offline). F01/F02 chưa đóng; tiêu chí không đổi để khớp số Dev.

## 5. Dừng — GateB/GateC CHƯA chạy (chờ duyệt)
- Chưa chạy GateB (F01), chưa chạy GateC, chưa chạy toàn bộ pytest hay chuỗi NB01→06.
- Đề xuất GateB (sẽ trình riêng để duyệt): fixture 14 hàng (T2.4) + rebuild cohort từ raw (T2.2/T3) + walk-forward cắt tại 1.114 ngày hoặc tập thay thế 17+ mốc (T2.3) + perturb 47 ngày × loại (T2.3) + T2.5. Ngân sách dự kiến: vài phút đến vài chục phút tuỳ có dùng tập thay thế; giữ nguyên env đã cài.

## 6. Log paths (scratch, không commit)
- `/tmp/da_gateA_run.log` — stdout chain GateA.
- `/tmp/da_gateA/nb04/chain_summary.json` — exit, steps, data/repo unchanged, provenance summary.
- `/tmp/da_gateA/nb04/provenance.jsonl` — mọi file đọc/ghi (8 cache + output NB04 + NB05/NB06 read).
- `/tmp/da_gateA/nb04/proj/outputs/nb04/nb04_vs_committed_cells.csv` — 852 ô lệch + dung sai.
- `/tmp/da_venv_install.log` — T1.1.
