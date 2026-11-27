#!/usr/bin/env python3
"""Reproduce exact-area screening of public Shenzhen food sampling notices.
Not a census or proof of current trade; only download official published attachments.
Requires openpyxl for reading published xlsx. No private data or login.
"""
import csv, hashlib, html, io, json, re, subprocess, pathlib, concurrent.futures
from urllib.parse import urljoin
from openpyxl import load_workbook
BASE="https://amr.sz.gov.cn/xxgk/qt/ztlm/spaqjg1/spaqcj/cyjytg/index.html"
OUT=pathlib.Path(__file__).resolve().parents[1]/"evidence"
ACCESS_DATE="2026-11-27"
def get(u):
    r=subprocess.run(["curl","-L","-f","-sS","--max-time","30",u],capture_output=True)
    if r.returncode: raise OSError(r.stderr.decode(errors="replace")[:300])
    return r.stdout
def anchors(content, base):
    s=content.decode("utf-8",errors="replace")
    for m in re.finditer(r'<a\b[^>]*?href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',s,re.S|re.I):
        t=html.unescape(re.sub(r'<[^>]*>','',m[2])).strip()
        yield t,urljoin(base,html.unescape(m[1]))
def find_notices():
    out=[]
    for title,url in anchors(get(BASE),BASE):
        if not "食品安全抽样检验情况通告" in title: continue
        date=(re.search(r"\d{4}-\d{2}-\d{2}",title) or [None])[0]
        if date and date >= "2025-07-01" and not any(w in title for w in ("月饼专项","保健食品专项")):
            out.append((title,url,date))
    return out
def read_notice(n):
    title,url,date=n
    audit=dict(notice_title=title,notice_url=url,notice_date=date,access_date=ACCESS_DATE)
    try:
        a=[(t,u) for t,u in anchors(get(url),url) if re.search(r"\.xlsx(?:\?|$)",u,re.I) and ("明细表" in t or "附件" in t or "合格" in t)]
        if not a: raise RuntimeError("no XLSX detail link")
        allrows=[]; audits=[]
        for label,attach in a:
            try:
                body=get(attach)
                audit2={**audit,"attachment_label":label,"attachment_url":attach,"sha256":hashlib.sha256(body).hexdigest()}
                wb=load_workbook(io.BytesIO(body),read_only=True,data_only=True)
                total=0; found=[]
                for sh in wb:
                    header_row=None; addr_i=None; name_i=None
                    for i,row in enumerate(sh.iter_rows(values_only=True),1):
                        vals=[str(v or "").strip() for v in row]
                        if not header_row:
                            if any("受检单位" in s for s in vals) and any("地址" in s for s in vals) or (any("被抽样" in s for s in vals) and any("地址" in s for s in vals)):
                                header_row=i
                                addr_i=next((j for j,s in enumerate(vals) if "地址" in s and any(w in s for w in ("受检","被抽样","抽检","经营"))),None)
                                name_i=next((j for j,s in enumerate(vals) if ("受检" in s or "被抽样" in s) and "名称" in s),None)
                                if addr_i is None or name_i is None: header_row=None; continue
                                cols=vals
                            continue
                        if addr_i>=len(vals) or name_i>=len(vals): continue
                        addr=vals[addr_i]; name=vals[name_i]
                        if not name or not addr: continue
                        total+=1
                        if not ("新和社区" in addr or re.search(r"新和[一二三四五六七八九123456789]区",addr)) or not any(w in addr for w in ("宝安","福海","福永")): continue
                        # Not part of this commercial competitor study: any child/school site record.
                        if any(w in name for w in ("幼儿园","托儿所","小学","中学","学校","托育")): continue
                        # A public source may identify individual stall owners in parentheses.
                        # Keep business names and source locator; omit personal suffixes from deliverable.
                        if not name.startswith("深圳") and "（" in name:
                            name=name.split("（",1)[0]
                        def val(pred):
                            return next((vals[j] for j,s in enumerate(cols) if pred(s) and j<len(vals)), "")
                        rowout=dict(notice_date=date,notice_url=url,attachment_url=attach,workbook_sha256=audit2["sha256"],sheet=sh.title,row=i,entity_name=name,address=addr,item=val(lambda s:("样品名称" in s or "食品名称" in s)),item_date_field=val(lambda s:("生产日期" in s or "购进日期" in s or "批号" in s)),result=val(lambda s:"检验结果" in s or "抽样结果" in s),food_class=val(lambda s:"食品分类" in s),source_id=f"REG-{date}-{i}",access_date=ACCESS_DATE)
                        found.append(rowout)
                wb.close()
                audit2.update(scanned_rows=total,matched_rows=len(found),status="read" if total else "header_unrecognized")
                audits.append(audit2);allrows += found
            except Exception as exc:
                audits.append({**audit,"attachment_url":attach,"status":"failed","error":str(exc)[:200]})
        return allrows,audits
    except Exception as exc:
        return [],[{**audit,"status":"failed","error":str(exc)[:200]}]
def main():
    notices=find_notices()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool: results=list(pool.map(read_notice,notices))
    rows=[r for rr,_ in results for r in rr]; audits=[a for _,aa in results for a in aa]
    if rows:
        p=OUT/"foodcheck_v4.csv"
        with p.open("w",encoding="utf-8-sig",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader();w.writerows(rows)
    (OUT/"foodcheck_source_audit_v4.json").write_text(json.dumps(audits,ensure_ascii=False,indent=2),encoding="utf-8")
    print("notices",len(notices),"read",sum(a.get("status")=="read" for a in audits),"rows",len(rows),"distinct businesses",len(set(r["entity_name"] for r in rows)))
    for r in rows: print(r["notice_date"],r["entity_name"],r["address"],r["item"],r["item_date_field"],r["result"])
if __name__=="__main__":main()
