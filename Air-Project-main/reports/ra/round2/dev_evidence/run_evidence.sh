#!/usr/bin/env bash
# Tạo lại toàn bộ bằng chứng của Dev (vòng sửa 2) từ một cây làm việc SẠCH ở commit mã cần kiểm.
#
#   bash run_evidence.sh <python của môi trường đã cài requirements-lock.txt> <thư mục làm việc NGOÀI dự án> [commit gốc để so] [commit DA]
#
# Ví dụ:  bash reports/ra/round2/dev_evidence/run_evidence.sh /home/user/.venv/bin/python /home/user/scratch/ev cd719cf
#
# Script chỉ ĐỌC repo: mọi notebook chạy trong bản sao dưới <thư mục làm việc>, mạng bị chặn ở mức socket.
# Mỗi bước ghi log riêng; mã thoát từng bước nằm trong <thư mục làm việc>/steps.tsv. Script thoát 1 nếu có bước nào khác 0.
# Bước đối chiếu sơ bộ với bản tham chiếu của DA chỉ chạy khi commit DA có trong repo:
#   git fetch --depth 1 origin 13e93ae12c483f01a573ee51ef9562a315e45068
# Cuối cùng, các file NHỎ (log, tóm tắt, bảng) được gom vào <thư mục làm việc>/dev_evidence/: đó là nội dung của thư mục
# `reports/ra/round2/dev_evidence/` trong repo. Bản sao dự án, notebook đã chạy và hai bảng output lớn của NB04 không được gom
# (chỉ ghi sha256). Cần khoảng 300 MB đĩa và 13 phút trên máy 2 CPU.
set -u
PY=${1:?thiếu đường dẫn python}
W=$(mkdir -p "${2:?thiếu thư mục làm việc}" && cd "$2" && pwd)
BASE=${3:-cd719cf}
DA_COMMIT=${4:-13e93ae12c483f01a573ee51ef9562a315e45068}
HERE=$(cd "$(dirname "$0")" && pwd)
SELF="$HERE/$(basename "$0")"
REPO=$(git rev-parse --show-toplevel)
P="$REPO/Air-Project-main"
cd "$P" || exit 2
case "$W/" in "$P"/*) echo "thư mục làm việc phải nằm NGOÀI $P"; exit 2;; esac
mkdir -p "$W"/{pytest,chains,compare,orig}
printf 'bước\tmã thoát\tlệnh (chạy từ Air-Project-main/)\n' > "$W/steps.tsv"
FAIL=0
export PYTHONDONTWRITEBYTECODE=1

step() {            # step <tên> <file log> <lệnh hiển thị> -- <lệnh thật...>
  local name=$1 log=$2 shown=$3; shift 4
  { echo "\$ $shown"; echo "commit: $(git rev-parse HEAD)"; echo "bắt đầu (UTC): $(date -u +%FT%TZ)"; } > "$log"
  "$@" >> "$log" 2>&1
  local code=$?
  { echo "[exit $code]"; echo "kết thúc (UTC): $(date -u +%FT%TZ)"; } >> "$log"
  printf '%s\t%s\t%s\n' "$name" "$code" "$shown" >> "$W/steps.tsv"
  [ "$code" -ne 0 ] && FAIL=1
  echo "  $name: exit $code"
}

# ---------------------------------------------------------------- 0. commit, cây làm việc, môi trường
{
  echo "commit mã được chạy : $(git rev-parse HEAD)"
  echo "nhánh               : $(git rev-parse --abbrev-ref HEAD)"
  echo "commit gốc để so    : $(git rev-parse "$BASE")"
  echo "git status --porcelain -- Air-Project-main (rỗng = sạch): '$(git status --porcelain -- .)'"
  echo "thời điểm (UTC)     : $(date -u +%FT%TZ)"
  echo "python              : $("$PY" -V 2>&1) ($PY)"
  echo "hệ điều hành        : $(uname -srm)"
  echo "CPU / RAM           : $(nproc) CPU, $(awk '/MemTotal/ {printf "%.1f GB", $2/1048576}' /proc/meminfo)"
  echo
  echo "tree git ở commit được chạy (git rev-parse HEAD:Air-Project-main/<thư mục>); hai commit có cùng tree thì cùng nội dung:"
  for d in src notebooks tools tests data reports/figures; do printf '  %-16s %s\n' "$d" "$(git rev-parse "HEAD:Air-Project-main/$d")"; done
  echo
  echo "sha256 của hai script đã chạy:"
  echo "  $(sha256sum "$SELF" | cut -d' ' -f1)  $(basename "$SELF")"
  echo "  $(sha256sum "$HERE/crosscheck_da_reference.py" | cut -d' ' -f1)  crosscheck_da_reference.py"
  echo
  echo "pip freeze:"
  "$PY" -m pip freeze 2>/dev/null
} > "$W/environment.txt"
if diff <("$PY" -m pip freeze 2>/dev/null | sort) <(grep -v '^#' requirements-lock.txt | sed '/^$/d' | sort) > "$W/environment_vs_lock.diff"; then
  echo "môi trường trùng requirements-lock.txt (diff rỗng)" > "$W/environment_vs_lock.diff"
else
  echo "LƯU Ý: môi trường khác requirements-lock.txt (xem environment_vs_lock.diff)"
fi
step pip_check "$W/pip_check.log" "python -m pip check" -- "$PY" -m pip check

# ---------------------------------------------------------------- 1. toàn bộ kiểm thử
step pytest "$W/pytest/pytest_full.log" \
  "AIR_TEST_EVIDENCE_DIR=<work>/pytest python -m pytest -q -rs --durations=15 --junitxml=<work>/pytest/junit.xml" -- \
  env AIR_TEST_EVIDENCE_DIR="$W/pytest" "$PY" -m pytest -q -rs --durations=15 --junitxml="$W/pytest/junit.xml"

# ---------------------------------------------------------------- 2. chuỗi notebook trong bản sao, chặn mạng
chain() {           # chain <tên> <notebooks> <weather>
  step "chain_$1" "$W/chains/$1.log" "python tools/run_chain.py --work <work>/chains --name $1 --notebooks $2 --weather $3 --timeout 2400 --force" -- \
    "$PY" tools/run_chain.py --work "$W/chains" --name "$1" --notebooks "$2" --weather "$3" --timeout 2400 --force
}
chain baseline  04,05,06          baseline     # NB04 từ cache; NB05, NB06 đọc bảng thời tiết baseline đã commit
chain nb04      04,05,06          nb04         # NB05, NB06 đọc bảng thời tiết do NB04 vừa tạo
chain eda       01,02,03,05       baseline     # nhánh làm sạch/EDA hồi cứu (không sửa ở vòng 2)
chain nb06_only 06                baseline     # đúng cấu hình đã tạo ra output commit trong notebook 06
chain all6_nb04 01,02,03,04,05,06 nb04         # cả sáu notebook nối tiếp; NB05, NB06 đọc bảng thời tiết do NB04 vừa tạo trong cùng lần chạy

# ---------------------------------------------------------------- 3. output đã commit trong NB04/NB06 = output khi chạy lại (kể cả hình)
step committed_outputs_nb04 "$W/compare/committed_outputs_nb04.log" \
  "python tools/adopt_outputs.py <work>/chains/baseline/executed/04_weather_merge.ipynb notebooks/04_weather_merge.ipynb --check" -- \
  "$PY" tools/adopt_outputs.py "$W/chains/baseline/executed/04_weather_merge.ipynb" notebooks/04_weather_merge.ipynb --check
step committed_outputs_nb06 "$W/compare/committed_outputs_nb06.log" \
  "python tools/adopt_outputs.py <work>/chains/nb06_only/executed/06_predict_aqi.ipynb notebooks/06_predict_aqi.ipynb --check" -- \
  "$PY" tools/adopt_outputs.py "$W/chains/nb06_only/executed/06_predict_aqi.ipynb" notebooks/06_predict_aqi.ipynb --check

# ---------------------------------------------------------------- 4. NB06 GỐC (commit gốc) chạy lại trong chính môi trường này
rm -rf "$W/orig/Air-Project-main" "$W/orig/executed"
git -C "$REPO" archive "$BASE" Air-Project-main | tar -x -C "$W/orig"
git -C "$REPO" show "$BASE:Air-Project-main/notebooks/06_predict_aqi.ipynb" > "$W/orig/06_predict_aqi.author.ipynb"
step original_nb06 "$W/orig/original_nb06.log" \
  "python tools/run_notebook.py <work>/orig/Air-Project-main 06_predict_aqi.ipynb --out <work>/orig/executed --timeout 2400 --block-network   # mã và dữ liệu của $BASE" -- \
  "$PY" tools/run_notebook.py "$W/orig/Air-Project-main" 06_predict_aqi.ipynb --out "$W/orig/executed" --timeout 2400 --block-network

# ---------------------------------------------------------------- 5. so output dạng chữ giữa các lần chạy (công cụ đo, luôn thoát 0)
IGN=(--ignore '^Thư mục gốc' --ignore '^\[đọc\]' --ignore '^\[ghi\]' --ignore '^ *LƯU Ý' --ignore '^Môi trường:')
cmp_nb() {          # cmp_nb <tên báo cáo> <A> <B>
  step "cmp_$1" "$W/compare/$1.log" "python tools/compare_notebook_outputs.py <A> <B> --out <work>/compare/$1.md  (A=${2#$W/}, B=${3#$W/})" -- \
    "$PY" tools/compare_notebook_outputs.py "$2" "$3" --out "$W/compare/$1.md" "${IGN[@]}"
}
cmp_nb nb06_author_outputs_vs_original_code_rerun   "$W/orig/06_predict_aqi.author.ipynb"                      "$W/orig/executed/06_predict_aqi.ipynb"
cmp_nb nb06_original_code_vs_forecast_path          "$W/orig/executed/06_predict_aqi.ipynb"                    "$W/chains/nb06_only/executed/06_predict_aqi.ipynb"
cmp_nb nb06_baseline_weather_vs_nb04_weather        "$W/chains/nb06_only/executed/06_predict_aqi.ipynb"        "$W/chains/nb04/executed/06_predict_aqi.ipynb"
cmp_nb nb05_baseline_weather_vs_nb04_weather        "$W/chains/baseline/executed/05_weather_correlation.ipynb" "$W/chains/nb04/executed/05_weather_correlation.ipynb"
for nb in 01_cleaning 02_cleaning_evidence 03_eda 05_weather_correlation; do
  cmp_nb "${nb}_committed_vs_rerun" "$P/notebooks/$nb.ipynb" "$W/chains/eda/executed/$nb.ipynb"
done

# ---------------------------------------------------------------- 6. hình của NB06: bản ở commit gốc so với bản hiện có trong repo
step figures "$W/compare/nb06_figures_old_vs_new.log" "python - (so điểm ảnh 5 hình model_0x giữa $BASE và HEAD; mã nằm trong run_evidence.sh)" -- \
  "$PY" - "$REPO" "$BASE" "$W/compare/nb06_figures_old_vs_new.tsv" "$W/chains/nb06_only/proj/reports/figures" <<'EOF'
import hashlib, io, subprocess, sys
from pathlib import Path
import numpy as np
import matplotlib.image as mpimg
repo, base, out, rerun = sys.argv[1], sys.argv[2], sys.argv[3], Path(sys.argv[4])
rows = ["hình\tsha256 ở commit gốc\tsha256 trong repo (HEAD)\tsha256 khi chạy lại NB06\tHEAD = chạy lại\tkích thước\tđiểm ảnh khác so với commit gốc\ttỉ lệ"]
bad = 0
for f in sorted((Path(repo) / "Air-Project-main/reports/figures").glob("model_0*.png")):
    old = subprocess.run(["git", "-C", repo, "show", f"{base}:Air-Project-main/reports/figures/{f.name}"], capture_output=True, check=True).stdout
    new, again = f.read_bytes(), (rerun / f.name).read_bytes()
    a, b = mpimg.imread(io.BytesIO(old), format="png"), mpimg.imread(io.BytesIO(new), format="png")
    if a.shape == b.shape:
        d = np.abs(a.astype(float) - b.astype(float)).max(axis=-1) > 0
        n, share = int(d.sum()), f"{d.mean():.4%}"
    else:
        n, share = "khác kích thước", ""
    h = lambda x: hashlib.sha256(x).hexdigest()
    bad += h(new) != h(again)
    rows.append(f"{f.name}\t{h(old)}\t{h(new)}\t{h(again)}\t{h(new) == h(again)}\t{a.shape[1]}x{a.shape[0]}\t{n}\t{share}")
Path(out).write_text("\n".join(rows) + "\n", encoding="utf-8")
print("\n".join(rows))
sys.exit(1 if bad else 0)            # hình đã commit phải trùng từng byte với hình do NB06 tạo lại ở môi trường đã ghim
EOF

# ---------------------------------------------------------------- 7. đối chiếu SƠ BỘ của Dev với bản tham chiếu DA đã khoá (không thay kiểm chứng của DA)
if git -C "$REPO" cat-file -e "$DA_COMMIT^{commit}" 2>/dev/null; then
  mkdir -p "$W/da_crosscheck"
  step da_crosscheck "$W/da_crosscheck/crosscheck_da_reference.log" \
    "python reports/ra/round2/dev_evidence/crosscheck_da_reference.py <work>/da_crosscheck $DA_COMMIT <work>/chains/nb06_only/proj/outputs/nb06/nb06_run_summary.json" -- \
    "$PY" "$HERE/crosscheck_da_reference.py" "$W/da_crosscheck" "$DA_COMMIT" "$W/chains/nb06_only/proj/outputs/nb06/nb06_run_summary.json"
else
  echo "  da_crosscheck: BỎ QUA (commit DA $DA_COMMIT không có trong repo; chạy: git fetch --depth 1 origin $DA_COMMIT)"
  printf 'da_crosscheck\tbỏ qua\tcommit DA %s không có trong repo\n' "$DA_COMMIT" >> "$W/steps.tsv"
fi

# ---------------------------------------------------------------- 8. các lần chạy khác nhau cho cùng file output (tính tất định)
determinism() {
  local bad=0 f b
  same() {          # same <bắt buộc|tham khảo> <A> <B> <nhãn>
    if cmp -s "$2" "$3"; then echo "TRÙNG  $4"
    elif [ "$1" = "bắt buộc" ]; then echo "KHÁC   $4"; bad=$((bad + 1))
    else echo "khác   $4   (tham khảo, không tính vào mã thoát)"; fi
  }
  echo "# Bắt buộc trùng từng byte"
  for f in "$W"/pytest/nb06_*; do
    b=$(basename "$f"); same "bắt buộc" "$f" "$W/chains/nb06_only/proj/outputs/nb06/$b" "output NB06 '$b': lần chạy trong pytest == chuỗi nb06_only"
  done
  for b in weather_daily_8cities.csv air_quality_8cities_weather.csv nb04_vs_committed_cells.csv; do
    same "bắt buộc" "$W/chains/baseline/proj/outputs/nb04/$b" "$W/chains/nb04/proj/outputs/nb04/$b" "output NB04 '$b': chuỗi baseline == chuỗi nb04"
  done
  same "bắt buộc" "$W/chains/nb04/proj/outputs/nb04/weather_daily_8cities.csv" "$W/chains/all6_nb04/proj/outputs/nb04/weather_daily_8cities.csv" "output NB04 'weather_daily_8cities.csv': chuỗi nb04 == chuỗi all6_nb04"
  same "bắt buộc" "$W/pytest/weather_daily_vs_baseline_cells.csv" "$W/chains/nb04/proj/outputs/nb04/nb04_vs_committed_cells.csv" "ô thời tiết khác bản đã commit: bảng do test ghi == bảng do NB04 ghi"
  echo
  echo "# Tham khảo (được phép khác: xem ghi chú)"
  for b in nb06_predictions.csv nb06_cohort_keys.csv nb06_masked_cells.csv nb06_retention.csv nb06_run_summary.json; do
    same "tham khảo" "$W/chains/baseline/proj/outputs/nb06/$b" "$W/chains/nb06_only/proj/outputs/nb06/$b" "output NB06 '$b': chuỗi baseline (04,05,06) == chuỗi nb06_only"
  done
  for b in nb06_predictions.csv nb06_cohort_keys.csv nb06_masked_cells.csv nb06_retention.csv; do
    same "tham khảo" "$W/chains/nb04/proj/outputs/nb06/$b" "$W/chains/all6_nb04/proj/outputs/nb06/$b" "output NB06 '$b': chuỗi nb04 == chuỗi all6_nb04 (cùng raw, cùng thời tiết mới; bảng sạch hồi cứu khác)"
  done
  same "tham khảo" "$W/chains/nb04/proj/outputs/nb04/air_quality_8cities_weather.csv" "$W/chains/all6_nb04/proj/outputs/nb04/air_quality_8cities_weather.csv" "output NB04 'air_quality_8cities_weather.csv': chuỗi nb04 == chuỗi all6_nb04 (ở all6_nb04, NB01 đã ghi lại bảng sạch của bản sao, lệch cỡ 1e-13)"
  echo
  echo "# sha256 của output NB04 (không gom vào dev_evidence vì lớn; tạo lại được bằng NB04)"
  (cd "$W/chains" && sha256sum nb04/proj/outputs/nb04/weather_daily_8cities.csv nb04/proj/outputs/nb04/air_quality_8cities_weather.csv all6_nb04/proj/outputs/nb04/air_quality_8cities_weather.csv)
  echo
  echo "# sha256 của các notebook đã chạy (không gom; notebook 04 và 06 trong repo đã mang output, xem bước committed_outputs_*)"
  (cd "$W/chains" && sha256sum */executed/*.ipynb)
  return $bad
}
step determinism "$W/compare/determinism_between_runs.txt" "(so từng byte các file output giữa các lần chạy; mã nằm trong run_evidence.sh)" -- determinism

# ---------------------------------------------------------------- 9. gom các file nhỏ vào <work>/dev_evidence
collect() {
  set -e
  local D="$W/dev_evidence" n f b
  rm -rf "$D"; mkdir -p "$D"/{pytest,chains,compare,orig}
  cp "$SELF" "$HERE/crosscheck_da_reference.py" "$D/"
  cp "$W/steps.tsv" "$W/environment.txt" "$W/environment_vs_lock.diff" "$W/pip_check.log" "$D/"
  cp "$W/pytest/pytest_full.log" "$W/pytest/junit.xml" "$D/pytest/"
  for f in "$W"/pytest/*.csv "$W"/pytest/chain_*; do      # bảng do test ghi + log các chuỗi do test chạy; bỏ bản sao output NB06 (trùng chuỗi nb06_only)
    b=$(basename "$f"); case "$b" in nb06_*) ;; *) cp "$f" "$D/pytest/";; esac
  done
  for n in baseline nb04 eda nb06_only all6_nb04; do
    mkdir -p "$D/chains/$n"
    cp "$W/chains/$n.log" "$D/chains/"
    cp "$W/chains/$n/chain_summary.json" "$W/chains/$n/provenance.jsonl" "$D/chains/$n/"
  done
  mkdir -p "$D/chains/nb06_only/nb06_outputs"
  cp "$W"/chains/nb06_only/proj/outputs/nb06/* "$D/chains/nb06_only/nb06_outputs/"
  mkdir -p "$D/chains/nb04/nb04_outputs"
  for f in nb04_manifest.json nb04_vs_committed_cells.csv nb04_vs_committed_summary.csv; do cp "$W/chains/nb04/proj/outputs/nb04/$f" "$D/chains/nb04/nb04_outputs/"; done
  for n in nb04 all6_nb04; do                              # NB06 với thời tiết mới: các bảng nhỏ (dự đoán và khoá mẫu không gom; cohort không phụ thuộc thời tiết)
    mkdir -p "$D/chains/$n/nb06_outputs"
    for f in nb06_run_summary.json nb06_snapshot_checks.csv nb06_alerts_test.csv nb06_path_comparison.csv nb06_path_comparison_paired.csv nb06_retention.csv nb06_masking_summary.csv nb06_cohort_diff.csv; do
      cp "$W/chains/$n/proj/outputs/nb06/$f" "$D/chains/$n/nb06_outputs/"
    done
  done
  cp "$W"/compare/* "$D/compare/"
  cp "$W/orig/original_nb06.log" "$D/orig/"
  if [ -d "$W/da_crosscheck" ]; then
    mkdir -p "$D/da_crosscheck"
    cp "$W/da_crosscheck/crosscheck_da_reference.log" "$W/da_crosscheck/crosscheck_da_reference.tsv" "$D/da_crosscheck/"
  fi
}
(collect); COLLECT_RC=$?          # không đặt trong `if`: ở đó `set -e` của hàm bị bỏ qua
if [ "$COLLECT_RC" -eq 0 ]; then
  echo "  đã gom $(find "$W/dev_evidence" -type f | wc -l) file ($(du -sh "$W/dev_evidence" | cut -f1)) vào $W/dev_evidence"
else
  echo "  LỖI khi gom file vào $W/dev_evidence"; FAIL=1
fi

echo
cat "$W/steps.tsv"
echo
[ "$FAIL" -eq 0 ] && echo "MỌI BƯỚC THOÁT 0" || echo "CÓ BƯỚC KHÁC 0 (xem steps.tsv)"
exit $FAIL
