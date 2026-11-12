"""DEV-02 / F01 - phép thử chống rò rỉ đi từ RAW cho đường dự báo (handoff DEV-02 mục 9; RA-DEC-02 mục 4 "Test bắt buộc").

Cách thử: lấy raw và thời tiết, CẮT ở ngày t (hoặc làm nhiễu mọi giá trị sau t), dựng lại đặc trưng, rồi so đặc trưng của ngày t
với bản dựng từ dữ liệu đầy đủ. So MỌI cột L1-L3, AQI và các cột chẩn đoán (nguồn forward-fill, cờ che), không dung sai.
Nhãn và điều kiện giữ mẫu được kiểm RIÊNG: chúng được phép phụ thuộc AQI(t+1), đặc trưng thì không.
"""
import numpy as np
import pandas as pd
import pytest

import forecast_utils as F
import model_utils as M
import utils as U
from conftest import evidence_dir

L3 = M.LEVELS["L3"]
COLS = ["AQI"] + L3 + F.DIAG_COLS

# 17 ngày cắt của DA ở V05 (12 ngày đầu là những ngày bảng sạch hồi cứu đã đổi khi cắt raw)
V05_CUTS = ["2017-06-14", "2017-07-08", "2017-07-09", "2017-07-30", "2017-08-12", "2017-08-29", "2017-08-30", "2017-11-09", "2017-11-13",
            "2018-02-06", "2018-06-15", "2018-09-15", "2018-12-01", "2019-06-30", "2019-11-15", "2020-01-10", "2020-02-29"]
# ngày có đặc trưng khác ở V07 (walk-forward của DA): số 0 treo của CO, điểm nghi lỗi lúc có lúc không
V07_DAYS = ["2017-07-10", "2017-07-11", "2017-07-14", "2017-07-15", "2017-07-16", "2017-07-29", "2017-08-06", "2017-08-18", "2017-10-10",
            "2017-10-24", "2017-11-26", "2018-01-02", "2018-03-18", "2018-05-01", "2018-05-02", "2018-05-05", "2018-07-16", "2018-08-29",
            "2018-11-03", "2019-01-04", "2019-02-19"]
# ranh các tập: ngày t cuối của train (dự đoán 30/06/2019), ngày t đầu của test, tương tự cho test / 03-07/2020, và hai đầu khoảng chung
BOUNDARY = ["2017-06-15", "2019-06-28", "2019-06-29", "2019-07-01", "2020-02-27", "2020-02-28", "2020-03-01", "2020-06-29", "2020-06-30"]
ALL_CUTS = sorted(set(V05_CUTS + V07_DAYS + BOUNDARY))


def same(a, b):
    return bool(F._same(a, b).all())


def test_feature_table_has_no_column_from_the_next_day(features_full):
    """Bảng đặc trưng as-of không chứa nhãn, tập, hay thời tiết ngày mai; các cột đó chỉ xuất hiện sau `attach_target`."""
    cols = set(features_full.columns)
    assert cols == {"City", "Date", "Date_target", "AQI", "today_poor"} | set(L3) | set(F.DIAG_COLS)
    assert not cols & ({"y", "y_log", "y_poor", "split"} | set(M.NEXT_FEATS))
    assert not set(M.NEXT_FEATS) & set(L3) and set(M.LEVELS["L1"]) < set(M.LEVELS["L2"]) < set(L3)


def test_cut_at_t_and_perturb_after_t_leave_features_of_t_unchanged(raw8, baseline_daily):
    """Tại mọi ngày có vấn đề ở V05/V07 và mọi ranh tập: cắt raw + thời tiết ở t, hoặc làm nhiễu mọi thứ sau t, đều không đổi
    một ô đặc trưng nào của ngày t (8 thành phố x toàn bộ cột L1-L3, AQI, nguồn điền, cờ che)."""
    chk = F.asof_check(ALL_CUTS, raw8, baseline_daily, seed=11)
    assert len(chk) == len(ALL_CUTS) and (chk["số thành phố"] == 8).all()
    assert (chk["ô khác (cắt raw ở t)"] == 0).all() and (chk["ô khác (nhiễu dữ liệu sau t)"] == 0).all()
    assert (pd.to_datetime(chk["dòng muộn nhất trong bản cắt"]) == pd.to_datetime(chk.index)).all()
    d = evidence_dir()
    if d is not None:
        chk.to_csv(d / "leakage_cut_and_perturb_check.csv")


def test_perturbation_really_changes_the_future_and_only_the_future(raw8, baseline_daily):
    """Phép làm nhiễu có 'lực': mọi cột sau t đổi nhiều, kể cả tạo chuỗi số 0 ngay sau t; trước và tại t giữ nguyên từng bit."""
    t = pd.Timestamp("2018-08-29")
    r2, w2 = F.perturb_after(raw8, baseline_daily, t, seed=3)
    before = raw8["Date"] <= t
    pd.testing.assert_frame_equal(r2[before], raw8[before])
    pd.testing.assert_frame_equal(w2[w2["Date"] <= t], baseline_daily[baseline_daily["Date"] <= t])
    for c in ["AQI", "CO", "PM2.5"]:
        a, b = raw8.loc[~before, c], r2.loc[~before, c]
        assert (a.notna() & (a != b)).mean() > 0.8, c
    nxt = r2[(r2["Date"] > t) & (r2["Date"] <= t + pd.Timedelta(days=5))]
    assert (nxt["CO"] == 0).mean() > 0.2                                     # có số 0 ngay sau t để thử quy tắc số 0 treo
    f1, f2 = F._features(raw8, baseline_daily), F._features(F.prepare_raw(r2), w2)
    later = f1["Date"] > t + pd.Timedelta(days=1)
    assert not same(f1.loc[later, "aqi_0"], f2.loc[later, "aqi_0"])           # đặc trưng của các ngày SAU t thì phải đổi


def test_retrospective_flatline_rule_fails_the_same_test_but_asof_rule_passes(raw8):
    """Đối chứng: cùng phép thử cắt ở t làm lộ lỗi của quy tắc hồi cứu. Amritsar, CO: số 0 xuất hiện 10/07/2017 và kéo dài."""
    x = raw8[raw8["City"] == "Amritsar"].reset_index(drop=True)
    t = pd.Timestamp("2017-07-10")
    i = int(np.flatnonzero((x["Date"] == t).to_numpy())[0])
    assert x["CO"].iloc[i] == 0 and (x["CO"].iloc[i:i + 3] == 0).all() and x["CO"].iloc[i - 1] != 0
    full, _ = U.flag_flatline_zeros(x[["CO"]], cols=["CO"], min_run=3)
    cut, _ = U.flag_flatline_zeros(x.loc[:i, ["CO"]], cols=["CO"], min_run=3)
    assert np.isnan(full["CO"].iloc[i]) and cut["CO"].iloc[i] == 0            # hồi cứu: giá trị ngày t đổi khi ngày sau xuất hiện
    r_full, r_cut = F.asof_pollutant(x["CO"].to_numpy()), F.asof_pollutant(x["CO"].to_numpy()[:i + 1])
    assert r_full["value"][i] == r_cut["value"][i] == 0.0 and not r_full["flat"][i]      # as-of: không đổi, giữ số 0 đã công bố
    assert np.isnan(r_full["value"][i + 2]) and r_full["flat"][i + 2]         # tới ngày thứ ba thì hàng của CHÍNH ngày đó bị che


@pytest.mark.slow
def test_walk_forward_every_day_of_the_common_window(raw8, baseline_daily, features_full):
    """Walk-forward đầy đủ: với MỖI ngày t của khoảng chung (1.114 ngày), dựng đặc trưng từ raw + thời tiết cắt ở t, so hàng t của
    8 thành phố với bảng đầy đủ. Không một ô nào được khác."""
    days = pd.date_range(F.COMMON_START, F.COMMON_END)
    full = features_full.set_index(["Date", "City"])[COLS].sort_index()
    n_rows = n_cells = n_diff = 0
    worst = []
    for t in days:
        r, w = raw8[raw8["Date"] <= t], baseline_daily[baseline_daily["Date"] <= t]
        f = F._features(r, w)
        a = f[f["Date"] == t].set_index("City")[COLS].sort_index()
        b = full.loc[t].sort_index()
        assert list(a.index) == list(b.index)
        d = int(sum((~F._same(a[c], b[c])).sum() for c in COLS))
        n_rows += len(a); n_cells += a.size; n_diff += d
        if d:
            worst.append((t.date(), d))
    d_ = evidence_dir()
    if d_ is not None:
        pd.DataFrame([{"số ngày cắt": len(days), "từ": days[0].date(), "đến": days[-1].date(), "hàng (thành phố, ngày) được so": n_rows,
                       "số cột mỗi hàng": len(COLS), "ô được so": n_cells, "ô khác": n_diff}]).to_csv(d_ / "leakage_walk_forward_all_days.csv", index=False)
    assert (len(days), n_rows) == (1114, 8912) and n_diff == 0, worst[:10]


# ----------------------------------------------------------------------------- nhãn và điều kiện giữ mẫu: kiểm riêng
def _row(d, city, t):
    return d[(d["City"] == city) & (d["Date"] == pd.Timestamp(t))].iloc[0]


def test_label_is_raw_aqi_of_next_calendar_day_and_never_filled(raw8, baseline_daily, ds_new):
    r = raw8.set_index(["City", "Date"])["AQI"]
    y = pd.Series([r.get((c, t)) for c, t in zip(ds_new["City"].astype(str), ds_new["Date_target"])])
    assert same(ds_new["y"], y) and ds_new["y"].notna().all()
    assert (ds_new["Date_target"] == ds_new["Date"] + pd.Timedelta(days=1)).all()
    assert same(ds_new["AQI"], [r.get((c, t)) for c, t in zip(ds_new["City"].astype(str), ds_new["Date"])])
    assert same(ds_new["y_log"], np.log(ds_new["y"])) and (ds_new["y_poor"] == (ds_new["y"] >= 201)).all()
    assert ds_new["y"].max() > 500 and ds_new["AQI"].max() > 500             # không cắt ở 500
    assert (ds_new["y"] == ds_new["y"].round()).all()                        # không có giá trị "lưng chừng" kiểu nội suy


def test_changing_next_day_aqi_changes_label_and_eligibility_but_not_features(raw8, baseline_daily):
    """Thêm, bỏ hoặc đổi AQI(t+1): hàng t có thể vào/ra mẫu đánh giá và nhãn đổi theo, nhưng đặc trưng của hàng t giữ nguyên."""
    city, t = "Delhi", pd.Timestamp("2019-01-10")
    t1 = t + pd.Timedelta(days=1)
    base = F.build_forecast_dataset(raw8, baseline_daily, verbose=False)
    row0 = _row(base, city, t)

    removed = raw8.copy()
    removed.loc[(removed["City"] == city) & (removed["Date"] == t1), "AQI"] = np.nan
    ds_removed = F.build_forecast_dataset(removed, baseline_daily, verbose=False)
    assert ((ds_removed["City"] == city) & (ds_removed["Date"] == t)).sum() == 0          # mất nhãn -> ra khỏi mẫu đánh giá
    assert ((ds_removed["City"] == city) & (ds_removed["Date"] == t1)).sum() == 0         # và ngày t+1 thiếu AQI(t) cũng ra
    f0 = F.make_forecast_features(raw8, baseline_daily)
    f1 = F.make_forecast_features(removed, baseline_daily)
    assert same(_row(f0, city, t)[COLS], _row(f1, city, t)[COLS])                         # nhưng đặc trưng của hàng t y nguyên

    changed = raw8.copy()
    changed.loc[(changed["City"] == city) & (changed["Date"] == t1), "AQI"] = 777.0
    ds_changed = F.build_forecast_dataset(changed, baseline_daily, verbose=False)
    row1 = _row(ds_changed, city, t)
    assert row1["y"] == 777.0 and row0["y"] != 777.0 and same(row0[COLS], row1[COLS])
    assert len(ds_changed) == len(base)

    restored = F.build_forecast_dataset(removed.assign(AQI=raw8["AQI"].to_numpy()), baseline_daily, verbose=False)
    assert len(restored) == len(base) == len(ds_removed) + 2                              # thêm lại AQI(t+1): hai hàng trở lại mẫu


def test_next_day_weather_exists_only_as_the_declared_scenario(raw8, baseline_daily, ds_new):
    """`*_next` (L4, kịch bản dự báo hoàn hảo) đúng bằng đặc trưng thời tiết của ngày t+1, và là NaN ở hàng cuối của bản cắt."""
    f = F.make_forecast_features(raw8, baseline_daily)
    nxt = f.set_index(["City", "Date"])[M.WEATHER_FEATS]
    got = ds_new.set_index([ds_new["City"].astype(str), "Date_target"])[M.NEXT_FEATS]
    want = nxt.reindex(got.index)
    assert same(got.to_numpy(), want.to_numpy())
    t = pd.Timestamp("2019-11-15")
    cut_raw = raw8[raw8["Date"] <= t]
    d = F.attach_target(F.make_forecast_features(raw8, baseline_daily, as_of=t), cut_raw)
    last = d[d["Date"] == t]
    assert len(last) == 8 and last[M.NEXT_FEATS].isna().all().all() and last["y"].isna().all()


def test_as_of_argument_cuts_raw_not_a_cleaned_table(raw8, baseline_daily):
    f = F.make_forecast_features(raw8, baseline_daily, as_of="2018-05-01")
    assert f["Date"].max() == pd.Timestamp("2018-05-01")
    full = F.make_forecast_features(raw8, baseline_daily)
    a = f[f["Date"] == "2018-05-01"].set_index("City")[COLS].sort_index()
    b = full[full["Date"] == "2018-05-01"].set_index("City")[COLS].sort_index()
    assert all(same(a[c], b[c]) for c in COLS)
    # ngày này bản "thời gian thực" của luật nghi lỗi từng xoá AQI 352 của Bengaluru (V07); đường dự báo giữ giá trị raw
    assert b.loc["Bengaluru", "AQI"] == 352.0 and b.loc["Bengaluru", "aqi_0"] == np.log(352.0)
