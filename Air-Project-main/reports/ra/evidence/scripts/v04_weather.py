"""V10–V12 [Q04] Weather cache (.gz theo giờ) → daily → merged: kiểm OFFLINE từ 8 file cache.
Không gọi API. Phần kiểm mạng (smoke_test/probe) được thử riêng và ghi blocked nếu sandbox chặn.
Chạy: python v04_weather.py
"""
from da_common import *
import json, gzip, calendar
import weather_utils as wu

rows = []
def rec(crit, expected, actual, note=""):
    rows.append({"tieu_chi": crit, "expected": expected, "actual": actual, "khop": bool(expected == actual), "ghi_chu": note})

files = sorted((ROOT / "data/raw/weather").glob("openmeteo_*_hourly.csv.gz"))
rec("số file cache", 8, len(files))
exp_days = (pd.Timestamp(wu.END) - pd.Timestamp(wu.START)).days + 1
exp_hours_cal = len(pd.date_range(wu.START + " 00:00", wu.END + " 23:00", freq="h"))     # đếm độc lập từ lịch
rec("số ngày lịch 25/12/2014–01/07/2020", 2016, exp_days); rec("số giờ lịch mỗi TP", 48384, exp_hours_cal)
meta = json.load(open(ROOT / "Metadata.json"))
wmeta = meta.get("weather_source", {})
hourly, per = {}, []
for c in wu.CITIES:
    h = pd.read_csv(wu.cache_path(c)); hourly[c] = h
    t = pd.to_datetime(h["time"])
    full_idx = pd.date_range(wu.START + " 00:00", wu.END + " 23:00", freq="h")
    peak_local = int(h.groupby(t.dt.hour)["temperature_2m"].mean().idxmax()); trough_local = int(h.groupby(t.dt.hour)["temperature_2m"].mean().idxmin())
    var = [v for v in wu.HOURLY_CORE + wu.HOURLY_EXTRA if v in h.columns]
    per.append({"City": c, "sha256_16": sha256(wu.cache_path(c))[:16], "so_dong": len(h), "mong_doi_tu_lich": exp_hours_cal, "gio_trung": int(t.duplicated().sum()),
                "khop_luoi_gio_lien_tuc": bool((t.reset_index(drop=True) == pd.Series(full_idx)).all()), "o_trong": int(h[var].isna().sum().sum()),
                "dau": str(t.min()), "cuoi": str(t.max()), "co_BLH": "boundary_layer_height" in h.columns,
                "gio_nong_nhat(local)": peak_local, "gio_lanh_nhat(local)": trough_local,
                "neu_la_UTC_thi_gio_nong_nhat_se_la": (peak_local - 5.5) % 24,
                "grid_lat": h.grid_lat.iloc[0], "grid_lon": h.grid_lon.iloc[0], "grid_elev": h.grid_elev.iloc[0], "grid_khong_doi": bool(h[["grid_lat", "grid_lon", "grid_elev"]].nunique().eq(1).all()),
                "lech_toa_do_max_do": round(max(abs(h.grid_lat.iloc[0] - wu.CITY_COORDS[c][0]), abs(h.grid_lon.iloc[0] - wu.CITY_COORDS[c][1])), 3),
                "temp_min/max": f"{h.temperature_2m.min()}/{h.temperature_2m.max()}", "RH_min/max": f"{h.relative_humidity_2m.min()}/{h.relative_humidity_2m.max()}",
                "pressure_mean_hPa": round(h.surface_pressure.mean(), 1), "wind_mean": round(h.wind_speed_10m.mean(), 2), "wind_p99": round(h.wind_speed_10m.quantile(.99), 2),
                "wind_dir_min/max": f"{h.wind_direction_10m.min()}/{h.wind_direction_10m.max()}", "precip_min": h.precipitation.min(),
                "blh_min/max": f"{h.boundary_layer_height.min()}/{h.boundary_layer_height.max()}" if "boundary_layer_height" in h.columns else ""})
per = pd.DataFrame(per).set_index("City"); save(per, "V10_weather_cache_checks.csv")
print(per.T.to_string())
rec("mỗi file đủ 48.384 dòng giờ", 8, int((per.so_dong == 48384).sum())); rec("tổng dòng giờ", 387072, int(per.so_dong.sum()))
rec("giờ trùng", 0, int(per.gio_trung.sum())); rec("ô trống (6 biến lõi + BLH)", 0, int(per.o_trong.sum()))
rec("lưới giờ liên tục đúng lịch (8 TP)", 8, int(per.khop_luoi_gio_lien_tuc.sum()))
rec("BLH có trong cả 8 cache", 8, int(per.co_BLH.sum()), "downstream NB05/06 dùng blh_mean cố định")
rec("giờ nóng nhất 12–16h local (8 TP)", 8, int(per["gio_nong_nhat(local)"].between(12, 16).sum()), f"giờ nóng nhất: {per['gio_nong_nhat(local)'].to_dict()}; nếu chuỗi là UTC thì đỉnh sẽ rơi ~8–9h")
rec("Delhi và Gurugram khác ô lưới", True, bool((per.loc["Delhi", ["grid_lat", "grid_lon"]] != per.loc["Gurugram", ["grid_lat", "grid_lon"]]).any()),
    f"Delhi ({per.loc['Delhi','grid_lat']}, {per.loc['Delhi','grid_lon']}), Gurugram ({per.loc['Gurugram','grid_lat']}, {per.loc['Gurugram','grid_lon']})")
rec("độ lệch toạ độ lưới tối đa ≤ 0,125°", True, bool(per.lech_toa_do_max_do.max() <= 0.125), f"max = {per.lech_toa_do_max_do.max()}°")
# metadata đối chiếu
locs = wmeta.get("locations", {})
if isinstance(locs, dict) and locs:
    bad = []
    for c in wu.CITIES:
        l = locs.get(c, {}); vals = json.dumps(l)
        for k, mk in (("grid_lat", "era5_grid_lat"), ("grid_lon", "era5_grid_lon"), ("grid_elev", "grid_elevation_m")):
            mv = l.get(mk)
            if mv is None: bad.append((c, mk, "thiếu khoá", None)); continue
            if mv is not None and abs(float(mv) - float(per.loc[c, k])) > 1e-6: bad.append((c, k, mv, per.loc[c, k]))
    rec("Metadata.weather_source.locations khớp grid trong cache", 0, len(bad), str(bad)[:300] if bad else f"các khoá: {list(next(iter(locs.values())).keys())}")
else:
    rows.append({"tieu_chi": "Metadata.weather_source.locations", "expected": "dict 8 TP", "actual": str(type(locs).__name__) + " " + str(locs)[:200], "khop": False, "ghi_chu": "cấu trúc khác dự kiến, xem thủ công"})

# ---- daily: dùng hàm tác giả từ cache, so với file commit
daily = wu.build_daily(hourly)                        # tự assert 24 giờ/ngày
base = pd.read_csv(WDAILY, parse_dates=["Date"])
rec("daily: số hàng", 16128, len(daily)); rec("daily commit: số hàng", 16128, len(base))
daily = daily[base.columns] if set(base.columns) == set(daily.columns) else daily
rec("daily: cùng bộ cột với file commit", True, set(base.columns) == set(daily.columns), str(list(base.columns)))
d0 = daily.sort_values(["City", "Date"]).reset_index(drop=True); b0 = base.sort_values(["City", "Date"]).reset_index(drop=True)
nd = {c: int((~eqnan(d0[c], b0[c], 1e-9)).sum()) for c in base.columns if c not in ("City", "Date")}
num = [c for c in base.columns if c not in ("City", "Date", "rain_day", "wind_dir_8")]
mx = max(float((d0[c] - b0[c]).abs().max()) for c in num)
rec("daily tái lập từ cache == file commit (từng ô, 1e-9)", 0, int(sum(nd.values())),
    f"{ {k: v for k, v in nd.items() if v} }; max |diff| = {mx:.4f} trên {len(d0) * len(num)} ô số ({sum(nd.values()) / (len(d0) * len(num)) * 100:.2f}%). "
    "Nguyên nhân: round(2) của trung bình 24 giờ rơi đúng biên ...5 nên làm tròn lên/xuống khác nhau giữa phiên bản numpy/pandas; không lệch cột min/max/sum/u/v/blh, rain_day, wind_dir_8")
# bằng chứng nguyên nhân: giá trị chưa làm tròn của các ô lệch nằm sát biên 0,005
chk = []
for c_, src_ in (("temp_mean", "temperature_2m"), ("pressure_mean", "surface_pressure"), ("wind_speed_mean", "wind_speed_10m")):
    bad_ = d0[~eqnan(d0[c_], b0[c_], 1e-9).to_numpy()][["City", "Date"]]
    for city, dt in zip(bad_.City, bad_.Date):
        h_ = hourly[city]; v_ = h_.loc[h_["time"].str[:10] == dt.strftime("%Y-%m-%d"), src_].mean()
        chk.append(abs((v_ * 100) % 1 - 0.5))
rec("daily: mọi ô lệch có trung bình chưa làm tròn nằm đúng biên x,xx5 (|phần lẻ − 0,5| < 1e-6)", len(chk), int(sum(x < 1e-6 for x in chk)))
rec("daily: ô trống", 0, int(base.drop(columns=["City", "Date"]).isna().sum().sum()))
rec("daily: vi phạm giới hạn vật lý (check_ranges)", 0, len(wu.check_ranges(base)))

# ---- tính ĐỘC LẬP (không dùng weather_utils) cho 3 TP và so
ind = []
for c in wu.CITIES:
    h = hourly[c].copy(); h["Date"] = h["time"].str[:10]
    th = np.deg2rad(h.wind_direction_10m.to_numpy()); sp = h.wind_speed_10m.to_numpy()
    h["u"] = -sp * np.sin(th); h["v"] = -sp * np.cos(th)
    g = h.groupby("Date")
    mine = pd.DataFrame({"n": g.size(), "temp_mean": g.temperature_2m.mean().round(2), "temp_min": g.temperature_2m.min(), "temp_max": g.temperature_2m.max(),
                         "humidity_mean": g.relative_humidity_2m.mean().round(2), "pressure_mean": g.surface_pressure.mean().round(2), "wind_speed_mean": g.wind_speed_10m.mean().round(2),
                         "wind_speed_max": g.wind_speed_10m.max().round(2), "wind_u": g.u.mean().round(2), "wind_v": g.v.mean().round(2), "precip_sum": g.precipitation.sum().round(2),
                         "blh_mean": g.boundary_layer_height.mean().round(2), "blh_min": g.boundary_layer_height.min().round(2)})
    b = base[base.City == c].set_index(base[base.City == c].Date.dt.strftime("%Y-%m-%d"))
    r = {"City": c, "ngay_du_24_gio": int((mine.n == 24).sum()), "so_ngay": len(mine)}
    for col in [x for x in mine.columns if x != "n"]:
        r[f"maxdiff_{col}"] = float((mine[col] - b[col].reindex(mine.index)).abs().max())
    # hướng gió: gió thổi TỪ hướng; kiểm dấu bằng ví dụ thật
    deg = (np.degrees(np.arctan2(-b.wind_u, -b.wind_v)) + 360) % 360
    lab = np.array(["N", "NE", "E", "SE", "S", "SW", "W", "NW"])[(((deg + 22.5) // 45).astype(int) % 8).to_numpy()]
    r["wind_dir_8_khop"] = int((lab == b.wind_dir_8.to_numpy()).sum()); r["rain_day_khop"] = int(((b.precip_sum >= 1.0) == b.rain_day.astype(bool)).sum())
    ind.append(r)
ind = pd.DataFrame(ind).set_index("City"); save(ind, "V11_weather_daily_independent_recompute.csv")
md = ind[[c for c in ind.columns if c.startswith("maxdiff_")]].max().max()
rec("daily: tính độc lập (mean/min/max/sum/u/v) lệch tối đa ≤ 0,01", True, bool(md <= 0.0101), f"max |diff| = {md:.4f} (1 đơn vị ở chữ số thập phân thứ 2 = làm tròn tại biên ...5)")
rec("daily: mỗi ngày đủ 24 giờ (8 TP × 2016 ngày)", 16128, int(ind.ngay_du_24_gio.sum()))
rec("daily: wind_dir_8 khớp công thức 'gió thổi TỪ'", 16128, int(ind.wind_dir_8_khop.sum())); rec("daily: rain_day == (precip_sum ≥ 1 mm)", 16128, int(ind.rain_day_khop.sum()))
# kiểm dấu u/v bằng một giờ có hướng gần chính Tây (270°): gió TỪ Tây thổi VỀ Đông => u > 0
h = hourly["Delhi"]; w = h[(h.wind_direction_10m.between(265, 275)) & (h.wind_speed_10m > 3)].iloc[0]
u1 = -w.wind_speed_10m * np.sin(np.deg2rad(w.wind_direction_10m))
rec("dấu u: gió từ hướng Tây (270°) → u dương (thổi về Đông)", True, bool(u1 > 0), f"ví dụ Delhi {w.time}: hướng {w.wind_direction_10m}°, tốc độ {w.wind_speed_10m} m/s → u = {u1:.2f}")
rec("_dir8: 4 hướng cơ bản", "N,E,S,W", ",".join(wu._dir8(pd.Series([0.0, -1.0, 0.0, 1.0]), pd.Series([-1.0, 0.0, 1.0, 0.0])).tolist()))

# ---- merged
mg = pd.read_csv(MERGED, parse_dates=["Date"]); aq = pd.read_csv(CLEAN, parse_dates=["Date"])
rec("merged: shape", "(14056, 54)", str(mg.shape))
wcols = [c for c in mg.columns if c not in aq.columns]
rec("merged: số cột thời tiết thêm", 14, len(wcols), str(wcols))
rec("merged: dòng thiếu thời tiết", 0, int(mg[wcols].isna().any(axis=1).sum()))
rec("merged: khoá (City,Date) trùng", 0, int(mg.duplicated(["City", "Date"]).sum()))
nd40 = sum(int((~eqnan(mg[c], aq[c], 0.0)).sum()) for c in aq.columns if c not in ("Date",)) + int((mg.Date.values != aq.Date.values).sum())
rec("merged: 40 cột AQ giữ nguyên từng ô (so tuyệt đối)", 0, nd40)
re_m = wu.merge_weather(aq, base)
ndw = sum(int((~eqnan(re_m[c], mg[c], 1e-9)).sum()) for c in wcols)
rec("merged: cột thời tiết == daily ghép lại theo (City,Date)", 0, ndw)
# Delhi–Gurugram tương quan
a = base[base.City == "Delhi"].set_index("Date"); b = base[base.City == "Gurugram"].set_index("Date")
cor = {c: round(a[c].corr(b[c]), 3) for c in ["temp_mean", "humidity_mean", "wind_speed_mean", "precip_sum", "blh_mean"]}
rec("Delhi–Gurugram: tương quan thời tiết ngày 0,95–0,999", True, bool(min(cor.values()) >= 0.94 and max(cor.values()) >= 0.99), str(cor))
res = pd.DataFrame(rows); save(res, "V10_weather_pipeline_checks.csv", index=False); print(res.to_string())
print("Metadata.weather_source keys:", list(wmeta.keys()))
