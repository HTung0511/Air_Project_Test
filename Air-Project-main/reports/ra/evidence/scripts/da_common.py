"""DA — hằng số/tiện ích dùng chung cho các script kiểm chứng (Bước 3).

Nguyên tắc: KHÔNG ghi vào data/, reports/figures/ hay bất kỳ artifact baseline nào.
Mọi đầu ra đi vào reports/ra/evidence/ (CSV nhỏ, hình) hoặc thư mục scratch ngoài repo.
"""
import hashlib, os, sys, warnings
sys.dont_write_bytecode = True
from pathlib import Path
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
HERE = Path(__file__).resolve()
EVID = HERE.parents[1]                      # reports/ra/evidence
ROOT = HERE.parents[4]                      # Air-Project-main (baseline, chỉ đọc)
SRC = ROOT / "src"
RAW = ROOT / "data" / "raw" / "city_day.csv"
CLEAN = ROOT / "data" / "processed" / "air_quality_8cities.csv"
WDAILY = ROOT / "data" / "processed" / "weather_daily_8cities.csv"
MERGED = ROOT / "data" / "processed" / "air_quality_8cities_weather.csv"
SCRATCH = Path(os.environ.get("DA_SCRATCH", "/home/user/scratch/da_tmp")); SCRATCH.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(SRC))

CITIES = ["Delhi", "Gurugram", "Lucknow", "Jaipur", "Bengaluru", "Amritsar", "Chennai", "Hyderabad"]
POLLUTANTS = ["PM2.5", "PM10", "NO", "NO2", "NOx", "NH3", "CO", "SO2", "O3", "Benzene", "Toluene"]
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 60); pd.set_option("display.max_rows", 200)


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def out(name):
    p = EVID / name; p.parent.mkdir(parents=True, exist_ok=True); return p


def save(df, name, index=True, **kw):
    p = out(name); df.to_csv(p, index=index, encoding="utf-8", **kw); print(f"[evidence] {p.relative_to(ROOT)}  ({len(df)} dòng)"); return p


def eqnan(a, b, tol=0.0):
    """So sánh từng phần tử; NaN == NaN; số so với dung sai tuyệt đối tol."""
    a, b = pd.Series(a).reset_index(drop=True), pd.Series(b).reset_index(drop=True)
    na, nb = a.isna(), b.isna()
    if pd.api.types.is_numeric_dtype(a) and pd.api.types.is_numeric_dtype(b) and a.dtype != bool and b.dtype != bool:
        return (na & nb) | ((a.astype(float) - b.astype(float)).abs() <= tol)
    return (na & nb) | (a.astype(object) == b.astype(object))
