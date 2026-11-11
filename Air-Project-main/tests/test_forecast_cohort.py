"""DEV-02 / F01 - nhãn, điều kiện giữ mẫu, cohort và phần đối chiếu với đường hồi cứu (RA-DEC-02 mục 2-3).

Không con số nào về cohort bị gõ cứng ở đây: số mẫu được đếm lại độc lập từ raw, và các mẫu "thêm" so với đường hồi cứu
được suy ra độc lập từ file điểm nghi lỗi của nhánh làm sạch rồi so với diff thực tế.
"""
import numpy as np
import pandas as pd
import pytest

import data_paths
import forecast_utils as F
import model_utils as M
from conftest import evidence_dir

L3 = M.LEVELS["L3"]


def keys(d):
    return set(zip(d["City"].astype(str), pd.to_datetime(d["Date"])))


@pytest.fixture(scope="module")
def raw_plain():
    """raw đọc lại bằng pandas thuần, không qua forecast_utils."""
    r = pd.read_csv(data_paths.RAW_FILE, parse_dates=["Date"])
    return r[r["City"].isin(M.CITIES)].reset_index(drop=True)


@pytest.fixture(scope="module")
def suspects():
    s = pd.read_csv(data_paths.ROOT / "reports" / "suspect_points_8cities.csv", encoding="utf-8-sig", parse_dates=["date"])
    return s[s["action"] == "đặt NaN"].reset_index(drop=True)


# ----------------------------------------------------------------------------- kiểm raw trước khi dùng
def test_raw_keys_continuity_and_values(raw_plain, raw8):
    assert len(raw8) == len(raw_plain) == 14056 and raw8.attrs["n_inserted_days"] == 0
    assert not raw8.duplicated(["City", "Date"]).any()
    assert (raw8.groupby("City")["Date"].diff().dropna() == pd.Timedelta("1D")).all()
    assert len(F.raw_value_violations(raw8)) == 0
    a = raw8["AQI"].dropna()
    assert np.isfinite(a).all() and (a > 0).all() and int((a > 500).sum()) > 0          # có AQI > 500 trong raw và chúng được giữ
    assert F.common_window(raw8) == (F.COMMON_START, F.COMMON_END) == (pd.Timestamp("2017-06-14"), pd.Timestamp("2020-07-01"))


@pytest.mark.parametrize("col, value, word", [("AQI", 0.0, "AQI có mặt phải hữu hạn và > 0"), ("AQI", -5.0, "> 0"), ("AQI", np.inf, "hữu hạn"),
                                              ("CO", -0.1, "nồng độ có mặt phải hữu hạn và >= 0"), ("PM2.5", np.inf, "hữu hạn")])
def test_invalid_raw_values_stop_with_count_date_and_rule(raw8, col, value, word):
    bad = raw8.copy()
    i = bad.index[(bad["City"] == "Delhi") & (bad["Date"] == "2019-03-03")][0]
    bad.loc[i, col] = value
    v = F.raw_value_violations(bad)
    assert len(v) == 1 and v.iloc[0]["City"] == "Delhi" and v.iloc[0]["Date"] == pd.Timestamp("2019-03-03") and v.iloc[0]["cot"] == col
    with pytest.raises(ValueError) as e:
        F.prepare_raw(bad)
    assert "1 ô không hợp lệ" in str(e.value) and word in str(e.value) and "2019-03-03" in str(e.value)


def test_duplicate_keys_and_missing_columns_stop(raw8):
    with pytest.raises(ValueError, match="trùng khoá"):
        F.prepare_raw(pd.concat([raw8, raw8.iloc[[7]]]))
    with pytest.raises(ValueError, match="thiếu cột"):
        F.prepare_raw(raw8.drop(columns="O3"))


def test_weather_problems_stop_instead_of_being_filled(raw8, baseline_daily):
    with pytest.raises(ValueError, match="blh_mean"):
        F.make_forecast_features(raw8, baseline_daily.drop(columns="blh_mean"))
    with pytest.raises(ValueError, match="không có thời tiết"):
        F.make_forecast_features(raw8, baseline_daily[baseline_daily["Date"] != "2019-05-05"])


# ----------------------------------------------------------------------------- số mẫu: đếm lại độc lập từ raw
def test_cohort_equals_independent_recount_from_raw(raw_plain, ds_new):
    r = raw_plain[raw_plain["AQI"].notna()][["City", "Date"]]
    has_next = r.assign(Date=r["Date"] - pd.Timedelta(days=1))                          # ngày t mà ngày lịch t+1 có AQI
    pairs = r.merge(has_next, on=["City", "Date"])
    pairs = pairs[(pairs["Date"] >= "2017-06-14") & (pairs["Date"] + pd.Timedelta(days=1) <= "2020-07-01")]
    assert keys(pairs) == keys(ds_new) and len(pairs) == len(ds_new)
    tgt = pairs["Date"] + pd.Timedelta(days=1)
    recount = {"train": int((tgt <= M.TRAIN_END).sum()), "test": int(((tgt >= M.TEST_START) & (tgt <= M.TEST_END)).sum()),
               "lockdown": int((tgt >= M.LOCK_START).sum())}
    assert ds_new["split"].value_counts().to_dict() == recount and sum(recount.values()) == len(ds_new)
    ret = F.retention(ds_new)
    assert list(ret.index) == ["train", "test", "lockdown", "Cộng"]
    assert ret.loc["Cộng", "giữ (có cả hai)"] == len(ds_new)
    assert (ret["cặp (thành phố, ngày t) trong khoảng"] == ret[["thiếu AQI(t)", "có AQI(t), thiếu AQI(t+1)", "giữ (có cả hai)"]].sum(axis=1)).all()
    assert ret.loc["Cộng", "cặp (thành phố, ngày t) trong khoảng"] == 8 * 1113                # 8 thành phố x số ngày t của khoảng chung
    assert int(ret.loc["Cộng", "ngày nặng trong số giữ"]) == int(ds_new["y_poor"].sum())
    d = evidence_dir()
    if d is not None:
        ret.to_csv(d / "cohort_retention_table.csv")
        ds_new.groupby("split").agg(n=("y", "size"), ngay_nang=("y_poor", "sum"), tu=("Date_target", "min"), den=("Date_target", "max")).to_csv(d / "cohort_counts_forecast_path.csv")


def test_dataset_order_split_and_types(ds_new):
    assert ds_new["Date_target"].is_monotonic_increasing and list(ds_new["City"].cat.categories) == M.CITIES
    order = ds_new.assign(_c=ds_new["City"].astype(str)).sort_values(["Date_target", "_c"]).index      # cùng thứ tự với model_utils.build_dataset
    assert (order == ds_new.index).all() and (ds_new.index == np.arange(len(ds_new))).all()
    both = pd.concat([ds_new[ds_new["split"] == "train"], ds_new[ds_new["split"] == "test"]])          # các lát của bảng ghép lại được
    assert len(both) == int(ds_new["split"].isin(["train", "test"]).sum())
    assert set(ds_new["split"]) == {"train", "test", "lockdown"}
    tr, te, lk = (ds_new[ds_new["split"] == s] for s in ("train", "test", "lockdown"))
    assert tr["Date_target"].max() == M.TRAIN_END and te["Date_target"].min() == M.TEST_START
    assert te["Date_target"].max() == M.TEST_END and lk["Date_target"].min() == M.LOCK_START and lk["Date_target"].max() == F.COMMON_END
    assert ds_new["Date"].min() == F.COMMON_START and not ds_new.duplicated(["City", "Date"]).any()
    assert set(L3 + M.NEXT_FEATS + ["y", "y_log", "y_poor", "AQI", "today_poor"]) <= set(ds_new.columns)
    assert ds_new[M.CAL_FEATS].notna().all().all() and ds_new[M.WEATHER_FEATS].drop(columns=["pressure_dev", "d_pressure"]).notna().all().all()


# ----------------------------------------------------------------------------- so với đường hồi cứu
def expected_extra_keys(suspects, raw_plain):
    """Suy ra ĐỘC LẬP các mẫu mà đường hồi cứu loại còn đường raw giữ: mỗi ô AQI bị nhánh làm sạch đặt NaN (ngày d) làm mất mẫu
    t = d (thiếu AQI hôm nay) và mẫu t = d-1 (thiếu nhãn), miễn là raw có AQI ở cả t và t+1 và t nằm trong khoảng chung."""
    aqi = raw_plain.set_index(["City", "Date"])["AQI"]
    out = set()
    for _, s in suspects[suspects["column"] == "AQI"].iterrows():
        for t in (s["date"], s["date"] - pd.Timedelta(days=1)):
            t1 = t + pd.Timedelta(days=1)
            if t >= F.COMMON_START and t1 <= F.COMMON_END and aqi.get((s["city"], t), np.nan) == aqi.get((s["city"], t), np.nan) \
                    and aqi.get((s["city"], t1), np.nan) == aqi.get((s["city"], t1), np.nan):
                out.add((s["city"], t))
    return out


def test_cohort_diff_against_retrospective_path_is_fully_explained(ds_new, ds_old, suspects, raw_plain):
    extra, lost = keys(ds_new) - keys(ds_old), keys(ds_old) - keys(ds_new)
    assert lost == set()                                                     # không mẫu nào của đường hồi cứu bị mất
    assert extra == expected_extra_keys(suspects, raw_plain)                 # mẫu thêm = đúng các mẫu mà luật nghi lỗi hồi cứu đã loại
    cd = F.cohort_diff(ds_new, ds_old)
    assert keys(cd) == extra and (cd["cohort"] == "chỉ có ở đường dự báo (raw)").all()
    assert cd["nguyen_nhan"].str.contains("bảng sạch hồi cứu đã xoá").all() and cd["nguyen_nhan"].str.contains("suspect_sensor_error").all()
    assert (cd["AQI_raw(t)"].notna() & cd["AQI_raw(t+1)"].notna()).all()
    assert (cd["AQI_sach(t)"].isna() | cd["AQI_sach(t+1)"].isna()).all()
    d = evidence_dir()
    if d is not None:
        cd.to_csv(d / "cohort_diff_forecast_vs_retrospective.csv", index=False)
        pd.DataFrame({"đường": ["hồi cứu (mã cũ)", "dự báo từ raw (mã mới)"],
                      **{s: [int((x["split"] == s).sum()) for x in (ds_old, ds_new)] for s in ("train", "test", "lockdown")},
                      "tổng": [len(ds_old), len(ds_new)],
                      "ngày nặng train": [int(x.loc[x["split"] == "train", "y_poor"].sum()) for x in (ds_old, ds_new)]}).to_csv(d / "cohort_counts_before_after.csv", index=False)


def test_test_and_holdout_keys_labels_and_features_are_identical_to_retrospective_path(ds_new, ds_old):
    """Trên snapshot hiện có: khác biệt giữa hai đường chỉ nằm ở train. Khoá, nhãn và mọi đặc trưng L1-L3 của test và của giai đoạn
    03-07/2020 trùng nhau (dung sai 1e-9), nên so sánh trên test là cùng mẫu, cùng nhãn."""
    for s in ("test", "lockdown"):
        a, b = ds_new[ds_new["split"] == s], ds_old[ds_old["split"] == s]
        assert keys(a) == keys(b)
    summ, cells = F.feature_diff(ds_new, ds_old)
    assert summ.loc["y", "ô khác"] == 0 and summ.loc["AQI", "ô khác"] == 0 and summ.loc["aqi_0", "ô khác"] == 0
    assert int(summ["ô khác: test"].sum()) == 0 and int(summ["ô khác: lockdown"].sum()) == 0
    assert int(summ["ô khác"].sum()) == int(summ["ô khác: train"].sum()) == len(cells) > 0
    assert set(cells["cột"]) <= {"aqi_1", "aqi_2", "aqi_wk", "co_0"}          # chỉ AQI trễ (do AQI raw được giữ) và CO (số 0 treo)
    d = evidence_dir()
    if d is not None:
        summ.to_csv(d / "feature_diff_common_keys_summary.csv")
        cells.to_csv(d / "feature_diff_common_keys_cells.csv", index=False)


def test_suspect_cells_keep_their_raw_values_in_the_forecast_path(features_full, raw_plain, suspects, ds_new, ds_old):
    """Mọi ô mà luật nghi lỗi hồi cứu đã xoá (trong khoảng chung) mang đúng giá trị RAW ở đường dự báo: không ô nào bị xoá hay thay.
    File điểm nghi lỗi ghi `value_original` làm tròn 1 chữ số, và có dòng mà raw vốn THIẾU (giá trị đó là số nội suy của nhánh hồi
    cứu): ở dòng như vậy đường dự báo không dùng số nội suy, chỉ dùng giá trị raw quan sát được gần nhất trong 2 ngày trước (nếu có)."""
    s = suspects[suspects["date"] >= F.COMMON_START]
    raw = raw_plain.set_index(["City", "Date"])
    f = features_full.set_index(["City", "Date"])
    kn, ko = keys(ds_new), keys(ds_old)
    rows, n_not_observed = [], 0
    for _, x in s.iterrows():
        k = (x["city"], x["date"])
        col = x["column"]
        feat = "aqi_0" if col == "AQI" else "pm25_0"
        raw_v = raw.loc[k, col]
        if raw_v == raw_v:                                                   # raw có giá trị: đường dự báo dùng đúng giá trị đó
            assert abs(raw_v - x["value_original"]) <= 0.05 + 1e-9
            if col == "AQI":
                assert f.loc[k, "AQI"] == raw_v and f.loc[k, "aqi_0"] == np.log(raw_v)
            else:
                assert f.loc[k, "pm25_0"] == np.log1p(raw_v) and f.loc[k, "pm25_0_lag"] == 0
            used = raw_v
        else:                                                                # raw thiếu: `value_original` là số nội suy, không phải số đo
            n_not_observed += 1
            assert col == "PM2.5"
            lag = int(f.loc[k, "pm25_0_lag"])
            used = np.nan if lag == -1 else raw.loc[(k[0], k[1] - pd.Timedelta(days=lag)), col]
            assert lag in (-1, 1, 2) and (np.isnan(f.loc[k, "pm25_0"]) if lag == -1 else f.loc[k, "pm25_0"] == np.log1p(used))
            assert not (used == used and abs(used - x["value_original"]) <= 0.05)
        rows.append({"City": k[0], "Date": k[1].date(), "cột": col, "value_original trong file điểm nghi lỗi": x["value_original"], "giá trị raw": raw_v,
                     "raw có giá trị": bool(raw_v == raw_v), "giá trị dùng làm đặc trưng ở đường dự báo": used, "đặc trưng": feat,
                     "lý do nhánh hồi cứu xoá": x["suggestion"], "ngày t có trong cohort dự báo": k in kn, "ngày t có trong cohort hồi cứu": k in ko})
    assert len(rows) == len(s) > 0
    d = evidence_dir()
    if d is not None:
        pd.DataFrame(rows).to_csv(d / "suspect_cells_in_window_kept_raw.csv", index=False)


def test_suspect_file_lists_values_that_were_never_observed(suspects, raw_plain):
    """Ghi nhận cho RA (không sửa nhánh hồi cứu): luật nghi lỗi hồi cứu chạy SAU bước nội suy, nên một số ô nó 'xoá vì nghi lỗi
    cảm biến' là số nội suy; raw không có số đo ở đó. Phép thử chỉ ghi lại hiện trạng để bằng chứng không bị trôi."""
    raw = raw_plain.set_index(["City", "Date"])
    s = suspects.assign(raw_value=[raw.loc[(c, d), col] for c, d, col in zip(suspects["city"], suspects["date"], suspects["column"])])
    not_obs = s[s["raw_value"].isna()]
    assert ((s["raw_value"] - s["value_original"]).abs().dropna() <= 0.05 + 1e-9).all()
    assert len(s) == 41 and set(not_obs["column"]) <= {"PM2.5"}
    d = evidence_dir()
    if d is not None:
        not_obs[["city", "date", "column", "value_original", "raw_value", "suggestion", "action"]].to_csv(d / "suspect_cells_without_raw_observation.csv", index=False)
        pd.DataFrame([{"ô bị nhánh hồi cứu đặt NaN vì nghi lỗi": len(s), "trong đó raw có số đo": int(s["raw_value"].notna().sum()),
                       "trong đó raw KHÔNG có số đo (giá trị bị xoá là số nội suy)": len(not_obs)}]).to_csv(d / "suspect_cells_observed_vs_interpolated.csv", index=False)


def test_flatline_cells_measured(features_full, raw8, ds_new):
    """Đo (không giả định) số ô CO bị quy tắc số 0 treo as-of che, và số 0 được giữ ở ngày 1-2 của chuỗi."""
    m = raw8.merge(features_full, on=["City", "Date"], validate="1:1", suffixes=("_raw", ""))
    win = m[(m["Date"] >= F.COMMON_START)]
    zero = win["CO"] == 0
    kept_zero = zero & ~win["co_0_flat"]
    assert int(win["co_0_flat"].sum()) > 0 and (win.loc[win["co_0_flat"], "CO"] == 0).all()
    assert (win.loc[kept_zero, "co_0"] == 0.0).all() and (win.loc[kept_zero, "co_0_lag"] == 0).all()
    for c in ("pm25_0", "no2_0", "so2_0", "o3_0"):
        assert not m[c + "_flat"].any()
    d = evidence_dir()
    if d is not None:
        in_ds = ds_new.assign(City=ds_new["City"].astype(str))
        pd.DataFrame([{"phạm vi": "mọi (thành phố, ngày) từ 14/06/2017", "ô CO bằng 0 trong raw": int(zero.sum()), "bị che (ngày thứ 3 trở đi của chuỗi)": int(win["co_0_flat"].sum()),
                       "giữ số 0 (ngày 1-2 của chuỗi)": int(kept_zero.sum())},
                      {"phạm vi": "các hàng của cohort dự báo", "ô CO bằng 0 trong raw": int((in_ds["co_0_flat"] | ((in_ds["co_0"] == 0) & (in_ds["co_0_lag"] == 0))).sum()),
                       "bị che (ngày thứ 3 trở đi của chuỗi)": int(in_ds["co_0_flat"].sum()), "giữ số 0 (ngày 1-2 của chuỗi)": int(((in_ds["co_0"] == 0) & (in_ds["co_0_lag"] == 0)).sum())}]
                     ).to_csv(d / "flatline_asof_counts.csv", index=False)


# ----------------------------------------------------------------------------- imputer/scaler chỉ học trên train; CV đúng thứ tự thời gian
def test_imputer_and_scaler_are_fit_on_train_only(ds_new):
    tr, te = ds_new[ds_new["split"] == "train"], ds_new[ds_new["split"] == "test"]
    pipe = M.make_pipe(L3, "ridge", alpha=30).fit(tr[L3 + ["City"]], tr["y_log"])
    num = pipe.named_steps["prep"].named_transformers_["num"]
    imp, sc = num.named_steps["imp"], num.named_steps["sc"]
    np.testing.assert_allclose(imp.statistics_, np.nanmedian(tr[L3].to_numpy(float), axis=0), rtol=0, atol=1e-12)
    filled = tr[L3].to_numpy(float).copy()
    for j in range(filled.shape[1]):
        filled[np.isnan(filled[:, j]), j] = imp.statistics_[j]
    np.testing.assert_allclose(sc.mean_[:len(L3)], filled.mean(axis=0), rtol=0, atol=1e-9)
    assert not np.allclose(imp.statistics_, np.nanmedian(pd.concat([tr, te])[L3].to_numpy(float), axis=0))   # khác với trung vị tính lẫn cả test
    assert tr[L3].isna().any().any()                                          # có giá trị thiếu thật để imputer xử lý


def test_time_series_cv_folds_respect_time(ds_new):
    tr = ds_new[ds_new["split"] == "train"].reset_index(drop=True)
    folds = list(M.time_cv(len(tr)).split(tr))
    assert len(folds) == M.TS_SPLITS == 4
    for a, b in folds:
        gap = (tr.iloc[b]["Date_target"].min() - tr.iloc[a]["Date_target"].max()).days
        assert gap >= 2 and a.max() < b.min()


# ----------------------------------------------------------------------------- giao thức và ba phép so RA yêu cầu
@pytest.fixture(scope="module")
def paths(ds_new, ds_old):
    return F.compare_paths(ds_new, ds_old)


@pytest.mark.slow
def test_protocol_reproduces_baseline_numbers_on_retrospective_path(paths):
    """`run_protocol` trên đường hồi cứu ra đúng các con số baseline mà DA đã tái lập ở vòng 1 (V20-V24): hàm đóng gói đúng giao thức NB06."""
    a = paths["runs"]["A. hồi cứu (mã cũ), cohort hồi cứu"]
    assert a["n"] == {"train": 5741, "test": 1947, "lockdown": 975} and a["alpha"] == {"L1": 10, "L2": 0.1, "L3": 30}
    assert a["thr"] == {F.PERSIST: 160.0, "L1": 169.0, "L2": 165.0, "L3": 166.0} and (a["n_oof"], a["heavy_oof"]) == (4592, 1193)
    for k, v in {F.PERSIST: 23.466, "L1": 22.937, "L2": 20.919, "L3": 19.519}.items():
        assert abs(a["mae"]["test"][k] - v) < 0.001, (k, a["mae"]["test"][k])
    for k, v in {F.PERSIST: 14.803, "L1": 14.085, "L2": 13.880, "L3": 13.783}.items():
        assert abs(a["mae"]["lockdown"][k] - v) < 0.001
    assert (a["alerts"]["L3@201"]["TP"], a["alerts"]["L3@201"]["FP"], a["alerts"]["L3@201"]["FN"]) == (346, 40, 43)
    assert (a["alerts"]["hôm nay@201"]["TP"], a["alerts"]["hôm nay@201"]["FP"], a["alerts"]["hôm nay@201"]["FN"]) == (333, 59, 56)


@pytest.mark.slow
def test_three_required_comparisons_are_like_for_like(paths, ds_new, ds_old):
    """A = mã cũ; B = mã mới trên cùng cohort với A (bỏ mẫu thêm theo diff THỰC TẾ); C = mã mới trên cohort raw.
    Cả ba có cùng khoá và cùng nhãn ở test VÀ ở giai đoạn 03-07/2020, nên hiệu MAE ở hai tập đó là so cặp trên cùng một outcome."""
    t, runs = paths["table"], paths["runs"]
    a, b, c = (runs[k] for k in t.index)
    extra = keys(ds_new) - keys(ds_old)
    assert set(paths["keys"]["chỉ có ở đường dự báo"]) == extra and len(paths["keys"]["chỉ có ở đường hồi cứu"]) == 0
    assert b["n"] == a["n"] and c["n"]["train"] == a["n"]["train"] + len(extra)
    assert c["n"]["test"] == a["n"]["test"] and c["n"]["lockdown"] == a["n"]["lockdown"]
    pz = paths["paired"]
    assert set(pz["tập"]) == {"test", "03-07/2020"} and len(pz) == 3 * 2 * 3            # 3 cặp biến thể x 2 tập x 3 mức
    assert pz["cùng khoá"].all() and pz["cùng nhãn"].all() and (pz["n (A)"] == pz["n (B)"]).all()
    assert (pz.loc[pz["tập"] == "test", "n (A)"] == a["n"]["test"]).all() and (pz.loc[pz["tập"] == "03-07/2020", "n (A)"] == a["n"]["lockdown"]).all()
    assert pz["ΔMAE"].notna().all() and (pz["KTC 95% thấp"] <= pz["ΔMAE"]).all() and (pz["ΔMAE"] <= pz["KTC 95% cao"]).all()
    for part in ("test", "lockdown"):                                                   # hiệu trong bảng so cặp = hiệu của hai MAE đã báo
        lab = "test" if part == "test" else "03-07/2020"
        row = pz[(pz["so sánh (A trừ B)"] == "C. − A.") & (pz["tập"] == lab) & (pz["mức"] == "L3")].iloc[0]
        assert abs(row["ΔMAE"] - (c["mae"][part]["L3"] - a["mae"][part]["L3"])) < 1e-9
        for r in (a, b, c):                                                             # nhãn và khoá đúng là của bảng đầu vào, theo đúng thứ tự
            assert len(r["eval"][part]["y"]) == r["n"][part] == len(r["eval"][part]["pred"]["L3"])
    assert a["mae"]["test"][F.PERSIST] == b["mae"]["test"][F.PERSIST] == c["mae"]["test"][F.PERSIST]      # baseline không phụ thuộc đường
    for r in (a, b, c):                                                       # mỗi biến thể tự chọn alpha/ngưỡng trên train của nó, trong lưới
        assert set(r["alpha"].values()) <= set(F.ALPHAS) and all(80 <= v <= 300 for v in r["thr"].values())
        assert r["mae"]["test"]["L3"] < r["mae"]["test"]["L2"] < r["mae"]["test"]["L1"] < r["mae"]["test"][F.PERSIST]
    d = evidence_dir()
    if d is not None:
        t.T.to_csv(d / "path_comparison_A_B_C.csv")
        paths["paired"].to_csv(d / "path_comparison_paired_mae.csv", index=False)


@pytest.mark.slow
def test_comparison_is_not_called_paired_when_labels_or_keys_differ(ds_new, ds_old):
    """RA-DEC-02 mục 2: nếu nhãn khác thì báo riêng, không gọi là so cặp cùng outcome. Ở đây cố ý làm hỏng bảng đối chiếu:
    (1) đổi MỘT nhãn test; (2) bỏ MỘT dòng của giai đoạn 03-07/2020. Bảng so cặp phải ghi rõ và KHÔNG tính hiệu MAE ở tập đó."""
    i_test = ds_old.index[ds_old["split"] == "test"][10]
    bad_label = ds_old.copy()
    bad_label.loc[i_test, "y"] = bad_label.loc[i_test, "y"] + 1.0
    pz = F.compare_paths(ds_new, bad_label, levels=("L1",), alphas=[10])["paired"]
    vs_a = pz[pz["so sánh (A trừ B)"].str.endswith("A.")]
    t_rows, l_rows = vs_a[vs_a["tập"] == "test"], vs_a[vs_a["tập"] == "03-07/2020"]
    assert t_rows["cùng khoá"].all() and not t_rows["cùng nhãn"].any() and t_rows["ΔMAE"].isna().all()   # cùng mẫu, khác outcome: không so cặp
    assert l_rows["cùng nhãn"].all() and l_rows["ΔMAE"].notna().all()                                     # tập không bị đụng vẫn so cặp được
    c_vs_b = pz[pz["so sánh (A trừ B)"] == "C. − B."]
    assert c_vs_b["cùng nhãn"].all() and c_vs_b["ΔMAE"].notna().all()                                     # hai biến thể mã mới không dùng bảng hỏng

    i_lock = ds_old.index[ds_old["split"] == "lockdown"][5]
    fewer = ds_old.drop(index=i_lock).reset_index(drop=True)
    res = F.compare_paths(ds_new, fewer, levels=("L1",), alphas=[10])
    pz = res["paired"]
    vs_a = pz[(pz["so sánh (A trừ B)"] == "C. − A.") & (pz["tập"] == "03-07/2020")]
    assert not vs_a["cùng khoá"].any() and not vs_a["cùng nhãn"].any() and vs_a["ΔMAE"].isna().all()
    assert (vs_a["n (A)"] == vs_a["n (B)"] + 1).all()                                                     # n hai bên được báo, thấy ngay lệch 1
    dropped = (str(ds_old.loc[i_lock, "City"]), pd.Timestamp(ds_old.loc[i_lock, "Date"]))
    assert dropped in set(res["keys"]["chỉ có ở đường dự báo"])                                           # và khoá bị bỏ hiện ra trong diff cohort
