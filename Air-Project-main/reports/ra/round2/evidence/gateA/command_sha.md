# GateA (F02) — Evidence index: commands, SHAs, environment

Bundle này là bằng chứng tối thiểu của GateA, do DA tự đo trên snapshot `a9757af`.
Không commit venv, cache, output lặp hay log khổng lồ. File gốc từ `/tmp` đã được copy vào đây.

## Môi trường
- Python 3.11.2 (CPython, Linux x86_64); venv `/tmp/da_venv_dev` (KHÔNG commit), dựng từ `requirements-lock.txt` (66 gói).
- `pip freeze` xem `pip_freeze.txt`. `pip check` sạch ("No broken requirements found").
- Mạng: sandbox không tới được `archive-api.open-meteo.com` (SSL đóng). `run_chain.py` mặc định chặn socket ở kernel.

## Nguồn dưới kiểm (SHA)
| Đối tượng | SHA |
|---|---|
| Mã Dev (đối tượng) | `a9757af398ddac2f8536e8019e4eb6b5900b4f75` (nhánh `arena/5cb21c04`, HEAD `ce78795227b184d9ab0c9a2d38e9d0185169c501`) |
| Protocol v1.0 | `e0eef8cccce7a09cbdbcb7de3cbdde9b35b2ab61` |
| DA prep snapshot | `13e93ae12c483f01a573ee51ef9562a315e45068` |
| Amendment v1.1 (DA) | `e7f339f370a7e3abb20c98c18d5888fa19eff79e` |
| Checkpoint GateA (DA) | `f11fd521c6091fa5b36c816052218f47df89c90a` |

## Lệnh DA đã chạy (độc lập)
1. Fetch snapshot: `git fetch --depth 1 origin a9757af…` rồi `git archive a9757af | tar -x` → `/tmp/devroot`.
2. Venv: `python3.11 -m venv /tmp/da_venv_dev`; `pip install -r requirements-lock.txt` (exit 0, ~39s).
3. T1.2: `ast.parse` từng ô mã NB04 → 16/16 OK, 0 SyntaxError.
4. T1.3/T1.8: `python tools/run_chain.py --work /tmp/da_gateA --name nb04 --notebooks 04,05,06 --weather nb04 --timeout 1500`
   → `chain_summary.json`: exit 0; `04` ok 16/16 5.1s 0 mạng; `05` ok 10/10 17.2s; `06` ok 27/27 37.6s; `network_blocked=true`; `data_files_changed_in_copy=[]`; `files_changed_in_repo=[]`.
5. T1.4/T1.5: `nb04_vs_committed_cells.csv` (852 ô lệch, max 0,01, chỉ `temp_mean`/`pressure_mean`/`wind_speed_mean`); `nb04_vs_committed_summary.csv`.
6. T1.6: `pytest tests/test_weather_cache.py "tests/test_notebooks_integration.py::test_nb04_with_a_broken_cache_stops_clearly_and_writes_nothing"` → 44 passed, 1 skipped → `broken_cache_cases.log`.
7. T1.7: test API thật skip (sandbox SSL) → blocked.

## SHA I/O chính
- NB04 sinh `weather_daily_8cities.csv` = `2c906e617ec965fe2a12e6f615ee77e9457a521928a162bf42efae3d828eabc7` (khớp claim Dev `2c906e61…`).
- Baseline committed `weather_daily_8cities.csv` = `45f3579a222c55c0156eb7571565bb7a818b89c64ad9b89eff97da02ef224c77` (khớp Dev `45f3579a…`).
- 8 cache weather raw đọc bởi NB04 (provenance kind "raw đã commit"): xem `provenance.jsonl`.

## File trong bundle
- `chain_summary.json` — tóm tắt chuỗi (exit, steps, data/repo unchanged, provenance summary).
- `provenance.jsonl` — mọi file đọc/ghi (8 cache + output NB04 + NB05/NB06 đọc output NB04).
- `nb04_vs_committed_summary.csv`, `nb04_vs_committed_cells.csv` — bảng tổng hợp + 852 ô lệch dung sai.
- `broken_cache_cases.log` — 8 ca cache hỏng (parametrized) pass rõ ràng.
- `pip_freeze.txt`, `environment.txt` — môi trường.
- `t1_results.md` — kết quả từng mục T1 (cũng ở `DA_CHECKPOINT.md`).
