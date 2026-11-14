"""Dựng bản đồ chỉ số UTF-16 của Google Docs từ bản xuất .docx.
Cách dùng: python3 mkwalk.py <docx> <out.json>
Mô hình chỉ số (đã kiểm chứng khớp 11/11 bảng và model_end):
  đoạn văn P : len = u16(text) + số_ảnh_inline + số_break + 1 (ký tự xuống dòng)
  bảng   TBL : len = 1 + Σ u16(ô) + 2·số_ô + số_dòng + 1
Chỉ số bắt đầu từ 1 (body). CHỈ dùng để định vị; trước mỗi lần sửa vẫn phải find_text lại.
"""
import sys,re,json,zipfile
def u16(s): return len(s.encode('utf-16-le'))//2
def unesc(t):
    return (t.replace('&amp;','&').replace('&lt;','<').replace('&gt;','>')
             .replace('&quot;','"').replace('&apos;',"'"))
docx,out=sys.argv[1],sys.argv[2]
xml=zipfile.ZipFile(docx).read('word/document.xml').decode('utf-8')
body=xml[xml.find('<w:body>')+8:xml.rfind('</w:body>')]
blocks=re.findall(r'<w:tbl>.*?</w:tbl>|<w:p [^>]*>.*?</w:p>|<w:p/>',body,re.S)
res=[];idx=1
STYLE={'Heading1':'Heading1','Heading2':'Heading2','Heading3':'Heading3','Heading4':'Heading4','Title':'Title','Subtitle':'Subtitle'}
for b in blocks:
    if b.startswith('<w:tbl'):
        rows=re.findall(r'<w:tr[ >].*?</w:tr>',b,re.S)
        cells=[[ unesc(''.join(re.findall(r'<w:t(?: [^>]*)?>(.*?)</w:t>',c,re.S))) for c in re.findall(r'<w:tc>.*?</w:tc>',r,re.S)] for r in rows]
        flat=[c for r in cells for c in r]
        L=1+sum(u16(c) for c in flat)+2*len(flat)+len(cells)+1
        res.append({'k':len(res),'t':'TBL','start':idx,'len':L,'cells':cells}); idx+=L
    else:
        t=''.join(re.findall(r'<w:t(?: [^>]*)?>(.*?)</w:t>',b,re.S))
        t=unesc(t)
        draw=len(re.findall(r'<wp:docPr ',b))
        brk=len(re.findall(r'<w:br w:type="page"/>',b))+len(re.findall(r'<w:sectPr[ >]',b))
        st=re.search(r'<w:pStyle w:val="([^"]+)"',b)
        raw=st.group(1) if st else 'Normal'
        style=STYLE.get(raw,raw)
        L=u16(t)+draw+brk+1
        res.append({'k':len(res),'t':'P','start':idx,'len':L,'style':style,'draw':draw,'brk':brk,'text':t}); idx+=L
json.dump(res,open(out,'w'),ensure_ascii=False)
print('elements',len(res),'model_end',idx-1,'tables',sum(1 for r in res if r['t']=='TBL'),'images',sum(r.get('draw',0) for r in res))
