"""DA vòng 2 — TẬP MẪU THAM CHIẾU của DA theo RA-DEC-02 mục 2 (nhãn = AQI raw của ngày lịch kế tiếp), dựng thẳng từ raw.

KHÔNG import src/ (cũ hay mới). Chỉ pandas/numpy. Dùng để đối chiếu với tập mẫu mà mã Dev tạo ra (DA-03); bản thân script
này KHÔNG kiểm mã Dev.

Dùng: python r2_ref_cohort.py <city_day.csv raw> <R2_B03_baseline_cohort_keys.csv> <air_quality_8cities.csv (bảng sạch baseline)> <thư mục out>
Quy tắc giữ mẫu: 8 thành phố; Date >= 14/06/2017; Date_target = Date + 1 ngày lịch <= 01/07/2020;
AQI_raw(t) và AQI_raw(t+1) đều có, hữu hạn, > 0. Chia tập theo Date_target.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd

raw_p, old_p, clean_p, out = sys.argv[1], sys.argv[2], sys.argv[3], Path(sys.argv[4]); out.mkdir(parents=True, exist_ok=True)
CITIES = ["Delhi", "Gurugram", "Lucknow", "Jaipur", "Bengaluru", "Amritsar", "Chennai", "Hyderabad"]
START, END = pd.Timestamp("2017-06-14"), pd.Timestamp("2020-07-01")
TRAIN_END, TEST_END = pd.Timestamp("2019-06-30"), pd.Timestamp("2020-02-29")
ONE = pd.Timedelta(days=1)
season = lambda m: ("Đông (12-2)" if m in (12, 1, 2) else "Hè (3-5)" if m in (3, 4, 5) else "Mưa (6-9)" if m in (6, 7, 8, 9) else "Sau mưa (10-11)")
split_of = lambda dt: np.where(dt <= TRAIN_END, "train", np.where(dt <= TEST_END, "test", "holdout"))

raw = pd.read_csv(raw_p, parse_dates=["Date"])
raw = raw[raw.City.isin(CITIES)][["City", "Date", "AQI", "PM2.5"]].copy()
chk = []
def rec(name, value, note=""):
    chk.append({"kiem_tra": name, "gia_tri": value, "ghi_chu": note})

rec("số dòng raw của 8 thành phố", len(raw))
rec("khóa (City, Date) trùng trong raw", int(raw.duplicated(["City", "Date"]).sum()), "phải bằng 0")
gaps = []
for c, g in raw.groupby("City"):
    full = pd.date_range(g.Date.min(), g.Date.max())
    miss = full.difference(g.Date)
    gaps.append({"City": c, "raw_tu": g.Date.min().date(), "raw_den": g.Date.max().date(), "so_dong": len(g), "ngay_lich_thieu_dong": len(miss)})
gaps = pd.DataFrame(gaps)
rec("ngày lịch không có dòng trong raw (8 TP, toàn chuỗi)", int(gaps.ngay_lich_thieu_dong.sum()), "nếu > 0 thì shift theo dòng sẽ lệch ngày; script này luôn nối theo ngày lịch")
rec("ngày bắt đầu muộn nhất trong 8 TP", str(gaps.raw_tu.max()), "kỳ vọng 2017-06-14")
rec("ngày kết thúc sớm nhất trong 8 TP", str(gaps.raw_den.min()), "kỳ vọng 2020-07-01")
w = raw[(raw.Date >= START) & (raw.Date <= END)]
a = w.AQI
rec("dòng raw trong khoảng 14/06/2017–01/07/2020", len(w))
rec("AQI raw thiếu (NaN) trong khoảng", int(a.isna().sum()))
rec("AQI raw không hữu hạn (±inf)", int(np.isinf(a).sum()))
rec("AQI raw <= 0", int((a <= 0).sum()))
rec("AQI raw > 500", int((a > 500).sum()), f"lớn nhất = {a.max():.0f}; KHÔNG cắt, KHÔNG loại (RA-DEC-02 mục 2)")
rec("AQI raw không nguyên", int((a.dropna() % 1 != 0).sum()))
valid = lambda s: s.notna() & np.isfinite(s) & (s > 0)

# ---- nhãn theo NGÀY LỊCH kế tiếp: nối (City, Date+1), không shift theo dòng
nxt = raw[["City", "Date", "AQI"]].rename(columns={"Date": "Date_target", "AQI": "y_raw"})
d = raw.rename(columns={"AQI": "AQI_raw_t"}).assign(Date_target=lambda x: x.Date + ONE).merge(nxt, on=["City", "Date_target"], how="left", validate="1:1")
in_win = (d.Date >= START) & (d.Date_target <= END)
ok_t, ok_y = valid(d.AQI_raw_t), valid(d.y_raw)
rec("cặp (TP, ngày t) trong khoảng, trước khi xét AQI", int(in_win.sum()))
rec("  bị loại vì thiếu AQI(t), có AQI(t+1)", int((in_win & ~ok_t & ok_y).sum()))
rec("  bị loại vì có AQI(t), thiếu AQI(t+1)", int((in_win & ok_t & ~ok_y).sum()))
rec("  bị loại vì thiếu cả hai", int((in_win & ~ok_t & ~ok_y).sum()))
new = d[in_win & ok_t & ok_y].copy()
new["split"] = split_of(new.Date_target)
new = new.sort_values(["Date_target", "City"]).reset_index(drop=True)
rec("C_new: số mẫu", len(new))
for s in ("train", "test", "holdout"):
    rec(f"C_new: {s}", int((new.split == s).sum()), f"ngày nặng (y>=201): {int(((new.split == s) & (new.y_raw >= 201)).sum())}; Date_target {new.Date_target[new.split == s].min().date()} – {new.Date_target[new.split == s].max().date()}")
new[["City", "Date", "Date_target", "split", "AQI_raw_t", "y_raw"]].to_csv(out / "R2_C01_ref_cohort_keys.csv", index=False, date_format="%Y-%m-%d")

# ---- so với tập mẫu cũ
old = pd.read_csv(old_p, parse_dates=["Date", "Date_target"]).rename(columns={"AQI": "AQI_old_t", "y": "y_old", "split": "split_old"})
cl = pd.read_csv(clean_p, parse_dates=["Date"])[["City", "Date", "AQI", "AQI_was_missing", "suspect_sensor_error"]]
m = new.merge(old[["City", "Date", "AQI_old_t", "y_old", "split_old"]], on=["City", "Date"], how="outer", indicator=True)
m["Date_target"] = m.Date + ONE
m["nhom"] = m._merge.map({"both": "chung", "left_only": "chỉ có ở C_new (thêm)", "right_only": "chỉ có ở C_old (bớt)"}).astype(str)
rec("C_old: số mẫu", len(old)); rec("khóa chung C_old ∩ C_new", int((m.nhom == "chung").sum()))
rec("khóa chỉ có ở C_new (thêm)", int((m._merge == "left_only").sum())); rec("khóa chỉ có ở C_old (bớt)", int((m._merge == "right_only").sum()))
both = m[m._merge == "both"]
rec("khóa chung có nhãn y khác nhau", int((both.y_raw != both.y_old).sum())); rec("khóa chung có AQI(t) khác nhau", int((both.AQI_raw_t != both.AQI_old_t).sum()))
rec("khóa chung có split khác nhau", int((both.split != both.split_old).sum()))
diff = m[m._merge != "both"].copy()
rw = raw.set_index(["City", "Date"]); cx = cl.set_index(["City", "Date"])
def look(df, idx_date, col, src):
    return [src[col].get((c, t), np.nan) for c, t in zip(df.City, df[idx_date])]
for tag, col in (("t", "Date"), ("t+1", "Date_target")):
    diff[f"AQI_raw({tag})"] = look(diff, col, "AQI", rw); diff[f"PM2.5_raw({tag})"] = look(diff, col, "PM2.5", rw)
    diff[f"AQI_bang_sach({tag})"] = look(diff, col, "AQI", cx); diff[f"suspect_sensor_error({tag})"] = look(diff, col, "suspect_sensor_error", cx)
diff["split_theo_Date_target"] = split_of(diff.Date_target); diff["mua"] = diff.Date_target.dt.month.map(season)
def why(r):
    if r.nhom.startswith("chỉ có ở C_new"):
        w_ = [f"bảng sạch đã xóa AQI({k})" for k in ("t", "t+1") if pd.isna(r[f"AQI_bang_sach({k})"]) and pd.notna(r[f"AQI_raw({k})"])]
        return "; ".join(w_) or "không rõ"
    w_ = [f"raw thiếu AQI({k}) nhưng bảng sạch có" for k in ("t", "t+1") if pd.isna(r[f"AQI_raw({k})"]) and pd.notna(r[f"AQI_bang_sach({k})"])]
    return "; ".join(w_) or "không rõ"
if len(diff):
    diff["ly_do"] = diff.apply(why, axis=1)
cols = ["nhom", "City", "Date", "Date_target", "split_theo_Date_target", "mua", "AQI_raw(t)", "AQI_raw(t+1)", "AQI_bang_sach(t)", "AQI_bang_sach(t+1)",
        "PM2.5_raw(t)", "PM2.5_raw(t+1)", "suspect_sensor_error(t)", "suspect_sensor_error(t+1)", "ly_do"]
diff.reindex(columns=cols).sort_values(["City", "Date"]).to_csv(out / "R2_C03_cohort_key_diff.csv", index=False, date_format="%Y-%m-%d")

# ---- đếm theo split × thành phố × mùa
new["mua"] = new.Date_target.dt.month.map(season); old["mua"] = old.Date_target.dt.month.map(season); old["split"] = split_of(old.Date_target)
rec("C_old: split lưu trong file trùng split tính lại theo Date_target", bool((old.split == old.split_old.replace({"lockdown": "holdout"})).all()))
cnt = (pd.concat([new.assign(bo="C_new", y=new.y_raw)[["bo", "split", "City", "mua", "y"]], old.assign(bo="C_old", y=old.y_old)[["bo", "split", "City", "mua", "y"]]])
       .groupby(["split", "City", "mua", "bo"]).agg(n=("y", "size"), ngay_nang=("y", lambda s: int((s >= 201).sum()))).unstack("bo").fillna(0).astype(int))
cnt.columns = [f"{a}_{b}" for a, b in cnt.columns]; cnt["n_chenh (new − old)"] = cnt.n_C_new - cnt.n_C_old
cnt.reset_index().to_csv(out / "R2_C02_cohort_counts_split_city_season.csv", index=False)
by = cnt.groupby("split")[["n_C_old", "n_C_new", "ngay_nang_C_old", "ngay_nang_C_new", "n_chenh (new − old)"]].sum().loc[["train", "test", "holdout"]]
pd.DataFrame(chk).to_csv(out / "R2_C04_raw_aqi_and_cohort_checks.csv", index=False)
gaps.to_csv(out / "R2_C04_raw_calendar_by_city.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 90)
print(pd.DataFrame(chk).to_string(index=False)); print(); print(by.to_string()); print(); print(gaps.to_string(index=False)); print()
print(diff.reindex(columns=cols).sort_values(["City", "Date"]).to_string(index=False))
