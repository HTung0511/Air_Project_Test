#!/usr/bin/env bash
# DA vòng 2 — chạy MỘT notebook trong bản sao, có theo dõi I/O (và tùy chọn tắt mạng). Không sửa notebook.
# Dùng: r2_run_nb.sh <python> <root bản sao Air-Project-main> <notebook.ipynb> <thư mục log> <nhãn bước> [block|noblock] [timeout_s]
# In một dòng: bước, exit code, thời gian. Log: <logdir>/<nhãn>.json (tóm tắt nbclient), <nhãn>.jsonl (I/O), io_summary.csv (nối thêm).
PY=$1; ROOT=$(realpath "$2"); NB=$3; LOGDIR=$4; TAG=$5; NET=${6:-noblock}; TMO=${7:-1500}
HERE=$(dirname "$(realpath "$0")"); R1="$HERE/../../../evidence/scripts"
mkdir -p "$LOGDIR"; rm -f "$LOGDIR/$TAG.jsonl"
export PYTHONPATH="$HERE/iotrace" DA_IO_TRACE="$LOGDIR/$TAG.jsonl" DA_IO_ROOT="$ROOT" PYTHONDONTWRITEBYTECODE=1
[ "$NET" = block ] && export DA_NET_BLOCK=1 || unset DA_NET_BLOCK
SECONDS=0
"$PY" "$R1/run_notebook.py" "$ROOT" "$NB" "$TMO" > "$LOGDIR/$TAG.json" 2> "$LOGDIR/$TAG.stderr"; RC=$?
unset PYTHONPATH DA_IO_TRACE DA_NET_BLOCK
echo "$TAG | $NB | net=$NET | exit=$RC | ${SECONDS}s | $(grep -E '"(status|code_cells|cells_executed)"' "$LOGDIR/$TAG.json" | tr -d '\n ')"
"$PY" "$HERE/r2_iotrace_summary.py" "$LOGDIR/$TAG.jsonl" "$ROOT" "$TAG" "$LOGDIR/io_summary.csv"
exit $RC
