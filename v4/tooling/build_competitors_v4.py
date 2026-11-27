import pathlib,csv,collections,re
p=pathlib.Path(__file__).resolve().parents[1]/'evidence'
rows=list(csv.DictReader((p/'foodcheck_v4.csv').open(encoding='utf-8-sig')))
g=collections.defaultdict(list)
for x in rows:g[x['entity_name']].append(x)
official=[]
for i,(n,ll) in enumerate(g.items(),1):
 addr=ll[0]['address']; items=list(dict.fromkeys(x['item'] for x in ll))
 if any(k in n for k in ('星汉','戈比太','垦拓','中盈建科')):
  cat='园区内部供餐/采购单位（替代）'; typ='非公开零售店候选';zone='工业园区'
 elif '汤包店' in n:
  cat='早餐包点';typ='公开商业主体';zone='新和一区'
 elif '饮品店' in n or '奶茶店' in n:
  cat='饮品';typ='公开商业主体';zone='新和二区'
 elif any(k in n for k in ('超市','百货','零食店')):
  cat='便利/包装食品';typ='公开商业主体';zone='新和二区' if any(k in addr for k in ('新和社区二区','新和社区2区')) else ('桥新路' if '桥新路' in addr else '悦盛一路' if '悦盛一路' in addr else '新和其他')
 elif any(k in n for k in ('渔港','大东海','鲜乐谷')):
  cat='海鲜正餐';typ='公开商业主体（同地址可存在多经营主体）';zone='福海海鲜市场'
 elif n in ('荔枝烧鸡','夜归人烧烤'):
  cat='烧烤小食';typ='历史摊贩样本';zone='新和二区（历史临时经营点）'
 elif '烧烤店' in n:
  cat='晚间餐饮';typ='公开商业主体';zone='新和一区'
 else:
  cat='快餐/餐饮';typ='公开商业主体';zone=('星港同创汇' if '星港' in addr else '工业园区' if '工业园' in addr or '华丽园区' in addr else '桥新路' if '桥新路' in addr else '新和二区' if '新和社区二区' in addr else '新和其他')
 alias=''; 
 if '福气满满饮品' in n:alias='与1点点官方目录地址一致，品牌关系待店主确认（不另计同址重复门店）'
 if '茂华优选' in n:alias='V3商铺配套中已见品牌，V4新增官方商品记录'
 if '林智文益禾堂' in n:alias='益禾堂奶茶（品牌字样源于经营主体名称）'
 official.append(dict(record_id=f"OFF-{i:02d}",name=n,source_cluster="官方监管抽样明细",zone=zone,geographic_scope="新和社区",address_or_anchor=addr,category=cat,entity_scope=typ,evidence_grade="A（当时商品/主体记录）",evidence_date="；".join(sorted({r['notice_date'] for r in ll})),item_or_detail="；".join(items),price_info="未公布",availability="抽样记录，今天仍营业未知，不是完整菜单",alias_note=alias,source_url="；".join(sorted({r['notice_url'] for r in ll})),raw_reference="；".join(r['source_id'] for r in ll),v4_delta="新增官方实证（主体或已有线索增强）"))
def lead(id,name,zone,scope,addr,cat,evi,date,item,price,url,typ='公开单店名称线索',alias='',delta='V4新增名称/证据线索'):
 return dict(record_id=id,name=name,source_cluster="第三方菜单/目录/挂牌等",zone=zone,geographic_scope=scope,address_or_anchor=addr,category=cat,entity_scope=typ,evidence_grade=evi,evidence_date=date,item_or_detail=item,price_info=price,availability="未现场核对；公开页面记录不代表现在营业",alias_note=alias,source_url=url,raw_reference=id,v4_delta=delta)
dti="https://drivethruindex.com/restaurants/cn/gd/%E6%B7%B1%E5%9C%B3/kfc-SZ2103"
pizza="https://drivethruindex.com/restaurants/cn/gd/%E6%B7%B1%E5%9C%B3/pizza-hut-GZ5650"
coffee="https://jt.dushiquan.net/shenzhen/station_4008/zb/3.html"
city8a="https://sz.city8.com/leisure/85hdas70ehopbbe440_address"
city8b="https://sz.city8.com/shopping/85hcu970ebw8b5159b_around"
city8c="https://ditu.city8.com/sz/enterprise/85hbz670ee09ba2131"
city8d="https://sz.city8.com/cater/85he1d70efvkbbc3ed_address"
city8e="https://sz.city8.com/enterprise/85hcs370efduba4e9d"
poi=[
lead("M01","肯德基（桥新路门店）","桥新路","新和社区（非三区）","桥新路17号15-16","连锁快餐/小食","B（独立第三方菜单实读）","2026-11-26","83项自提价，非早餐专项","蛋挞8、鸡肉卷18.5、鸡腿堡20.5元",dti),
lead("M02","必胜客（桥头永福路）","桥头商区","相邻社区","福海街道桥头社区永福路120号","西式正餐/小食","B（独立第三方菜单实读）","2026-11-26","98项App自提价，非早餐专项","详见价格CSV",pizza),
lead("M03","越师傅·越式法棍三明治（福永店）","星港同创汇","新和社区办公商业带","宝安大道6099号星港同创汇天玑座","便携特色餐","B（游记单次消费）","2026-11-10","法棍加蛋/鸡腿卷/蒜香烤片","21/8/3元；该次消费","https://hk.trip.com/moments/detail/bao-an-district-2015100-156845124/",delta="V3已有")
]
for i,(n,z,s,a,t,h) in enumerate([
("73Cafe柒叁咖啡","新和西巷","新和社区","新和西十巷1号","特色饮品","目录称平日13:00-21:00"),
("瑞幸咖啡（星港同创汇店）","星港同创汇","新和社区办公商业带","宝安大道6099号","咖啡","目录称平日07:00-20:00"),
("谷咖猎头咖啡书缘","星港同创汇","新和社区办公商业带","星港同创汇天枢座LT-02号","咖啡/休闲","目录称10:00-21:00"),
("星巴克（同泰时代广场店）","桥头商区","相邻社区","桥头社区宝安大道6259号同泰时代广场F1","咖啡/轻食","目录称06:30-23:15"),
("瑞幸咖啡（福永意库店）","福洲大道办公商业带","福永扩展区","福洲大道福海工业区二区一层9号101","咖啡","目录称平日07:00-22:00"),
("King Coffee（福永意库店）","福洲大道办公商业带","福永扩展区","丰业路福永意库2-105铺","咖啡","目录称09:30-22:30"),
("欧菲咖啡（福永意库店）","福洲大道办公商业带","福永扩展区","宝安大道福永意库14栋1楼","咖啡","目录称08:00-22:30"),
("悦叻星","福海科技园","福海商业区","福海科技园A区B2栋新鸿天大厦101号","咖啡","目录称10:00-21:00")
],4):poi.append(lead(f"M{i:02d}",n,z,s,a,t,"B（目录完整正文）","发布日期未知；2026-11-27读取",h+"，时段未经现场确认","未公布",coffee))
for i,(n,cat,anchor,url) in enumerate([
("尚品汤包（新和店）","早餐包点","永和大道/新和工业路商业带",city8a),
("土家香酱饼","早餐小吃","永和大道/悦盛商业带",city8a),
("新和二蛋炸串","小食","永和大道/悦盛商业带",city8a),
("东北饺子馆","粉面饺子","永和大道/悦盛商业带",city8a),
("坚记猪扒包","便携快餐","新和工业路/悦昌路商业带",city8c),
("江波石磨肠粉","早餐肠粉","永和路/悦昌路商业带",city8e),
("潮汕手工汤粉","粉面","新和三区/五区间商业带",city8b),
("第9味老上海馄饨（新和二区十六巷店）","馄饨/粉面","新和二区十六巷店名",city8b),
("周嬢嬢小面馆","粉面","新和三区/五区间商业带",city8b),
("氿号冒菜","快餐","新和三区/五区间商业带",city8b),
("四眼烧烤（新和店）","晚餐/烧烤","新和三区/五区间商业带",city8b),
("异乡缘烧烤","晚餐/烧烤","新和三区/五区间商业带",city8b),
("爽爽甜品（新和工业一巷店）","甜品/小食","新和工业一巷店名",city8d),
("吉小胖黄焖鸡米饭（新和店）","快餐","新和工业一巷/桥新路商业带",city8d),
("糖水铺（桥新路店）","糖水","桥新路店名",city8d),
("牛小鲜港式牛杂粉面饭","粉面/简餐","新和工业路/悦昌路商业带",city8c),
("一品轩柳州螺蛳粉","粉面/简餐","新和工业路/悦昌路商业带",city8c)
],12):poi.append(lead(f"M{i:02d}",n,anchor,"新和附近目录线索；具体店址未核",anchor+"（目录来源锚点非该店确切地址）",cat,"C（公开地图周边推荐索引）","2024-06-03目录" if url==city8b else "发布日期未知；2026-11-27检索","由名称识别品类，尚未取得本店菜单","未取得",url))
poi.append(lead("M29","邻步量贩零食超市（新和社区店）","新和社区","新和社区（确切分区未知）","二十巷13号101室（卖方挂牌地址）","零食量贩","C（挂牌索引）","公告/挂牌实际时间未知；2026-11-27索引","60㎡,转让费面议；卖方称经营中","租金7500元/月；非商品价","https://sz.sydc.anjuke.com/sp-zu/baoan-fuyong-lx4/",typ="挂牌线索，租约未核"))
poi.append(lead("M30","曾记正宗隆江猪脚饭","华达村","新和社区","华达村一巷5号102室","快餐","B（两目录名称交叉）","发布日期未知；2026-11-27检索","目录名称","未取得","https://sz.fang.anjuke.com/loupan/471842/fujin-0104.html；"+city8c))
poi.append(lead("M31","红荔村肠粉（福永华强城店）","塘尾","相邻社区","塘尾社区华强城市花园三期2栋A座103A","肠粉/粥品","B（目录/消费记录）","2025-10/11至2026-03评论","目录列06:00-21:00；游记提油条豆浆肠粉","确价未见","https://hk.trip.com/restaurant/china/shenzhen/detail/restaurant-133672479/",delta="V3已有；为对照保留"))
poi.append(lead("M32","和平夜市街","和平综合市场旁","相邻社区","玻璃围村和平综合市场旁（新闻）","夜间食品消费替代","B（本地新闻正文）","2025-10-13","报道开街时69个摊位；糖水、寿司、柠檬茶等；非单店","无租金及菜单价格","https://www.baoanone.com/content204441.html",typ="邻区整体案例，不计作单一竞争店"))
allrows=official+poi
with (p/'competitors_v4.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(allrows[0]));w.writeheader();w.writerows(allrows)
print(len(official),len(poi),len(allrows),collections.Counter(r['category'] for r in official))
