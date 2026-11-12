"""ĐỐI CHIẾU SƠ BỘ CỦA DEV với bản tham chiếu mà DA đã khoá TRƯỚC khi thấy mã Dev (nhánh DA, commit 13e93ae).

Mục đích: phát hiện sớm chỗ Dev và DA hiểu khác nhau về RA-DEC-02 (chuỗi số 0 as-of, forward-fill, nhãn, cohort) trước khi DA
mất một vòng kiểm. Đây KHÔNG phải kiểm chứng độc lập và không thay cho kết quả của DA: chính Dev chạy, trên máy của Dev.

Script chạy mã tham chiếu của DA (không import `src/`) và so với `src/forecast_utils.py` của Dev:
  1. Trên raw thật: 9 đặc trưng (5 chất ô nhiễm + aqi_0, aqi_1, aqi_2, aqi_wk) của MỌI dòng (thành phố, ngày) của 8 thành phố,
     so với `r2_ref_asof.reference`.
  2. Tập khoá mẫu, AQI(t), nhãn và split so với `R2_C01_ref_cohort_keys.csv`.
  3. Hai bộ ca biên do DA tiêm vào raw (`r2_ref_asof.py fixture`): 11 ca trên raw đủ dòng và 3 ca trên raw bị xoá dòng (ngày lịch
     thiếu), so với KỲ VỌNG VIẾT TAY của DA; và kiểm hàng của ngày t không đổi khi cắt raw ở t.
  4. (nếu cho file `nb06_run_summary.json` của một lần chạy NB06) Bộ máy tính metric của DA (`r2_protocol.py`, độc lập với `src/`)
     chạy trên bảng mẫu của Dev, so với con số NB06 đã ghi: alpha, ngưỡng F2, MAE/RMSE/R² test, MAE 03-07/2020, TP/FP/FN/TN, hiệu MAE.

Dùng (từ thư mục dự án `Air-Project-main/`; commit DA phải có trong repo: `git fetch --depth 1 origin 13e93ae12c483f01a573ee51ef9562a315e45068`):
  python reports/ra/round2/dev_evidence/crosscheck_da_reference.py <thư mục làm việc ngoài dự án> [commit DA] [nb06_run_summary.json]
Kết quả: in ra màn hình và ghi `<thư mục làm việc>/crosscheck_da_reference.tsv`. Mã thoát 0 nếu mọi phép so khớp, 1 nếu có chỗ khác.
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT = Path.cwd()
sys.path.insert(0, str(PROJECT / "src"))
import forecast_utils as fu  # noqa: E402

work = Path(sys.argv[1]).resolve()
da_commit = sys.argv[2] if len(sys.argv) > 2 else "13e93ae12c483f01a573ee51ef9562a315e45068"
nb06_summary = Path(sys.argv[3]).resolve() if len(sys.argv) > 3 else None
work.mkdir(parents=True, exist_ok=True)
DA_DIR = "Air-Project-main/reports/ra/round2/evidence"


def da_file(rel):
    """Lấy một file của DA đúng ở commit đã khoá (git show), ghi vào thư mục làm việc."""
    out = work / Path(rel).name
    r = subprocess.run(["git", "show", f"{da_commit}:{DA_DIR}/{rel}"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"không lấy được {rel} ở commit {da_commit}: {r.stderr.decode()[:300]}\n"
                         f"(chạy trước: git fetch --depth 1 origin {da_commit})")
    out.write_bytes(r.stdout)
    return out


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ref_script = da_file("scripts/r2_ref_asof.py")
ref_keys = pd.read_csv(da_file("R2_C01_ref_cohort_keys.csv"), parse_dates=["Date", "Date_target"])
r2 = load_module("r2_ref_asof", ref_script)

rows = []


def note(check, ok, detail):
    rows.append({"phép so": check, "khớp": bool(ok), "chi tiết": detail})
    print(("KHỚP  " if ok else "KHÁC  ") + check + ": " + detail)


wx = fu.load_weather_daily()
raw_file = PROJECT / "data" / "raw" / "city_day.csv"

# ---------------------------------------------------------------- 1. đặc trưng trên raw thật
ref = r2.reference(pd.read_csv(raw_file, parse_dates=["Date"])).set_index(["City", "Date"]).sort_index()
mine = fu.make_forecast_features(fu.load_raw(), wx).set_index(["City", "Date"]).sort_index()
note("raw thật: cùng tập dòng (thành phố, ngày)", ref.index.equals(mine.index), f"DA {len(ref):,} dòng, Dev {len(mine):,} dòng")
feats = list(r2.POLL.values()) + ["aqi_0", "aqi_1", "aqi_2", "aqi_wk"]
for c in feats:
    a, b = ref[c].to_numpy(float), mine[c].to_numpy(float)
    nan_diff = int((np.isnan(a) ^ np.isnan(b)).sum())
    mx = float(np.nanmax(np.abs(a - b))) if (~np.isnan(a - b)).any() else 0.0
    note(f"raw thật: đặc trưng {c}", nan_diff == 0 and mx <= 1e-12, f"{len(a):,} ô; mặt nạ NaN khác {nan_diff}; chênh lớn nhất {mx:.1e}")

# ---------------------------------------------------------------- 2. cohort, AQI(t), nhãn, split
ds = fu.build_forecast_dataset(verbose=False)
dev = ds.assign(City=ds["City"].astype(str)).set_index(["City", "Date"])
da = ref_keys.set_index(["City", "Date"])
only_da, only_dev = da.index.difference(dev.index), dev.index.difference(da.index)
note("cohort: tập khoá (City, Date)", len(only_da) == 0 and len(only_dev) == 0,
     f"DA {len(da):,} khoá, Dev {len(dev):,} khoá; chỉ có ở DA {len(only_da)}, chỉ có ở Dev {len(only_dev)}")
common = da.index.intersection(dev.index)
split_name = {"lockdown": "holdout"}
dev_split = dev.loc[common, "split"].map(lambda s: split_name.get(s, s))
da_split = da.loc[common, "split"].astype(str)
note("cohort: AQI raw của ngày t", bool((da.loc[common, "AQI_raw_t"].to_numpy(float) == dev.loc[common, "AQI"].to_numpy(float)).all()), f"{len(common):,} khoá chung")
note("cohort: nhãn = AQI raw của ngày t+1", bool((da.loc[common, "y_raw"].to_numpy(float) == dev.loc[common, "y"].to_numpy(float)).all()), f"{len(common):,} khoá chung")
note("cohort: ngày được dự đoán", bool((da.loc[common, "Date_target"].to_numpy() == dev.loc[common, "Date_target"].to_numpy()).all()), f"{len(common):,} khoá chung")
same_split = (da_split.to_numpy() == dev_split.to_numpy())
note("cohort: split theo ngày được dự đoán", bool(same_split.all()),
     f"tên tập của DA {sorted(set(da_split))}, của Dev {sorted(set(dev.loc[common, 'split']))} ('lockdown' của Dev = 'holdout' của DA); khác {int((~same_split).sum())}")

# ---------------------------------------------------------------- 3. ca biên do DA tiêm vào raw, kỳ vọng viết tay
r = subprocess.run([sys.executable, str(ref_script), "fixture", str(raw_file), str(work)], capture_output=True, text=True)
note("ca biên: script của DA tự kiểm (viết tay khớp tham chiếu DA)", r.returncode == 0, r.stdout.strip().splitlines()[-1][:200] if r.stdout.strip() else r.stderr[-200:])
exp = pd.read_csv(work / "R2_F01_fixture_expected.csv", parse_dates=["Date"])
for bo, fname in (("chinh", "R2_F01_fixture_city_day.csv"), ("thieu_ngay", "R2_F01_fixture_thieu_ngay_city_day.csv")):
    raw = fu.load_raw(work / fname)
    f = fu.make_forecast_features(raw, wx).set_index(["City", "Date"])
    e = exp[exp["bo"].str.startswith(bo)]
    got = np.array([f.loc[(x.City, x.Date), x.dac_trung] for x in e.itertuples()])
    want = np.log1p(e["ky_vong_truoc_log1p"].to_numpy(float))            # kỳ vọng viết tay (trước log1p), tính lại đủ chính xác
    exact = (got == want) | (np.isnan(got) & np.isnan(want))
    d_csv = float(np.nanmax(np.abs(got - e["ky_vong_dac_trung"].to_numpy(float))))
    note(f"ca biên bộ '{bo}': giá trị as-of so với kỳ vọng viết tay của DA", bool(exact.all()),
         f"{int(exact.sum())}/{len(e)} hàng trùng chính xác với log1p(kỳ vọng); raw {len(raw):,} dòng, Dev chèn {raw.attrs.get('n_inserted_days', 0)} ngày lịch thiếu; "
         f"lệch lớn nhất so với cột `ky_vong_dac_trung` trong CSV (ghi 12 chữ số có nghĩa): {d_csv:.1e}")
    changed = 0
    for x in e.itertuples():
        cut = fu.make_forecast_features(raw, wx, as_of=x.Date).set_index(["City", "Date"])
        a, b = cut.loc[(x.City, x.Date), x.dac_trung], f.loc[(x.City, x.Date), x.dac_trung]
        changed += int(not ((np.isnan(a) and np.isnan(b)) or a == b))
    note(f"ca biên bộ '{bo}': hàng của ngày t khi cắt raw ở t", changed == 0, f"{changed}/{len(e)} hàng đổi")
for big in ("R2_F01_fixture_city_day.csv", "R2_F01_fixture_thieu_ngay_city_day.csv"):   # hai file raw ca biên (2,5 MB mỗi file): tạo lại được, không giữ
    (work / big).unlink(missing_ok=True)

# ---------------------------------------------------------------- 4. bộ máy metric của DA trên bảng mẫu của Dev, so với số NB06 đã ghi
if nb06_summary is not None:
    import model_utils as M
    r2p = load_module("r2_protocol", da_file("scripts/r2_protocol.py"))
    run = json.loads(nb06_summary.read_text(encoding="utf-8"))
    levels = {k: M.LEVELS[k] for k in ("L1", "L2", "L3")}
    got = r2p.run(ds, levels, "bảng mẫu của Dev")
    alpha_nb = {k: run["alpha"][k] for k in levels}
    note("metric (máy DA): alpha L1-L3", got["alphas"] == alpha_nb, f"máy DA {got['alphas']}; NB06 {alpha_nb}")
    thr_nb = {k: run["ngưỡng F2"][k] for k in got["thresholds"]}
    note("metric (máy DA): ngưỡng F2", got["thresholds"] == thr_nb, f"máy DA {got['thresholds']}; NB06 {thr_nb}")
    m = got["metrics"]
    t = m[m["tap"] == "test"].set_index("mo_hinh")
    names = [k for k in t.index if k in run["test"]]
    d = max(abs(float(t.loc[k, a]) - run["test"][k][c]) for k in names
            for a, c in (("MAE", "MAE"), ("RMSE", "RMSE"), ("R2", "R²"), ("MAE_ngay_nang", "MAE ngày nặng"), ("MAE_con_lai", "MAE ngày còn lại")))
    note("metric (máy DA): MAE, RMSE, R², MAE ngày nặng/còn lại trên test", d <= 1e-9, f"{len(names)} mô hình ({', '.join(names)}); chênh lớn nhất {d:.1e}")
    h = m[m["tap"] == "holdout"].set_index("mo_hinh")
    names = [k for k in h.index if k in run["03-07/2020"]]
    d = max(abs(float(h.loc[k, "MAE"]) - run["03-07/2020"][k]["MAE"]) for k in names)
    note("metric (máy DA): MAE 03-07/2020", d <= 1e-9, f"{len(names)} mô hình; chênh lớn nhất {d:.1e}")
    al = got["alerts"]
    al = al[al["tap"] == "test"]
    n_cmp = n_bad = 0
    for x in al.itertuples():
        w = run["cảnh báo test"].get(f"{x.mo_hinh} (ngưỡng {int(x.nguong)})")
        if w is not None:
            n_cmp += 1
            n_bad += (x.TP, x.FP, x.FN, x.TN) != (w["TP"], w["FP"], w["FN"], w["TN"])
    note("metric (máy DA): TP/FP/FN/TN trên test, ngưỡng 201 và ngưỡng F2", n_cmp == len(al) and n_bad == 0, f"{n_cmp}/{len(al)} quy tắc so được; {n_bad} quy tắc khác số đếm")
    pm = got["paired_mae"]
    pm = pm[(pm["tap"] == "test") & (pm["khoi_ngay"] == 14)]
    d, n_cmp = 0.0, 0
    for x in pm.itertuples():
        w = run["hiệu MAE test"].get(f"{x.A} − {x.B}")
        if w is not None:
            n_cmp += 1
            d = max(d, abs(x.dMAE - w["hiệu"]), abs(x.lo - w["KTC thấp"]), abs(x.hi - w["KTC cao"]))
    note("metric (máy DA): hiệu MAE và khoảng 95% (khối 14 ngày) trên test", n_cmp == len(pm) and d <= 1e-9, f"{n_cmp}/{len(pm)} phép so; chênh lớn nhất {d:.1e}")

out = pd.DataFrame(rows)
out.to_csv(work / "crosscheck_da_reference.tsv", sep="\t", index=False)
print(f"\n{int(out['khớp'].sum())}/{len(out)} phép so khớp. Commit DA: {da_commit}. Đây là đối chiếu sơ bộ của Dev, không thay cho kiểm chứng của DA.")
sys.exit(0 if out["khớp"].all() else 1)
