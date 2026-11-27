#!/usr/bin/env python3
"""Independent V2 mobile PDF inspection: native PDF links/text, fit-width span font sizes, screenshots."""
import sys, os, math, json, statistics
from pathlib import Path
from collections import Counter
import fitz
from PIL import Image, ImageOps, ImageDraw
def inspect(path, outdir):
    p=fitz.open(path)
    outdir=Path(outdir); outdir.mkdir(parents=True,exist_ok=True)
    report={"file":str(path),"page_count":len(p),"page_dimensions_pt":[],"internal_links":0,"external_links":0,
            "invalid_internal_link_destinations":[],"total_chars":0,"pages":[],"out_of_bounds_spans":[]}
    for n,page in enumerate(p):
        number=n+1; wr=page.rect.width; hr=page.rect.height
        dims=[round(wr,2),round(hr,2)]
        if dims not in report['page_dimensions_pt']: report['page_dimensions_pt'].append(dims)
        all_spans=[sp for b in page.get_text("dict")["blocks"] if b["type"]==0 for l in b["lines"] for sp in l["spans"] if sp["text"].strip()]
        txt=page.get_text().strip(); report["total_chars"]+=len(txt)
        report["internal_links"]+=sum(l["kind"]==fitz.LINK_GOTO for l in page.get_links())
        report["external_links"]+=sum(l["kind"]==fitz.LINK_URI for l in page.get_links())
        for l in page.get_links():
            if l["kind"]==fitz.LINK_GOTO and not 0<=l.get("page",-1)<len(p): report["invalid_internal_link_destinations"].append([number,l.get("page")])
        for sp in all_spans:
            x0,y0,x1,y1=sp["bbox"]
            if min(x0,y0)<-1 or x1>wr+1 or y1>hr+1:
                report["out_of_bounds_spans"].append([number,sp["text"][:100],[round(v,2) for v in sp["bbox"]]])
        sz=[(sp["size"],len(sp["text"].strip())) for sp in all_spans]
        def weighted_median(vals):
            vals=[s for s,count in vals for x in range(count)]
            return statistics.median(vals) if vals else 0
        entry={'page':number,'ratio_w_h':round(wr/hr,3),'chars':len(txt),'title_preview':txt[:100].replace('\n',' / '),
               'fit_font_char_weighted_median_px':{q:round(weighted_median(sz)*q/wr,2) for q in [360,390,430]},
               'fit_font_chars_under_13_px_360':sum(count for size,count in sz if size*360/wr<13),
               'image_count':len(page.get_images(full=True)),'link_count':len(page.get_links())}
        report["pages"].append(entry)
        for q in (360,390,430):
            target=outdir/f"width{q}"; target.mkdir(exist_ok=True)
            pix=page.get_pixmap(matrix=fitz.Matrix(q/wr,q/wr),alpha=False)
            pix.save(str(target/f"p{number:03d}.png"))
    for q in (360,390,430):
        files=list(sorted((outdir/f"width{q}").glob("*.png")))
        # 4x4 contact sheets at quarter-resolution, used for structural visual review, not font readability
        for start in range(0,len(files),16):
            chunk=files[start:start+16]; thumb_width=180; thumb_height=400
            sheet=Image.new("RGB",(4*thumb_width,4*(thumb_height+25)),(240,240,240))
            draw=ImageDraw.Draw(sheet)
            for idx,fp in enumerate(chunk):
                im=Image.open(fp).convert("RGB")
                im.thumbnail((thumb_width-8,thumb_height-8))
                x=(idx%4)*thumb_width+(thumb_width-im.width)//2; y=(idx//4)*(thumb_height+25)
                sheet.paste(im,(x,y)); draw.text(((idx%4)*thumb_width+5,y+thumb_height),fp.stem,fill="black")
            sheet.save(outdir/f"contact_{q}_{start//16+1:02d}.png")
    (outdir/"inspection.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(f"{len(p)} pages; dimensions {report['page_dimensions_pt']}; internal {report['internal_links']}; external {report['external_links']}; out of bounds {len(report['out_of_bounds_spans'])}; char count {report['total_chars']}")
    for page in report["pages"]:
        print(page["page"],page["fit_font_char_weighted_median_px"],page["fit_font_chars_under_13_px_360"],page["image_count"],page["title_preview"][:55])
    return report
if __name__=="__main__":
    if len(sys.argv)<3:
        raise SystemExit("usage: check_v2_pdf.py PDF OUTPUTDIR")
    inspect(*sys.argv[1:3])
