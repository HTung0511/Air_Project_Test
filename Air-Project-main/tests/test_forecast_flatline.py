"""DEV-02 / F01 - quy tắc "số 0 treo" và forward-fill theo snapshot as-of t (RA-DEC-02 mục 4).

Điều phải đúng:
  * Ngày thứ nhất và thứ hai của một chuỗi số 0 giữ số 0; từ ngày thứ ba, số 0 của ngày hiện tại bị che.
  * Một chuỗi không nối qua ngày thiếu số liệu, ngày lịch bị thiếu, hay ranh thành phố.
  * Số 0 đã thuộc chuỗi >= 3 ngày (tính đến hết t) không được làm nguồn forward-fill cho hàng t.
  * Hàng của ngày t chỉ phụ thuộc dữ liệu <= t: thêm ngày mới vào cuối chuỗi không làm đổi các hàng đã có.
  * Không nội suy, không backward-fill; forward-fill tối đa 2 ngày.
"""
import numpy as np
import pandas as pd
import pytest

import forecast_utils as F
import utils as U

NAN = np.nan


def asof(v):
    r = F.asof_pollutant(np.array(v, float))
    return r["value"].tolist(), r["lag"].tolist(), r["flat"].tolist()


def same(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return bool(((a == b) | (np.isnan(a) & np.isnan(b))).all())


# ----------------------------------------------------------------------------- hai "trọng tài" độc lập với mã chính
def oracle_prefix(v, min_run=F.FLATLINE_MIN_RUN, limit=F.FFILL_LIMIT):
    """Trọng tài 1 - đúng nghĩa đen của contract: với MỖI ngày t, lấy prefix v[<= t], áp chính hàm số 0 treo của nhánh làm sạch
    (`utils.flag_flatline_zeros`) lên prefix đó, forward-fill tối đa `limit`, rồi đọc giá trị của ngày t."""
    out = []
    for t in range(len(v)):
        pre = pd.DataFrame({"x": np.asarray(v[:t + 1], float)})
        masked, _ = U.flag_flatline_zeros(pre, cols=["x"], min_run=min_run)
        out.append(masked["x"].ffill(limit=limit).iloc[-1])
    return out


def oracle_loop(v, min_run=F.FLATLINE_MIN_RUN, limit=F.FFILL_LIMIT):
    """Trọng tài 2 - vòng lặp thuần Python, viết khác hẳn mã chính: trả (value, lag, flat) cho từng ngày."""
    v = [float(x) for x in v]
    vals, lags, flats = [], [], []
    for t in range(len(v)):
        def run_len_as_of_t(s):                              # độ dài chuỗi số 0 chứa ngày s, chỉ đếm trong đoạn [.., t]
            if not v[s] == 0:
                return 0
            a = s
            while a - 1 >= 0 and v[a - 1] == 0:
                a -= 1
            b = s
            while b + 1 <= t and v[b + 1] == 0:
                b += 1
            return b - a + 1
        val, lag = NAN, -1
        for k in range(limit + 1):
            s = t - k
            if s < 0:
                break
            if v[s] == v[s] and run_len_as_of_t(s) < min_run:
                val, lag = v[s], k
                break
        vals.append(val); lags.append(lag); flats.append(run_len_as_of_t(t) >= min_run)
    return vals, lags, flats


# ----------------------------------------------------------------------------- ví dụ viết tay
def test_trailing_zero_run():
    assert F.trailing_zero_run([5, 0, 0, 0, NAN, 0, 3, 0]).tolist() == [0, 1, 2, 3, 0, 1, 0, 1]
    assert F.trailing_zero_run([0, 0]).tolist() == [1, 2] and F.trailing_zero_run([]).tolist() == []


@pytest.mark.parametrize("n_zero, expect_value, expect_flat", [
    (1, [5, 0, 4], [False, False, False]),
    (2, [5, 0, 0, 4], [False, False, False, False]),
    (3, [5, 0, 0, NAN, 4], [False, False, False, True, False]),
    (4, [5, 0, 0, NAN, NAN, 4], [False, False, False, True, True, False]),
])
def test_zero_run_of_length_1_to_4_mid_series(n_zero, expect_value, expect_flat):
    """Chuỗi 1 hoặc 2 số 0: giữ. Từ số 0 thứ ba: che (và 5 nằm ngoài tầm forward-fill 2 ngày vì hai số 0 trước cũng bị loại)."""
    value, lag, flat = asof([5] + [0] * n_zero + [4])
    assert same(value, expect_value) and flat == expect_flat


def test_zero_run_at_series_start():
    value, lag, flat = asof([0, 0, 0, 0, 2])
    assert same(value, [0, 0, NAN, NAN, 2]) and flat == [False, False, True, True, False] and lag == [0, 0, -1, -1, 0]


def test_masked_zeros_are_not_a_forward_fill_source():
    """Sau một chuỗi 3 số 0 là ngày thiếu: hàng đó không được điền bằng số 0 đã bị coi là treo."""
    value, lag, flat = asof([7, 0, 0, 0, NAN, NAN, 3])
    assert same(value, [7, 0, 0, NAN, NAN, NAN, 3]) and lag == [0, 0, 0, -1, -1, -1, 0]


def test_unconfirmed_zeros_are_a_valid_fill_source():
    """Chuỗi mới có 2 số 0 rồi thiếu: chưa đủ bằng chứng là treo, nên số 0 đã công bố vẫn được dùng để điền (tối đa 2 ngày)."""
    value, lag, flat = asof([7, 0, 0, NAN, NAN, NAN, 3])
    assert same(value, [7, 0, 0, 0, 0, NAN, 3]) and lag == [0, 0, 0, 1, 2, -1, 0] and not any(flat)


def test_missing_day_breaks_a_zero_run():
    """0, 0, thiếu, 0, 0: hai chuỗi dài 2, không phải một chuỗi dài 4 hay 5. Không ô nào bị che."""
    value, lag, flat = asof([4, 0, 0, NAN, 0, 0, 6])
    assert same(value, [4, 0, 0, 0, 0, 0, 6]) and not any(flat)
    assert F.trailing_zero_run([4, 0, 0, NAN, 0, 0, 6]).tolist() == [0, 1, 2, 0, 1, 2, 0]


def test_no_interpolation_and_no_backward_fill():
    value, lag, _ = asof([5, NAN, NAN, NAN, 9])
    assert same(value, [5, 5, 5, NAN, 9]) and lag == [0, 1, 2, -1, 0]        # không có 6, 7, 8 và ngày thứ 4 không lấy 9 của ngày sau
    value, lag, _ = asof([NAN, NAN, 7])
    assert same(value, [NAN, NAN, 7])


def test_forward_fill_limit_is_two_days():
    assert F.FFILL_LIMIT == 2 and F.FLATLINE_MIN_RUN == 3
    value, lag, _ = asof([3, NAN, NAN, NAN, NAN])
    assert same(value, [3, 3, 3, NAN, NAN])


def test_earlier_rows_do_not_change_when_days_are_appended():
    """RA-DEC-02 mục 4.3: hàng ngày 1 và 2 của một chuỗi số 0 không đổi khi ngày 3, 4 xuất hiện; hàng ngày 3 bị che trong prefix của chính nó."""
    base = [6, 0, 0]
    v2, l2, f2 = asof(base)
    for more in ([0], [0, 0], [0, 0, 0, 5], [NAN, 0, 0, 0]):
        v, l, f = asof(base + more)
        assert same(v[:3], v2) and l[:3] == l2 and f[:3] == f2
    v, l, f = asof(base + [0, 0])
    assert same(v, [6, 0, 0, NAN, NAN]) and f == [False, False, False, True, True] and l == [0, 0, 0, -1, -1]


# ----------------------------------------------------------------------------- tính chất, trên chuỗi ngẫu nhiên
def random_series(rng, n):
    kind = rng.choice(4, size=n, p=[0.35, 0.4, 0.2, 0.05])
    v = np.where(kind == 0, 0.0, np.where(kind == 2, np.nan, rng.integers(1, 9, n).astype(float)))
    return v


@pytest.mark.parametrize("seed", range(25))
def test_matches_both_oracles_on_random_series(seed):
    rng = np.random.default_rng(seed)
    v = random_series(rng, int(rng.integers(1, 70)))
    value, lag, flat = asof(v)
    o_val, o_lag, o_flat = oracle_loop(v)
    assert same(value, o_val) and lag == o_lag and flat == o_flat
    assert same(value, oracle_prefix(v))


@pytest.mark.parametrize("seed", range(25))
def test_prefix_consistency_on_random_series(seed):
    """Tính nhân quả viết thành tính chất: kết quả tại mọi i < L của chuỗi cắt ở L trùng với kết quả của chuỗi đầy đủ."""
    rng = np.random.default_rng(1000 + seed)
    v = random_series(rng, 60)
    full = F.asof_pollutant(v)
    for L in range(1, len(v) + 1):
        part = F.asof_pollutant(v[:L])
        for k in ("value", "lag", "flat", "run"):
            assert same(part[k], full[k][:L]), (L, k)


# ----------------------------------------------------------------------------- trên raw thật
def test_real_raw_matches_loop_oracle_for_all_feature_pollutants(raw8):
    """Cả 5 chất, cả 8 thành phố, MỌI ngày: mã chính trùng trọng tài vòng lặp ở giá trị, nguồn điền và cờ che."""
    n = 0
    for city, x in raw8.groupby("City", sort=False):
        for col in F.FLATLINE_COLS:
            v = x[col].to_numpy()
            r = F.asof_pollutant(v)
            o_val, o_lag, o_flat = oracle_loop(v)
            assert same(r["value"], o_val) and r["lag"].tolist() == o_lag and r["flat"].tolist() == o_flat, (city, col)
            n += len(v)
    assert n == 5 * len(raw8)


@pytest.mark.slow
def test_real_co_matches_literal_prefix_oracle_in_common_window(raw8):
    """CO (chất duy nhất có số 0 trong raw): với mọi ngày của khoảng chung, cắt chuỗi ở ngày đó rồi áp hàm số 0 treo của nhánh
    làm sạch lên prefix. Kết quả phải trùng mã chính. Đây là phép walk-forward đúng nghĩa đen cho quy tắc số 0 treo."""
    n = n_flat = 0
    for city, x in raw8.groupby("City", sort=False):
        x = x.reset_index(drop=True)
        v = x["CO"].to_numpy()
        r = F.asof_pollutant(v)
        for t in np.flatnonzero((x["Date"] >= F.COMMON_START).to_numpy()):
            pre = pd.DataFrame({"x": v[:t + 1]})
            masked, _ = U.flag_flatline_zeros(pre, cols=["x"], min_run=F.FLATLINE_MIN_RUN)
            expect = masked["x"].ffill(limit=F.FFILL_LIMIT).iloc[-1]
            assert same([r["value"][t]], [expect]), (city, x["Date"][t])
            n += 1; n_flat += int(r["flat"][t])
    assert n == 8 * 1114 and n_flat > 0


def test_only_co_has_zeros_so_other_pollutants_reduce_to_plain_ffill(raw8, features_full):
    """PM2.5, NO2, SO2, O3 không có số 0 nào trong raw, nên với chúng quy tắc chỉ còn là forward-fill 2 ngày của raw."""
    zeros = {c: int((raw8[c] == 0).sum()) for c in F.FLATLINE_COLS}
    assert zeros["CO"] > 0 and all(zeros[c] == 0 for c in F.FLATLINE_COLS if c != "CO"), zeros
    m = raw8.merge(features_full, on=["City", "Date"], validate="1:1", suffixes=("_raw", ""))
    for feat, col in F.POLL_SOURCE.items():
        if col == "CO":
            continue
        plain = np.log1p(m.groupby("City")[col].ffill(limit=2))
        assert same(m[feat], plain) and not m[feat + "_flat"].any(), feat


def test_feature_values_are_always_an_observed_raw_value_never_interpolated(raw8, features_full):
    """Mọi giá trị đặc trưng chất ô nhiễm đúng bằng log1p của MỘT giá trị raw quan sát được ở ngày t, t-1 hoặc t-2 (theo cột *_lag)."""
    m = raw8.merge(features_full, on=["City", "Date"], validate="1:1", suffixes=("_raw", ""))
    for feat, col in F.POLL_SOURCE.items():
        lag = m[feat + "_lag"].to_numpy()
        src = np.full(len(m), np.nan)
        for k in range(F.FFILL_LIMIT + 1):
            shifted = m.groupby("City")[col].shift(k).to_numpy()
            src[lag == k] = shifted[lag == k]
        assert same(m[feat], np.log1p(src)), feat
        assert set(np.unique(lag)) <= {-1, 0, 1, 2}
        assert (m[feat].isna().to_numpy() == (lag == -1)).all()


def test_flatline_rule_is_limited_to_the_declared_columns(raw8, features_full, baseline_daily):
    """Quy tắc chỉ áp cho 5 chất làm đặc trưng. AQI và thời tiết không bị che: mưa bằng 0 nhiều ngày liền vẫn là số 0."""
    assert F.FLATLINE_COLS == ["PM2.5", "NO2", "CO", "SO2", "O3"]
    m = features_full.merge(baseline_daily[["City", "Date", "precip_sum"]], on=["City", "Date"], validate="1:1")
    assert same(m["precip_log"], np.log1p(m["precip_sum"]))
    assert int((m["precip_sum"] == 0).sum()) > 1000 and m["precip_log"].notna().all()
    r = raw8.merge(features_full, on=["City", "Date"], validate="1:1", suffixes=("_raw", ""))
    assert same(r["aqi_0"], np.log(r["AQI_raw"])) and same(r["AQI"], r["AQI_raw"])


# ----------------------------------------------------------------------------- ranh thành phố, ranh train/test, ngày lịch thiếu
def tiny_raw(rows):
    """rows: list (City, Date, AQI, CO). Các chất khác đặt 1.0."""
    d = pd.DataFrame(rows, columns=["City", "Date", "AQI", "CO"])
    d["Date"] = pd.to_datetime(d["Date"])
    for c in ("PM2.5", "NO2", "SO2", "O3"):
        d[c] = 1.0
    return d


def tiny_weather(raw):
    w = raw[["City", "Date"]].drop_duplicates().copy()
    full = []
    for city, x in w.groupby("City"):
        full.append(pd.DataFrame({"City": city, "Date": pd.date_range(x.Date.min() - pd.Timedelta(days=3), x.Date.max() + pd.Timedelta(days=3))}))
    w = pd.concat(full, ignore_index=True)
    for i, c in enumerate(F.WEATHER_SOURCE_COLS):
        w[c] = 1.0 + i + np.arange(len(w)) * 0.01
    return w


def feats(raw):
    return F.make_forecast_features(raw, tiny_weather(raw)).set_index(["City", "Date"])


def test_zero_run_and_fill_do_not_cross_city_boundary():
    rows = [("Delhi", f"2019-01-0{i}", 100, v) for i, v in zip(range(1, 5), [3, 5, 0, 0])] + \
           [("Jaipur", f"2019-01-0{i}", 100, v) for i, v in zip(range(1, 5), [0, NAN, 0, 0])]
    f = feats(tiny_raw(rows))
    j = f.loc["Jaipur"]
    assert j["co_0"].tolist()[0] == 0.0 and not j["co_0_flat"].any()         # số 0 đầu của Jaipur là ngày thứ nhất, không phải ngày thứ ba
    assert j["co_0_lag"].tolist() == [0, 1, 0, 0]
    rows = [("Delhi", "2019-01-01", 100, 5.0), ("Delhi", "2019-01-02", 100, 6.0), ("Jaipur", "2019-01-01", 100, NAN), ("Jaipur", "2019-01-02", 100, 2.0)]
    f = feats(tiny_raw(rows))
    assert np.isnan(f.loc[("Jaipur", pd.Timestamp("2019-01-01")), "co_0"])    # không kéo 6.0 của Delhi sang
    assert np.isnan(f.loc[("Jaipur", pd.Timestamp("2019-01-01")), "aqi_1"])


def test_zero_run_straddling_the_train_test_boundary():
    """Chuỗi số 0 bắt đầu 29/06/2019 (train) và kéo sang tháng 7 (test): hai hàng cuối train giữ số 0 dù tháng 7 có gì."""
    days = pd.date_range("2019-06-25", "2019-07-04")
    co = [4, 4, 4, 4, 0, 0, 0, 0, 0, 2]                                      # 0 từ 29/06
    full = tiny_raw([("Delhi", d, 150, v) for d, v in zip(days, co)])
    f_full = feats(full).loc["Delhi"]
    f_cut = feats(full[full.Date <= "2019-06-30"]).loc["Delhi"]
    for d in ("2019-06-29", "2019-06-30"):
        assert f_full.loc[d, "co_0"] == 0.0 and not f_full.loc[d, "co_0_flat"]
        assert f_cut.loc[d, "co_0"] == f_full.loc[d, "co_0"] and f_cut.loc[d, "co_0_lag"] == f_full.loc[d, "co_0_lag"]
    assert np.isnan(f_full.loc["2019-07-01", "co_0"]) and f_full.loc["2019-07-01", "co_0_flat"]
    tgt = F.attach_target(F.make_forecast_features(full, tiny_weather(full)), F.prepare_raw(full)).set_index("Date")
    assert tgt.loc["2019-06-29", "split"] == "train" and tgt.loc["2019-06-30", "split"] == "test"     # chia theo ngày ĐƯỢC DỰ ĐOÁN


def test_missing_calendar_day_is_not_skipped_over():
    """Raw thiếu hẳn một ngày lịch: chuỗi được chèn dòng NaN, nên nhãn của ngày trước chỗ thiếu là NaN (không lấy nhầm ngày kế tiếp
    trong file) và chuỗi số 0 không nối qua chỗ thiếu."""
    rows = [("Delhi", "2019-01-01", 100, 0), ("Delhi", "2019-01-02", 110, 0), ("Delhi", "2019-01-04", 130, 0), ("Delhi", "2019-01-05", 140, 0)]
    raw = tiny_raw(rows)
    prep = F.prepare_raw(raw)
    assert len(prep) == 5 and prep.attrs["n_inserted_days"] == 1 and prep["AQI"].isna().sum() == 1
    f = F.make_forecast_features(raw, tiny_weather(raw))
    d = F.attach_target(f, prep).set_index("Date")
    assert np.isnan(d.loc["2019-01-02", "y"]) and d.loc["2019-01-01", "y"] == 110 and d.loc["2019-01-04", "y"] == 140
    assert np.isnan(d.loc["2019-01-04", "aqi_1"]) and d.loc["2019-01-04", "aqi_2"] == np.log(110)
    assert not d["co_0_flat"].any() and d["co_0"].tolist() == [0.0] * 5      # 0,0,(thiếu),0,0: không chuỗi nào đủ 3
    assert d["co_0_lag"].tolist() == [0, 0, 1, 0, 0]


def test_short_series_and_fully_missing_pollutant():
    """Đầu chuỗi ngắn và một chất thiếu hoàn toàn: không lỗi; đặc trưng thiếu là NaN, để imputer xử lý."""
    raw = tiny_raw([("Delhi", "2019-01-01", 100, NAN), ("Delhi", "2019-01-02", 120, NAN)])
    f = feats(raw).loc["Delhi"]
    assert f["co_0"].isna().all() and (f["co_0_lag"] == -1).all()
    assert np.isnan(f["aqi_wk"]).all() and np.isnan(f["aqi_1"].iloc[0]) and f["aqi_1"].iloc[1] == np.log(100)
    assert np.isnan(f["pressure_dev"]).all() and np.isnan(f["d_pressure"].iloc[0])
    one = feats(tiny_raw([("Delhi", "2019-01-01", 100, 0.0)]))
    assert len(one) == 1 and one["co_0"].iloc[0] == 0.0


# ----------------------------------------------------------------------------- ghi lại mọi lần che và điền thực tế (RA-DEC-02 mục 3)
def test_masking_log_lists_every_masked_cell_and_every_fill_source():
    """Một chuỗi viết tay: 4, 0, 0, 0, 0, NaN, 7, NaN, NaN, NaN, 0. Bảng tóm tắt và danh sách ô bị che phải đúng từng ô."""
    days = pd.date_range("2018-03-01", periods=12)
    co = [4, 0, 0, 0, 0, NAN, 7, NAN, NAN, NAN, 0, 5]
    raw = tiny_raw([("Delhi", d, 100 + i, v) for i, (d, v) in enumerate(zip(days, co))])
    ds = F.build_forecast_dataset(raw, tiny_weather(raw), verbose=False, start=days[0], end=days[-1])
    assert len(ds) == 11 and (ds["split"] == "train").all()                   # 11 cặp (t, t+1), nhãn là AQI của ngày lịch kế tiếp
    row = F.masking_summary(ds).loc[("co_0", "CO", "train")]
    # ngày:        1  2  3  4  5  6    7  8  9  10   11
    # nguồn (lag): 0  0  0  -1 -1 -1   0  1  2  -1   0      (ngày 4, 5: số 0 bị che; ngày 6: thiếu, hai ngày trước là số 0 đã che)
    assert ds["co_0_lag"].tolist() == [0, 0, 0, -1, -1, -1, 0, 1, 2, -1, 0]
    assert row["số mẫu"] == 11 and row["che số 0 treo tại t"] == 2 and row["giá trị dùng là số 0"] == 3      # ngày 2, 3 và 11 giữ số 0
    assert [row[c] for c in F.SOURCE_COLS] == [5, 1, 1, 4] and sum(row[c] for c in F.SOURCE_COLS) == row["số mẫu"]
    cells = F.masked_cells(ds, raw)
    assert cells["Date"].tolist() == [days[3], days[4]] and cells["cot_raw"].tolist() == ["CO", "CO"]
    assert cells["gia_tri_raw"].tolist() == [0.0, 0.0] and cells["chuoi_0_den_t"].tolist() == [3, 4]          # độ dài chuỗi TÍNH ĐẾN t
    assert cells["nguon_dien"].tolist() == [-1, -1] and cells["gia_tri_nguon"].isna().all()
    other = F.masking_summary(ds).drop(index="co_0", level="đặc trưng")
    assert (other["che số 0 treo tại t"] == 0).all() and (other[F.SOURCE_COLS[0]] == other["số mẫu"]).all()   # các chất khác: không che, không điền


def test_masking_log_on_real_data_matches_a_direct_count_from_raw(raw8, ds_new):
    """Trên dữ liệu thật: số ô bị che đếm lại THẲNG từ raw bằng vòng lặp thuần Python (không qua `asof_pollutant`) phải bằng bảng tóm tắt;
    mỗi mẫu có đúng một nguồn; ô bị che không bao giờ được điền."""
    tab, cells = F.masking_summary(ds_new), F.masked_cells(ds_new, raw8)
    assert (tab[F.SOURCE_COLS].sum(axis=1) == tab["số mẫu"]).all() and len(cells) == int(tab["che số 0 treo tại t"].sum())
    assert (cells["gia_tri_raw"] == 0).all() and (cells["chuoi_0_den_t"] >= F.FLATLINE_MIN_RUN).all() and (cells["nguon_dien"] == -1).all()
    keys = set(zip(ds_new["City"].astype(str), ds_new["Date"]))
    expect = []
    for col in F.FLATLINE_COLS:
        for city, x in raw8.groupby("City"):
            run = 0
            for d, v in zip(x["Date"], x[col]):
                run = run + 1 if v == 0 else 0                                # NaN == 0 là False: ngày thiếu làm đứt chuỗi
                if run >= F.FLATLINE_MIN_RUN and (city, d) in keys:
                    expect.append((col, city, d, run))
    got = list(zip(cells["cot_raw"], cells["City"], cells["Date"], cells["chuoi_0_den_t"]))
    assert sorted(got) == sorted(expect) and len(expect) > 0
    assert set(cells["cot_raw"]) == {"CO"}                                    # snapshot hiện có: chỉ CO có số 0 trong raw
