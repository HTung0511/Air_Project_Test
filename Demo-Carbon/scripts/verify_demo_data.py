#!/usr/bin/env python3
"""Kiểm tra dữ liệu demo: tính lại một số chỉ số và kiểm tra cỡ mẫu từ JSON.

Đối chiếu với CSV nguồn do RA thực hiện trước đây là một mức kiểm tra riêng;
script này không đọc CSV nguồn hay xác minh SHA. Script cũng không xác thực toàn
bộ pipeline từ dữ liệu thô; F01 vẫn đang mở.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "src" / "data" / "aqiDemoData.json"


def assert_close(name: str, actual: float, expected: float, tol: float = 1e-4):
    diff = abs(actual - expected)
    if diff > tol:
        raise AssertionError(f"[FAIL] {name}: actual={actual}, expected={expected}, diff={diff}")
    print(f"[PASS] {name}: {actual:.6f} (expected {expected:.6f}, diff={diff:.2e})")


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    prov = data["provenance"]
    records = data["records"]
    cities = data["cities"]

    print("=== 1. KIỂM TRA CỠ MẪU TỪ JSON DEMO ===")
    assert len(cities) == 8, "Phải có đúng 8 thành phố"
    assert len(records) == 2922, f"Tổng số dòng phải là 2922, thực tế: {len(records)}"

    test_recs = [r for r in records if r["s"] == "test"]
    hold_recs = [r for r in records if r["s"] == "holdout"]
    assert len(test_recs) == 1947, f"Tập test phải có 1947 cặp, thực tế: {len(test_recs)}"
    assert len(hold_recs) == 975, f"Tập holdout phải có 975 cặp, thực tế: {len(hold_recs)}"

    test_heavy = sum(1 for r in test_recs if r["y"] >= 201.0)
    hold_heavy = sum(1 for r in hold_recs if r["y"] >= 201.0)
    assert test_heavy == 389, f"Tập test phải có 389 cặp nặng (y>=201), thực tế: {test_heavy}"
    assert hold_heavy == 18, f"Tập holdout phải có 18 cặp nặng (y>=201), thực tế: {hold_heavy}"
    print(f"[PASS] Test: n={len(test_recs)}, ngày nặng={test_heavy} | Holdout: n={len(hold_recs)}, ngày nặng={hold_heavy}")

    print("\n=== 2. KIỂM TRA PHẠM VI NGÀY ĐẦU VÀO (t) VÀ NGÀY ĐÍCH (t+1) ===")
    test_t_min = min(r["t"] for r in test_recs)
    test_t_max = max(r["t"] for r in test_recs)
    test_t1_min = min(r["t1"] for r in test_recs)
    test_t1_max = max(r["t1"] for r in test_recs)
    assert (test_t_min, test_t_max) == ("2019-06-30", "2020-02-28")
    assert (test_t1_min, test_t1_max) == ("2019-07-01", "2020-02-29")
    print(f"[PASS] Phạm vi Test: t=[{test_t_min}..{test_t_max}] -> t+1=[{test_t1_min}..{test_t1_max}]")

    hold_t_min = min(r["t"] for r in hold_recs)
    hold_t_max = max(r["t"] for r in hold_recs)
    hold_t1_min = min(r["t1"] for r in hold_recs)
    hold_t1_max = max(r["t1"] for r in hold_recs)
    assert (hold_t_min, hold_t_max) == ("2020-02-29", "2020-06-30")
    assert (hold_t1_min, hold_t1_max) == ("2020-03-01", "2020-07-01")
    print(f"[PASS] Phạm vi Holdout: t=[{hold_t_min}..{hold_t_max}] -> t+1=[{hold_t1_min}..{hold_t1_max}]")

    print("\n=== 3. ĐỐI SOÁT MAE TRÊN TEST VÀ HOLDOUT ===")
    mae_test_l3 = sum(abs(r["y"] - r["l3"]) for r in test_recs) / len(test_recs)
    mae_test_base = sum(abs(r["y"] - r["aqi"]) for r in test_recs) / len(test_recs)
    mae_hold_l3 = sum(abs(r["y"] - r["l3"]) for r in hold_recs) / len(hold_recs)
    mae_hold_base = sum(abs(r["y"] - r["aqi"]) for r in hold_recs) / len(hold_recs)

    assert_close("Test MAE Ridge L3", mae_test_l3, 19.519018, 1e-5)
    assert_close("Test MAE Baseline (Ngày mai = hôm nay)", mae_test_base, 23.466359, 1e-5)
    assert_close("Holdout MAE Ridge L3", mae_hold_l3, 13.783362, 1e-5)
    assert_close("Holdout MAE Baseline (Ngày mai = hôm nay)", mae_hold_base, 14.803077, 1e-5)

    print("\n=== 4. ĐỐI SOÁT TP / FP / FN / TN THEO GIÁ TRỊ GỐC (KHÔNG LÀM TRÒN TRƯỚC) ===")
    def verify_confusion(recs, key, thr, exp_tp, exp_fp, exp_fn, exp_tn, label):
        tp = sum(1 for r in recs if r["y"] >= 201.0 and r[key] >= thr)
        fp = sum(1 for r in recs if r["y"] < 201.0 and r[key] >= thr)
        fn = sum(1 for r in recs if r["y"] >= 201.0 and r[key] < thr)
        tn = sum(1 for r in recs if r["y"] < 201.0 and r[key] < thr)
        assert (tp, fp, fn, tn) == (exp_tp, exp_fp, exp_fn, exp_tn), (
            f"[FAIL] {label}: got {(tp, fp, fn, tn)}, expected {(exp_tp, exp_fp, exp_fn, exp_tn)}"
        )
        print(f"[PASS] {label}: TP={tp}, FP={fp}, FN={fn}, TN={tn}")

    verify_confusion(test_recs, "l3", 166.0, 377, 113, 12, 1445, "Test Ridge L3 @ F2 (166)")
    verify_confusion(test_recs, "aqi", 160.0, 374, 143, 15, 1415, "Test Baseline @ F2 (160)")
    verify_confusion(test_recs, "l3", 201.0, 346, 40, 43, 1518, "Test Ridge L3 @ 201")
    verify_confusion(test_recs, "aqi", 201.0, 333, 59, 56, 1499, "Test Baseline @ 201")

    verify_confusion(hold_recs, "l3", 166.0, 13, 44, 5, 913, "Holdout Ridge L3 @ F2 (166)")
    verify_confusion(hold_recs, "aqi", 160.0, 13, 51, 5, 906, "Holdout Baseline @ F2 (160)")
    verify_confusion(hold_recs, "l3", 201.0, 6, 6, 12, 951, "Holdout Ridge L3 @ 201")
    verify_confusion(hold_recs, "aqi", 201.0, 5, 13, 13, 944, "Holdout Baseline @ 201")

    print("\n=== 5. KIỂM TRA CA BIÊN SÁT NGƯỠNG (AMRITSAR t=2020-01-03 -> t+1=2020-01-04) ===")
    amr = next(r for r in test_recs if r["c"] == "Amritsar" and r["t"] == "2020-01-03")
    assert amr["t1"] == "2020-01-04"
    assert_close("Amritsar 2020-01-03 pred_Ridge L3", amr["l3"], 165.973826, 1e-6)
    assert amr["l3"] < 166.0, "Giá trị gốc 165.973826 phải nhỏ hơn 166.0 (không phát cảnh báo)"
    assert amr["y"] == 221.0, "AQI thực tế t+1 phải là 221.0"
    print(f"[PASS] Ca biên Amritsar t=2020-01-03: pred_L3={amr['l3']:.6f} (<166) -> Bỏ sót (FN), thực tế y={amr['y']}")

    print("\n=== 6. THÔNG TIN PROVENANCE ĐƯỢC GHI TRONG JSON (KHÔNG XÁC MINH SHA HAY CSV) ===")
    print(f"[INFO] Artifact dự báo: {prov['predictions_artifact']} @ commit {prov['predictions_commit']}")
    print(f"[INFO] SHA-256 R2_B04 theo provenance:  {prov['predictions_sha256']}")
    print(f"[INFO] Đối chiếu V21 đã ghi trong provenance:   {prov['v21_crosscheck_artifact']} @ commit {prov['v21_crosscheck_commit']} (max diff={prov['v21_max_abs_diff']})")
    print("[INFO] Đối chiếu CSV nguồn của RA là kiểm tra trước đây, không được thực hiện bởi script này.")
    print("[INFO] Chưa xác thực toàn bộ pipeline từ dữ liệu thô; F01 vẫn đang mở.")
    print("\n=> Các phép kiểm dữ liệu demo đã chạy đạt.")


if __name__ == "__main__":
    main()
