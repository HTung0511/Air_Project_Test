"""GateB-PILOT (DA, độc lập) — đo chi phí cutoff + smoke fixture nhỏ.
Chỉ chạy đo, KHÔNG full 1.114 ngày, KHÔNG 47 ngày x mọi perturb, KHÔNG T2.5 nặng.
Chọn 3 mốc cutoff MÙ (chỉ từ raw, trước khi xem kết quả Dev)."""
import time, numpy as np, pandas as pd
import forecast_utils as F
from eda_utils import CITIES

t0 = time.time()
raw = F.load_raw(verbose=False)          # full raw, prepared (chèn ngày thiếu thành NaN)
weather = F.load_weather_daily()         # baseline committed daily weather
print(f"[load] raw={raw.shape} weather={weather.shape}  t={time.time()-t0:.2f}s")

# ---- chọn 3 mốc cutoff MÙ (chỉ đọc raw AQI/Date) ----
def detect_cuts():
    flat_ends, gaps = [], []
    for city in CITIES:
        x = raw[raw.City == city].sort_values("Date")
        a = x["AQI"].to_numpy(float)
        z = (a == 0)
        idx = np.arange(len(a))
        last = np.maximum.accumulate(np.where(~z, idx, -1))
        run = np.where(z, idx - last, 0)
        if (run >= 3).any():
            flat_ends.append(x["Date"].iloc[int(np.argmax(run >= 3))])
        full = pd.date_range(x["Date"].min(), x["Date"].max(), freq="D")
        present = set(x["Date"])
        miss = [d for d in full if d not in present]
        if miss:
            gaps.append(miss[len(miss)//2])
    t1 = min(flat_ends) if flat_ends else pd.Timestamp("2017-06-16")   # gần flatline
    t2 = min(gaps) if gaps else pd.Timestamp("2018-01-01")             # gần gap lịch
    t3 = pd.Timestamp("2019-02-01")                                   # bình thường
    return t1, t2, t3

t1, t2, t3 = detect_cuts()
print(f"[cuts-chosen-blind] t1(flatline)={t1.date()} t2(gap)={t2.date()} t3(normal)={t3.date()}")

# ---- rebuild cohort (T2.2 / mục 3) ----
tc = time.time()
ds = F.build_forecast_dataset(raw, weather, verbose=False)
cohort = ds.groupby("split").size().to_dict()
print(f"[cohort] total={len(ds)} by_split={cohort}  t={time.time()-tc:.3f}s")

# ---- đo chi phí cutoff tại 3 mốc ----
cut_results = {}
for name, t in [("t1_flatline", t1), ("t2_gap", t2), ("t3_normal", t3)]:
    tc = time.time()
    f = F.make_forecast_features(raw, weather, as_of=t)
    el = time.time() - tc
    cut_results[name] = (str(t.date()), len(f), round(el, 4))
    print(f"[cutoff] {name} {t.date()}: rows={len(f)} time={el:.4f}s")

# ---- fixture nhỏ: asof_pollutant trên ví dụ protocol (RA-DEC-03 DA-Q1) ----
seqs = {
    "A,0,0,0,B":               [5.0, 0, 0, 0, 7.0],
    "A,0,0,NaN,0,B":           [5.0, 0, 0, np.nan, 0, 7.0],
    "A,0,0,0,NaN,NaN,B":      [5.0, 0, 0, 0, np.nan, np.nan, 7.0],
}
print("[fixture-small] asof_pollutant (value/flat/run):")
for name, v in seqs.items():
    r = F.asof_pollutant(np.array(v, float))
    print(f"  {name}: val={np.round(r['value'],2).tolist()} flat={r['flat'].tolist()} run={r['run'].tolist()}")

print(f"[TOTAL pilot] {time.time()-t0:.2f}s")
print("CUT_RESULTS_JSON=" + __import__("json").dumps(cut_results))
