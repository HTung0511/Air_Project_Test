# GateA (F02) — Kết quả từng mục T1 (DA tự đo, snapshot `a9757af`)

| Mã | Kết quả | Bằng chứng chính |
|---|---|---|
| T1.1 | ✅ đạt | venv 3.11.2; `pip install -r requirements-lock.txt` exit 0; `pip check` sạch |
| T1.2 | ✅ đạt | 16/16 ô mã NB04 `ast.parse` OK trên 3.11.2, 0 SyntaxError |
| T1.3 | ✅ đạt | NB04 ok 16/16 ô, 5.1s, `network_attempts=0`; cache không đổi; `data_files_changed_in_copy=[]` |
| T1.4 | ✅ đạt | `nb04_vs_committed_cells.csv`: 852 ô lệch, chỉ `temp_mean`/`pressure_mean`/`wind_speed_mean`, max 0,01; 8 cache đọc (provenance "raw đã commit") |
| T1.5 | ✅ đạt | 852 ô lệch đều trong dung sai đã duyệt; 11 cột còn lại 0 khác |
| T1.6 | ✅ đạt | 8/8 ca cache hỏng dừng rõ, không ghi output nào (`broken_cache_cases.log`) |
| T1.7 | ⛔ blocked | API thật không tới được (`archive-api.open-meteo.com` SSL đóng ở sandbox); 1 skip — trùng item "API thật ❓" của Dev |
| T1.8 | ✅ đạt | NB05/NB06 đọc `outputs/nb04/weather_daily_8cities.csv` SHA `2c906e61…` ("KHÔNG phải baseline") |

**Tổng: 7 đạt / 0 trượt / 1 blocked (T1.7 do môi trường, không phải lỗi mã Dev).**

Chi tiết lệnh/SHA/môi trường: `command_sha.md`. Log gốc: `/tmp/da_gateA/nb04/` (chain_summary.json, provenance.jsonl).
