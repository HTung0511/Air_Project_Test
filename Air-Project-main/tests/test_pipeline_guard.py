"""NEW-002 - `pipeline.investigate` không còn lỗi khi chuỗi chưa có số liệu khí hoặc không có điểm nào để điều tra,
và nhánh làm sạch hồi cứu cho ra đúng kết quả cũ trên toàn bộ dữ liệu.
"""
import io

import numpy as np
import pandas as pd
import pytest

import data_paths
import pipeline as P
import utils as U
from gap_utils import contextual_ratio

RAW = str(data_paths.RAW_FILE)


def _city(city, cut=None):
    d = U.load_and_split_city(city, raw_path=RAW)
    if cut is not None:
        d = d[d.Date <= cut]
    d, _ = U.impute_time_series(d, city, drop_cols=["Xylene"], verbose=False)
    return d.drop(columns=[c for c in d.columns if c.startswith("Xylene")])


def investigate_original(d, col, top=5, skip_pm25=(), extra_dates=()):
    """Bản sao NGUYÊN VĂN của `pipeline.investigate` tại commit gốc cd719cf (trước khi thêm guard). Chỉ dùng để đối chiếu."""
    ratio = contextual_ratio(d[col])
    others = [g for g in P.GASES if g in d.columns and d[g].notna().any()]
    R = pd.DataFrame({g: contextual_ratio(d[g]) for g in others})
    has10 = "PM10" in d.columns and d["PM10"].notna().any()
    pm25_r = contextual_ratio(d["PM2.5"])
    pm10_r = contextual_ratio(d["PM10"]) if has10 else pd.Series(np.nan, index=d.index)
    skip = set(skip_pm25)
    for t in skip:
        pm25_r[t] = np.nan
    dates = list(d[col].nlargest(top).index)
    dates += [t for t in extra_dates if t in d.index and d.loc[t, col] == d.loc[t, col] and t not in dates]
    rows = []
    for t in dates:
        co = [g for g in others if R.loc[t, g] >= 1.5]
        pm10_ok = has10 and pm10_r[t] == pm10_r[t] and pm10_r[t] >= 1.5
        expl = (col == "AQI") and (pm10_ok or (np.nan_to_num(pm25_r[t], nan=-1) >= 1.5))
        p_ratio = d.loc[t, "PM2.5"] / d.loc[t, "PM10"] if has10 and d.loc[t, "PM10"] > 0 else np.nan
        winter = t.month in P.WINTER
        if col == "AQI" and t in skip and not pm10_ok:                  goi_y = "NGHI LOI (theo PM2.5 nghi loi cung ngay)"
        elif col == "PM2.5" and p_ratio == p_ratio and p_ratio > 1.5:   goi_y = "NGHI LOI (PM2.5 > 1,5 x PM10)"
        elif winter and ratio[t] < 3:                                   goi_y = "that (mua cao diem)"
        elif expl or len(co) >= 3:                                      goi_y = "that (chat khac cung tang)"
        elif (not winter) and ratio[t] >= 4:                            goi_y = "NGHI LOI (co lap, trai mua)"
        else:                                                           goi_y = "chua ro -> giu + co"
        rows.append(dict(date=t, column=col, value_original=round(d.loc[t, col], 1),
                         gap_vs_neighbors=round(ratio[t], 1), month=t.month,
                         pm25_div_pm10=round(p_ratio, 2) if p_ratio == p_ratio else np.nan,
                         other_gases_up=f"{len(co)}/{R.loc[t].notna().sum()}", suggestion=goi_y))
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------- tái hiện NEW-002 và các trường hợp biên
@pytest.mark.parametrize("cut", ["2017-06-14", "2017-06-15", "2017-06-18"])
def test_new002_series_with_no_gas_data_no_longer_raises(cut):
    """Jaipur khi raw bị cắt ở 14-18/06/2017: có PM2.5 và AQI nhưng chưa có khí nào. Trước đây: KeyError ở dòng 60."""
    d = _city("Jaipur", cut)
    assert not any(d[g].notna().any() for g in P.GASES if g in d.columns)     # đúng tình huống "không có khí"
    with pytest.raises(KeyError):
        investigate_original(d.set_index("Date"), "PM2.5")                    # bản gốc đúng là lỗi ở đây
    out, ev = P.apply_suspect_rule(d)
    assert len(out) == len(d) and not out["suspect_sensor_error"].any()
    assert set(ev["other_gases_up"]) == {"0/0"} and list(ev.columns) == P.EVIDENCE_COLS + ["action"]
    assert set(ev["action"]) == {"giữ nguyên"}
    pd.testing.assert_series_equal(out["PM2.5"], d["PM2.5"]); pd.testing.assert_series_equal(out["AQI"], d["AQI"])


def test_new002_once_gas_data_exists_result_equals_original():
    d = _city("Jaipur", "2017-07-31").set_index("Date")
    pd.testing.assert_frame_equal(P.investigate(d, "PM2.5"), investigate_original(d, "PM2.5"))


def test_empty_frame_returns_empty_evidence_with_columns():
    d = _city("Jaipur").iloc[0:0]
    out, ev = P.apply_suspect_rule(d)
    assert len(out) == 0 and len(ev) == 0 and list(ev.columns) == P.EVIDENCE_COLS + ["action"]
    assert "suspect_sensor_error" in out.columns


def test_target_columns_all_missing_flags_nothing_and_matches_original():
    """PM2.5 và AQI toàn NaN: `nlargest` của pandas vẫn trả các dòng NaN, nên bảng bằng chứng có dòng nhưng không dòng nào bị
    nghi lỗi. Hành vi này của luật hồi cứu được giữ nguyên (giống hệt bản gốc), guard không đổi nó."""
    d = _city("Jaipur").head(40).copy()
    d[["PM2.5", "AQI"]] = np.nan
    out, ev = P.apply_suspect_rule(d)
    assert not out["suspect_sensor_error"].any() and set(ev["action"]) <= {"giữ nguyên"}
    di = d.set_index("Date")
    pd.testing.assert_frame_equal(P.investigate(di, "PM2.5"), investigate_original(di, "PM2.5"))


def test_missing_pm10_and_short_series_do_not_raise():
    d = _city("Lucknow").head(3)                                              # Lucknow không có PM10; chuỗi 3 ngày
    out, ev = P.apply_suspect_rule(d)
    assert len(out) == 3 and ev["pm25_div_pm10"].isna().all()


# ----------------------------------------------------------------------------- nhánh hồi cứu trên toàn bộ dữ liệu: không đổi
@pytest.fixture(scope="module")
def full_clean():
    frames, evs = [], []
    for c in P.CITIES:
        f, e = P.clean_city(c, RAW)
        frames.append(f); evs.append(e)
    return frames, P.merge_cities(frames), pd.concat(evs, ignore_index=True)


@pytest.mark.slow
def test_guarded_investigate_equals_original_on_full_data():
    """Trên chuỗi đầy đủ của cả 8 thành phố, hàm đã thêm guard trả đúng từng ô như bản gốc (PM2.5, rồi AQI kèm ngày nghi lỗi)."""
    for city in P.CITIES:
        d = _city(city).set_index("Date")
        a, b = P.investigate(d, "PM2.5"), investigate_original(d, "PM2.5")
        pd.testing.assert_frame_equal(a, b)
        sus = [t for t in a.loc[a.suggestion.str.startswith("NGHI"), "date"]]
        pd.testing.assert_frame_equal(P.investigate(d, "AQI", skip_pm25=sus, extra_dates=sus),
                                      investigate_original(d, "AQI", skip_pm25=sus, extra_dates=sus))


@pytest.mark.slow
def test_retrospective_cleaning_reproduces_committed_table(full_clean):
    """raw -> bảng sạch hồi cứu vẫn ra đúng `air_quality_8cities.csv` đã commit: cùng khoá, cùng vị trí NaN, số lệch <= 1e-9."""
    _, merged, _ = full_clean
    buf = io.StringIO(); merged.to_csv(buf, index=False)
    a = pd.read_csv(io.StringIO(buf.getvalue()))
    b = pd.read_csv(data_paths.BASELINE_CLEAN)
    assert a.shape == b.shape == (14056, 40) and list(a.columns) == list(b.columns)
    assert (a.isna().to_numpy() == b.isna().to_numpy()).all()
    pd.testing.assert_frame_equal(a, b, check_exact=False, rtol=0, atol=1e-9)
    num = [c for c in a.columns if pd.api.types.is_float_dtype(a[c])]
    assert float((a[num] - b[num]).abs().max().max()) < 1e-9


@pytest.mark.slow
def test_suspect_report_reproduces_committed_file(full_clean):
    _, merged, report = full_clean
    committed = pd.read_csv(data_paths.ROOT / "reports" / "suspect_points_8cities.csv", encoding="utf-8-sig")
    k = ["city", "column", "date"]
    a = report.assign(date=pd.to_datetime(report.date).dt.strftime("%Y-%m-%d")).sort_values(k).reset_index(drop=True)[committed.columns]
    b = committed.assign(date=pd.to_datetime(committed.date).dt.strftime("%Y-%m-%d")).sort_values(k).reset_index(drop=True)
    pd.testing.assert_frame_equal(a, b, check_exact=False, rtol=0, atol=1e-9, check_dtype=False)
    n_nan = (report.action == "đặt NaN")
    assert (len(report), int(n_nan.sum())) == (len(committed), int((committed.action == "đặt NaN").sum()))
    assert int(merged["suspect_sensor_error"].sum()) == report.loc[n_nan, ["city", "date"]].drop_duplicates().shape[0]
