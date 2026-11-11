"""V25 [Q08] kiểm kê hình/tài liệu nộp; V26 [Q09] đối chiếu checklist BA. Chỉ kiểm kê sự tồn tại và đếm; không đánh giá chất lượng trình bày.
Chạy: python v25_docs.py
"""
from da_common import *
import re, json, glob
from PIL import Image
REPO = ROOT.parent
rows = []
for p in sorted((ROOT / "reports" / "figures").glob("*.png")):
    im = Image.open(p); dpi = im.info.get("dpi"); rows.append({"file": p.name, "kB": round(p.stat().st_size / 1024, 1), "rong_px": im.size[0], "cao_px": im.size[1], "dpi": round(dpi[0]) if dpi else None,
                                                             "nhom": p.name.split("_")[0], "<500kB": p.stat().st_size < 500 * 1024, "dpi==150": bool(dpi and round(dpi[0]) == 150)})
F = pd.DataFrame(rows); save(F, "V25_figures_inventory.csv", index=False); print(F.to_string()); print(F.groupby("nhom").size().to_dict())
exp = [f"eda_0{i}_" for i in range(6)] + [f"corr_0{i}_" for i in range(1, 5)] + [f"model_0{i}_" for i in range(1, 6)]
print("15 hình checklist yêu cầu, có đủ:", {e: bool(F.file.str.startswith(e).any()) for e in exp})
# tài liệu nộp
allf = [str(p.relative_to(REPO)) for p in REPO.rglob("*") if p.is_file() and ".git/" not in str(p) and "/ra/evidence/" not in str(p)]
kinds = {"pdf": [f for f in allf if f.lower().endswith(".pdf")], "pptx/slide": [f for f in allf if re.search(r"\.(pptx?|key)$|slide", f, re.I)], "docx": [f for f in allf if f.lower().endswith((".docx", ".doc"))],
         "bao_cao (*report*/*bao_cao*.md)": [f for f in allf if re.search(r"bao.?cao|report", f.split("/")[-1], re.I)], "bien_ban/van_dap": [f for f in allf if re.search(r"bien.?ban|van.?dap|qa|defen", f.split("/")[-1], re.I)],
         "LICENSE": [f for f in allf if re.search(r"licen[sc]e", f, re.I)], "ngữ cảnh.txt": [f for f in allf if "ngữ cảnh" in f or "ngu_canh" in f.lower()]}
txt = {f: open(REPO / f, encoding="utf-8", errors="ignore").read() for f in allf if f.lower().endswith((".md", ".json", ".txt"))}
nbt = {}
for p in sorted((ROOT / "notebooks").glob("*.ipynb")):
    nb = json.load(open(p)); nbt[str(p.relative_to(REPO))] = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "markdown")
def where(pat, pool): return {f: len(re.findall(pat, t, re.I)) for f, t in pool.items() if re.search(pat, t, re.I)}
doc = [{"muc": k, "so_file": len(v), "file": "; ".join(v[:8])} for k, v in kinds.items()]
for nm, pat in [("quyền riêng tư / privacy", r"quyền riêng tư|privacy|dữ liệu cá nhân"), ("thiên lệch / bias", r"thiên lệch|\bbias\b|thiên kiến"), ("khai báo dùng AI", r"khai báo.{0,20}AI|sử dụng AI|ChatGPT|Claude|Copilot|trợ lý AI|AI assist"),
                ("giấy phép / CC BY", r"CC BY|giấy phép|license"), ("ngày truy cập", r"ngày truy cập|truy cập ngày|accessed"), ("URL nguồn Kaggle/CPCB", r"kaggle\.com|cpcb\.nic\.in"), ("tài liệu tham khảo / bibliography", r"tài liệu tham khảo|references|bibliograph"),
                ("notebook 07", r"notebook 07|07_"), ("production / triển khai thật", r"production|triển khai thật|thời gian thực")]:
    a = where(pat, {k: v for k, v in txt.items() if "/ra/" not in k and "CHECKLIST" not in k and "BAN_GIAO" not in k}); b = where(pat, nbt)
    doc.append({"muc": f"chuỗi '{nm}'", "so_file": len(a) + len(b), "file": "; ".join(f"{k.split('/')[-1]}({v})" for k, v in {**a, **b}.items())[:400]})
D = pd.DataFrame(doc); save(D, "V25_documents_inventory.csv", index=False); pd.set_option("display.max_colwidth", 200); pd.set_option("display.width", 300); print(D.to_string())
print("notebooks/archive:", sorted(p.name for p in (ROOT / "notebooks" / "archive").glob("*")) if (ROOT / "notebooks" / "archive").exists() else None)

# ---------- V26 checklist
ck = open(REPO / "CHECKLIST_KIEM_CHUNG.md", encoding="utf-8").read(); bg = open(REPO / "BAN_GIAO_BA-RA.md", encoding="utf-8").read()
ids = re.findall(r"\*\*(CK-\d+\.\d+)\*\*", ck); uid = sorted(set(ids), key=lambda s: tuple(map(int, s[3:].split("."))))
per = pd.Series([i.split("-")[1].split(".")[0] for i in uid]).value_counts().sort_index().to_dict()
lv = {}
for m in re.finditer(r"^\| \*\*(CK-\d+\.\d+)\*\*.*$", ck, re.M):
    cells = [x.strip() for x in m.group(0).strip("|").split("|")]; lvl = [x for x in cells if x in ("B", "K")]; lv[m.group(1)] = lvl[0] if lvl else "?"
lvs = pd.Series(lv); bk = pd.crosstab(lvs.index.str.extract(r"CK-(\d+)")[0].values, lvs.values)
r = [{"muc": "số ID CK duy nhất trong CHECKLIST", "gia_tri": len(uid), "chi_tiet": str(per)}, {"muc": "B/K theo phần", "gia_tri": "", "chi_tiet": bk.to_dict()},
     {"muc": "BAN_GIAO nói số tiêu chí", "gia_tri": "; ".join(sorted(set(re.findall(r"\b\d{2}\s*(?:tiêu chí|ID|mục kiểm|mã)", bg)))), "chi_tiet": ""},
     {"muc": "CHECKLIST tự nói số tiêu chí", "gia_tri": "; ".join(sorted(set(re.findall(r"\b\d{2}\s*(?:tiêu chí|ID|mục kiểm|mã)", ck)))), "chi_tiet": ""},
     {"muc": "chuỗi '2069' / '2.069' trong CHECKLIST", "gia_tri": len(re.findall(r"2\.?069", ck)), "chi_tiet": " | ".join(x.strip()[:160] for x in re.findall(r"[^\n|]*2\.?069[^\n|]*", ck)[:3])},
     {"muc": "chuỗi '2169' / '2.169' trong CHECKLIST", "gia_tri": len(re.findall(r"2\.?169", ck)), "chi_tiet": ""},
     {"muc": "CK-5.3 '3 cặp'", "gia_tri": "", "chi_tiet": " | ".join(x.strip()[:300] for x in re.findall(r"[^\n]*CK-5\.3[^\n]*", ck)[:1])},
     {"muc": "CK-3.7 '3 cặp hay đổi chỗ'", "gia_tri": "", "chi_tiet": " | ".join(x.strip()[:200] for x in re.findall(r"3 cặp[^|\n]*", ck)[:3])},
     {"muc": "Ngưỡng đạt P3 (dòng công thức)", "gia_tri": "", "chi_tiet": " | ".join(x.strip()[:200] for x in re.findall(r"PASS \d+/\d+ B[^\n]*", ck)[:6])},
     {"muc": "CK-3.8 nói Bonferroni cho", "gia_tri": "", "chi_tiet": " | ".join(re.findall(r"Bonferroni cho \d+ tests", ck))},
     {"muc": "MAR/MNAR trong CHECKLIST", "gia_tri": len(re.findall(r"MAR|MNAR|MCAR", ck)), "chi_tiet": " | ".join(x.strip()[:200] for x in re.findall(r"[^|\n]*(?:MNAR|MCAR)[^|\n]*", ck)[:2])},
     {"muc": "đường dẫn hoa/thường: file thật", "gia_tri": "", "chi_tiet": str(sorted(p.name for p in ROOT.glob("*") if p.is_file()))},
     {"muc": "đường dẫn CHECKLIST nhắc 'requirements.txt' (thường) / 'Requirements.txt'", "gia_tri": f"{len(re.findall('requirements.txt', ck))}/{len(re.findall('Requirements.txt', ck))}", "chi_tiet": f"data_dictionary.md {len(re.findall('data_dictionary.md', ck))} / Data_dictionary.md {len(re.findall('Data_dictionary.md', ck))}; metadata.json {len(re.findall('metadata.json', ck))} / Metadata.json {len(re.findall('Metadata.json', ck))}"},
     {"muc": "Branch ghi trong CHECKLIST", "gia_tri": "; ".join(re.findall(r"arena/[0-9a-f]+-[\w-]+", ck)[:2]), "chi_tiet": "nhánh DA đang chạy: arena/b5aacef3-air-project-test"}]
K = pd.DataFrame(r); save(K, "V26_checklist_crosscheck.csv", index=False); print(K.to_string())
print("ID thuộc P3:", [i for i in uid if i.startswith("CK-3.")]); print("ID trùng:", [i for i in set(ids) if ids.count(i) > 1][:10])
