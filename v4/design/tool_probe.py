"""Actual capability probes: same Chinese title/math and a shape through ReportLab,
Pillow raster, fitz prototype. Browser attempt is also recorded by shell.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import fitz
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import json,subprocess,shutil
OUT=Path(__file__).resolve().parents[1]/'prototypes'
t='开业资金14.15万元：付款及占用11.72万，\n备用2.43万。模拟净收入32,860元。'
# ReportLab CID font (unembedded). Compare rendering and extraction.
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
p=OUT/'tool_reportlab_probe.pdf';c=Canvas(str(p),pagesize=(390,180));c.setFillColorRGB(.95,.95,.92);c.rect(0,0,390,180,fill=1,stroke=0);c.setFillColorRGB(.15,.22,.24);c.setFont('STSong-Light',18)
for i,line in enumerate(t.splitlines()):c.drawString(20,130-i*30,line)
c.setFillColorRGB(.2,.4,.5);c.rect(20,40,320,20,fill=1,stroke=0);c.showPage();c.save()
d=fitz.open(p);d[0].get_pixmap().save(OUT/'tool_reportlab_probe.png');report_extract=d[0].get_text()
# Pillow has sharp raster at 3x but assembled as PDF loses searchable text.
p2=OUT/'tool_pillow_probe.pdf';im=Image.new('RGB',(1170,540),'#f5f2ea');dr=ImageDraw.Draw(im);f=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',48,index=2)
dr.multiline_text((60,100),t,font=f,fill='#1b343a',spacing=12);dr.rectangle((60,360,1020,420),fill='#366575');im.save(p2,resolution=216.0);im.resize((390,180)).save(OUT/'tool_pillow_probe.png');pil_extract=fitz.open(p2)[0].get_text()
# Browser printing capability check (no install).
r=subprocess.run(['chromium','--version'],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=15) if shutil.which('chromium') else None
# fitz actual final candidate extraction, font and photo source links
p3=OUT/'style_flow.pdf';doc=fitz.open(p3);tot=sum(len(p.get_text()) for p in doc)
results={'reportlab':{'text':report_extract,'extractable':bool(report_extract),'fonts':d[0].get_fonts()},'pillow':{'extractable':bool(pil_extract),'raster':'1170x540'},'chromium':{'found':r is not None,'returncode':r.returncode if r else None,'stdout':r.stdout if r else '', 'stderr':r.stderr if r else ''},'fitz':{'pdf_pages':len(doc),'extractable_characters':tot,'fonts':doc[0].get_fonts(),'links':len(doc[0].get_links())}}
(OUT/'tool_probe_results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print(json.dumps(results,ensure_ascii=False,indent=2))
