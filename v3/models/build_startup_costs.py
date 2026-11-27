"""Reproduce V3 (2026-11-27) fitout and equipment planning assumptions.
Before changing a price/quantity, record new source and date in COSTS.md.
Default output is the V3 canonical data, or pass --output to compare revisions.
"""
import argparse, json, pathlib
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=pathlib.Path, default=pathlib.Path(__file__).resolve().parents[1]/'evidence/startup_costs.json')
args=parser.parse_args()
out=args.output
tiers=('low','base','high')
sizes={'A':[20,30,40],'B':[18,28,38],'C':[30,45,60],'D':[45,70,95],'E':[8,12,20]}
capacity={'A':[260,390,550],'B':[220,360,500],'C':[280,420,550],'D':[220,420,600],'E':[160,250,340]}
# name, 3 modeled unit prices, evidence IDs / estimate flag
items={
 'steam':('商用蒸制设备', [1600,1900,2800], 'K04'),
 'fridge':('立式冷藏冷冻柜', [2800,3400,5200], 'K05,K06'),
 'coldprep':('冷藏工作台', [1700,2500,4500], 'K05,K06'),
 'warming':('保温售卖设备',[1300,1600,2400],'K06'),
 'induction':('商用电磁炉/加热灶',[1200,2200,3200],'K07'),
 'sink':('清洗水槽组',[1800,2600,3500],'K05,K06'),
 'worktable':('不锈钢工作台',[650,1100,1800],'K05,K06'),
 'rack':('货架及存储单元',[600,900,1500],'推算'),
 'pos':('收银机及扫码设备',[1000,1500,2500],'K08'),
 'display':('冷藏展示柜',[2500,3700,4800],'K06'),
 'press':('三明治压烤/轻食加热机',[800,1200,2000],'推算'),
 'smallwares':('刀具、容器、电子秤等成组工具',[800,1500,2500],'推算'),
 'urn':('热水/饮品设备',[500,800,1200],'推算'),
 'sealer':('封口打包工具',[300,600,1200],'推算'),
 'microwave':('复热设备',[650,900,1500],'推算'),
 'freezer':('独立冷冻柜',[2600,3500,4800],'K05'),
 'cookline':('多品类专用煎炒设备组',[2200,4000,6500],'K07'),
 'seating':('桌椅/食客区家具组',[1000,2000,3500],'推算'),
 'disinfect':('餐具消毒/清洁设施',[1200,1800,2400],'推算')
}
# quantities in low, base, high tier; zero shared host equipment under E requires explicit contract.
quant={
 'A':{'steam':[1,1,2],'fridge':[1,1,2],'warming':[1,1,2],'induction':[1,1,2],'sink':[1,1,1],'worktable':[1,2,2],'rack':[1,1,2],'pos':[1,1,1],'smallwares':[1,1,2],'urn':[1,1,1],'sealer':[1,1,1],'disinfect':[1,1,1]},
 'B':{'fridge':[1,1,1],'coldprep':[1,1,2],'press':[1,2,2],'warming':[0,1,1],'sink':[1,1,1],'worktable':[1,1,2],'rack':[1,1,2],'pos':[1,1,1],'smallwares':[1,1,2],'sealer':[1,1,1],'microwave':[1,1,1],'urn':[1,1,1],'disinfect':[1,1,1]},
 'C':{'steam':[1,2,2],'fridge':[1,1,2],'display':[1,1,2],'warming':[1,1,2],'induction':[1,1,2],'sink':[1,1,1],'worktable':[1,2,2],'rack':[2,3,4],'pos':[1,1,1],'smallwares':[1,1,2],'urn':[1,1,1],'sealer':[1,1,1],'disinfect':[1,1,1]},
 'D':{'steam':[1,2,2],'fridge':[1,2,2],'coldprep':[1,1,2],'warming':[1,1,2],'cookline':[1,1,2],'sink':[1,2,2],'worktable':[2,3,4],'rack':[2,3,4],'pos':[1,1,2],'display':[1,1,2],'smallwares':[2,2,3],'urn':[1,1,2],'sealer':[1,1,1],'freezer':[0,1,2],'seating':[1,2,3],'disinfect':[1,1,2]},
 'E':{'steam':[0,1,1],'fridge':[0,0,1],'warming':[1,1,1],'rack':[1,1,1],'pos':[1,1,1],'smallwares':[1,1,1],'sealer':[1,1,1],'urn':[0,0,1]}
}
# floor/ceiling/wall simple base, water electric/drainage, entrance signage, exhaust, site finishing (separate non-equipment expenditures)
fit={
 'A':[(350,3000,1500,1500,1000),(500,8000,3000,5000,2000),(650,14000,5500,10000,4500)],
 'B':[(350,3000,1500,800,900),(500,7000,3500,2500,2000),(650,13000,5500,6500,4000)],
 'C':[(350,3500,2200,1800,1500),(500,12000,5000,6500,3500),(650,20000,8500,14000,8000)],
 'D':[(500,9000,3000,8500,2000),(650,24000,8000,20000,7500),(850,40000,14000,45000,17000)],
 'E':[(0,0,500,0,1500),(0,0,1000,0,4000),(0,0,2000,0,8000)]
}
# startup food stock: perishable days x daily order planning x ingredient unit cost, separate dry supplies + packaging.
inventory={
 'A':[(2,100,2.5,400,450,0,0,0),(3,150,2.7,800,800,0,0,0),(3,220,3.0,1200,1200,0,0,0)],
 'B':[(2,90,4.0,400,500,0,0,0),(3,130,4.5,700,1000,0,0,0),(3,180,5.0,1200,1500,0,0,0)],
 'C':[(2,130,2.9,500,550,40,3,7),(3,180,3.2,900,1000,80,3,8),(3,260,3.5,1400,1600,120,4,9)],
 'D':[(2,160,4.8,700,700,0,0,0),(3,250,5.8,1100,1300,0,0,0),(3,340,6.5,1600,2000,0,0,0)],
 'E':[(2,70,2.8,200,300,0,0,0),(2,100,3.0,350,450,0,0,0),(3,140,3.4,600,700,0,0,0)]
}
monthly={
 'A':[(200,650,450,200),(360,950,650,350),(600,1400,900,500)],
 'B':[(180,600,450,200),(336,900,650,400),(570,1300,900,550)],
 'C':[(300,950,600,300),(540,1300,800,500),(900,1800,1200,700)],
 'D':[(450,1500,800,350),(840,2500,1300,650),(1425,3800,1800,1000)],
 'E':[(0,250,250,100),(0,450,350,200),(0,700,500,300)],
}
# utilities monthly modeled as baseline; electricity incremental above demand baseline belongs only once, not a second full bill.
preopening={
 'A':[(500,400,500,500),(800,700,800,1000),(1200,1000,1500,2200)],
 'B':[(500,500,500,600),(800,800,800,1200),(1200,1200,1500,2200)],
 'C':[(500,500,700,650),(800,800,1000,1500),(1200,1200,1800,2600)],
 'D':[(800,700,1000,1000),(1200,1200,1600,2400),(1800,1800,2500,4000)],
 'E':[(300,300,300,200),(500,500,500,500),(700,700,800,1000)]
}
delivery={'A':[1500,2600,4200],'B':[1800,3000,4800],'C':[1800,3200,5200],'D':[2500,4500,7200],'E':[1000,1800,3000]}
p={}
for mode,sz in sizes.items():
  p[mode]={}
  for i,t in enumerate(tiers):
    area=sz[i]; rate,water,sign,vent,site=fit[mode][i]
    fits=[{'name':'地砖、墙面、吊顶等基础修整','qty':area,'unit_price':rate,'subtotal':area*rate},*({'name':n,'qty':1,'unit_price':v,'subtotal':v} for n,v in [('给排水、电路增容及基础安装',water),('门面/招牌',sign),('排风/油烟及风管改造',vent),('现场收尾/交接区卫生隔断及预备',site)])]
    eq=[]
    for key,counts in quant[mode].items():
        q=counts[i]
        if q:
            name,prices,src=items[key]; price=prices[i]
            eq.append({'name':name,'qty':q,'unit_price':price,'subtotal':q*price,'source':src})
    # ordinary equipment freight/assembly, no structural electrical or exhaust.
    freight=round(sum(row['subtotal'] for row in eq)*[0.05,0.07,0.10][i]/100)*100
    eq.append({'name':'设备运输、就位、调试','qty':1,'unit_price':freight,'subtotal':freight,'source':'按设备金额的5%/7%/10%估算并取百元'})
    days,orders,food,dry,pack,sku,units,cogs=inventory[mode][i]
    raw=round(days*orders*food)
    inv=[{'name':'开业鲜食原料','days':days,'orders_day':orders,'unit_price':food,'subtotal':raw},{'name':'干货及调味品缓冲','subtotal':dry},{'name':'首批包装、袋、杯、纸品','subtotal':pack},{'name':'常温零食库存','sku':sku,'units_per_sku':units,'unit_price':cogs,'subtotal':sku*units*cogs}]
    pre=[{'name':n,'subtotal':v} for n,v in zip(['健康检查及经营准备','消毒及卫生用品','开业耗材及菜单物料','试营业及线下宣传'],preopening[mode][i])]
    mf=monthly[mode][i]
    ds=delivery[mode][i]
    ds_photo=round(ds*.25/100)*100
    ds_setup=round(ds*.25/100)*100
    delitems=[{'name':'菜单拍照及上线物料','subtotal':ds_photo},{'name':'额外打单/打包工具','subtotal':ds_setup},{'name':'开通初期引流储备','subtotal':ds-ds_photo-ds_setup}]
    p[mode][t]={'area_m2':area,'fitout':sum(r['subtotal'] for r in fits),'fitout_items':fits,'equipment':sum(r['subtotal'] for r in eq),'equipment_items':eq,'opening_inventory':sum(r['subtotal'] for r in inv),'inventory_items':inv,'preopening':sum(r['subtotal'] for r in pre),'preopening_items':pre,'delivery_setup':ds,'delivery_setup_items':delitems,'property_fee':mf[0],'utilities_fixed':mf[1],'other_fixed':mf[2],'marketing_fixed':mf[3],'equipment_capacity_day':capacity[mode][i], 'setup_context':['已营业餐饮/轻食铺少量改造；剩余设备或装修须扣除重置预算、押金','空置第二手餐饮铺，基础给排水电力合适，常规新做门面、工作区和采购设备；租约及合规需过关','需较大水电、排风及门面改造，标准新设备；仍不含整栋建筑的重大工程'][i] if mode!='E' else '合规分时使用既有空间和合同内主设施；改造仅限交接卫生与可撤走专用区装置','evidence_status':'预算推算，非实时报价；面积与采购数量/工序口径明示；日设备能力设计假设未测'}
for mode, row in p.items():
    for tier,r in row.items():
        for total,detail in [('fitout','fitout_items'),('equipment','equipment_items'),('opening_inventory','inventory_items'),('preopening','preopening_items'),('delivery_setup','delivery_setup_items')]:
            assert r[total] == sum(item['subtotal'] for item in r[detail]), (mode,tier,total)
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for mode,v in p.items():
    print(mode,[(t,{k:r[k] for k in ('area_m2','fitout','equipment','opening_inventory','preopening','delivery_setup','property_fee','utilities_fixed','other_fixed','marketing_fixed','equipment_capacity_day')}) for t,r in v.items()])
