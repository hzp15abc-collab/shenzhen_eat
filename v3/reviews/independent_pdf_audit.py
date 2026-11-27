#!/usr/bin/env python3
"""Render every page at three phone widths and check text and navigation; output under scratch only."""
import fitz, json, sys, collections, math, re
from pathlib import Path
from PIL import Image,ImageDraw
fp=Path(sys.argv[1]); out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
d=fitz.open(fp)
metrics=[]
for i,p in enumerate(d,1):
    spans=[s for b in p.get_text('dict',flags=fitz.TEXTFLAGS_DICT & ~fitz.TEXT_PRESERVE_IMAGES)['blocks'] if b['type']==0 for l in b['lines'] for s in l['spans'] if s['text'].strip()]
    lines=[l for b in p.get_text('dict',flags=fitz.TEXTFLAGS_DICT & ~fitz.TEXT_PRESERVE_IMAGES)['blocks'] if b['type']==0 for l in b['lines']]
    bad=[]
    for s in spans:
        x0,y0,x1,y1=s['bbox']
        if x0<-.5 or y0<-.5 or x1>p.rect.width+.5 or y1>p.rect.height+.5:
            bad.append((s['text'],s['bbox']))
    badlinks=[x for x in p.get_links() if x['kind']==fitz.LINK_GOTO and not 0<=x.get('page',-1)<len(d)]
    x=p.get_text()
    metrics.append(dict(page=i,page_size=[p.rect.width,p.rect.height],chars=len(x),spans=len(spans),size_min=min([s['size'] for s in spans],default=0),size_median=sorted([s['size'] for s in spans] or [0])[len(spans)//2],replacement=x.count('\ufffd'),overflow=len(bad),overflow_items=bad,links=len(p.get_links()),badlinks=len(badlinks),text_head=x[:180]))
    for w in (360,390,430):
        pix=p.get_pixmap(matrix=fitz.Matrix(w/p.rect.width,w/p.rect.width),alpha=False)
        pix.save(str(out/f'{i:03}_{w}.png'))
for start in range(1,len(d)+1,12):
    stop=min(len(d)+1,start+12)
    cw=185;ch=410
    sheet=Image.new('RGB',(cw*4,ch*math.ceil((stop-start)/4)), '#dedede')
    draw=ImageDraw.Draw(sheet)
    for j,i in enumerate(range(start,stop)):
        im=Image.open(out/f'{i:03}_390.png').convert('RGB');im.thumbnail((cw-8,ch-22))
        x=(j%4)*cw+(cw-im.width)//2;y=(j//4)*ch+18
        sheet.paste(im,(x,y));draw.text((x,y-14),f'p{i}',fill='black')
    sheet.save(out/f'contact_{start:03}-{stop-1:03}.jpg',quality=87)
summary=dict(filename=fp.name,pages=len(d),dimensions=list({tuple(m['page_size']) for m in metrics}),pages_with_links=sum(m['links']>0 for m in metrics),links=sum(m['links'] for m in metrics),broken_links=sum(m['badlinks'] for m in metrics),bookmarks=d.get_toc(),replacement=sum(m['replacement'] for m in metrics),overflow=sum(m['overflow'] for m in metrics),pages_rendered=3*len(d),metrics=metrics)
(out/'metrics.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
for k in ['filename','pages','dimensions','pages_with_links','links','broken_links','bookmarks','replacement','overflow','pages_rendered']:
    print(k,summary[k])
print('page text summary')
for m in metrics: print(m['page'],round(m['size_median'],1),m['chars'],m['links'],m['overflow'],m['replacement'],m['text_head'].replace('\n',' / ')[:95])
