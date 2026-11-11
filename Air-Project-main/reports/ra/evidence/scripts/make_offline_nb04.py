"""Tạo bản NB04 chạy OFFLINE trong thư mục scratch (KHÔNG sửa notebook gốc trong repo).
Chỉ thay đúng 1 ô: `wu.smoke_test(); USE_BLH = bool(wu.probe_variable(...))` (hai lời gọi mạng) bằng việc
đọc USE_BLH từ 8 file cache. Mọi ô khác giữ nguyên từng ký tự. Lý do: sandbox DA chặn archive-api.open-meteo.com.
Dùng: python make_offline_nb04.py <work_root>
"""
import sys, nbformat, pathlib
root = pathlib.Path(sys.argv[1]); src = root / "notebooks" / "04_weather_merge.ipynb"
nb = nbformat.read(src, as_version=4); n = 0
for c in nb.cells:
    if c.cell_type == "code" and "wu.smoke_test()" in c.source:
        c.source = ("# [DA-offline] thay 2 lời gọi mạng (smoke_test, probe_variable) bằng đọc cache; mọi ô khác giữ nguyên\n"
                    "USE_BLH = all('boundary_layer_height' in pd.read_csv(wu.cache_path(c), nrows=1).columns for c in wu.CITIES)\n"
                    "print('Có boundary_layer_height trong cả 8 cache (offline):', USE_BLH)")
        n += 1
assert n == 1, n
nbformat.write(nb, root / "notebooks" / "04_weather_merge_offline.ipynb"); print("đã thay", n, "ô ->", root / "notebooks" / "04_weather_merge_offline.ipynb")
