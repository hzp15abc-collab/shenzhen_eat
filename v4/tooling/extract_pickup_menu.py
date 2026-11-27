#!/usr/bin/env python3
"""Extract public price observer tables; not a customer's verified transaction.
Direct menu body date instead of dynamic footer/search snippet. Uses official
public webpage inputs from user-approved sources; no login/API probing.
"""
import csv,hashlib,html,re,subprocess,pathlib,json
OUT=pathlib.Path(__file__).resolve().parents[1]/"evidence"
SOURCES=[
("KFC-XINHE","肯德基（新和桥新路门店）","新和社区桥新路商业带","本社区（非三区）","https://drivethruindex.com/restaurants/cn/gd/%E6%B7%B1%E5%9C%B3/kfc-SZ2103"),
("PH-QIAOTOU","必胜客（桥头永福路门店）","福海街道桥头社区永福路120号","相邻社区","https://drivethruindex.com/restaurants/cn/gd/%E6%B7%B1%E5%9C%B3/pizza-hut-GZ5650"),
]
def parse(s):
    t=s.decode("utf-8")
    m=re.search(r"Full menu with prices \((\d+) items\)</h2>\s*<p[^>]*>(.*?)</p>\s*<div[^>]*><table>(.*?)</table>",t,re.S)
    if not m:raise RuntimeError("menu section not found")
    markdown=re.sub(r"<[^>]*>","",m.group(2))
    date=re.search(r"checked (\d{4}-\d{2}-\d{2})", markdown)[1]
    rows=[]; group=""
    for row in re.findall(r"<tr(?:\s[^>]*)?>(.*?)</tr>",m.group(3),re.S):
        a=re.search(r'<th colspan="2">(.*?)</th>',row,re.S)
        if a:
            group=html.unescape(re.sub(r"<[^>]*>","",a[1])).strip();continue
        td=re.findall(r"<td(?:\s[^>]*)?>(.*?)</td>",row,re.S)
        if len(td)!=2:continue
        name,price=(html.unescape(re.sub(r"<[^>]*>","",x)).strip() for x in td)
        match=re.fullmatch(r"¥([\d.]+)",price)
        if match: rows.append((group,name,match.group(1)))
    assert len(rows)==int(m[1]),(len(rows),m[1])
    return rows,date
def main():
    items=[]; audits=[]
    for id,name,zone,relevance,url in SOURCES:
        r=subprocess.run(["curl","-L","-f","-sS","--max-time","30",url],capture_output=True,check=True)
        body=r.stdout
        rows,date=parse(body)
        audit=dict(source_id=id,source_url=url,menu_body_date=date,access_date="2026-11-27",count=len(rows),sha256=hashlib.sha256(body).hexdigest(),source_type="第三方价格观测者称来自品牌App自提价",limits="不是餐厅直接确认、外卖配送价、消费小票、早餐菜单、顾客订单均价或销量")
        audits.append(audit)
        for i,(category,product,price) in enumerate(rows,1):
            items.append(dict(id=f"{id}-{i:03d}",store=name,zone=zone,geographic_scope=relevance,product_category=category,product=product,price_rmb=price,price_kind="品牌App自提标价（第三方记录）",data_date=date,access_date="2026-11-27",source_url=url,source_id=id,evidence="B:第三方明示采价口径，非本人订单",model_use="仅作替代品级别对照，不用作平均客单或平台佣金"))
    # Local single third-party reported meal (in V3 as well, not new V4).
    trip="https://hk.trip.com/moments/detail/bao-an-district-2015100-156845124/"
    for i,(name,price) in enumerate([("烟熏鸡胸法棍加太阳蛋",21),("蒜香黄油烤片",3),("越南爆汁鸡腿卷",8)],1):
        items.append(dict(id=f"TRIP-OLD-{i:03d}",store="越师傅·越式法棍三明治（福永店）",zone="星港同创汇天玑座",geographic_scope="本社区（办公商业带）",product_category="便携轻食/小食",product=name,price_rmb=price,price_kind="用户游记该次消费自报",data_date="2026-11-10",access_date="2026-11-27",source_url=trip,source_id="TRIP-OLD",evidence="B:单次用户记录，V3已有",model_use="只说明该次消费，不代表稳定菜单或当地平均客单"))
    p=OUT/"local_prices_v4.csv"
    with p.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(items[0]));w.writeheader();w.writerows(items)
    (OUT/"menu_source_audit_v4.json").write_text(json.dumps(audits,ensure_ascii=False,indent=2),encoding="utf-8")
    print("rows",len(items),[(a["source_id"],a["menu_body_date"],a["count"]) for a in audits])
    for a in items:
        if a["source_id"]=="KFC-XINHE" and a["product"] in ("香辣鸡腿堡","老北京鸡肉卷","葡式蛋挞(1只/多只装)","薯条","原味冰淇淋花筒","红豆派","牛奶(热)","拿铁","美式"):print(a["product"],a["price_rmb"])
if __name__=="__main__":main()
