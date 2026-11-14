"""Tách các ô (panel) từ ảnh gốc của nhóm để bảo đảm cỡ chữ khi in, KHÔNG mất thông tin.

Cách dùng: python3 split_panels.py
Đọc 4 PNG trong Air-Project-main/reports/figures/, ghi các ô cắt ra
deliverables/layout_assets/panels/ và in kế hoạch chèn (khổ hiển thị pt).

Nguyên tắc kiểm chứng (in ra, không im lặng):
  1. Miền NGOÀI mỗi biên cắt (sát biên, trong khoảng ô đi qua) phải sạch mực
     -> không cắt qua chữ hay nét vẽ.
  2. Hợp các ô + dải tiêu đề + dải ghi chú phủ ĐỦ 100% điểm mực ảnh gốc (mất = 0).
  3. Dải tiêu đề chung / ghi chú nguồn chung (chữ xám) KHÔNG chèn lại dạng ảnh;
     chữ của chúng được chép NGUYÊN VĂN vào chú thích / dòng Nguồn trong Docs.
     Bản pixels của hai dải vẫn giữ trong repo để truy vết.
Cỡ chữ hiệu dụng của ô khi hiển thị rộng D pt = glyph_px * D / w_o,
glyph_px suy từ eff_p90 đo ở khổ 450 pt của ảnh nguyên (legibility_metrics.json).
"""
import json
import os

import numpy as np
from PIL import Image

SRC = 'Air-Project-main/reports/figures/'
OUT = 'deliverables/layout_assets/panels/'
MET = 'deliverables/layout_assets/legibility_metrics.json'
INK = 230
MIN_GAP = 6
TARGET_PT = 9.5
MAX_W = 450.0

FIGS = {
    'hinh04': ('fill_strategies_lucknow_jaipur.png', 'Hình 4'),
    'hinh12': ('corr_01_raw_vs_adjusted.png', 'Hình 12'),
    'hinh14': ('corr_03_humidity_deciles.png', 'Hình 14'),
    'hinh17': ('model_01_residual_diagnostics.png', 'Hình 17'),
}


def zero_runs(v, minlen, lo, hi):
    out, s = [], None
    for i, x in enumerate(v):
        if x == 0:
            if s is None:
                s = i
        else:
            if s is not None and i - s >= minlen:
                out.append((s, i - 1))
            s = None
    if s is not None and len(v) - s >= minlen:
        out.append((s, len(v) - 1))
    return [(a, b) for a, b in out if a >= lo and b <= hi]


def col_cuts(region, W, gap=12):
    """Điểm cắt dọc: giữa các rãnh sạch mực >= gap px, mỗi mảnh >= 0.35W."""
    mids = [(a + b + 1) // 2 for a, b in zero_runs(region.sum(0), gap, int(0.02 * W), int(0.98 * W))]
    cuts = [0]
    for m in mids:
        if m - cuts[-1] >= 0.30 * W:
            cuts.append(m)
    tail = W - cuts[-1]
    if tail >= 0.30 * W:
        cuts.append(W)
    elif tail < 0.22 * W and len(cuts) > 2:
        cuts.pop()          # mảnh đuôi hẹp (vd thanh màu): ghép vào ô kề trái
        cuts.append(W)
    elif len(cuts) > 2:
        cuts.append(W)      # mảnh đuôi xấp xỉ 0.3W: chấp nhận
    else:
        cuts[-1] = W
    return cuts


def main():
    os.makedirs(OUT, exist_ok=True)
    p90 = {m['fig']: m['eff_p90'] for m in json.load(open(MET))}
    plan = {}
    for key, (fname, label) in FIGS.items():
        a = np.array(Image.open(SRC + fname).convert('L'))
        H, W = a.shape
        ink = a < INK
        total_ink = int(ink.sum())
        gray = (a >= 90) & (a < 215)
        row_ink = ink.sum(1)
        row_gray = gray.sum(1)
        # dải ghi chú nguồn: dải liền dưới cùng mà mọi hàng mực đều >=85% xám
        note_start = H
        y = H - 1
        while y > 0.60 * H:
            if row_ink[y] == 0 or row_ink[y] <= 24 or row_gray[y] >= 0.60 * row_ink[y]:
                note_start = y
                y -= 1
            else:
                break
        if note_start >= H - 4:
            note_start = H
        hruns = zero_runs(row_ink, MIN_GAP, 0, H - 1)
        # khớp mép dải ghi chú lên đầu rãnh trống kề trên (bỏ hàng anti-alias sót)
        for a0, b0 in hruns:
            if a0 > 0.55 * H and a0 <= note_start and b0 >= note_start - 3:
                note_start = a0
                break
        tops = [b0 for a0, b0 in hruns if b0 < 0.30 * H]
        title_end = (max(tops) + 1) if tops else 0
        # đường cắt dọc thử trên toàn vùng giữa tiêu đề và ghi chú
        vc = col_cuts(ink[title_end:note_start], W)
        inner = vc[1:-1]
        # tiêu đề dùng chung <=> có đường cắt dọc cắt qua mực của dải tiêu đề
        shared = title_end > 0 and any(ink[0:title_end, c - 2:c + 2].any() for c in inner)
        if not shared:
            title_end = 0
        reg = ink[title_end:note_start]
        # cắt hàng: CHỈ MỘT điểm cắt = rãnh ngang RỘNG NHẤT mà hai phía >= 30% cao vùng
        span = note_start - title_end
        best = None
        for a0, b0 in hruns:
            m = (a0 + b0 + 1) // 2
            if title_end + 20 < m < note_start - 20 and min(m - title_end, note_start - m) >= 0.30 * span:
                if best is None or (b0 - a0) > best[1]:
                    best = (m, b0 - a0)
        rcuts = [title_end] + ([best[0]] if best else []) + [note_start]
        rows = [(rcuts[i], rcuts[i + 1]) for i in range(len(rcuts) - 1) if rcuts[i + 1] - rcuts[i] > 40]
        pieces, strips = [], []
        if shared:
            strips.append(('tieu_de', (0, 0, W, title_end)))
        if note_start < H and ink[note_start:H].sum() > 0:
            strips.append(('ghi_chu', (0, note_start, W, H)))
        for r0, r1 in rows:
            cuts = col_cuts(ink[r0:r1], W)
            for c0, c1 in [(cuts[i], cuts[i + 1]) for i in range(len(cuts) - 1)]:
                box = (c0, r0, c1, r1)
                # chỉ đường cắt NỘI BỘ mới cần kiểm chứng sạch mực (±4 px)
                if 0 < c0 < W:
                    assert ink[r0:r1, c0 - 4:c0 + 4].sum() == 0, f'{fname}: cắt dọc {c0} bẩn'
                if 0 < c1 < W:
                    assert ink[r0:r1, c1 - 4:c1 + 4].sum() == 0, f'{fname}: cắt dọc {c1} bẩn'
                if title_end < r0 < note_start:
                    assert ink[r0 - 4:r0 + 4, c0:c1].sum() == 0, f'{fname}: cắt ngang {r0} bẩn'
                if title_end < r1 < note_start:
                    assert ink[r1 - 4:r1 + 4, c0:c1].sum() == 0, f'{fname}: cắt ngang {r1} bẩn'
                pieces.append(box)
        mask = np.zeros_like(ink)
        for x0, y0, x1, y1 in pieces + [b for _, b in strips]:
            mask[y0:y1, x0:x1] = True
        lost_mask = ink & ~mask
        lost = int(lost_mask.sum())
        if lost:
            ys, xs = np.where(lost_mask)
            print(f'    !! {fname}: mất {lost} mực tại x[{xs.min()},{xs.max()}] y[{ys.min()},{ys.max()}]')
        assert lost == 0, f'{fname}: mất {lost} điểm mực ngoài các ô/dải'
        glyph = p90[label] * W / 450.0
        items = []
        for i, (x0, y0, x1, y1) in enumerate(pieces):
            w, h = x1 - x0, y1 - y0
            d = min(MAX_W, max(TARGET_PT * w / glyph, 150.0))
            name = f'{key}_{chr(97 + i)}.png'
            Image.open(SRC + fname).crop((x0, y0, x1, y1)).save(OUT + name)
            items.append({'file': name, 'box': [x0, y0, x1, y1], 'w_px': w, 'h_px': h,
                          'display_pt': round(d, 1), 'height_pt': round(d * h / w, 1),
                          'eff_pt': round(glyph * d / w, 2)})
        for sname, (x0, y0, x1, y1) in strips:
            Image.open(SRC + fname).crop((x0, y0, x1, y1)).save(OUT + f'{key}_{sname}.png')
        plan[key] = {'src': fname, 'label': label, 'size': [W, H], 'glyph_px': round(glyph, 2),
                     'total_ink': total_ink, 'lost_ink': 0, 'shared_title': bool(shared),
                     'pieces': items, 'strips': [s for s, _ in strips]}
        print(f'{label} {fname} {W}x{H} glyph={glyph:.1f}px tiêu đề chung={shared} '
              f'ô={len(items)} dải={len(strips)} mất_mực=0')
        for it in items:
            print(f'    {it["file"]}: {it["w_px"]}x{it["h_px"]}px -> {it["display_pt"]}x{it["height_pt"]}pt, chữ {it["eff_pt"]}pt')
    json.dump(plan, open(OUT + 'plan.json', 'w'), ensure_ascii=False, indent=1)
    print('kế hoạch:', OUT + 'plan.json')


if __name__ == '__main__':
    main()
