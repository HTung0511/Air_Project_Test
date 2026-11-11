"""Đường dựng dữ liệu DỰ BÁO đi thẳng từ raw (vòng 2, F01). `notebooks/06_predict_aqi.ipynb` dùng module này.

Vì sao có file này
    `model_utils.make_features` đọc bảng ĐÃ làm sạch `air_quality_8cities.csv`. Bảng đó được làm sạch một lần trên TOÀN chuỗi
    (số 0 treo tính theo cả chuỗi, nội suy giữa hai đầu mút, luật nghi lỗi top-5 + cửa sổ căn giữa), nên giá trị của ngày t có
    thể phụ thuộc vào các ngày SAU t; cắt `as_of` trên bảng đã sạch không thấy được điều đó (F01; DA V05/V07). Module này
    không đọc bảng đã sạch. Đường hồi cứu (`model_utils.make_features`, `build_dataset`) được GIỮ NGUYÊN để đối chiếu và cho EDA.

Contract (RA-DEC-02 mục 2-4; bản đầy đủ: `reports/ra/round2/dev_label_feature_protocol.md`)
    * Một mẫu (City, t) dự đoán y = AQI raw của NGÀY LỊCH t+1. Đặc trưng chỉ dùng thông tin có đến hết ngày t.
    * AQI (nhãn, AQI hôm nay và các ngày trước): lấy đúng giá trị trong raw `city_day.csv`. Không nội suy, không điền, không cắt
      ở 500, không xoá theo luật nghi lỗi hồi cứu. AQI có mặt phải hữu hạn và > 0, nếu không thì DỪNG và báo (không lặng lẽ bỏ).
    * Chất ô nhiễm làm đặc trưng (PM2.5, NO2, CO, SO2, O3): giá trị raw của ngày t, với hai xử lý chỉ nhìn về quá khứ:
        - Số 0 treo theo snapshot as-of t: số 0 của ngày t bị che khi chuỗi số 0 LIÊN TIẾP kết thúc tại t, tính trên dữ liệu
          <= t, đã dài từ 3 ngày. Ngày thứ nhất và thứ hai của chuỗi giữ số 0 đã công bố. Chuỗi không nối qua ngày thiếu.
        - Forward-fill tối đa 2 ngày từ giá trị hợp lệ gần nhất. "Hợp lệ" xét trong prefix <= t của CHÍNH hàng đó: số 0 thuộc
          một chuỗi đã đủ 3 ngày tính đến t không được làm nguồn điền. Hàng của ngày t-1, t-2 đã tính thì không sửa lại.
      Không nội suy, không backward-fill, không dùng luật nghi lỗi top-5/cửa sổ căn giữa. Phần còn thiếu để NaN; imputer trong
      `Pipeline` (trung vị, chỉ fit trên train) xử lý, đúng như trước.
    * Thời tiết: bảng theo ngày (mặc định baseline đã commit; xem `data_paths.py`), chỉ các ngày <= t, cùng công thức với
      `model_utils`. Thời tiết ngày t+1 (`*_next`) chỉ thuộc kịch bản "cận trên" L4 và được gắn ở bước nhãn, không ở bước đặc trưng.
    * Giữ mẫu: AQI raw có ở cả t và t+1; t >= 14/06/2017 và t+1 <= 01/07/2020. Chia tập theo ngày ĐƯỢC DỰ ĐOÁN (t+1), mốc như cũ.
    * Nhãn chỉ đi vào `attach_target` (tạo y, chọn mẫu đánh giá, kịch bản L4); `make_forecast_features` không có cột nào của t+1.

Đây là đánh giá trên AQI được ghi trong MỘT snapshot raw hiện có. Nó không chứng minh raw là số đo đúng tại trạm và không mô
phỏng việc CPCB sửa số liệu về sau.
"""
from pathlib import Path

import numpy as np
import pandas as pd

import data_paths
from eda_utils import CITIES, POOR_AQI, USABLE
from model_utils import (TRAIN_END, TEST_START, TEST_END, LOCK_START, LEVELS, POLL_FEATS, WEATHER_FEATS, NEXT_FEATS,  # noqa: F401
                         WEATHER_FILE, make_pipe, cv_score, oof_predict, mae, rmse, baseline_preds, alert_metrics,
                         best_threshold, calendar_blocks, boot_mae_diff, build_dataset as build_dataset_retrospective)

PROTOCOL = "RA-DEC-02 (11/11/2026)"
RAW_FILE = data_paths.RAW_FILE
COMMON_START, COMMON_END = pd.Timestamp("2017-06-14"), pd.Timestamp("2020-07-01")   # khoảng chung của 8 thành phố (phạm vi đã chốt)

POLL_SOURCE = dict(zip(POLL_FEATS, USABLE))     # {"pm25_0": "PM2.5", "no2_0": "NO2", "co_0": "CO", "so2_0": "SO2", "o3_0": "O3"}
FLATLINE_COLS = list(USABLE)                    # quy tắc số 0 treo CHỈ áp cho 5 cột này; không áp cho AQI và thời tiết
FLATLINE_MIN_RUN = 3                            # cùng ngưỡng với nhánh làm sạch hồi cứu (utils.flag_flatline_zeros)
FFILL_LIMIT = 2                                 # forward-fill tối đa 2 ngày, cùng giới hạn với model_utils.make_features
WEATHER_SOURCE_COLS = ["temp_mean", "humidity_mean", "pressure_mean", "wind_speed_mean", "wind_u", "wind_v", "precip_sum", "blh_mean"]
RAW_COLS = ["City", "Date", "AQI"] + USABLE
DIAG_COLS = [f + s for f in POLL_FEATS for s in ("_lag", "_flat")]   # cột chẩn đoán (không phải đặc trưng): nguồn điền và cờ che
ALPHAS = [0.1, 1, 10, 30, 100, 300]             # lưới alpha của notebook 06 (ô chọn tham số)
PERSIST = "Ngày mai = hôm nay"


# ----------------------------------------------------------------------------- đọc và kiểm raw
def raw_value_violations(raw):
    """Các ô raw vi phạm kiểm tra xác định trước: AQI có mặt phải hữu hạn và > 0; nồng độ có mặt phải hữu hạn và >= 0.
    Trả về bảng (City, Date, cột, giá trị, quy tắc). Mong đợi: bảng rỗng."""
    rows = []
    for col, rule, bad in [("AQI", "AQI có mặt phải hữu hạn và > 0", lambda x: ~np.isfinite(x) | (x <= 0))] + \
                          [(p, "nồng độ có mặt phải hữu hạn và >= 0", lambda x: ~np.isfinite(x) | (x < 0)) for p in USABLE]:
        x = pd.to_numeric(raw[col], errors="coerce")
        unreadable = raw[col].notna() & x.isna()
        mask = (x.notna() & bad(x.astype(float))) | unreadable
        if mask.any():
            rows.append(raw.loc[mask, ["City", "Date"]].assign(cot=col, gia_tri=raw.loc[mask, col].to_numpy(), quy_tac=rule))
    cols = ["City", "Date", "cot", "gia_tri", "quy_tac"]
    return pd.concat(rows, ignore_index=True)[cols] if rows else pd.DataFrame(columns=cols)


def prepare_raw(raw):
    """Chuẩn hoá và KIỂM raw trước khi dùng: đủ cột, khoá (City, Date) không trùng, mỗi thành phố là chuỗi ngày LIÊN TỤC
    (ngày lịch bị thiếu được chèn thành dòng NaN để mọi phép dịch theo dòng đúng bằng dịch theo ngày lịch), giá trị hợp lệ.
    Vi phạm giá trị hoặc khoá trùng thì ném ValueError kèm số lượng, ngày và quy tắc; không bỏ dòng, không thay số."""
    missing = [c for c in RAW_COLS if c not in raw.columns]
    if missing:
        raise ValueError(f"raw thiếu cột: {missing}")
    d = raw[RAW_COLS].copy()
    d["City"] = d["City"].astype(str)
    d["Date"] = pd.to_datetime(d["Date"])
    if (d["Date"] != d["Date"].dt.normalize()).any():
        raise ValueError("cột Date của raw có giờ khác 00:00; mong đợi dữ liệu theo ngày")
    dup = d.duplicated(["City", "Date"], keep=False)
    if dup.any():
        ex = d.loc[dup, ["City", "Date"]].drop_duplicates().head(5).to_dict("records")
        raise ValueError(f"raw có {int(dup.sum())} dòng trùng khoá (City, Date), ví dụ {ex}")
    bad = raw_value_violations(d)
    if len(bad):
        raise ValueError(f"raw có {len(bad)} ô không hợp lệ (không tự bỏ hay thay; cần quyết định của RA):\n{bad.head(10).to_string(index=False)}")
    for c in ["AQI"] + USABLE:
        d[c] = pd.to_numeric(d[c]).astype(float)
    parts, n_inserted = [], 0
    for city, x in d.groupby("City", sort=False):
        x = x.sort_values("Date")
        full = pd.date_range(x["Date"].min(), x["Date"].max(), freq="D")
        if len(full) != len(x):
            n_inserted += len(full) - len(x)
            x = x.set_index("Date").reindex(full).rename_axis("Date").reset_index()
            x["City"] = city
        parts.append(x[RAW_COLS])
    out = pd.concat(parts, ignore_index=True).sort_values(["City", "Date"]).reset_index(drop=True) if parts else d.iloc[0:0]
    out.attrs["n_inserted_days"] = n_inserted
    return out


def load_raw(path=None, cities=CITIES, verbose=False):
    """Đọc raw `city_day.csv`, lấy các thành phố cần, rồi `prepare_raw`. Ghi nhận file đã đọc (đường dẫn + sha256)."""
    path = Path(path or RAW_FILE)
    data_paths.record_input("raw chất lượng không khí (city_day.csv)", path, quiet=not verbose)
    raw = pd.read_csv(path, usecols=RAW_COLS)
    out = prepare_raw(raw[raw["City"].isin(list(cities))])
    if verbose and out.attrs["n_inserted_days"]:
        print(f"  raw thiếu {out.attrs['n_inserted_days']} ngày lịch; đã chèn dòng NaN để chuỗi liên tục")
    return out


def load_weather_daily(path=None, verbose=False):
    """Bảng thời tiết theo ngày (mặc định: file do `data_paths.weather_daily_path()` chỉ định). Ghi nhận file đã đọc."""
    path = Path(path or WEATHER_FILE)
    data_paths.record_input("thời tiết theo ngày", path, quiet=not verbose)
    w = pd.read_csv(path, parse_dates=["Date"])
    return w


def common_window(raw):
    """(ngày muộn nhất mà mọi thành phố đã có dòng dữ liệu, ngày sớm nhất mà có thành phố hết dữ liệu)."""
    g = raw.groupby("City")["Date"]
    return g.min().max(), g.max().min()


# ----------------------------------------------------------------------------- số 0 treo và forward-fill, as-of t
def trailing_zero_run(v):
    """Với mỗi vị trí i: số giá trị ĐÚNG BẰNG 0 liên tiếp kết thúc tại i (0 nếu v[i] khác 0 hoặc thiếu). Chỉ nhìn về trước."""
    v = np.asarray(v, float)
    z = v == 0                                             # NaN == 0 là False: ngày thiếu làm đứt chuỗi
    idx = np.arange(len(v))
    last_break = np.maximum.accumulate(np.where(~z, idx, -1))
    return np.where(z, idx - last_break, 0).astype(np.int64)


def _lag(a, k, fill):
    """a[t-k] theo vị trí; k ngày đầu chuỗi nhận `fill`."""
    if k == 0:
        return a
    out = np.full(len(a), fill, dtype=a.dtype)
    out[k:] = a[:len(a) - k]
    return out


def asof_pollutant(v, min_run=FLATLINE_MIN_RUN, limit=FFILL_LIMIT):
    """Giá trị của một chất dùng làm đặc trưng cho từng ngày t, tính CHỈ từ v[<= t]. `v`: chuỗi raw theo ngày liên tục của MỘT thành phố.

    Với mỗi t, xét lần lượt ngày t, t-1, ..., t-limit và lấy giá trị hợp lệ đầu tiên. Giá trị của ngày s (<= t) hợp lệ khi nó có
    mặt và KHÔNG phải số 0 thuộc một chuỗi số 0 liên tiếp mà, tính đến hết t, đã dài >= min_run. Độ dài "tính đến hết t" của chuỗi
    chứa s là độ dài chuỗi đó sau khi cắt ở t; nó không dùng ngày nào sau t.

    Trả về dict các mảng cùng độ dài: value (NaN nếu không có nguồn hợp lệ), lag (0..limit; -1 nếu không có),
    flat (True nếu giá trị của CHÍNH ngày t bị che vì số 0 treo), run (độ dài chuỗi số 0 kết thúc tại t).
    """
    v = np.asarray(v, float)
    z = v == 0
    r = trailing_zero_run(v)
    value = np.full(len(v), np.nan)
    lag = np.full(len(v), -1, dtype=np.int64)
    flat = np.zeros(len(v), dtype=bool)
    for k in range(limit + 1):
        vk, zk = _lag(v, k, np.nan), _lag(z, k, False)
        run_len, alive = _lag(r, k, 0), zk.copy()          # độ dài chuỗi chứa ngày t-k, kéo dần tới t nếu chuỗi còn tiếp diễn
        for m in range(1, k + 1):
            alive = alive & _lag(z, k - m, False)
            run_len = np.where(alive, _lag(r, k - m, 0), run_len)
        masked = zk & (run_len >= min_run)
        if k == 0:
            flat = masked
        take = ~np.isnan(vk) & ~masked & (lag == -1)
        value[take], lag[take] = vk[take], k
    return {"value": value, "lag": lag, "flat": flat, "run": r}


# ----------------------------------------------------------------------------- đặc trưng as-of (không có cột nào của t+1)
def _features(raw, weather):
    """`raw` đã qua `prepare_raw`. Một dòng cho mỗi (City, Date) của raw."""
    need = ["City", "Date"] + WEATHER_SOURCE_COLS
    missing = [c for c in need if c not in weather.columns]
    if missing:
        raise ValueError(f"bảng thời tiết theo ngày thiếu cột: {missing} (NB06 cần cả `blh_mean`)")
    w = weather[need].copy()
    w["City"] = w["City"].astype(str)
    w["Date"] = pd.to_datetime(w["Date"])
    if w.duplicated(["City", "Date"]).any():
        raise ValueError("bảng thời tiết theo ngày có khoá (City, Date) trùng")
    d = raw.merge(w, on=["City", "Date"], how="left", validate="1:1").sort_values(["City", "Date"]).reset_index(drop=True)
    n_no_weather = int(d[WEATHER_SOURCE_COLS].isna().any(axis=1).sum())
    if n_no_weather:
        ex = d.loc[d[WEATHER_SOURCE_COLS].isna().any(axis=1), ["City", "Date"]].head(3).to_dict("records")
        raise ValueError(f"{n_no_weather} dòng raw không có thời tiết tương ứng (ví dụ {ex}); không tự điền thời tiết")
    if len(d):
        assert (d.groupby("City")["Date"].diff().dropna() == pd.Timedelta("1D")).all(), "chuỗi ngày bị đứt: dịch theo dòng sẽ sai"
    g = d.groupby("City", sort=False)

    # AQI: cùng công thức với model_utils, nhưng trên AQI raw
    la = np.log(d["AQI"])
    d["aqi_0"] = la
    d["aqi_1"] = la.groupby(d["City"]).shift(1)
    d["aqi_2"] = la.groupby(d["City"]).shift(2)
    wk = g["AQI"].transform(lambda s: s.shift(1).rolling(7, min_periods=3).mean())      # trung bình 7 ngày TRƯỚC hôm nay
    d["aqi_wk"] = np.log(wk)

    # chất ô nhiễm: số 0 treo as-of t, forward-fill <= 2 ngày, rồi log1p. Tính riêng từng thành phố (không kéo qua ranh thành phố)
    for name, col in POLL_SOURCE.items():
        value, lag, flat = np.full(len(d), np.nan), np.full(len(d), -1, dtype=np.int64), np.zeros(len(d), dtype=bool)
        for _, ix in g.indices.items():
            res = asof_pollutant(d[col].to_numpy()[ix])
            value[ix], lag[ix], flat[ix] = res["value"], res["lag"], res["flat"]
        d[name] = np.log1p(value)
        d[name + "_lag"] = lag
        d[name + "_flat"] = flat

    # thời tiết đến hết hôm nay: cùng công thức với model_utils
    d["d_pressure"] = d["pressure_mean"] - g["pressure_mean"].shift(1)
    d["pressure_dev"] = d["pressure_mean"] - g["pressure_mean"].transform(lambda s: s.shift(1).rolling(30, min_periods=10).mean())
    d["precip_log"] = np.log1p(d["precip_sum"])

    d["Date_target"] = d["Date"] + pd.Timedelta(days=1)
    doy = d["Date_target"].dt.day_of_year                                                # ngày trong năm của ngày được dự đoán: biết trước
    d["doy_sin"], d["doy_cos"] = np.sin(2 * np.pi * doy / 365.25), np.cos(2 * np.pi * doy / 365.25)
    d["today_poor"] = d["AQI"] >= POOR_AQI
    return d[["City", "Date", "Date_target", "AQI", "today_poor"] + LEVELS["L3"] + DIAG_COLS]


def make_forecast_features(raw=None, weather=None, as_of=None, verbose=False):
    """Đặc trưng L1-L3 as-of cho mọi (City, Date) của raw. KHÔNG có nhãn và không có cột nào của ngày t+1.

    `as_of`: nếu cho một ngày, raw và thời tiết bị cắt ở ngày đó TRƯỚC khi tính. So đặc trưng của ngày `as_of` giữa bản cắt và
    bản đầy đủ là phép thử rò rỉ đi từ raw (khác với `model_utils.make_features(as_of=...)`, vốn cắt bảng đã làm sạch).
    """
    raw = load_raw(verbose=verbose) if raw is None else prepare_raw(raw)
    weather = load_weather_daily(verbose=verbose) if weather is None else weather
    if as_of is not None:
        as_of = pd.Timestamp(as_of)
        raw = raw[raw["Date"] <= as_of]
        weather = weather[pd.to_datetime(weather["Date"]) <= as_of]
    return _features(raw, weather)


# ----------------------------------------------------------------------------- nhãn, chọn mẫu, chia tập
def attach_target(feat, raw):
    """Gắn NHÃN và các cột chỉ dành cho đánh giá/kịch bản vào bảng đặc trưng:
    y = AQI raw của ngày lịch t+1 (ghép theo NGÀY, không dịch theo dòng), y_log, y_poor, split theo ngày được dự đoán, và thời
    tiết của ngày t+1 (`*_next`, chỉ cho kịch bản "cận trên" L4). Tách riêng để tương lai không thể lọt vào đặc trưng L1-L3."""
    lab = raw[["City", "Date", "AQI"]].rename(columns={"Date": "Date_target", "AQI": "y"})
    out = feat.merge(lab, on=["City", "Date_target"], how="left", validate="1:1")
    nxt = feat[["City", "Date"] + WEATHER_FEATS].rename(columns={"Date": "Date_target", **{f: f + "_next" for f in WEATHER_FEATS}})
    out = out.merge(nxt, on=["City", "Date_target"], how="left", validate="1:1")
    out["y_log"] = np.log(out["y"])
    out["y_poor"] = out["y"] >= POOR_AQI
    out["split"] = np.select([out["Date_target"] <= TRAIN_END, (out["Date_target"] >= TEST_START) & (out["Date_target"] <= TEST_END),
                              out["Date_target"] >= LOCK_START], ["train", "test", "lockdown"], default="other")
    return out


def retention_table(d, start=COMMON_START, end=COMMON_END):
    """Bảng giữ mẫu theo tập: số cặp (thành phố, ngày t) trong khoảng, số thiếu AQI(t), số thiếu AQI(t+1), số giữ lại."""
    w = d[(d["Date"] >= start) & (d["Date_target"] <= end)]
    has_t, has_y = w["AQI"].notna(), w["y"].notna()
    tab = pd.DataFrame({"cặp (thành phố, ngày t) trong khoảng": w.groupby("split").size(),
                        "thiếu AQI(t)": (~has_t).groupby(w["split"]).sum(),
                        "có AQI(t), thiếu AQI(t+1)": (has_t & ~has_y).groupby(w["split"]).sum(),
                        "giữ (có cả hai)": (has_t & has_y).groupby(w["split"]).sum(),
                        "ngày nặng trong số giữ": (has_t & has_y & w["y_poor"]).groupby(w["split"]).sum()})
    tab = tab.reindex([s for s in ["train", "test", "lockdown"] if s in tab.index]).astype(int)
    tab.loc["Cộng"] = tab.sum()
    return tab


def retention(ds):
    """Bảng giữ mẫu của một bảng do `build_forecast_dataset` dựng (đếm trên toàn bộ cặp trong khoảng, trước khi lọc)."""
    return pd.DataFrame(ds.attrs["retention"]).rename_axis("split")


def build_forecast_dataset(raw=None, weather=None, verbose=True, start=None, end=None):
    """Bảng (thành phố, ngày hôm nay t) -> AQI raw của ngày t+1, kèm đặc trưng as-of, sẵn sàng cho mô hình.

    Giữ dòng có AQI raw ở CẢ t và t+1, với t >= start và t+1 <= end (mặc định khoảng chung 14/06/2017 - 01/07/2020); sắp theo
    ngày được dự đoán (bắt buộc cho TimeSeriesSplit). Bảng giữ mẫu: `retention(ds)`.
    """
    raw = load_raw(verbose=verbose) if raw is None else prepare_raw(raw)
    weather = load_weather_daily(verbose=verbose) if weather is None else weather
    if start is None and end is None:
        got = common_window(raw)
        if got != (COMMON_START, COMMON_END):
            raise ValueError(f"khoảng chung của raw là {got[0]:%d/%m/%Y} - {got[1]:%d/%m/%Y}, khác phạm vi đã chốt "
                             f"{COMMON_START:%d/%m/%Y} - {COMMON_END:%d/%m/%Y}; truyền start/end nếu cố ý dùng dữ liệu khác")
    start, end = pd.Timestamp(start or COMMON_START), pd.Timestamp(end or COMMON_END)
    d = attach_target(_features(raw, weather), raw)
    keep = d["AQI"].notna() & d["y"].notna() & (d["Date"] >= start) & (d["Date_target"] <= end)
    out = d[keep].sort_values(["Date_target", "City"]).reset_index(drop=True)
    out["City"] = pd.Categorical(out["City"], categories=CITIES, ordered=True)
    # .attrs chỉ chứa kiểu Python thuần: một DataFrame đặt trong attrs làm pd.concat trên các lát của bảng này báo lỗi
    out.attrs["retention"] = retention_table(d, start, end).to_dict()
    out.attrs["protocol"] = PROTOCOL
    if verbose:
        print(out.groupby("split").agg(dong=("y", "size"), ngay_nang=("y_poor", "sum"), tu=("Date_target", "min"), den=("Date_target", "max")))
    return out


# ----------------------------------------------------------------------------- phép thử rò rỉ đi từ raw
def perturb_after(raw, weather, cut, seed=0):
    """Bản sao của raw và thời tiết trong đó MỌI giá trị sau ngày `cut` bị làm nhiễu mạnh: nhân hệ số ngẫu nhiên, và ở raw còn
    đặt ngẫu nhiên thành 0 (tạo chuỗi số 0 vắt qua `cut`) hoặc thành thiếu. Dữ liệu đến hết `cut` giữ nguyên từng bit."""
    rng = np.random.default_rng(seed)
    cut = pd.Timestamp(cut)
    r, w = raw.copy(), weather.copy()
    after = (pd.to_datetime(r["Date"]) > cut).to_numpy()
    n = int(after.sum())
    for c in ["AQI"] + USABLE:
        x = r.loc[after, c].to_numpy(float) * rng.uniform(0.2, 5.0, n)
        u = rng.random(n)
        if c != "AQI":
            x[u < 0.5] = 0.0                               # nhiều số 0 liền nhau ngay sau cut: thử trực tiếp quy tắc số 0 treo
        x[u > 0.9] = np.nan
        r.loc[after, c] = x
    after_w = (pd.to_datetime(w["Date"]) > cut).to_numpy()
    for c in WEATHER_SOURCE_COLS:
        w.loc[after_w, c] = w.loc[after_w, c].to_numpy(float) * rng.uniform(0.5, 1.5, int(after_w.sum())) + 3.0
    return r, w


def _same(a, b):
    """So từng ô, NaN bằng NaN, không dung sai."""
    a, b = np.asarray(a), np.asarray(b)
    if a.dtype.kind == "f" or b.dtype.kind == "f":
        a, b = a.astype(float), b.astype(float)
        return (a == b) | (np.isnan(a) & np.isnan(b))
    return a == b


def asof_check(cuts, raw=None, weather=None, seed=0):
    """Phép thử rò rỉ đi từ raw. Với mỗi ngày cắt t so đặc trưng của ngày t (mọi cột L1-L3, AQI và các cột chẩn đoán) giữa bản
    đầy đủ và (a) bản dựng từ raw + thời tiết chỉ gồm các ngày <= t; (b) bản dựng từ dữ liệu mà mọi giá trị sau t đã bị làm nhiễu.
    Trả về bảng: mỗi dòng một ngày cắt, số (thành phố) được so và số ô khác ở từng phép. Đặc trưng hợp lệ thì hai cột đều 0."""
    raw = load_raw() if raw is None else prepare_raw(raw)
    weather = load_weather_daily() if weather is None else weather
    cols = ["AQI"] + LEVELS["L3"] + DIAG_COLS
    full = _features(raw, weather)
    rows = []
    for t in [pd.Timestamp(c) for c in cuts]:
        base = full[full["Date"] == t].set_index("City")[cols].sort_index()
        cutf = make_forecast_features(raw, weather, as_of=t)
        a = cutf[cutf["Date"] == t].set_index("City")[cols].sort_index()
        r2, w2 = perturb_after(raw, weather, t, seed=seed)
        pf = _features(prepare_raw(r2), w2)
        b = pf[pf["Date"] == t].set_index("City")[cols].sort_index()
        assert list(a.index) == list(base.index) == list(b.index)
        rows.append({"ngày cắt t": t.date(), "số thành phố": len(base),
                     "ô khác (cắt raw ở t)": int(sum((~_same(a[c], base[c])).sum() for c in cols)),
                     "ô khác (nhiễu dữ liệu sau t)": int(sum((~_same(b[c], base[c])).sum() for c in cols)),
                     "dòng muộn nhất trong bản cắt": cutf["Date"].max().date()})
    return pd.DataFrame(rows).set_index("ngày cắt t")


# ----------------------------------------------------------------------------- đối chiếu với đường hồi cứu
def _keys(d):
    return pd.MultiIndex.from_arrays([d["City"].astype(str), pd.to_datetime(d["Date"])], names=["City", "Date"])


def cohort_diff(new, old, raw=None, clean_path=None):
    """Các khoá (City, ngày t) chỉ có ở MỘT trong hai cohort, kèm AQI raw và AQI của bảng sạch hồi cứu tại t và t+1, và nguyên nhân.
    `new`: bảng của đường dự báo; `old`: bảng của đường hồi cứu. Không giả định trước số lượng."""
    raw = load_raw() if raw is None else prepare_raw(raw)
    clean_path = Path(clean_path or data_paths.BASELINE_CLEAN)
    clean = pd.read_csv(clean_path, usecols=["City", "Date", "AQI", "suspect_sensor_error"], parse_dates=["Date"])
    r = raw.set_index(["City", "Date"])["AQI"]
    c = clean.assign(City=clean["City"].astype(str)).set_index(["City", "Date"])
    kn, ko = _keys(new), _keys(old)
    rows = []
    for side, idx, src in (("chỉ có ở đường dự báo (raw)", kn.difference(ko), new), ("chỉ có ở đường hồi cứu", ko.difference(kn), old)):
        split_of = pd.Series(src["split"].to_numpy(), index=_keys(src))
        for city, t in idx:
            t1 = t + pd.Timedelta(days=1)
            vals = {"AQI_raw(t)": r.get((city, t), np.nan), "AQI_raw(t+1)": r.get((city, t1), np.nan),
                    "AQI_sach(t)": c["AQI"].get((city, t), np.nan), "AQI_sach(t+1)": c["AQI"].get((city, t1), np.nan)}
            why = []
            for lab, a_raw, a_clean, when in (("AQI(t)", vals["AQI_raw(t)"], vals["AQI_sach(t)"], t), ("AQI(t+1), tức nhãn", vals["AQI_raw(t+1)"], vals["AQI_sach(t+1)"], t1)):
                if a_raw == a_raw and a_clean != a_clean:
                    flagged = bool(c["suspect_sensor_error"].get((city, when), False))
                    why.append(f"bảng sạch hồi cứu đã xoá {lab}" + (" (cờ suspect_sensor_error)" if flagged else " (không có cờ nghi lỗi)"))
                elif a_raw != a_raw:
                    why.append(f"raw thiếu {lab}")
            rows.append({"cohort": side, "City": city, "Date": t.date(), "Date_target": t1.date(), "split": split_of[(city, t)], **vals,
                         "y_poor": bool(vals["AQI_raw(t+1)"] >= POOR_AQI) if vals["AQI_raw(t+1)"] == vals["AQI_raw(t+1)"] else None,
                         "nguyen_nhan": "; ".join(why) or "chưa rõ"})
    cols = ["cohort", "City", "Date", "Date_target", "split", "AQI_raw(t)", "AQI_raw(t+1)", "AQI_sach(t)", "AQI_sach(t+1)", "y_poor", "nguyen_nhan"]
    return pd.DataFrame(rows, columns=cols).sort_values(["cohort", "City", "Date"]).reset_index(drop=True)


def feature_diff(new, old, feats=None, tol=1e-9):
    """So đặc trưng và nhãn của hai bảng trên các khoá CHUNG. Trả về (tóm tắt theo cột và theo tập, danh sách từng ô khác)."""
    feats = list(feats or (["AQI", "y"] + LEVELS["L3"]))
    a = new.assign(City=new["City"].astype(str)).set_index(["City", "Date"])
    b = old.assign(City=old["City"].astype(str)).set_index(["City", "Date"])
    common = a.index.intersection(b.index)
    a, b = a.loc[common], b.loc[common]
    summary, cells = [], []
    for f in feats:
        x, y = a[f].to_numpy(float), b[f].to_numpy(float)
        nan_diff = np.isnan(x) ^ np.isnan(y)
        diff = nan_diff | (np.abs(x - y) > tol)
        row = {"cột": f, "khoá chung": len(common), "ô khác": int(diff.sum()), "khác do một bên NaN": int(nan_diff.sum()),
               "max |lệch| (hai bên có giá trị)": float(np.nanmax(np.abs(x - y))) if (~np.isnan(x - y)).any() else 0.0}
        for s in ["train", "test", "lockdown"]:
            row[f"ô khác: {s}"] = int((diff & (a["split"].to_numpy() == s)).sum())
        summary.append(row)
        for i in np.flatnonzero(diff):
            cells.append({"City": common[i][0], "Date": common[i][1].date(), "split": a["split"].iloc[i], "cột": f,
                          "đường dự báo (raw)": x[i], "đường hồi cứu": y[i]})
    return pd.DataFrame(summary).set_index("cột"), pd.DataFrame(cells, columns=["City", "Date", "split", "cột", "đường dự báo (raw)", "đường hồi cứu"])


# ----------------------------------------------------------------------------- giao thức notebook 06, đóng gói để so các đường
def run_protocol(ds, levels=("L1", "L2", "L3"), alphas=ALPHAS):
    """Đúng giao thức Ridge của notebook 06 trên một bảng `ds`: alpha chọn bằng TimeSeriesSplit BÊN TRONG train; ngưỡng cảnh báo
    chọn bằng F2 trên dự đoán ngoài mẫu của train; fit trên toàn train; đo trên test và giai đoạn 03-07/2020. Không có lựa chọn
    nào nhìn test. Trả về dict: n, heavy, alpha, cv_mae, thr, mae, rmse, alerts, và `eval` = dự đoán theo khoá của test và của
    giai đoạn 03-07/2020 (khoá, nhãn, khối bootstrap, dự đoán từng mức) để so cặp giữa các biến thể."""
    tr, te, lk = (ds[ds["split"] == s].reset_index(drop=True) for s in ("train", "test", "lockdown"))
    out = {"n": {"train": len(tr), "test": len(te), "lockdown": len(lk)},
           "heavy": {"train": int(tr["y_poor"].sum()), "test": int(te["y_poor"].sum()), "lockdown": int(lk["y_poor"].sum())},
           "alpha": {}, "cv_mae": {}, "thr": {}, "mae": {"test": {}, "lockdown": {}}, "rmse": {"test": {}}, "alerts": {},
           "eval": {name: {"keys": _keys(d), "y": d["y"].to_numpy(float), "blocks": calendar_blocks(d["Date_target"]),
                           "pred": {PERSIST: d["AQI"].to_numpy(float)}} for name, d in (("test", te), ("lockdown", lk))}}
    y_tr, y_te = tr["y_poor"].to_numpy(), te["y_poor"].to_numpy()
    out["mae"]["test"][PERSIST], out["mae"]["lockdown"][PERSIST] = mae(te["y"], te["AQI"]), mae(lk["y"], lk["AQI"])
    out["rmse"]["test"][PERSIST] = rmse(te["y"], te["AQI"])
    idx_ref = None
    for lv in levels:
        f = LEVELS[lv]
        cv = {a: cv_score(tr, f, lambda a=a, f=f: make_pipe(f, "ridge", alpha=a))[0] for a in alphas}
        best = min(cv, key=lambda a: cv[a])
        out["alpha"][lv], out["cv_mae"][lv] = best, cv[best]
        m = make_pipe(f, "ridge", alpha=best).fit(tr[f + ["City"]], tr["y_log"])
        p_te, p_lk = np.exp(m.predict(te[f + ["City"]])), np.exp(m.predict(lk[f + ["City"]]))
        out["mae"]["test"][lv], out["mae"]["lockdown"][lv], out["rmse"]["test"][lv] = mae(te["y"], p_te), mae(lk["y"], p_lk), rmse(te["y"], p_te)
        out["eval"]["test"]["pred"][lv], out["eval"]["lockdown"]["pred"][lv] = p_te, p_lk
        idx, oof = oof_predict(tr, f, lambda f=f, best=best: make_pipe(f, "ridge", alpha=best))
        if idx_ref is None:
            idx_ref = idx
            out["thr"][PERSIST] = best_threshold(y_tr[idx], tr["AQI"].to_numpy()[idx])[0]
            out["n_oof"], out["heavy_oof"] = len(idx), int(y_tr[idx].sum())
        assert (idx == idx_ref).all()                       # mọi ngưỡng chọn trên CÙNG các dòng validation
        out["thr"][lv] = best_threshold(y_tr[idx], oof)[0]
        for tag, t in (("201", float(POOR_AQI)), ("F2", out["thr"][lv])):
            a_ = alert_metrics(y_te, p_te >= t)
            out["alerts"][f"{lv}@{tag}"] = {k: a_[k] for k in ("TP", "FP", "FN", "recall", "precision")}
    for tag, t in (("201", float(POOR_AQI)), ("F2", out["thr"][PERSIST])):
        a_ = alert_metrics(y_te, te["AQI"].to_numpy() >= t)
        out["alerts"][f"hôm nay@{tag}"] = {k: a_[k] for k in ("TP", "FP", "FN", "recall", "precision")}
    return out


def compare_paths(new=None, old=None, levels=("L1", "L2", "L3"), alphas=ALPHAS, verbose=False):
    """Ba phép so RA yêu cầu để tách tác động (RA-DEC-02 mục 2):
      A. đường hồi cứu (mã cũ), cohort của chính nó;
      B. đường dự báo từ raw (mã mới) trên CÙNG cohort với A, tức bỏ các mẫu chỉ đường mới có (theo diff thực tế);
      C. đường dự báo từ raw (mã mới) trên cohort raw đầy đủ: kết quả chính của notebook.
    Cả ba chạy cùng một giao thức (`run_protocol`), mỗi biến thể tự chọn alpha và ngưỡng trên train của nó.
    Trả về dict: table (mỗi dòng một biến thể), paired (hiệu MAE so cặp trên test và trên 03-07/2020; mỗi dòng ghi n, khoá có
    trùng không, nhãn có trùng không; hiệu chỉ được tính khi cả khoá lẫn nhãn trùng), runs, keys."""
    new = build_forecast_dataset(verbose=verbose) if new is None else new
    old = build_dataset_retrospective(verbose=False) if old is None else old
    kn, ko = _keys(new), _keys(old)
    both = new[kn.isin(ko)].reset_index(drop=True)
    variants = {"A. hồi cứu (mã cũ), cohort hồi cứu": old,
                "B. dự báo từ raw (mã mới), bỏ mẫu chỉ có ở raw": both,
                "C. dự báo từ raw (mã mới), cohort raw": new}
    runs = {k: run_protocol(v, levels, alphas) for k, v in variants.items()}
    rows = []
    for k, r in runs.items():
        row = {"biến thể": k, "n train": r["n"]["train"], "n test": r["n"]["test"], "n 03-07/2020": r["n"]["lockdown"],
               "ngày nặng train": r["heavy"]["train"], "ngày nặng test": r["heavy"]["test"],
               **{f"alpha {lv}": r["alpha"][lv] for lv in levels},
               f"ngưỡng F2 hôm nay": r["thr"][PERSIST], **{f"ngưỡng F2 {lv}": r["thr"][lv] for lv in levels},
               "MAE test hôm nay": r["mae"]["test"][PERSIST], **{f"MAE test {lv}": r["mae"]["test"][lv] for lv in levels},
               "MAE 03-07/2020 hôm nay": r["mae"]["lockdown"][PERSIST], **{f"MAE 03-07/2020 {lv}": r["mae"]["lockdown"][lv] for lv in levels}}
        for lv in levels:
            for tag in ("201", "F2"):
                a_ = r["alerts"][f"{lv}@{tag}"]
                row[f"{lv}@{tag} TP/FP/FN"] = f"{a_['TP']}/{a_['FP']}/{a_['FN']}"
        rows.append(row)
    table = pd.DataFrame(rows).set_index("biến thể")

    names = list(runs)
    paired = []
    for a_name, b_name in ((names[1], names[0]), (names[2], names[0]), (names[2], names[1])):
        for part, part_label in (("test", "test"), ("lockdown", "03-07/2020")):
            ea, eb = runs[a_name]["eval"][part], runs[b_name]["eval"][part]
            same_keys = len(ea["keys"]) == len(eb["keys"]) and bool((ea["keys"] == eb["keys"]).all())
            same_y = same_keys and bool(np.array_equal(ea["y"], eb["y"]))
            for lv in levels:
                rec = {"so sánh (A trừ B)": f"{a_name[:2]} − {b_name[:2]}", "tập": part_label, "mức": lv,
                       "n (A)": len(ea["keys"]), "n (B)": len(eb["keys"]), "cùng khoá": same_keys, "cùng nhãn": same_y}
                if same_y:                                    # chỉ gọi là so cặp khi cùng mẫu VÀ cùng outcome
                    d_, lo, hi = boot_mae_diff(ea["blocks"], np.abs(ea["y"] - ea["pred"][lv]), np.abs(eb["y"] - eb["pred"][lv]))
                    rec.update({"ΔMAE": d_, "KTC 95% thấp": lo, "KTC 95% cao": hi,
                                "max |lệch dự đoán|": float(np.max(np.abs(ea["pred"][lv] - eb["pred"][lv])))})
                paired.append(rec)
    return {"table": table, "paired": pd.DataFrame(paired), "runs": runs,
            "keys": {"chỉ có ở đường dự báo": kn.difference(ko), "chỉ có ở đường hồi cứu": ko.difference(kn)}}
