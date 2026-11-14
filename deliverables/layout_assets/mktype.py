"""Đo typography theo chỉ số Google Docs, dựng từ bản xuất .docx.
Cách dùng: python3 mktype.py <docx> <out.json>

Mỗi phần tử (đoạn P / bảng TBL) mang cùng mô hình chỉ số như mkwalk.py,
kèm thông tin trình bày đo được từ run thật (không suy từ style):
  sizes   : danh sách cỡ chữ (pt) xuất hiện trong các run có chữ của phần tử
  fonts   : danh sách họ chữ
  bold/italic/align/line/spacing : định dạng đoạn
  runs    : số run có chữ
Mục đích: lập kế hoạch đổi cỡ chữ theo khoảng chỉ số liên tục, tránh áp
mù một cỡ lên bìa/heading/đoạn đệm.
"""
import sys, re, json, zipfile


def u16(s):
    return len(s.encode('utf-16-le')) // 2


def unesc(t):
    return (t.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
             .replace('&quot;', '"').replace('&apos;', "'"))


def half_to_pt(v):
    return round(float(v) / 2, 2)


def para_info(b):
    """Trích thông tin trình bày của một đoạn <w:p>."""
    ppr_m = re.search(r'<w:pPr>(.*?)</w:pPr>', b, re.S)
    ppr = ppr_m.group(1) if ppr_m else ''
    style_m = re.search(r'<w:pStyle w:val="([^"]+)"', ppr)
    style = style_m.group(1) if style_m else 'Normal'
    align_m = re.search(r'<w:jc w:val="([^"]+)"', ppr)
    align = align_m.group(1) if align_m else ''
    line_m = re.search(r'<w:spacing[^>]*w:line="(\d+)"', ppr)
    line = int(line_m.group(1)) if line_m else None
    rule_m = re.search(r'<w:spacing[^>]*w:lineRule="([^"]+)"', ppr)
    rule = rule_m.group(1) if rule_m else ''
    keep = '<w:keepNext w:val="1"/>' in ppr
    # cỡ chữ/họ chữ thật của các run có chữ
    sizes, fonts, bold, italic = [], [], 0, 0
    for r in re.findall(r'<w:r[ >].*?</w:r>', b, re.S):
        if not re.search(r'<w:t(?: [^>]*)?>', r):
            continue
        rpr_m = re.search(r'<w:rPr>(.*?)</w:rPr>', r, re.S)
        rpr = rpr_m.group(1) if rpr_m else ''
        sz = re.search(r'<w:sz w:val="([\d.]+)"', rpr)
        if sz:
            sizes.append(half_to_pt(sz.group(1)))
        f = re.search(r'<w:rFonts[^>]*w:ascii="([^"]+)"', rpr)
        if f:
            fonts.append(f.group(1))
        if '<w:b/>' in rpr or '<w:b w:val="1"/>' in rpr:
            bold += 1
        if '<w:i/>' in rpr or '<w:i w:val="1"/>' in rpr:
            italic += 1
    text = unesc(''.join(re.findall(r'<w:t(?: [^>]*)?>(.*?)</w:t>', b, re.S)))
    return {
        'style': style, 'align': align, 'line': line, 'rule': rule, 'keep': keep,
        'sizes': sorted(set(sizes)), 'fonts': sorted(set(fonts)),
        'bold': bold, 'italic': italic, 'text': text,
    }


def main():
    docx, out = sys.argv[1], sys.argv[2]
    xml = zipfile.ZipFile(docx).read('word/document.xml').decode('utf-8')
    body = xml[xml.find('<w:body>') + 8:xml.rfind('</w:body>')]
    blocks = re.findall(r'<w:tbl>.*?</w:tbl>|<w:p [^>]*>.*?</w:p>|<w:p/>', body, re.S)
    res, idx = [], 1
    for b in blocks:
        if b.startswith('<w:tbl'):
            rows = re.findall(r'<w:tr[ >].*?</w:tr>', b, re.S)
            cells, cell_sizes = [], []
            for r in rows:
                row_txt, row_sz = [], []
                for c in re.findall(r'<w:tc>.*?</w:tc>', r, re.S):
                    t = unesc(''.join(re.findall(r'<w:t(?: [^>]*)?>(.*?)</w:t>', c, re.S)))
                    row_txt.append(t)
                    for sz in re.findall(r'<w:sz w:val="([\d.]+)"', c):
                        row_sz.append(half_to_pt(sz))
                cells.append(row_txt)
                cell_sizes.append(row_sz)
            flat = [c for r in cells for c in r]
            allsz = sorted({s for r in cell_sizes for s in r})
            L = 1 + sum(u16(c) for c in flat) + 2 * len(flat) + len(cells) + 1
            res.append({'k': len(res), 't': 'TBL', 'start': idx, 'len': L,
                        'rows': len(cells), 'cols': len(cells[0]) if cells else 0,
                        'sizes': allsz, 'cells': cells})
            idx += L
        else:
            info = para_info(b)
            draw = len(re.findall(r'<wp:docPr ', b))
            brk = len(re.findall(r'<w:br w:type="page"/>', b)) + len(re.findall(r'<w:sectPr[ >]', b))
            L = u16(info['text']) + draw + brk + 1
            res.append({'k': len(res), 't': 'P', 'start': idx, 'len': L,
                        'draw': draw, 'brk': brk, **info})
            idx += L
    json.dump(res, open(out, 'w'), ensure_ascii=False)
    print('elements', len(res), 'model_end', idx - 1)


if __name__ == '__main__':
    main()
