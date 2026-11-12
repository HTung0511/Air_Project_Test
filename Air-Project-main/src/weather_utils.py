"""Hàm và hằng số dùng chung cho notebook thời tiết (`notebooks/04_weather_merge.ipynb`).

Việc làm: lấy thời tiết theo giờ của Open-Meteo (dữ liệu tái phân tích ERA5) cho 8 thành phố, kiểm tra, gộp theo ngày,
rồi ghép vào `data/processed/air_quality_8cities.csv`.

Quy ước (vòng 2, F02 - xem `reports/ra/round2/dev_change_log.md`):
  * ĐỌC CACHE TRƯỚC, theo từng thành phố. Cache hợp lệ = đủ cột bắt buộc (kể cả lớp biên khí quyển), đủ khoảng thời gian,
    đúng lưới giờ, không giờ trùng, không ô trống (`validate_hourly`). Cả 8 cache hợp lệ thì KHÔNG gọi mạng lần nào.
  * Mặc định OFFLINE: thiếu hoặc hỏng cache thì dừng với lỗi nêu rõ thành phố, file và tiêu chí hỏng; không bịa dữ liệu,
    không dùng bản cũ/bản thiếu thay thế. Chỉ khi đặt `AIR_WEATHER_MODE=online` mới tải, và chỉ tải thành phố cần tải.
  * Lớp biên khí quyển (`boundary_layer_height`) là biến BẮT BUỘC vì NB05/NB06 dùng `blh_mean`. Có hay không được xác định
    từ schema của cache; thiếu thì báo lỗi chứ không lặng lẽ bỏ.
  * Không sửa, không ghi đè file nào trong `data/`: cache gốc `data/raw/weather/` chỉ được đọc; bản tải mới lưu ở
    `outputs/weather_downloads/`; output mới của NB04 lưu ở `outputs/nb04/` (xem `src/data_paths.py`).
  * Không sửa `air_quality_8cities.csv`; bảng ghép là file riêng `air_quality_8cities_weather.csv`.
  * Chưa scale, chưa tạo biến trễ (lag): để bước dựng mô hình, sau khi chia train/test theo thời gian.
"""
import gzip
import json
import os
import platform
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

import data_paths

ROOT = Path(__file__).resolve().parents[1]
RAW_WEATHER = ROOT / "data" / "raw" / "weather"          # cache gốc đã commit: chỉ đọc
AQ_FILE = ROOT / "data" / "processed" / "air_quality_8cities.csv"
# Hai file baseline ĐÃ COMMIT. Giữ tên hằng số cũ để mã đang dùng không gãy, nhưng NB04 không còn ghi vào đây:
# output mới đi qua `save_outputs()` tới `output_paths()` (mặc định `outputs/nb04/`).
OUT_MERGED = ROOT / "data" / "processed" / "air_quality_8cities_weather.csv"
OUT_DAILY = ROOT / "data" / "processed" / "weather_daily_8cities.csv"
BASELINE_MERGED, BASELINE_DAILY = OUT_MERGED, OUT_DAILY

API_URL = "https://archive-api.open-meteo.com/v1/archive"
MODEL = "era5"                    # một mô hình duy nhất cho cả 8 thành phố; đặt None nếu API báo lỗi tham số `models`
TIMEZONE = "Asia/Kolkata"         # phải trùng múi giờ của "ngày" trong dữ liệu CPCB (UTC+5:30)
START, END = "2014-12-25", "2020-07-01"   # lấy dư vài ngày đầu để sau này tạo biến trễ mà không mất ngày đầu
ATTRIBUTION = "Weather data by Open-Meteo.com (CC BY 4.0), dữ liệu tái phân tích ERA5 (ECMWF / Copernicus)"

CITIES = ["Delhi", "Gurugram", "Lucknow", "Jaipur", "Bengaluru", "Amritsar", "Chennai", "Hyderabad"]
KEYS = ["City", "Date"]

# toạ độ trung tâm thành phố (gần đúng); API sẽ trả về toạ độ ô lưới thật sự được dùng
CITY_COORDS = {
    "Delhi":     (28.61, 77.21),
    "Gurugram":  (28.46, 77.03),
    "Lucknow":   (26.85, 80.95),
    "Jaipur":    (26.91, 75.79),
    "Bengaluru": (12.97, 77.59),
    "Amritsar":  (31.63, 74.87),
    "Chennai":   (13.08, 80.27),
    "Hyderabad": (17.39, 78.49),
}

HOURLY_CORE = ["temperature_2m", "relative_humidity_2m", "surface_pressure",
               "wind_speed_10m", "wind_direction_10m", "precipitation"]
HOURLY_EXTRA = ["boundary_layer_height"]      # lớp biên khí quyển: NB05/NB06 cần `blh_mean`
REQUIRED_HOURLY = HOURLY_CORE + HOURLY_EXTRA   # biến bắt buộc của một cache hợp lệ (BLH không còn là tuỳ chọn)
PROVENANCE_COLS = ["grid_lat", "grid_lon", "grid_elev"]   # ô lưới ERA5 thật sự được dùng, API trả về; giữ để truy nguồn
# đơn vị API phải trả (yêu cầu `wind_speed_unit=ms`); bản tải mới sai đơn vị hoặc sai múi giờ thì bị từ chối, không lưu
HOURLY_UNITS = {"temperature_2m": "°C", "relative_humidity_2m": "%", "surface_pressure": "hPa", "wind_speed_10m": "m/s",
                "wind_direction_10m": "°", "precipitation": "mm", "boundary_layer_height": "m"}
UTC_OFFSET_SECONDS = 19800                     # Asia/Kolkata = UTC+5:30, không có giờ mùa hè nên ngày nào cũng đủ 24 giờ
RETRY_SLEEP = 5                                # giây chờ giữa các lần thử lại (nhân với số lần đã thử)
N_API_CALLS = 0                                # số lần đã gọi `requests.get` trong tiến trình này (cache đủ thì phải là 0)

# dung sai khi so bảng theo ngày mới với baseline đã commit (RA-DEC-02 mục 5). `hourly_to_daily` làm tròn 2 chữ số; khi
# trung bình 24 giờ rơi đúng biên x,xx5 thì sai khác 1 đơn vị cuối của phép cộng số thực (khác phiên bản numpy/pandas) làm
# tròn lên hoặc xuống. Chỉ ba cột trung bình dưới đây được lệch, chỉ tối đa 0,01 và chỉ tại ô chứng minh được là sát biên.
TOL_MEAN_COLS = {"temp_mean": "temperature_2m", "pressure_mean": "surface_pressure", "wind_speed_mean": "wind_speed_10m"}
ROUND_TOL = 0.01          # 1 đơn vị ở chữ số thập phân thứ hai
ABS_EPS = 1e-9            # sai số số học cho mọi phép so số thực (đọc/ghi CSV)
BOUNDARY_EPS = 1e-6       # "sát biên": phần lẻ của (trung bình chưa làm tròn x 100) cách 0,5 không quá ngưỡng này
EXACT_COLS = ["rain_day", "wind_dir_8"]        # so chính xác
RAIN_DAY_MM = 1.0                              # ngày mưa = tổng mưa >= 1 mm (ngưỡng thường dùng trong khí tượng)
DIRS8 = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

# (cột, kiểu, đơn vị, ý nghĩa, cách tính từ dữ liệu theo giờ)
WEATHER_DICT = [
    ("temp_mean", "float", "°C", "Nhiệt độ không khí ở độ cao 2 m, trung bình ngày", "mean của 24 giá trị giờ"),
    ("temp_min", "float", "°C", "Nhiệt độ thấp nhất trong ngày", "min của 24 giá trị giờ"),
    ("temp_max", "float", "°C", "Nhiệt độ cao nhất trong ngày", "max của 24 giá trị giờ"),
    ("humidity_mean", "float", "%", "Độ ẩm tương đối ở 2 m, trung bình ngày", "mean của 24 giá trị giờ"),
    ("pressure_mean", "float", "hPa", "Áp suất bề mặt, trung bình ngày (phụ thuộc độ cao: Bengaluru thấp hơn các thành phố khác)", "mean của 24 giá trị giờ"),
    ("wind_speed_mean", "float", "m/s", "Tốc độ gió ở 10 m, trung bình ngày", "mean của 24 giá trị giờ"),
    ("wind_speed_max", "float", "m/s", "Tốc độ gió giờ lớn nhất trong ngày", "max của 24 giá trị giờ"),
    ("wind_u", "float", "m/s", "Thành phần gió hướng Đông (dương = gió thổi về phía Đông), trung bình ngày", "u = -tốc độ × sin(hướng), rồi mean theo ngày"),
    ("wind_v", "float", "m/s", "Thành phần gió hướng Bắc (dương = gió thổi về phía Bắc), trung bình ngày", "v = -tốc độ × cos(hướng), rồi mean theo ngày"),
    ("wind_dir_8", "text", "—", "Hướng gió chính trong ngày (gió thổi TỪ hướng nào), 8 hướng. Chỉ để mô tả, không dùng làm biến số", "hướng của vector (wind_u, wind_v), làm tròn 8 hướng"),
    ("precip_sum", "float", "mm", "Tổng lượng mưa trong ngày", "sum của 24 giá trị giờ"),
    ("rain_day", "bool", "—", f"True nếu tổng mưa >= {RAIN_DAY_MM:g} mm", "precip_sum >= ngưỡng"),
]
WEATHER_DICT_BLH = [
    ("blh_mean", "float", "m", "Chiều cao lớp biên khí quyển, trung bình ngày (thấp = chất ô nhiễm bị nén sát mặt đất)", "mean của 24 giá trị giờ"),
    ("blh_min", "float", "m", "Chiều cao lớp biên thấp nhất trong ngày", "min của 24 giá trị giờ"),
]

# giới hạn vật lý: ngoài khoảng này là lỗi dữ liệu hoặc lỗi đơn vị, không phải thời tiết thật
RANGES = {
    "temp_mean": (-10, 50), "temp_min": (-10, 50), "temp_max": (-10, 55),
    "humidity_mean": (0, 100), "pressure_mean": (800, 1100),
    "wind_speed_mean": (0, 25), "wind_speed_max": (0, 40),
    "precip_sum": (0, 500),
    "blh_mean": (0, 4500), "blh_min": (0, 4500),      # chỉ kiểm khi cột có trong bảng
}


# ----------------------------------------------------------------------------- lỗi có ngữ cảnh
class WeatherError(Exception):
    """Lỗi của bước lấy thời tiết. Cố ý KHÔNG kế thừa RuntimeError để các khối `except RuntimeError` không nuốt mất nó."""


class WeatherOfflineError(WeatherError):
    """Có đoạn mã định gọi mạng trong khi đang ở chế độ offline."""


class WeatherCacheError(WeatherError):
    """Không có nguồn dữ liệu giờ hợp lệ cho ít nhất một thành phố (thiếu file hoặc file không qua kiểm tra)."""


class WeatherDownloadError(WeatherError):
    """Gọi API thất bại, hoặc API trả dữ liệu không dùng được. Thông báo luôn nêu thành phố, file đích và biến."""


def network_mode(mode=None):
    """'offline' (mặc định) hoặc 'online'. Lấy từ tham số, nếu không có thì từ biến môi trường `AIR_WEATHER_MODE`."""
    m = (mode or os.environ.get(data_paths.ENV_MODE) or "offline").strip().lower()
    if m not in ("offline", "online"):
        raise ValueError(f"Chế độ thời tiết không hợp lệ: {m!r} (chỉ nhận 'offline' hoặc 'online')")
    return m


def _vars_text(variables):
    return ", ".join(variables)


# ----------------------------------------------------------------------------- gọi API (chỉ khi online)
def _request(params, retries=5):
    """Gọi API, tự thử lại khi bị giới hạn tần suất (429) hoặc lỗi máy chủ (5xx). Nơi DUY NHẤT gọi `requests.get`."""
    global N_API_CALLS
    for attempt in range(1, retries + 1):
        N_API_CALLS += 1
        try:
            r = requests.get(API_URL, params=params, timeout=120)
        except requests.RequestException as e:
            if attempt == retries:
                raise
            print(f"  lỗi mạng ({e.__class__.__name__}), thử lại sau {RETRY_SLEEP * attempt}s")
            time.sleep(RETRY_SLEEP * attempt)
            continue
        if r.status_code == 200:
            return r.json()
        if r.status_code == 429:
            print("  bị giới hạn tần suất (429), chờ rồi thử lại")
            time.sleep(13 * RETRY_SLEEP)
            continue
        if r.status_code >= 500:
            time.sleep(RETRY_SLEEP * attempt)
            continue
        try:
            reason = r.json().get("reason", r.text)
        except ValueError:
            reason = r.text
        raise RuntimeError(f"Open-Meteo trả lỗi {r.status_code}: {reason}")
    raise RuntimeError("Hết số lần thử mà API vẫn không trả dữ liệu")


def _params(city, variables, start, end):
    lat, lon = CITY_COORDS[city]
    p = {"latitude": lat, "longitude": lon, "start_date": start, "end_date": end,
         "hourly": ",".join(variables), "timezone": TIMEZONE, "wind_speed_unit": "ms"}
    if MODEL:
        p["models"] = MODEL
    return p


def _to_frame(data, variables):
    h = pd.DataFrame({"time": data["hourly"]["time"], **{v: data["hourly"][v] for v in variables}})
    h["grid_lat"], h["grid_lon"], h["grid_elev"] = data["latitude"], data["longitude"], data.get("elevation", np.nan)
    return h


def _context(city, target, variables, start, end):
    where = f"file đích: {data_paths.show(target)}" if target is not None else "không lưu file"
    return f"thành phố {city}; {where}; biến: {_vars_text(variables)}; khoảng {start} -> {end}"


def _check_response(data, city, variables, target, start, end):
    """API phải trả đủ biến, đúng múi giờ và đúng đơn vị; nếu không thì từ chối (không lưu, không dùng)."""
    ctx = _context(city, target, variables, start, end)
    hourly = data.get("hourly") if isinstance(data, dict) else None
    if not isinstance(hourly, dict) or "time" not in hourly:
        raise WeatherDownloadError(f"API không trả khối `hourly` có cột time ({ctx}).")
    for v in variables:
        if v not in hourly:
            raise WeatherDownloadError(f"API không trả biến `{v}` ({ctx}).")
        if len(hourly[v]) != len(hourly["time"]):
            raise WeatherDownloadError(f"API trả biến `{v}` có {len(hourly[v])} giá trị, khác số mốc giờ {len(hourly['time'])} ({ctx}).")
        if not pd.Series(hourly[v], dtype="float64").notna().any():
            raise WeatherDownloadError(f"API trả toàn giá trị rỗng cho biến `{v}` ({ctx}). Không bỏ biến này để chạy tiếp.")
    if data.get("timezone") != TIMEZONE:
        raise WeatherDownloadError(f"API trả múi giờ {data.get('timezone')!r}, mong đợi {TIMEZONE!r} ({ctx}).")
    if data.get("utc_offset_seconds", UTC_OFFSET_SECONDS) != UTC_OFFSET_SECONDS:
        raise WeatherDownloadError(f"API trả độ lệch UTC {data.get('utc_offset_seconds')} giây, mong đợi {UTC_OFFSET_SECONDS} ({ctx}).")
    units = data.get("hourly_units")
    if not isinstance(units, dict):
        raise WeatherDownloadError(f"API không trả `hourly_units` nên không xác nhận được đơn vị ({ctx}).")
    for v in variables:
        if units.get(v) != HOURLY_UNITS[v]:
            raise WeatherDownloadError(f"Biến `{v}`: API trả đơn vị {units.get(v)!r}, mong đợi {HOURLY_UNITS[v]!r} ({ctx}).")


def _download(city, variables, start, end, mode=None, target=None):
    """Một lần gọi API cho một thành phố. Chỉ chạy khi online; lỗi nào cũng nêu thành phố, file đích và biến."""
    ctx = _context(city, target, variables, start, end)
    if network_mode(mode) != "online":
        raise WeatherOfflineError(f"Đang ở chế độ offline nên không gọi API ({ctx}). Muốn tải: đặt {data_paths.ENV_MODE}=online.")
    try:
        data = _request(_params(city, variables, start, end))
    except (requests.RequestException, RuntimeError, ValueError) as e:
        raise WeatherDownloadError(f"Không tải được thời tiết ({ctx}). Lỗi: {type(e).__name__}: {e}") from e
    _check_response(data, city, variables, target, start, end)
    h = _to_frame(data, variables)
    h.attrs.update(from_cache=False, source="API", api_meta={
        k: data.get(k) for k in ("latitude", "longitude", "elevation", "timezone", "timezone_abbreviation",
                                 "utc_offset_seconds", "generationtime_ms", "hourly_units")})
    return h


# ----------------------------------------------------------------------------- kiểm tra một bảng theo giờ
def _expected_grid(start, end):
    return pd.date_range(pd.Timestamp(start), pd.Timestamp(end) + pd.Timedelta(hours=23), freq="h")


def validate_hourly(h, variables=None, start=START, end=END):
    """Kiểm một bảng theo giờ có dùng được không. Trả về (bảng đã cắt đúng [start, end] hoặc None, số liệu, danh sách vấn đề).

    Tiêu chí: đủ cột (time, biến bắt buộc, cột ô lưới); cột time đọc được và tăng dần; đủ mọi giờ của [start, end], không
    giờ nào trùng, không mốc nào lệch lưới giờ; biến là số và không có ô trống. Danh sách vấn đề rỗng nghĩa là hợp lệ.
    """
    variables = list(variables or REQUIRED_HOURLY)
    problems = []
    stats = {"so_dong_file": len(h), "co_BLH": "boundary_layer_height" in h.columns}
    missing_cols = [c for c in ["time"] + variables + PROVENANCE_COLS if c not in h.columns]
    if missing_cols:
        problems.append("thiếu cột: " + ", ".join(missing_cols))
    if "time" not in h.columns:
        return None, stats, problems

    t = pd.to_datetime(h["time"].astype(str), format="%Y-%m-%dT%H:%M", errors="coerce")
    n_bad = int(t.isna().sum())
    if n_bad:
        problems.append(f"{n_bad} dòng có cột time không đọc được (mong đợi dạng YYYY-MM-DDTHH:MM)")
    if not t.dropna().is_monotonic_increasing:
        problems.append("cột time không tăng dần")

    grid = _expected_grid(start, end)
    inside = t.between(grid[0], grid[-1])
    ti = t[inside]
    n_dup = int(ti.duplicated().sum())
    n_off = int((~ti.isin(grid)).sum())
    missing_hours = grid.difference(pd.DatetimeIndex(ti.unique()))
    stats.update(so_dong=int(inside.sum()), mong_doi=len(grid), gio_trung=n_dup, gio_thieu=len(missing_hours), gio_lech_luoi=n_off,
                 dau=ti.min().strftime("%Y-%m-%d %H:%M") if len(ti) else None, cuoi=ti.max().strftime("%Y-%m-%d %H:%M") if len(ti) else None)
    if n_dup:
        problems.append(f"{n_dup} giờ bị trùng (ví dụ {ti[ti.duplicated()].iloc[0]:%Y-%m-%d %H:%M})")
    if n_off:
        problems.append(f"{n_off} mốc thời gian không nằm trên lưới giờ")
    if len(missing_hours):
        problems.append(f"thiếu {len(missing_hours)} giờ trong khoảng {start} -> {end} (ví dụ {missing_hours[0]:%Y-%m-%d %H:%M})")

    out = h.loc[inside.to_numpy()].reset_index(drop=True)
    empty = {}
    for v in variables:
        if v not in h.columns:
            continue
        if not pd.api.types.is_numeric_dtype(out[v]):
            problems.append(f"biến `{v}` không phải kiểu số")
            continue
        n_nan = int(out[v].isna().sum())
        if n_nan:
            empty[v] = n_nan
            first = pd.to_datetime(out.loc[out[v].isna(), "time"].iloc[0])
            problems.append(f"biến `{v}` có {n_nan} ô trống (ô đầu tiên {first:%Y-%m-%d %H:%M})")
    stats["o_trong"] = int(sum(empty.values()))
    stats["o_trong_theo_bien"] = empty
    for c in ("grid_lat", "grid_lon"):
        if c in out.columns and len(out) and (out[c].isna().any() or out[c].nunique() != 1):
            problems.append(f"cột `{c}` trống hoặc không cố định trong file (mỗi thành phố chỉ dùng một ô lưới)")
    return out, stats, problems


def cache_path(city, cache_dir=None):
    return Path(cache_dir or data_paths.weather_cache_dir()) / f"openmeteo_{city.lower()}_hourly.csv.gz"


def download_path(city, download_dir=None):
    return Path(download_dir or data_paths.weather_download_dir()) / f"openmeteo_{city.lower()}_hourly.csv.gz"


def validate_cache(city, path, variables=None, start=START, end=END):
    """Đọc và kiểm một file cache. Trả về dict: city, path, exists, sha256, ok, problems, stats, frame (bảng đã cắt)."""
    path = Path(path)
    rep = {"city": city, "path": path, "exists": path.is_file(), "sha256": None, "ok": False, "problems": [], "stats": {}, "frame": None}
    if not rep["exists"]:
        rep["problems"] = ["không có file"]
        return rep
    rep["sha256"] = data_paths.sha256_file(path)
    try:
        h = pd.read_csv(path)
    except Exception as e:                                  # noqa: BLE001 - file hỏng kiểu gì cũng phải thành một vấn đề được báo
        rep["problems"] = [f"không đọc được file ({type(e).__name__}: {e})"]
        return rep
    rep["frame"], rep["stats"], rep["problems"] = validate_hourly(h, variables, start, end)
    rep["ok"] = not rep["problems"]
    return rep


def _sources(city, cache_dir=None, download_dir=None):
    """Thứ tự tìm dữ liệu giờ của một thành phố: cache gốc (chỉ đọc) rồi tới bản tải mới của các lần chạy online trước."""
    return [("cache gốc", cache_path(city, cache_dir)), ("bản tải mới", download_path(city, download_dir))]


def _find_valid(city, variables, start, end, cache_dir, download_dir):
    reports = []
    for kind, path in _sources(city, cache_dir, download_dir):
        rep = validate_cache(city, path, variables, start, end)
        rep["kind"] = kind
        reports.append(rep)
        if rep["ok"]:
            return rep, reports
    return None, reports


def _why_invalid(city, reports):
    return [f"  - {city}, {r['kind']} {data_paths.show(r['path'])}: " + "; ".join(r["problems"]) for r in reports]


def cache_status(variables=None, cities=CITIES, start=START, end=END, cache_dir=None, download_dir=None):
    """Bảng tình trạng dữ liệu giờ của từng thành phố. Chỉ đọc file, KHÔNG gọi mạng."""
    variables = list(variables or REQUIRED_HOURLY)
    rows = []
    for c in cities:
        good, reports = _find_valid(c, variables, start, end, cache_dir, download_dir)
        r = good or reports[0]
        st = r["stats"]
        rows.append({"City": c, "hop_le": good is not None, "nguon": r["kind"] if good else "không có nguồn hợp lệ",
                     "file": data_paths.show(r["path"]), "sha256_16": (r["sha256"] or "")[:16],
                     "so_dong": st.get("so_dong"), "mong_doi": st.get("mong_doi"), "gio_trung": st.get("gio_trung"),
                     "gio_thieu": st.get("gio_thieu"), "o_trong": st.get("o_trong"), "co_BLH": st.get("co_BLH"),
                     "van_de": "" if good else " | ".join("; ".join(x["problems"]) for x in reports)})
    return pd.DataFrame(rows).set_index("City")


def _save_download(h, city, target, variables, start, end):
    """Lưu bản tải mới. Mở file ở chế độ tạo mới ('x'): không bao giờ ghi đè một file đã có."""
    target.parent.mkdir(parents=True, exist_ok=True)
    data_paths.check_writable(target)
    with open(target, "xb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as gz:
            gz.write(h.to_csv(index=False).encode("utf-8"))
    meta = {"city": city, "file": target.name, "sha256": data_paths.sha256_file(target), "rows": len(h),
            "api_url": API_URL, "params": _params(city, variables, start, end), "response": h.attrs.get("api_meta"),
            "downloaded_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "attribution": ATTRIBUTION}
    Path(str(target) + ".provenance.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    return meta


def fetch_city(city, variables=None, start=START, end=END, use_cache=True, mode=None, cache_dir=None, download_dir=None):
    """Dữ liệu theo giờ của một thành phố, ĐỌC CACHE TRƯỚC.

    Có nguồn hợp lệ (cache gốc, hoặc bản tải mới của lần chạy online trước) thì đọc lại và không gọi API. Không có thì:
    offline -> `WeatherCacheError` nêu file và tiêu chí hỏng; online -> tải đúng thành phố này, kiểm bằng cùng bộ tiêu chí,
    lưu vào thư mục bản tải mới (không ghi đè file nào). `use_cache=False` chỉ dành cho thử API: gọi thẳng, không lưu.
    """
    variables = list(variables or REQUIRED_HOURLY)
    if not use_cache:
        return _download(city, variables, start, end, mode=mode)
    good, reports = _find_valid(city, variables, start, end, cache_dir, download_dir)
    if good is not None:
        h = good["frame"]
        h.attrs.update(from_cache=True, source=good["kind"], path=str(good["path"]), sha256=good["sha256"])
        data_paths.record_input(f"thời tiết theo giờ {city} ({good['kind']})", good["path"], quiet=True)
        return h
    why = _why_invalid(city, reports)
    target = download_path(city, download_dir)
    if network_mode(mode) != "online":
        raise WeatherCacheError(
            f"Không có dữ liệu thời tiết theo giờ hợp lệ cho {city} (chế độ offline, không gọi mạng):\n" + "\n".join(why)
            + f"\nBiến bắt buộc: {_vars_text(variables)}. Khoảng: {start} -> {end}."
            + f"\nCách xử lý: khôi phục file cache gốc, hoặc cho tải lại bằng {data_paths.ENV_MODE}=online "
              f"(bản tải mới lưu ở {data_paths.show(target.parent)}, không ghi đè file gốc).")
    if target.exists():
        raise WeatherCacheError(
            f"{city}: bản tải trước đó {data_paths.show(target)} không hợp lệ và sẽ không bị ghi đè:\n" + "\n".join(why)
            + "\nHãy tự xoá hoặc đổi tên file đó rồi chạy lại.")
    h = _download(city, variables, start, end, mode=mode, target=target)
    checked, _, problems = validate_hourly(h, variables, start, end)
    if problems:
        raise WeatherDownloadError(f"Dữ liệu vừa tải không qua kiểm tra nên không lưu ({_context(city, target, variables, start, end)}): "
                                   + "; ".join(problems))
    meta = _save_download(h, city, target, variables, start, end)
    checked.attrs.update(from_cache=False, source="API (vừa tải)", path=str(target), sha256=meta["sha256"], api_meta=h.attrs.get("api_meta"))
    data_paths.record_output(f"bản tải mới thời tiết theo giờ {city}", target, quiet=True)
    return checked


def fetch_all(variables=None, cities=CITIES, pause=3, mode=None, cache_dir=None, download_dir=None, start=START, end=END):
    """Dữ liệu giờ của các thành phố, trả về dict {thành phố: bảng theo giờ}. Đọc cache trước; chỉ tải thành phố thiếu.

    Offline mà có thành phố không có nguồn hợp lệ: dừng TRƯỚC khi trả bất cứ thứ gì, liệt kê mọi thành phố có vấn đề.
    """
    variables = list(variables or REQUIRED_HOURLY)
    m = network_mode(mode)
    if m != "online":
        bad = []
        for c in cities:
            good, reports = _find_valid(c, variables, start, end, cache_dir, download_dir)
            if good is None:
                bad += _why_invalid(c, reports)
        if bad:
            raise WeatherCacheError(
                "Không có dữ liệu thời tiết theo giờ hợp lệ (chế độ offline, không gọi mạng):\n" + "\n".join(bad)
                + f"\nBiến bắt buộc: {_vars_text(variables)}. Khoảng: {start} -> {end}."
                + f"\nCách xử lý: khôi phục file cache gốc, hoặc cho tải lại bằng {data_paths.ENV_MODE}=online "
                  f"(bản tải mới lưu ở {data_paths.show(data_paths.weather_download_dir() if download_dir is None else download_dir)}, "
                  f"không ghi đè file gốc).")
    out = {}
    for i, c in enumerate(cities):
        out[c] = fetch_city(c, variables, start, end, mode=m, cache_dir=cache_dir, download_dir=download_dir)
        cached = out[c].attrs.get("from_cache", False)
        print(f"{c}: {len(out[c]):,} dòng giờ ({out[c].attrs.get('source')}: {data_paths.show(out[c].attrs['path'])}, "
              f"sha256 {out[c].attrs['sha256'][:16]})")
        if not cached and i < len(cities) - 1:
            time.sleep(pause)
    return out


def smoke_test(mode=None):
    """Tải thử 7 ngày của Delhi, không lưu. Chỉ để chẩn đoán API khi ONLINE; NB04 không còn gọi hàm này."""
    h = fetch_city("Delhi", HOURLY_CORE, "2019-01-01", "2019-01-07", use_cache=False, mode=mode)
    print(f"OK: {len(h)} dòng giờ (mong đợi 168), ô lưới dùng: lat {h.grid_lat[0]}, lon {h.grid_lon[0]}, cao {h.grid_elev[0]} m")
    return h


def probe_variable(var, mode=None):
    """True nếu API trả được biến `var` (có giá trị thật) cho Delhi. Chỉ để chẩn đoán khi ONLINE; NB04 không còn gọi.

    Lỗi mạng hoặc đang offline KHÔNG được hiểu là "API không có biến này": ném lỗi, để không ai dựa vào kết quả False giả
    mà bỏ biến. Chỉ khi API trả lời rõ là không phục vụ được (lỗi 4xx, thiếu biến, toàn rỗng) mới trả False.
    """
    ctx = _context("Delhi", None, [var], "2019-01-01", "2019-01-07")
    if network_mode(mode) != "online":
        raise WeatherOfflineError(f"Đang ở chế độ offline nên không thử được biến qua API ({ctx}).")
    try:
        data = _request(_params("Delhi", [var], "2019-01-01", "2019-01-07"), retries=2)
    except requests.RequestException as e:
        raise WeatherDownloadError(f"Không thử được biến qua API ({ctx}). Lỗi mạng: {type(e).__name__}: {e}") from e
    except RuntimeError as e:
        print(f"API không phục vụ được {var}: {e}")
        return False
    values = data.get("hourly", {}).get(var)
    return values is not None and bool(pd.Series(values, dtype="float64").notna().any())


# ----------------------------------------------------------------------------- kiểm tra dữ liệu giờ
def check_hourly(h, variables, start=START, end=END):
    """Số liệu kiểm tra cho bảng theo giờ của một thành phố (notebook sẽ assert trên kết quả)."""
    t = pd.to_datetime(h["time"])
    expected_days = (pd.Timestamp(end) - pd.Timestamp(start)).days + 1
    return {
        "so_dong": len(h),
        "mong_doi": expected_days * 24,
        "gio_trung": int(t.duplicated().sum()),
        "o_trong": int(h[variables].isna().sum().sum()),
        "dau": t.min().strftime("%Y-%m-%d %H:%M"),
        "cuoi": t.max().strftime("%Y-%m-%d %H:%M"),
    }


# ----------------------------------------------------------------------------- gộp theo ngày
def _dir8(u, v):
    deg = (np.degrees(np.arctan2(-u, -v)) + 360) % 360          # gió thổi TỪ hướng này
    idx = ((deg + 22.5) // 45).astype(int) % 8
    return pd.Series(np.array(DIRS8)[idx.to_numpy()], index=u.index)


def hourly_to_daily(h):
    """Gộp bảng theo giờ của một thành phố thành bảng theo ngày (theo múi giờ Asia/Kolkata)."""
    h = h.copy()
    h["Date"] = pd.to_datetime(h["time"]).dt.normalize()
    ang = np.deg2rad(h["wind_direction_10m"])
    h["_u"] = -h["wind_speed_10m"] * np.sin(ang)                # hướng gió là hướng gió thổi TỪ đâu, nên có dấu trừ
    h["_v"] = -h["wind_speed_10m"] * np.cos(ang)
    g = h.groupby("Date")
    d = pd.DataFrame({
        "temp_mean": g["temperature_2m"].mean(),
        "temp_min": g["temperature_2m"].min(),
        "temp_max": g["temperature_2m"].max(),
        "humidity_mean": g["relative_humidity_2m"].mean(),
        "pressure_mean": g["surface_pressure"].mean(),
        "wind_speed_mean": g["wind_speed_10m"].mean(),
        "wind_speed_max": g["wind_speed_10m"].max(),
        "wind_u": g["_u"].mean(),
        "wind_v": g["_v"].mean(),
        "precip_sum": g["precipitation"].sum(min_count=1),
    })
    if "boundary_layer_height" in h.columns:
        d["blh_mean"] = g["boundary_layer_height"].mean()
        d["blh_min"] = g["boundary_layer_height"].min()
    num = d.columns
    d[num] = d[num].round(2)
    d["rain_day"] = d["precip_sum"] >= RAIN_DAY_MM
    d["wind_dir_8"] = _dir8(d["wind_u"], d["wind_v"])
    d["n_hours"] = g.size()                                     # cột kiểm tra, bỏ ở bước cuối
    return d.reset_index()


def build_daily(hourly):
    """Ghép các thành phố thành một bảng theo ngày: City, Date, các cột thời tiết (cột kiểm tra n_hours đã được assert rồi bỏ)."""
    parts = []
    for city, h in hourly.items():
        d = hourly_to_daily(h)
        d.insert(0, "City", city)
        parts.append(d)
    daily = pd.concat(parts, ignore_index=True)
    bad = daily[daily["n_hours"] != 24]
    assert bad.empty, f"{len(bad)} ngày không đủ 24 giờ, ví dụ:\n{bad.head()}"
    return daily.drop(columns="n_hours")


def weather_cols(daily):
    return [c for c in daily.columns if c not in KEYS]


# ----------------------------------------------------------------------------- kiểm tra hợp lý
def check_ranges(daily):
    """Các ô nằm ngoài giới hạn vật lý (RANGES) và ngày có nhiệt độ min > mean hoặc mean > max. Mong đợi: bảng rỗng."""
    rows = []
    for col, (lo, hi) in RANGES.items():
        if col not in daily.columns:
            continue
        bad = daily[(daily[col] < lo) | (daily[col] > hi)]
        rows += [bad.assign(vi_pham=f"{col} ngoài [{lo}, {hi}]")[KEYS + [col, "vi_pham"]].rename(columns={col: "gia_tri"})]
    order = daily[(daily["temp_min"] > daily["temp_mean"] + 0.01) | (daily["temp_mean"] > daily["temp_max"] + 0.01)]
    rows += [order.assign(vi_pham="temp_min <= temp_mean <= temp_max bị vi phạm", gia_tri=order["temp_mean"])[KEYS + ["gia_tri", "vi_pham"]]]
    return pd.concat(rows, ignore_index=True)


def soft_checks(daily):
    """Kiểm tra theo kiến thức khí hậu. Chỉ cảnh báo (không dừng), vì ngưỡng là ước lượng thô."""
    d = daily.assign(month=daily["Date"].dt.month, year=daily["Date"].dt.year)
    warns = []
    jan = d[d.month == 1].groupby("City")["temp_mean"].mean()
    may = d[d.month == 5].groupby("City")["temp_mean"].mean()
    if jan["Amritsar"] >= 15:
        warns.append(f"Amritsar tháng 1 trung bình {jan['Amritsar']:.1f}°C, cao bất thường cho mùa đông Punjab (mong đợi dưới 15)")
    if jan["Chennai"] <= 22:
        warns.append(f"Chennai tháng 1 trung bình {jan['Chennai']:.1f}°C, thấp bất thường (mong đợi trên 22)")
    if may["Chennai"] <= 30:
        warns.append(f"Chennai tháng 5 trung bình {may['Chennai']:.1f}°C, thấp bất thường (mong đợi trên 30)")
    full = d[(d.year >= 2016) & (d.year <= 2019)]
    for c in ["Delhi", "Jaipur", "Lucknow"]:
        x = full[full.City == c]
        share = x[x.month.between(6, 9)]["precip_sum"].sum() / x["precip_sum"].sum()
        if share < 0.6:
            warns.append(f"{c}: chỉ {share:.0%} lượng mưa rơi vào tháng 6-9, thấp bất thường cho vùng gió mùa hè (mong đợi trên 60%)")
    return warns


def city_summary(daily):
    """Bảng tóm tắt theo thành phố, dùng cho nhật ký và để mắt thường kiểm tra."""
    d = daily.assign(year=daily["Date"].dt.year)
    full = d[d.year.between(2016, 2019)]
    return pd.DataFrame({
        "so_ngay": d.groupby("City").size(),
        "nhiet_do_tb": d.groupby("City")["temp_mean"].mean().round(1),
        "do_am_tb": d.groupby("City")["humidity_mean"].mean().round(0),
        "gio_tb_m/s": d.groupby("City")["wind_speed_mean"].mean().round(1),
        "mua_mm_moi_nam": (full.groupby("City")["precip_sum"].sum() / 4).round(0),
        "ty_le_ngay_mua": d.groupby("City")["rain_day"].mean().round(2),
    }).loc[CITIES]


# ----------------------------------------------------------------------------- ghép vào bảng chính
def merge_weather(aq, daily):
    """Ghép trái theo (City, Date). Mỗi dòng của bảng chính khớp đúng một dòng thời tiết (validate m:1)."""
    return aq.merge(daily, on=KEYS, how="left", validate="m:1")


def dictionary_markdown(has_blh=False):
    rows = WEATHER_DICT + (WEATHER_DICT_BLH if has_blh else [])
    lines = ["| Cột | Kiểu | Đơn vị | Ý nghĩa | Cách tính |", "|---|---|---|---|---|"]
    lines += [f"| `{c}` | {t} | {u} | {m} | {h} |" for c, t, u, m, h in rows]
    return "\n".join(lines)


# ----------------------------------------------------------------------------- lưu output mới (không ghi đè baseline)
def output_paths(out_dir=None):
    """(file bảng ghép, file thời tiết theo ngày) mà NB04 sẽ ghi. Mặc định `outputs/nb04/`, đổi bằng `AIR_NB04_OUT_DIR`."""
    d = Path(out_dir) if out_dir is not None else data_paths.nb04_out_dir()
    return d / data_paths.MERGED_NAME, d / data_paths.DAILY_NAME


def save_outputs(merged, daily, hourly=None, out_dir=None):
    """Ghi hai bảng output của NB04 và một file `nb04_manifest.json` (đầu vào, đầu ra, sha256, môi trường).

    Từ chối ghi vào `data/` của dự án trừ khi bật rõ `AIR_ALLOW_BASELINE_OVERWRITE=1` (chỉ dùng trong bản sao).
    Trả về (đường dẫn bảng ghép, đường dẫn bảng theo ngày).
    """
    p_merged, p_daily = output_paths(out_dir)
    for p in (p_merged, p_daily):
        data_paths.check_writable(p)
    p_daily.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(p_merged, index=False)
    daily.to_csv(p_daily, index=False)
    outs = [data_paths.record_output("bảng ghép chất lượng không khí + thời tiết", p_merged),
            data_paths.record_output("thời tiết theo ngày", p_daily)]
    manifest = {
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mode": network_mode(), "api_calls_in_process": N_API_CALLS,
        "python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__,
        "range": [START, END], "timezone": TIMEZONE, "model": MODEL, "required_hourly": REQUIRED_HOURLY,
        "inputs": {"air_quality": {"path": str(AQ_FILE), "sha256": data_paths.sha256_file(AQ_FILE)},
                   "hourly": {c: {k: h.attrs.get(k) for k in ("source", "path", "sha256")} for c, h in (hourly or {}).items()}},
        "outputs": [{k: r[k] for k in ("role", "path", "sha256", "bytes")} for r in outs],
    }
    (p_daily.parent / "nb04_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    return p_merged, p_daily


# ----------------------------------------------------------------------------- so với baseline theo dung sai đã duyệt
def unrounded_means(hourly):
    """Trung bình 24 giờ CHƯA làm tròn của ba cột được phép lệch, để chứng minh một ô lệch có nằm sát biên x,xx5 không."""
    parts = []
    for city, h in hourly.items():
        day = pd.to_datetime(h["time"]).dt.normalize()
        m = h.groupby(day)[list(TOL_MEAN_COLS.values())].mean()
        m.columns = [c + "_unrounded" for c in TOL_MEAN_COLS]
        m.index.name = "Date"
        m = m.reset_index()
        m.insert(0, "City", city)
        parts.append(m)
    return pd.concat(parts, ignore_index=True)


def compare_daily(new, base, hourly):
    """So bảng thời tiết theo ngày `new` với bảng baseline `base`, theo đúng dung sai RA đã duyệt (RA-DEC-02 mục 5).

    * Bộ cột, khoá (City, Date), vị trí NaN, `rain_day`, `wind_dir_8`: phải trùng chính xác.
    * `temp_mean`, `pressure_mean`, `wind_speed_mean`: được lệch tối đa ROUND_TOL (+ ABS_EPS), và CHỈ KHI trung bình 24 giờ
      chưa làm tròn (tính lại từ `hourly`) nằm sát biên x,xx5 và cả hai giá trị đều là một cách làm tròn của trung bình đó.
    * Mọi cột số khác: lệch không quá ABS_EPS.
    Dung sai không phải miễn kiểm: mọi ô khác nhau đều được liệt kê. Trả về dict:
      ok (bool), problems (list lỗi cấu trúc), cells (mọi ô khác nhau, có cột `trong_dung_sai`), summary (theo cột).
    """
    problems = []
    if list(new.columns) != list(base.columns):
        problems.append(f"bộ cột khác nhau: mới {list(new.columns)} | baseline {list(base.columns)}")
        return {"ok": False, "problems": problems, "cells": pd.DataFrame(), "summary": pd.DataFrame()}
    a = new.assign(Date=pd.to_datetime(new["Date"]), City=new["City"].astype(str)).sort_values(KEYS).reset_index(drop=True)
    b = base.assign(Date=pd.to_datetime(base["Date"]), City=base["City"].astype(str)).sort_values(KEYS).reset_index(drop=True)
    for name, d in (("mới", a), ("baseline", b)):
        if d.duplicated(KEYS).any():
            problems.append(f"bảng {name} có khoá (City, Date) trùng")
    if len(a) != len(b) or not (a[KEYS].to_numpy() == b[KEYS].to_numpy()).all():
        problems.append(f"bộ khoá (City, Date) khác nhau: mới {len(a)} dòng, baseline {len(b)} dòng")
        return {"ok": False, "problems": problems, "cells": pd.DataFrame(), "summary": pd.DataFrame()}

    um = a[KEYS].merge(unrounded_means(hourly), on=KEYS, how="left", validate="1:1")
    cells, summary = [], []
    for col in [c for c in a.columns if c not in KEYS]:
        x, y = a[col], b[col]
        nan_diff = x.isna() ^ y.isna()
        if col in EXACT_COLS or not (pd.api.types.is_numeric_dtype(x) and pd.api.types.is_numeric_dtype(y)) \
                or pd.api.types.is_bool_dtype(x) or pd.api.types.is_bool_dtype(y):
            diff = (x.astype(str) != y.astype(str)) | nan_diff
            absdiff = pd.Series(np.nan, index=x.index)
            allowed = pd.Series(False, index=x.index)
        else:
            absdiff = (x.astype(float) - y.astype(float)).abs()
            diff = (absdiff > ABS_EPS) | nan_diff
            allowed = pd.Series(False, index=x.index)
            if col in TOL_MEAN_COLS:
                u = um[col + "_unrounded"]
                frac = u * 100 - np.floor(u * 100)
                near = (frac - 0.5).abs() <= BOUNDARY_EPS
                both_round = ((x - u).abs() <= ROUND_TOL / 2 + BOUNDARY_EPS) & ((y - u).abs() <= ROUND_TOL / 2 + BOUNDARY_EPS)
                allowed = diff & ~nan_diff & (absdiff <= ROUND_TOL + ABS_EPS) & near & both_round
        idx = np.flatnonzero(diff.to_numpy())
        for i in idx:
            cells.append({"City": a.City[i], "Date": a.Date[i].date(), "cot": col, "moi": x[i], "baseline": y[i],
                          "abs_lech": absdiff[i], "tb_chua_lam_tron": um[col + "_unrounded"][i] if col in TOL_MEAN_COLS else np.nan,
                          "trong_dung_sai": bool(allowed[i])})
        summary.append({"cot": col, "so_o": len(x), "o_khac": int(diff.sum()), "o_trong_dung_sai": int(allowed.sum()),
                        "o_vi_pham": int((diff & ~allowed).sum()), "max_abs_lech": float(absdiff[diff].max()) if diff.any() and absdiff[diff].notna().any() else 0.0,
                        "quy_tac": "chính xác" if col in EXACT_COLS else f"<= {ROUND_TOL} tại biên x,xx5" if col in TOL_MEAN_COLS else f"<= {ABS_EPS}"})
    cells = pd.DataFrame(cells, columns=["City", "Date", "cot", "moi", "baseline", "abs_lech", "tb_chua_lam_tron", "trong_dung_sai"])
    summary = pd.DataFrame(summary).set_index("cot")
    return {"ok": not problems and int(summary["o_vi_pham"].sum()) == 0, "problems": problems, "cells": cells, "summary": summary}
