"""DEV-01 / F02 - dung sai khi so bảng thời tiết theo ngày vừa tạo lại với baseline đã commit (RA-DEC-02 mục 5).

Dung sai đã duyệt: CHỈ `temp_mean`, `pressure_mean`, `wind_speed_mean` được lệch, tối đa 0,01, và chỉ ở ô mà trung bình 24 giờ
chưa làm tròn nằm sát biên x,xx5. Mọi cột số khác: 1e-9. Khoá, schema, NaN, `rain_day`, `wind_dir_8`: chính xác.
Các test "âm" bên dưới chứng minh dung sai này KHÔNG che được lỗi đơn vị, lỗi lệch ngày hay lệch 0,01 ở chỗ không phải biên.
"""
import numpy as np
import pandas as pd
import pytest

import data_paths
import weather_utils as wu
from conftest import evidence_dir


@pytest.fixture(scope="module")
def real_cmp(daily_real, baseline_daily, hourly_real):
    return wu.compare_daily(daily_real, baseline_daily, hourly_real)


def _cmp(new, base, hourly):
    return wu.compare_daily(new, base, hourly)


def test_declared_tolerance_constants():
    assert wu.ROUND_TOL == 0.01 and wu.ABS_EPS == 1e-9 and wu.BOUNDARY_EPS == 1e-6
    assert set(wu.TOL_MEAN_COLS) == {"temp_mean", "pressure_mean", "wind_speed_mean"} and wu.EXACT_COLS == ["rain_day", "wind_dir_8"]


def test_regenerated_daily_matches_baseline_within_approved_tolerance(real_cmp, daily_real, baseline_daily):
    """Tạo lại từ 8 cache gốc trong môi trường này: mọi ô khác baseline đều nằm trong dung sai đã duyệt."""
    r = real_cmp
    assert r["problems"] == [] and r["ok"]
    assert daily_real.shape == baseline_daily.shape == (16128, 16)
    cells, summ = r["cells"], r["summary"]
    assert int(summ["o_vi_pham"].sum()) == 0 and cells["trong_dung_sai"].all()
    assert set(cells["cot"]) <= set(wu.TOL_MEAN_COLS)                         # không cột nào khác bị lệch
    assert cells["abs_lech"].max() <= wu.ROUND_TOL + wu.ABS_EPS
    frac = cells["tb_chua_lam_tron"] * 100 - np.floor(cells["tb_chua_lam_tron"] * 100)
    assert ((frac - 0.5).abs() <= wu.BOUNDARY_EPS).all()                      # từng ô lệch đều sát biên x,xx5
    d = evidence_dir()
    if d is not None:                                                         # số ô lệch KHÔNG bị ép bằng 852: ghi lại con số đo được
        cells.to_csv(d / "weather_daily_vs_baseline_cells.csv", index=False)
        summ.to_csv(d / "weather_daily_vs_baseline_summary.csv")


def test_unrounded_means_reproduce_the_rounded_table(daily_real, hourly_real):
    um = wu.unrounded_means(hourly_real)
    m = daily_real.merge(um, on=wu.KEYS, validate="1:1")
    for c in wu.TOL_MEAN_COLS:
        assert ((m[c] - m[c + "_unrounded"]).abs() <= 0.005 + 1e-9).all()


def _boundary_cell(real_cmp, col="temp_mean"):
    c = real_cmp["cells"]
    return c[c["cot"] == col].iloc[0]


def _locate(df, city, date):
    return df.index[(df["City"] == city) & (df["Date"] == pd.Timestamp(date))][0]


def test_same_table_has_no_differences(daily_real, hourly_real):
    r = _cmp(daily_real, daily_real.copy(), hourly_real)
    assert r["ok"] and len(r["cells"]) == 0


def test_a_001_shift_away_from_the_boundary_is_a_violation(daily_real, hourly_real, real_cmp):
    """Lệch 0,01 ở một ô mà trung bình chưa làm tròn KHÔNG sát biên: không được tha."""
    um = wu.unrounded_means(hourly_real)
    frac = um["temp_mean_unrounded"] * 100 - np.floor(um["temp_mean_unrounded"] * 100)
    far = um[(frac - 0.5).abs() > 0.2].iloc[0]
    base = daily_real.copy()
    i = _locate(base, far["City"], far["Date"])
    base.loc[i, "temp_mean"] = round(base.loc[i, "temp_mean"] + 0.01, 2)
    r = _cmp(daily_real, base, hourly_real)
    assert not r["ok"] and len(r["cells"]) == 1 and not r["cells"]["trong_dung_sai"].iloc[0]


def test_a_002_shift_at_the_boundary_is_a_violation(daily_real, hourly_real, real_cmp):
    cell = _boundary_cell(real_cmp)
    base = daily_real.copy()
    i = _locate(base, cell["City"], cell["Date"])
    base.loc[i, "temp_mean"] = round(daily_real.loc[i, "temp_mean"] + 0.02, 2)
    r = _cmp(daily_real, base, hourly_real)
    assert not r["ok"] and not r["cells"]["trong_dung_sai"].any()


def test_at_the_boundary_only_the_two_valid_roundings_pass(daily_real, hourly_real, real_cmp):
    """Tại ô sát biên, chỉ hai cách làm tròn của chính trung bình đó được coi là tương đương; lệch 0,01 về phía còn lại thì không."""
    cell = _boundary_cell(real_cmp)
    i = _locate(daily_real, cell["City"], cell["Date"])
    lo, hi = np.floor(cell["tb_chua_lam_tron"] * 100) / 100, np.ceil(cell["tb_chua_lam_tron"] * 100) / 100
    assert {round(cell["moi"], 2), round(cell["baseline"], 2)} == {round(lo, 2), round(hi, 2)}
    new, base = daily_real.copy(), daily_real.copy()
    new.loc[i, "temp_mean"], base.loc[i, "temp_mean"] = round(lo, 2), round(hi, 2)
    assert _cmp(new, base, hourly_real)["ok"]
    base.loc[i, "temp_mean"] = round(lo - 0.01, 2)                            # cách `new` đúng 0,01 nhưng không phải một cách làm tròn hợp lệ
    r = _cmp(new, base, hourly_real)
    assert not r["ok"] and not r["cells"]["trong_dung_sai"].iloc[0]


@pytest.mark.parametrize("col", ["humidity_mean", "wind_u", "blh_mean", "temp_min", "precip_sum", "wind_speed_max"])
def test_other_numeric_columns_get_no_rounding_tolerance(daily_real, hourly_real, col):
    base = daily_real.copy()
    base.loc[100, col] = base.loc[100, col] + 0.01
    r = _cmp(daily_real, base, hourly_real)
    assert not r["ok"] and r["summary"].loc[col, "o_vi_pham"] == 1


def test_unit_errors_are_not_hidden(daily_real, hourly_real):
    for col, f in [("wind_speed_mean", lambda x: (x * 3.6).round(2)),        # m/s -> km/h
                   ("temp_mean", lambda x: (x + 273.15).round(2)),            # °C -> K
                   ("pressure_mean", lambda x: (x * 100).round(2))]:          # hPa -> Pa
        base = daily_real.copy()
        base[col] = f(base[col])
        r = _cmp(daily_real, base, hourly_real)
        assert not r["ok"] and r["summary"].loc[col, "o_vi_pham"] > 15000, col


def test_a_one_day_shift_is_not_hidden(daily_real, hourly_real):
    """Lỗi múi giờ/lệch ngày: giá trị của Delhi bị dịch một ngày."""
    base = daily_real.copy()
    m = base["City"] == "Delhi"
    cols = [c for c in base.columns if c not in wu.KEYS]
    base.loc[m, cols] = base.loc[m, cols].shift(1).bfill().to_numpy()
    r = _cmp(daily_real, base, hourly_real)
    assert not r["ok"] and r["summary"]["o_vi_pham"].sum() > 10000


def test_exact_columns_nan_keys_and_schema(daily_real, hourly_real):
    base = daily_real.copy(); base.loc[5, "rain_day"] = not base.loc[5, "rain_day"]
    assert not _cmp(daily_real, base, hourly_real)["ok"]
    base = daily_real.copy(); base.loc[5, "wind_dir_8"] = "N" if base.loc[5, "wind_dir_8"] != "N" else "S"
    assert not _cmp(daily_real, base, hourly_real)["ok"]
    base = daily_real.copy(); base.loc[5, "temp_mean"] = np.nan
    r = _cmp(daily_real, base, hourly_real)
    assert not r["ok"] and r["summary"].loc["temp_mean", "o_vi_pham"] == 1
    r = _cmp(daily_real, daily_real.iloc[:-1], hourly_real)
    assert not r["ok"] and "khoá" in r["problems"][0]
    r = _cmp(daily_real, daily_real.drop(columns="blh_min"), hourly_real)
    assert not r["ok"] and "bộ cột" in r["problems"][0]
    shifted = daily_real.copy(); shifted["Date"] = shifted["Date"] + pd.Timedelta(days=1)
    assert not _cmp(daily_real, shifted, hourly_real)["ok"]


def test_merge_keeps_air_quality_columns_and_adds_weather(daily_real):
    aq = pd.read_csv(wu.AQ_FILE, parse_dates=["Date"])
    merged = wu.merge_weather(aq, daily_real)
    wcols = wu.weather_cols(daily_real)
    assert merged.shape == (14056, 54) and len(wcols) == 14 and not merged.duplicated(wu.KEYS).any()
    pd.testing.assert_frame_equal(merged[aq.columns], aq)
    assert merged[wcols].notna().all().all()
    assert {"blh_mean", "blh_min"} <= set(wcols)


def test_physical_and_timezone_checks_still_hold(daily_real, hourly_real):
    assert wu.check_ranges(daily_real).empty
    peak = {c: int(h.groupby(pd.to_datetime(h["time"]).dt.hour)["temperature_2m"].mean().idxmax()) for c, h in hourly_real.items()}
    assert all(12 <= x <= 16 for x in peak.values()), peak                    # giờ nóng nhất rơi vào buổi chiều giờ địa phương
