"""V4 market atlas: actual evidence-first editorial structure + frozen verified five-mode financial reader layer."""
from pathlib import Path
import json,csv,sys,math
from atlas_engine import *
ROOT=Path(__file__).resolve().parents[2];V=ROOT/'v4';AS=ROOT/'v2/assets';A=V/'assets'
F=json.loads((V/'models/reader_finance_v4.json').read_text()); R=F['reader']
D=json.loads((V/'models/report_data_v4.json').read_text())
PH={x['filename']:x for x in json.loads((AS/'PHOTO_MANIFEST.json').read_text())}
PHOTO4={r['filename']:r for r in json.loads((A/'PHOTO_REFERENCES_V4.json').read_text())}
COND={x['key']:x for x in F.get('conditional_tests',[])}
TITLE='深圳宝安福海新和社区早餐与休闲零食市场调研及商业可行性分析报告'
OUT=ROOT/'deliverables'/(TITLE+'_V4_手机图解版.pdf')
charset=set(Path(__file__).read_text()+Path(__file__).with_name('atlas_engine.py').read_text()+json.dumps(F,ensure_ascii=False)+json.dumps(PH,ensure_ascii=False)+json.dumps(PHOTO4,ensure_ascii=False))
for q in [*range(32,127),0x2212,0x2192,0x2197,0x2193,0x25cf,0x00d7,0x00f7,0x2248,0x33a1]:charset.add(chr(q))
b=Atlas(OUT,''.join(charset),V/'design'/'fonts')
def start(key,c,t=None,k=None,accent=TEAL):b.start(key,c,t,k,accent)
def end():b.finish()
def actual(fn,h=150,short=None):
 x=PH[fn];b.image(AS/fn,short or x['caption']+'｜'+x['author']+' · '+x['license']+'（历史照片）',h,x['source_url'])
def real_tuple(fn,caption):
 x=PH[fn];return (AS/fn, caption,x['source_url'])
def fake(k,h=156,caption='生成情景示意，不是新和实际门店或经营现场。'):
 b.image(A/f'scenario_{k}.jpg',caption,h)
def source(l,u):b.source(l,u)
def note(s):b.note(s)
def condkey(pref):
 for k,v in COND.items():
  if pref in v['label'] or pref in k:return v
 return None
def need_cond(pref):return condkey(pref) or {}
def num(v):return money(v)
def mv(v):return money(v)+'元' if abs(float(v))>=10000 else money(v)
def textnom(s):
 return s.replace('／','/').replace('＋','+')
def ch(k):return '04 / '+k+' · '+N[k]
N={'A':'传统早餐','B':'便携特色早餐','C':'早餐＋休闲零食','D':'多时段餐饮','E':'分时合作／店中店'}
SN={'A':'传统早餐','B':'特色早餐','C':'早餐＋零食','D':'多时段','E':'分时共享'}
SRC={
'gov':'https://www.baoan.gov.cn/xxgk/jgk/jdbsc/content/post_12887016.html',
'primary':'https://www.sz.gov.cn/school/ba/baqxx/content/post_9457858.html',
'middle':'https://www.sz.gov.cn/school/ba/jnygz/content/post_9457237.html',
'newbudget':'https://www.sz.gov.cn/attachment/1/1707/1707300/12781639.pdf',
'meal':'https://cnki.istiz.org.cn/kcms/detail/detailall.aspx?dbcode=CJFQ&dbname=CJFD2025&filename=xiws202505008',
'income':'https://www.sz.gov.cn/zfgb/2026/gb1416/content/post_12848555.html',
'canteen':'https://static.nfnews.com/content/202505/08/c11268879.html?enterColumnId=13298',
'keyto':'https://www.keyto.com/uploads/file/20250513/f2f405023992a51ebad4696ed3a3146d.pdf',
'planning':'https://www.ccgp.gov.cn/cggg/dfgg/gkzb/202611/t20261105_27631162.htm',
'culture':'https://www.sz.gov.cn/cn/xxgk/zfxxgj/gqdt/content/post_13042340.html',
'7eleven':'https://www.jiemian.com/article/15272717.html',
'vietnam':'https://hk.trip.com/moments/detail/bao-an-district-2015100-156845124/',
'rent32':'https://m.shangpu5.com/zhuanrang/show-16522.html',
'rent35':'https://sz.sydc.anjuke.com/sp-zhuan/d4601627457739778/',
'rent25':'https://m.shangpu5.com/zhuanrang/show-11195.html',
'rent76':'https://www.shangpu5.com/zhuanrang/show-16371.html',
'rent42':'https://sz.shangpu5.com/zhuanrang/show-12955.html',
'rent139':'https://sz.shangpu5.com/zhuanrang/show-9106.html',
'share':'https://finance.sina.com.cn/tech/roll/2024-11-07/doc-incvfpzf7705577.shtml',
'stall':'https://www.sznews.com/news/content/mb/2024-08/01/content_31122134.htm',
'double':'https://www.meiyiduo.com/html/news_220.html',
'permit':'https://www.sz.gov.cn/hdjlpt/detail?pid=3397633&via=pc',
'layout':'https://www.sz.gov.cn/attachment/1/1510/1510737/11737941.pdf',
'deliverylaw':'https://www.samr.gov.cn/zw/zfxxgk/fdzdgknr/fgs/art/2026/art_d04d512f5ad8470eb61a652c0061dc3a.html',
'mt':'https://rules-center.meituan.com/m/detail/guize/1079?activeRule=1',
'tb':'https://terms.alicdn.com/legal-agreement/terms/suit_bu1_other/suit_bu1_other202111251946_14275.html',
'tbdelivery':'https://terms.alicdn.com/legal-agreement/terms/suit_bu1_other/suit_bu1_other202111252158_23065.html',
'wage':'https://hrss.sz.gov.cn/tzgg/content/post_12954870.html',
'jobs':'https://www.58.com/ppeseoll30587/',
'repo':'https://github.com/hzp15abc-collab/shenzhen_eat/blob/main/v4/PROJECT_HOME.md',
'competitor':'https://github.com/hzp15abc-collab/shenzhen_eat/blob/main/v4/research/COMPETITOR_LOCAL.md',
'property':'https://github.com/hzp15abc-collab/shenzhen_eat/blob/main/v4/research/PROPERTY_OPERATIONS.md',
'customer':'https://github.com/hzp15abc-collab/shenzhen_eat/blob/main/v4/research/CUSTOMERS_PRODUCTS.md',
'finance':'https://github.com/hzp15abc-collab/shenzhen_eat/blob/main/v4/models/MODEL_SPEC_V4.md',
'kfc':'https://drivethruindex.com/restaurants/cn/gd/%E6%B7%B1%E5%9C%B3/kfc-SZ2103',
'check1':'https://amr.sz.gov.cn/xxgk/qt/ztlm/spaqjg1/spaqcj/cyjytg/content/post_12558203.html',
'check2':'https://amr.sz.gov.cn/xxgk/qt/ztlm/spaqjg1/spaqcj/cyjytg/content/post_12945842.html',
'adultmeal':'https://wsyj.cbpt.cnki.net/portal/journal/portal/client/paper/5078fd4c8f502e3f505967ddb37f4613',
'equip':'https://www.365trade.com.cn/jhwzb/828835.jhtml',
}
# cover : editorial, real community / simulated food separated clearly.
b.start('cover','市场研究   /   商业可行性',accent=GOLD,background=DARK,light=True)
b.txt('深圳宝安福海新和社区',24,60,CW,19.5,'#EED6AF','b',26)
b.txt('早餐与休闲零食\n市场调研及\n商业可行性分析报告',24,101,CW,31,WHITE,'s',42)
b.txt('第一次做生意，也能看懂的完整账本',24,241,CW,15,'#DCE9DE','r',21)
b.img(A/'xinhe_seafood_market_2026_a.jpg',24,285,CW,187)
b.txt('福永海鲜市场外景 · 2026年10月29日实拍',24,478,CW,11.5,'#DCE9DE','b',16)
b.txt('LN9267 / CC BY-SA 4.0；不代表单店营业额或客流',24,497,CW,10.6,'#DCE9DE','r',15);b.link((24,478,366,518),url=PHOTO4['xinhe_seafood_market_2026_a.jpg']['source_url'])
for i,k in enumerate(['A','B','C']):b.img(A/f'scenario_{k}.jpg',24+i*115,532,112,86)
b.txt('上：福永近区商业实景；下：经营情景生成示意',24,625,CW,11.4,'#DCE9DE','r',16)
b.txt('看清这里的市场，再看五种做法。\n从真实报价、商品与人力，到利润、现金和退出。',24,660,CW,17,WHITE,'r',25)
b.txt('第四版 / 手机图解版 · 2026年11月27日',24,744,CW,12.8,'#EED6AF','b',18)
b.y=773;end()
start('overview','先读全局','五种做法，五笔不同的账','先比较同一组条件：两人自营、工资为0、标准投入、基准市场、线下75%＋外卖25%。')
# editorial feature list
for k,x in R.items():
 y=b.y; b.img(A/f'scenario_{k}.jpg',24,y,84,77);b.rect(24,y,4,77,PAL[k]);b.txt(k+'  '+N[k],120,y,CW-96,15.0,INK,'b',20)
 b.txt('筹资 '+money(x['opening']['initial_funding'])+'   |   首年平均月结余',120,y+22,CW-96,11.9,MUTED,'r',16)
 p=x['years']['annual'][0]['avg_monthly_profit']; ex=x['exit'][1]['total_net_investor_loss']
 b.fit(money(p),120,y+39,100,20,15,RED if p<0 else TEAL,'b')
 b.right('半年'+loss(ex),W-24,y+44,12.1,RED if ex>0 else TEAL,'b',137)
 b.line(120,y+75,W-24,y+75,LINE,.6);b.link((24,y,W-24,y+77),target=k+'1');b.y+=84
note('开业资金含账面储备；经营结余未扣合伙人工资，不等于当月可分配钱。半年损失为两位合计，非最大风险。照片为生成经营示意；金额是模拟，不是当地店铺真实流水。')
end()
start('toc','阅读地图','你想先看哪一部分？','每一部分有图、结论和可回查依据；各模式目录可直接进入。')
for a,d,t in [('01  这个地方','商圈／两校／消费者／真实商品和竞争','area'),('02  铺面与现实成本','转让费／剩余租期／施工／共享场地','rent'),('03  两个人怎样把店做起来','工作台、人员、外卖、售卖与真实现金','work'),('04  五种经营方式','各模式产品、钱、人、三年和退出','modes'),('05  放在一起比较','成本、订单、客单、竞争、渠道、止损','cross'),('06  真正要核实的事项','实测计划、证据和来源，不把估算当事实','verify')]:b.nav(a,d,t)
b.tag('三种证据，一眼辨认','绿色：有公开来源的事实；橙色：预算或条件模拟；灰色：未获真实交易或现场资料。所有金额为人民币，“万”指万元。')
end()
# map and demand
start('area','01 / 商圈地图','新和，不只是学校周边','这里的商业需求由家庭、居民、产业员工、通勤成年人及不同机构共同组成。')
b.image(A/'xinhe_bus_terminal_2026.jpg','新和公交总站 · 2026.10.13，LN9267 / CC BY-SA 4.0。公共设施实景，不代表客流。',140,PHOTO4['xinhe_bus_terminal_2026.jpg']['source_url'],focus=(.5,.95))
# contextual map: non-geospatial not child movements
y=b.y;b.rect(24,y,342,202,'#EEF1E6')
# central commercial zones
for x,yy,w,h,c,label,sub in [(36,y+18,144,64,LEAF,'住宅与社区商业','新和各区、沿街底商'),(194,y+18,160,64,ICE,'工业及办公','新和工业路、产业园'),(36,y+106,144,64,PALE,'两所学校','供餐与家庭消费情境'),(194,y+106,160,64,GRAY,'交通与便民设施','公交、便利店、工作餐')]:
 b.rect(x,yy,w,h,c);b.txt(label,x+8,yy+8,w-16,15,INK,'b',20);b.txt(sub,x+8,yy+34,w-16,11.8,MUTED,'r',16)
b.rect(133,y+83,124,24,DARK);b.txt('新和社区商圈',142,y+87,113,12.3,WHITE,'b',15)
b.line(180,y+82,194,y+82,LINE,2);b.line(180,y+105,194,y+105,LINE,2)
b.y=y+208;note('根据用户提供的腾讯地图位置及公开地区资料整理为商业关系图。不是按距离绘制，不代表真实流量、通学路线或精确铺段排名。')
b.metricline([('福海管理人口','约53万','街道范围'),('企业','4,500余','工矿商贸企业')],LEAF)
source('福海街道官方概况（2026）',SRC['gov']);end()
start('street_photos','01 / 这里的样子','先看看真实街坊的商业形态','图片有具体时间与来源，不把看见的店面当客流或营业额。')
for fn,h,cap in [('xinhe_seafood_market_2026_a.jpg',204,'福永海鲜市场外景 · 近区商圈背景 · 2026.10.29'),('nearby_snack_haoye_2024.jpg',121,'邻近商圈零食店 · 2024'),('nearby_mcdonalds_2026_a.jpg',121,'福海附近连锁快餐 · 2026.10.22')]:
 img=PHOTO4[fn];b.image(A/fn,cap+' | '+img['author']+' / '+img['license']+'，裁切。',h,img['source_url'])
note('这三类真实商业环境体现当地存在便民消费与餐饮替代。没有取得准确新和单店现时营业资料，不以历史照片当现在。')
end()
start('school','01 / 商圈地图','学校在旁边≠学生会买','两所学校是研究背景。不能把在校人数当成外买早餐人数。')
# evidence document style
b.rect(M,b.y,CW,111,LEAF);b.txt('福新小学 / 公办',M+13,b.y+10,CW-26,17,TEAL,'b',22)
b.txt('2026预算新增证据',M+13,b.y+38,CW-26,13,TEAL,'b',18)
b.txt('133万元',M+13,b.y+61,142,26,DARK,'b',30)
b.txt('午餐午休管理经费\n另有自营食堂事务开支',M+166,b.y+65,158,12.5,INK,'r',16.5)
b.y+=119
b.para('新年度部门预算另显示学生及教职工人数增长；一般管理事务含自营食堂开支。不能仍把旧目录的配餐当成当前完整事实。2022年曾为1,798名学生；现时人数及实际早餐安排未知。',14.2)
b.rect(M,b.y,CW,91,ICE);b.txt('鹏晖中英文学校 / 民办九年一贯',M+13,b.y+10,CW-26,16,NAVY,'b',20)
b.txt('公开旧目录记载堂食、不提供住宿。当前供餐、在校规模、家长购买比例仍需确认。',M+13,b.y+41,CW-26,13.6,INK,'r',18.5);b.y+=99
b.headline('全国调查仅作消费背景')
b.stack([('家中',66.3,TEAL),('学校',25.8,BLUE),('其他',7.9,GOLD)],100,22)
b.mini_legend([('家里','66.3%',TEAL),('学校','25.8%',BLUE),('其他','7.9%',GOLD)],3)
note('2019—2021年全国跨地区52,535名6—17岁调查；非本地学校早餐数据。未知是否在家、学校或购买，不能按此推当地销量。')
source('福新小学2026部门预算（第2–3页）',SRC['newbudget']);source('鹏晖学校官方旧目录',SRC['middle']);source('全国营养调查摘要',SRC['meal'])
end()
start('buyers','01 / 客群','四类人，不买同一种早餐','把购买理由、替代品和实际支付价格放在一起看；不从全国收入或学校数量硬推本地客单。')
b.photo_split([real_tuple('qiaohe_market.jpg','福海邻近菜市场 · 2023'),real_tuple('tongtai_foodstreet_05.jpg','同泰时代广场餐饮 · 2024')],116)
for title,why,alt,co in [('家庭／居民','卫生、价格、方便、回家吃','家里自做、校内供给、社区商店',TEAL),('产业员工','够饱、有确定价格、少等候','园区公共食堂、内部食堂',BLUE),('上班与通勤成人','拿了就走、可预约、稳定口味','便利店、熟悉早餐摊',GOLD),('周末居民与其他成人','休闲、加餐、更多选择','奶茶、超市、咖啡、夜市',BROWN)]:
 yy=b.y;b.rect(M,yy,4,77,co);b.txt(title,M+12,yy,CW-20,15.7,INK,'b',20);b.txt('买单理由：'+why,M+12,yy+24,CW-20,13.4,INK,'r',18);b.txt('替代：'+alt,M+12,yy+46,CW-20,12.2,MUTED,'r',17);b.y+=83
note('客群及购买理由是待实地验证的业务假设，不代表已访谈消费者。深圳全市收入不能代替当地家庭收入。')
end()
start('habit','01 / 客群','“每天会吃早餐”和“每天会买早餐”不同','2026年发表的成人城市早餐研究：2021年7–8月、31个省级地区、18–60岁，共11,162名问卷对象。')
b.headline('在工作日与休息日每天吃早餐的受访者')
for title,frac,n,co in [('工作日 5天',.814,9089,TEAL),('休息日 2天',.701,7821,BLUE)]:
 y=b.y;b.txt(title,M,y,185,16,INK,'b',21);b.right(perc(frac),W-M,y,24,co)
 b.rect(M,y+36,CW,21,GRAY);b.rect(M,y+36,CW*frac,21,co);b.y+=69;b.note(f'样本中 {whole(n)} 人')
b.tag('不是外购率','差11.3个百分点，说明工作日/周末可能是不同消费情景；这不是深圳新和本地数据，也不是出门买早餐的比例。')
b.para('在实地验证时，需要把周中、休息日、雨天及产业园放假分开。真实消费者可能在家吃、由学校/公司提供，或选择便利店、其他餐饮。',15.2)
b.metricline([('深圳全市人均收入','84,945元/年','2025可支配收入'),('深圳全市人均消费','53,548元/年','2025消费支出')],LEAF)
b.note('全市居民口径不是新和社区或两校家庭收入，不能换算本地早餐客单。')
source('深圳2025统计公报',SRC['income'])
source('《卫生研究》2026.03成人早餐调查摘要',SRC['adultmeal']);end()
start('canteens','01 / 真实价格','工业园员工多，食堂也在竞争','这次新增了邻近产业区的真实用餐价格。对做午间和晚间简餐尤其重要。')
b.band('福海中粮（福安）机器人科技园','10–14元','2025年5月当地媒体现场价签；福海片区，非新和三区成交价。')
b.stack([('10元',10,TEAL),('12元',12,BLUE),('14元',14,GOLD)],36,20)
# three actual prices
b.metricline([('1荤1素','10元','真实价签'),('2荤1素','12元','真实价签'),('3荤1素','14元','真实价签')])
b.para('报道提到园区26家企业、3,500多名员工、公共食堂500餐位。新和社区企业2024年排放公开报告另记录园区食堂外包。数量大不等于店铺有同样多的客户。',15.1)
b.tag('商业含义','多时段餐饮若无法与食堂比价格、速度或便利，模型的高客单很可能撑不住。后面将用真实价格方向做压力测试。',GOLD,PALE)
source('宝安融媒 2025年5月食堂报道',SRC['canteen']);source('新和企业2024年排放公开报告',SRC['keyto']);end()
# competitive evidence
start('competition','01 / 竞争调查','本地真的有哪些东西在卖？','新一轮查了监管部门公开的食品抽检附件，不再只依赖地图名称和点评数量。')
b.band('2025.07—2026.09 · 精确新和地址记录','137条','13份政府抽检附件筛出的公开监管样品记录、32个主体。是抽检样本，不是在营门店总数。')
for title,body,co in [('传统包点','旺记早阳汤包店（一区）：菜包、白馒头、红糖馒头、发糕。2025年12月通告。',TEAL),('奶茶与饮品','新和二区益禾堂、古茗：四季春轻乳茶、云岭茉莉。2026年8–9月通告（样品日期字段5月）。',BLUE),('零食和小食','桥新路零食店夹心饼干；惠佰家牛奶、提子蛋糕、五香蛋；悦盛一路粥、椰乳与冰品。',GOLD),('快餐及供给替代','抽检有烧鸭、叉烧等快餐商品及产业园食堂主体；不能推算交易量。',BROWN)]:
 b.circle(M+5,b.y+9,4,co);y=b.txt(title,M+15,b.y,CW-15,15.8,INK,'b',20);b.y=b.txt(body,M+15,y+1,CW-15,13.6,MUTED,'r',19)+9
note('抽检证明当时出现该经营主体及商品，并非今天仍营业、全部商品合格或实际经营状况。逐条原始记录、地址与来源在附表。')
source('市监2025.12.19抽检通告',SRC['check1']);source('市监2026年第7期抽检通告',SRC['check2']);source('完整监管样本及商户调查',SRC['competitor']);end()
start('supply_map','01 / 竞争调查','不是只有早餐摊：一张供给图','32个抽检主体按其公开商品及业务粗分，仅是抽检样本的构成，绝不是本地店铺比例。')
cats=[('快餐/餐饮',10,TEAL),('饮品',5,BLUE),('包装零食/便利',5,GOLD),('海鲜市场',4,BROWN),('供餐采购',4,'#7C8F75'),('临时摊',2,'#9CADB9'),('包点',1,TEAL),('晚餐',1,'#A68A9E')]
for lab,n,co in cats:
 y=b.y;b.txt(lab,M,y,127,14.2,INK,'b',19); b.rect(M+132,y+6,165,11,GRAY);b.rect(M+132,y+6,165*n/10,11,co);b.right(str(n),W-M,y,16,INK);b.y+=29
b.photo_split([(A/'nearby_snack_sku_haoye_2024.jpg','相邻零食陈列实拍 · 2024 · CC0',PHOTO4['nearby_snack_sku_haoye_2024.jpg']['source_url']),(A/'nearby_noodle_haoye_2024.jpg','相邻粉面餐饮实拍 · 2024 · CC0',PHOTO4['nearby_noodle_haoye_2024.jpg']['source_url'])],124)
b.tag('从竞争找到待验证的空间','福围2026有美宜多＋零食有鸣“一店双区”官方案例；这是组合形式，不等于新和早餐＋零食已盈利。用具体商品与价格找自己的差异。',GOLD,PALE)
source('美宜多官方融合店案例',SRC['double']);end()
start('price','01 / 竞争调查','附近价格，到底落在哪？','不同渠道、品牌和时间必须分开；这些是真实公开证据，不是直接拿来做新店的售价。')
b.headline('新和当地 · KFC App自提菜单')
b.para('桥新路17号15–16第三方自提菜单，标注2026年11月26日采价；83个商品。不是该店早餐专菜单，也不是美团外卖价格。',14.3)
b.table(['商品例','自提公开价','口径'],[['红豆派','7元','菜单'],['蛋挞','8元','菜单'],['薯条','9.5元','菜单'],['鸡肉卷','18.5元','菜单'],['香辣鸡腿堡','20.5元','菜单']],[135,100,107],13.5)
b.headline('深圳对照 · 便利店及特色轻食')
b.table(['真实参照','价格','范围'],[['大口饭团','7.5元','深圳店'],['主食＋饮品','12.9/14.9元','深圳店'],['法棍＋蛋','21元','新和个案'],['鸡腿卷','8元','新和个案']],[130,125,87],13.0)
note('另有邻区必胜客98项自提价，原价格表共184项（含旧个案3条）。标价不是平均客单，份量及成交待验。')
source('深圳7-Eleven走访（2026.10）',SRC['7eleven']);source('新和越师傅用户消费记录（2026.11）',SRC['vietnam']);source('新和KFC第三方公开自提菜单',SRC['kfc']);end()
start('opportunity','01 / 产品与竞争','有机会的，不等于没人做','把“新鲜感”与“能长期赚钱”分开。这里不是推荐品类，而是四种待检验的差异化。')
b.photo_split([real_tuple('baozi_food.jpg','深圳包点实拍 · 同类参考'),real_tuple('sandwich_combo.jpg','深圳便携餐实拍 · 同类参考')],127)
for a,why,risk in [('A  高频传统','6–10元组合；蒸包、粥、蛋、无糖豆饮','容易替代；挑战是等待与剩货'),('B  便携新口味','饭团、三明治、法棍；10–16元价带试验','冷藏、损耗、售价与稳定回购'),('C  组合加购','早餐＋少量可追溯零食、奶、水、健康加餐','占货架、库存周转、与便利店竞争'),('D/E  时间空间','午间简餐、下午茶、分时合作；场地复用','多工序、人力、许可、合作方退出')]:
 yy=b.y;b.txt(a,M,yy,CW,15.8,INK,'b',20);b.y=b.txt(why,M,yy+22,CW,13.6,INK,'r',19);b.y=b.txt('要验证：'+risk,M,b.y+2,CW,12.2,MUTED,'r',17)+9;b.line(M,b.y-3,W-M,b.y-3,LINE,.6)
note('健康与口味的平衡：不靠高糖、高盐刺激消费；食材、过敏原、分量、冷藏与复购都要主动验证。价格带为试销假设。')
end()
# location and rental
start('rent','02 / 铺面与成本','租金便宜，转让费未必便宜','本轮新增完整挂牌正文，包含租约剩余期。以下都是广告报价，并非成交价或现在可租。')
b.table(['样本','月租','转让/剩租'],[['新和32㎡米粉','3,040元','4.2万 / 7月'],['五区35㎡餐馆','2,660元','3万 / 未知'],['新福园25㎡早餐','2,800元','4.8万 / 12月'],['福园一路76㎡快餐','5,985元','1.2万 / 24月'],['新和工业园139㎡','5,800元','面议 / 42月']],[138,94,110],13.1)
b.tag('一个关键变化','从前我们只知道32㎡米粉店4.2万元转让；新找到完整详情，广告剩7个月。若没有续租，仅转让费要每月回收6,000元，尚未计其它钱。',RED,ROSE)
note('新和二区42㎡黄焖鸡5000元月租、11万元转让的广告现在显示“已成交”。45㎡饺子、130㎡宵夜广告也显示结束；只做历史报价，不列为可租。')
source('32㎡米粉完整详情',SRC['rent32']);source('35㎡餐馆 2026.09更新',SRC['rent35']);source('25㎡早餐店',SRC['rent25']);source('76㎡园区快餐',SRC['rent76']);end()
start('rent_math','02 / 铺面与成本','同一个铺，为什么还要多问一句？','A传统早餐套入32㎡米粉广告两个价格条件。其它运营假设沿用标准档，不是该铺完整报价。')
v=need_cond('32㎡米粉')
b.metricline([('广告净转让待确认','4.2万','剩余租期7月'),('广告月租','3,040元','非签约金额')],LEAF)
b.headline('7个月能把顶手费赚回来吗？')
b.stack([('已覆盖',v['lease_end']['business_cashflow_cumulative'],TEAL),('缺口',42000-v['lease_end']['business_cashflow_cumulative'],GOLD)],42000,24)
b.metricline([('7个月经营净现金',money(v['lease_end']['business_cashflow_cumulative']),'同条件模拟'),('转让费','4.2万','单项广告报价')])
b.tag('先确认合同而不是只看便宜','若实际到期、不得续租且无提前退租违约金，这个模拟的两位终局净损失约7.83万元。未核实际签约、资产包组成，不能说此店一定亏。',RED,ROSE)
b.para('若广告带设备、已有装修或押金，必须扣除可复用资产的重叠金额。签约前当场核房东权属与同意、剩租期限、续租权、许可和恢复原状费用。')
source('广告原文',SRC['rent32']);end()
start('lease_options','02 / 铺面与成本','合同不同，筹到的钱也会不同','只替换可查挂牌里的两项价格（租金和转让），其他参数仍沿用模式标准档；不是已核实整铺预算。')
rows=[]
for key,lab in [('A_rent_32m_7mo','A 32㎡米粉'),('A_rent_25m_12mo','A 25㎡早餐'),('A_rent_25m_reuse_20k','A 如能证实复用2万'),('D_rent_76m_24mo','D 76㎡园区快餐')]:
 q=COND[key];rows.append([lab,money(q['initial_funding']),money(q['base_funding']),money(q['funding_delta'])])
b.table(['条件例','筹资','原预算','变化'],rows,[128,73,73,68],12.3)
b.headline('可复用资产不是“省了一口价”')
b.para('若25㎡早餐铺广告的设备经核对，确认价值2万元的重置项目确可复用，模拟筹资相应减少2万元；并不是已经确认其设备价值或房东合同。',15)
b.tag('真正要确认的问题','这四个例子只有报价线索。高投入仍可能很高：五种标准/高档投入口径另见同条件比较；不能把便宜挂牌当实际资金。',GOLD,PALE)
source('25㎡早餐广告',SRC['rent25']);source('76㎡园区快餐广告',SRC['rent76']);end()
start('zones','02 / 铺面与成本','四类地段，店长要查什么？','这是候选地段的比较方法，不是精确铺位排名。')
b.photo_split([real_tuple('qiaohe_street.jpg','福海桥和路街坊门面 · 2023'),real_tuple('tongtai_foodstreet_01.jpg','福海同泰时代广场 · 2024')],122)
for title,check,co in [('住宅生活街段','居民便利消费、复购；看营业合规、店外等候、邻居、低租与可见性。',TEAL),('成熟餐饮街段','已有包点、饮料、快餐；看同类价位、转让清单、并店竞争和租期。',BLUE),('产业商业街段','工作餐和成人加餐；食堂是实在替代；观察普通成人实际交易与工厂假期。',GOLD),('办公/交通商业','便携、快捷与预约；便利店为替代，看物业条件及总租赁费用。',BROWN)]:
 y=b.y;b.rect(M,y,4,62,co);b.txt(title,M+12,y,CW-20,15.2,INK,'b',20);b.y=b.txt(check,M+12,y+22,CW-20,13.7,MUTED,'r',19)+10
b.tag('最新土地风险','2026年11月新和土地整备单元规划研究曾公开招标；后续公告镜像称投标不足三家废标。不是已确定拆迁或具体铺位时间。签约须查最新规划及解约责任。',RED,ROSE)
source('采购公告（2026.11.05）',SRC['planning']);end()
start('sharing','02 / 铺面与成本','共享铺位，省的是闲置租金','深圳有真实商业尝试，但不同场地、主体、责任与时段不能混用。')
b.photo_split([real_tuple('tongtai_booth.jpg','福海周边档位实拍 · 2024'),(A/'scenario_E.jpg','分区经营生成示意',None)],112)
b.band('真实外地段案例 · 龙华民治（2024）','13,000元/月','整店60–70㎡；午晚市另方承担6,000，早餐方负担7,000，早餐夫妻还聘帮手。非新和租金。')
b.stack([('早餐方',7000,GOLD),('另一方',6000,TEAL)],13000,22)
b.mini_legend([('早餐方','7,000元',GOLD),('另一方','6,000元',TEAL)],2)
b.para('罗湖另有22个独立档口集成排烟、上下水、消防等条件，每户独立证照；不能将其与同一地址两个主体借用一张证混淆。',14.6)
b.tag('必须先过许可和合同','深圳2026年4月官方答复：食品经营许可证原则一地一证。E共享与两个平台上线都以实际经营主体、地址、现场许可获确认及合同成立为前提。',RED,ROSE)
source('深圳合租报道（2024）',SRC['share']);source('市场监管答复（2026.04）',SRC['permit']);end()
start('layout','02 / 铺面与成本','30㎡的门面，要放得下生意','这张示意图是经营逻辑，不是具体房东铺位或工程图。先检查许可条件，再决定租金和设备。')
# illustrative floor plan
y=b.y; b.rect(M,y,CW,235,'#E9ECE4',INK)
# 4 zones
for x,yy,w,h,co,lab,sub in [(M+8,y+10,158,95,LEAF,'备料 / 冷藏','收货、原料、温控'),(M+176,y+10,158,95,PALE,'热制 / 组装','蒸制、加热、清洁'),(M+8,y+117,158,106,ICE,'洗消 / 清洁','洗手、洗消、保洁'),(M+176,y+117,158,106,WHITE,'前台 / 打包','收银、交接、取餐')]:
 b.rect(x,yy,w,h,co,LINE);b.txt(lab,x+8,yy+16,w-16,15.3,INK,'b',20);b.txt(sub,x+8,yy+48,w-16,12.2,MUTED,'r',17)
b.txt('→',M+160,y+42,22,20,GOLD,'b');b.txt('↓',M+246,y+96,20,19,GOLD,'b')
b.y=y+245
b.para('深圳小餐饮标准关注原料与成品、冷热、生熟、洗消与保洁分区。不同模式有不同排烟、火源、电容量、给排水及现场许可。即使小店装修也不能图便宜而跳过。',14.6)
b.tag('装修设备真成本','装修涉及地面墙面、水电、排风、招牌等；买设备还要运输、安装、维护和调试。模型分别计价，实际必须以安装报价和现场条件替换。',GOLD,PALE)
source('深圳 DB4403/T 530—2024 小餐饮布局标准',SRC['layout']);source('装修及设备与铺租研究',SRC['property']);end()
# operations
start('procurement','02 / 铺面与成本','设备便宜，不代表厨房工程便宜','以公开可核采购单作量级参照，不是新和小店正式采购或安装报价。')
b.band('深圳供货商 · 哈尔滨食堂项目（2026.06）','82,780元','全部供货安装调试验收。地区、规模、数量不同，只作采购明细的真实对照。')
b.table(['采购实际项目','金额/单价'],[['12盘蒸饭车','1,950元'],['1.5米双层工作台','950元'],['1.5米冷藏操作台','1,800元'],['水池','1,150元'],['油烟净化＋管道＋新风','41,500元']],[220,122],13.5)
b.tag('为什么先看铺','仅烟道、净化、新风整组就可能占项目大头。低档模型假定可复用并通过许可；实际烟道/电路整改、运输和安装必须报价，不随意套用此大型项目价。',GOLD,PALE)
b.note('供应链线索：宝安包点生坯供应、宝安仓蔬菜配送及深圳餐饮食材采购中标；资质、配送范围、起订量、真实价格须询价，未用商业目录作价格。')
source('采购成交结果及分项',SRC['equip']);source('采购、供应和可核成本清单',SRC['property']);end()
start('work','03 / 人和经营','两位合伙人，不是两台机器','老板工资=0元，但每人的知识、时间、工作强度、产能和资金分担都要计算。')
fake('partners',157,'两位经营者分工写实示意（生成）；不是实际店家照片。')
b.bullets([('第一位：制作与食品安全','验收原料、批次备料、加热、味道与温控、报损。'),('第二位：运营与交付','接单收银、包装、平台、进货账、客服、陈列与交接洗消。'),('两人都要会：','采购成本、配方、库存、财务、许可与应急；谁缺技能，需要额外工时或招聘。')])
b.metricline([('普通员工标准雇主预算','7,200元/月','毛薪＋社保等'),('热厨人员另测','1.16万/月','专业技能条件测试')],LEAF)
note('深圳2026最低工资2,700元/月。完整雇员费用按岗位和合同；不是照搬最低工资。所有两人基准工资均为0。')
source('深圳最低工资官方通知',SRC['wage']);source('实际招聘与经营安排研究',SRC['property']);end()
start('wages','03 / 人和经营','招聘广告上的工资，不是完整用工费','新增6项福永招聘资料；这里选其中4项岗位广告，真实班次、吃住、面试工资与劳动合同需核实。')
b.table(['福永岗位广告','月毛薪'],[['纯外卖后厨学徒（首月）','4,000–4,500元'],['厨工/配菜打荷','4,000–5,000元'],['熟练后厨备货出餐','6,000–7,000元'],['早餐面点中工','4,800–5,500元']],[205,137],13.4)
b.headline('模型不是只算员工到手钱')
b.stack([('毛薪示例',5000,BLUE),('雇主社保等准备',1600,TEAL),('餐补/雇主其他预算',600,GOLD)],7200,23)
b.mini_legend([('毛薪示例','5,000元',BLUE),('雇主社保等准备','1,600元',TEAL),('其他预算','600元',GOLD)],3,11.7)
b.band('普通员工标准完整月成本预算','7,200元','真实法定缴费基数、工时、加班、餐补、社保/公积金须按合同确认；非实际已聘。')
b.note('学徒广告2026.03更新，其余公开索引发布时间未见，当前岗位未核；不是同一工作强度。专业厨师单列敏感度，店主两人仍然不计工资。')
source('学徒招聘公开详情', 'https://www.mmsrcw.com/job/305503878.html');source('福永后厨公开招聘索引', 'https://www.zhipin.com/zhaopin/c537cfe9f489845e0HZ-29q7GA~~/');source('福永面点招聘索引','https://www.yupao.com/s/yp15924842/');end()
start('capacity','03 / 人和经营','每天来多少人，和做得到多少单是两回事','模型先模拟商业需求，再用两人实际工作能力和设备限制。不是把人口乘一个百分比就当实际订单。')
x=R['A'];c=x['capacity']
# diagram demand and constraint
b.rect(M,b.y,CW,78,ICE);b.txt('一般商业接触机会 × 假设转化',M+12,b.y+9,CW-24,13.7,NAVY,'b',19);b.fit(f"{whole(x['month12']['demand']['addressable_opportunities'])} × {perc(x['month12']['demand']['conversion'])} ≈ {whole(c['desired_orders'])}单",M+12,b.y+35,CW-24,25,18)
b.y+=87
b.headline('三条上限：看最紧的一条')
for label,val,co in [('全天可服务人分钟',c['day_limit_service_orders'],TEAL),('高峰可服务时段',c['day_limit_peak_orders'],GOLD),('设备能力',c['day_limit_equipment_orders'],BLUE)]:
 yy=b.y;b.txt(label,M,yy,CW*.6,14,MUTED,'b',19);b.right(whole(val)+'单/日',W-M,yy,17,INK)
 vmax=max(c['day_limit_service_orders'],c['day_limit_peak_orders'],c['day_limit_equipment_orders']);b.rect(M,yy+24,CW,10,GRAY);b.rect(M,yy+24,CW*val/vmax,10,co);b.y+=43
b.band('同时考虑需求与三条上限',whole(c['realized_orders'])+'单/日',f"A标准基准第12月；两人各{c['partner_daily_hours_each']:g}小时，实际雇员{c['paid_staff']}名。")
b.tag('新增员工并不总是合算','若一位员工月成本7,200元、每单只余3元、每月26天，需要额外92单/日才能覆盖工资。订单需求、技能、峰时若不足，人数增加反而会提高亏损。',GOLD,PALE)
note('这里的机会数、转化、出餐时间均为模型假设；没有本地客流/顾客复购实测。')
end()
start('delivery','03 / 渠道','一笔外卖15元，最终留下多少？','A标准基准，第12个月示例。把商家到账和利润分开。两平台分别计算，基准费率刻意一样，实际合同未知。')
x=R['A']['month12'];u=x['channel'][1]['unit'];q=x['channel'][2]['unit']
# receipt style
b.rect(M,b.y,CW,66,DARK);b.txt('商品标价',M+12,b.y+12,137,14,WHITE,'b',18);b.right(yuan(u['list_ticket']),W-M-12,b.y+12,30,WHITE);b.txt('不含消费者另付骑手配送费',M+12,b.y+45,CW-24,11.2,'#DDE9DE','r',15);b.y+=78
for lab,v in [('减商家优惠、预计退款',u['discount']+u['refund']),('减技术/交易服务费',u['platform_fee']),('减商家承担配送',u['delivery_fee']),('减食材（含损耗）',u['food_cost']),('减包装、税费等',u['packaging']+u['tax_budget']+u['payment_fee']+u['host_fee'])]:
 yy=b.y;b.txt(lab,M,yy,CW*.67,14,INK,'r',19);b.right('−'+yuan(v),W-M,yy,15.2,RED);b.line(M,yy+26,W-M,yy+26,LINE,.7);b.y+=31
b.band('每单给房租等固定支出的余额',yuan(u['contribution']),'尚不是净利润；平台技术费、配送、活动承担、包装、退款每项都要确认。')
b.metricline([('美团商家每单留下',yuan(u['contribution']),'基准估算'),('淘宝闪购每单留下',yuan(q['contribution']),'基准估算')],LEAF)
note('美团官方规则：实际费率后台展示。淘宝闪购交易费与配送履约分别规定，支付宝入口若同一后台不重复计。实际当地商户合同、菜单和费用未取到。')
source('美团商户规则',SRC['mt']);source('淘宝闪购配送技术服务协议',SRC['tbdelivery']);end()
start('channels','03 / 渠道','外卖不是凭空多出一批订单','三种渠道比例只是情景。线下与外卖共享同一个厨房，顾客和订单不能重复加。')
for lab,on,dl in [('线下经营',100,0),('混合经营',75,25),('外卖较多',40,60)]:
 b.headline(lab)
 b.stack([('现场',on,TEAL),('美团',dl/2,BLUE),('淘宝',dl/2,GOLD)],100,28)
 b.note(f'现场 {on}%   |   美团 {dl/2:g}%   |   淘宝闪购 {dl/2:g}%')
b.para('在线上真正新增订单以前，先分配同一个需求池；未来如果实证平台获得额外需求，才修改模拟。平台也会增添接单、核单、打包、交接工作量。',14.7)
b.tag('开通不是只交佣金','开通物料、平台保证金、每月推广、优惠、退款、包装、商家配送、账期，即使顾客价更贵也可能留下更少。店中店/共享须先验实际主体与许可。',GOLD,PALE)
source('网络餐饮平台食品安全监管规定',SRC['deliverylaw']);end()
start('modes','04 / 模式导航','做法不止一种。每种都算完整账。','点图进入经营方式；产品、两人分工、开办、每月现金、三年和退出一条线。')
for k,x in R.items():
 y=b.y;b.img(A/f'scenario_{k}.jpg',M,y,102,84);b.rect(M,y,4,84,PAL[k]);b.txt(k+'  '+N[k],M+115,y+3,CW-115,15.2,INK,'b',21);b.txt(f"{whole(x['opening']['area'])}㎡ · 筹资{money(x['opening']['initial_funding'])}",M+115,y+33,CW-115,14.1,MUTED,'r',19)
 b.right('查看 →',W-M,y+59,12.3,PAL[k]);b.link((M,y,W-M,y+84),target=k+'1');b.y+=92
note('五张照片均为生成经营情景示意，不是现有门店。所有模式标准情景及其他投入档/需求/渠道分别比较；不指定首选。')
end()
# five differentiated chapters, shared financial grammar only where comparisons benefit.
PRODUCT={
'A':{'title':'吃得惯，拿得到','menu':'包点＋蛋＋豆浆；粥、米粉、面少品类','tickets':[6,8.5,10],'real':'baozi_food.jpg','realcap':'深圳同类包点 · 实拍','focus':'稳定口味、速度、单价','risk':'蒸制与打包同时来单；保温、剩货和等待。','skills':'蒸批、质量与温控；订单收银和包装；低SKU试销。','place':'住宅生活商业及成人通勤消费；有成熟同类品类。','flow':['备料','蒸制','保温','装袋','补货洗消']},
'B':{'title':'特色要有付溢价的理由','menu':'饭团、鸡蛋蔬菜三明治＋奶或无糖饮','tickets':[10,12.5,16],'real':'sandwich_combo.jpg','realcap':'深圳同类便携组合 · 实拍','focus':'携带方便、配方标准','risk':'冷链、短保期和更贵食材；高客单不保证复购。','skills':'配方与冷热分区；效期、包装与自提订单。','place':'社区和办公、成人通勤；便利店、连锁快餐同样便携。','flow':['备料','冷藏','组装','包装','效期盘点']},
'C':{'title':'加一件商品，也加一层库存','menu':'早餐热食＋奶、水、原味酸奶、少量包装零食','tickets':[8,10,13],'real':'nearby_snack_haoye_2024.jpg','realcap':'福海相邻零食商铺 · 实拍（CC0）','focus':'同一订单的搭配、加购','risk':'库存资金、临期、货架陈列；不把每个加购当新客。','skills':'热食批量生产；货架、有效期、陈列与盘点。','place':'家庭/居民及成人加餐；便利店、零食集合店直接竞争。','flow':['进货','备餐','陈列','组合售卖','盘点报损']},
'D':{'title':'把租了一天的铺，用多个时段','menu':'早餐＋午间简餐；下午加餐或晚餐另做验证','tickets':[13,16,22],'real':'tongtai_foodstreet_05.jpg','realcap':'福海周边简餐门面 · 实拍','focus':'相同食材设备复用，分时需求','risk':'高峰人手、专业热厨、食堂10–14元替代；不假设全天无休。','skills':'热厨、批次生产、控制交叉污染；轮班、前台与洗消。','place':'产业生活复合街段，午晚时段成人需求必须实测。','flow':['早备料','早餐','午间简餐','加餐/晚餐','清场']},
'E':{'title':'只租使用时段，责任却不能分半','menu':'少SKU早餐；借鉴独立档位、按时段与许可经营','tickets':[6,8,10],'real':'tongtai_booth.jpg','realcap':'福海周边小食档位 · 实拍','focus':'合作分摊场地、物料和清洁交接','risk':'房东同意、现场许可、另一方退出、存货及资产归属。','skills':'限定时段、交接卫生；独立合同、账目、费用和退出。','place':'可独立许可、经房东同意的物理档位或真实分时合作。','flow':['入场交接','备料','售卖','收款','清洁交接']},
}
def pathphoto(fn):
 if fn in PHOTO4:return A/fn,PHOTO4[fn]['source_url']
 return AS/fn,PH[fn]['source_url']
def recovery_label(v):return '第'+str(int(v))+'月' if v else '36月内未覆盖'
def ym(n):return ('−' if n<0 else '')+whole(abs(n))+'元'
def tval(items,key):return next((i['amount'] for i in items if i['key']==key),0)
def chainrow(label,value,delta=None,c=TEAL):
 y=b.y;detailh=b.h(delta,CW-24,11.7,'r',15.7) if delta else 0;hh=29+detailh+7
 b.rect(M,y,CW,hh,WHITE,LINE);b.rect(M,y,5,hh,c)
 b.txt(label,M+12,y+6,CW*.53,12.8,MUTED,'b',17);b.right(value,W-M-11,y+4,22.4,RED if value.startswith('−') else c,'b',CW*.46)
 if delta:b.txt(delta,M+12,y+29,CW-24,11.7,MUTED,'r',15.7)
 b.y+=hh+10
 if delta is not None:b.txt('↓',W/2-5,b.y-9,12,11,c,'b',13)
for k,x in R.items():
 p=PRODUCT[k];o=x['opening'];c=x['capacity'];m=x['month12'];yrs=x['years'];ex=x['exit'][1];co=PAL[k]
 # 1 visual field guide
 start(k+'1',ch(k),p['title'],N[k]+' · '+f"标准档 {whole(o['area'])}㎡",co)
 fp,link=pathphoto(p['real'])
 b.photo_split([(A/f'scenario_{k}.jpg','经营情景生成示意',None),(fp,p['realcap'],link)],120 if k=='E' else 134)
 b.headline('核心产品怎么组合？')
 b.para(p['menu'],15.0)
 b.rect(M,b.y,CW,55,PALE);b.txt('现场单均价 低 / 基准 / 高（试销假设）',M+9,b.y+6,CW-18,11.8,BROWN,'b',16)
 b.fit(' / '.join(yuan(v) for v in p['tickets']),M+9,b.y+24,CW-18,22,15,INK,'b')
 b.y+=64
 b.headline('一条工作线，两个人协作')
 # 5 steps horizontal, short words
 ww=(CW-12)/5; yy=b.y
 for i,st in enumerate(p['flow']):
  xx=M+i*(ww+3);b.rect(xx,yy,ww,48,LEAF if i%2==0 else ICE);b.txt(st,xx+4,yy+9,ww-8,12.8,INK,'b',17)
  if i<4:b.txt('→',xx+ww-3,yy+14,13,11,GOLD,'b',13)
 b.y+=57
 b.note('甲：'+c['role1']+'；乙：'+c['role2']+'。')
 b.metricline([('两人每日投入',f"{c['partner_daily_hours_each']:g}小时/人",'均不计工资'),('标准模拟雇员',str(c['paid_staff'])+'人','规模增加可招聘')],LEAF)
 b.tag('能力与风险',p['skills']+' '+p['risk'],co,GRAY)
 note('客户/选址：'+p['place'].rstrip('。；')+'；需实测。')
 end()
 # 2 Opening detailed
 start(k+'2',ch(k),'开门那天，哪些钱要准备？','标准投入／基准市场／混合渠道。装修和设备为逐项预算，不是商铺现成的完整报价。',co)
 b.band('两位合计开业筹资',money(o['initial_funding']),'每人约'+money(o['initial_each_50_50'])+'（假设各50%）。老板工资均0元。',DARK)
 b.stack([('已付或占用',o['start_spent_or_tied'],GOLD),('留在账户',o['account_reserve'],TEAL)],o['initial_funding'],22)
 b.metricline([('实付／占用',money(o['start_spent_or_tied']),'押金和存货也占现金'),('周转备用',money(o['account_reserve']),'留在账上，并非已花掉')])
 # compacts detailed 9 items in 2 column lists incl reserve
 b.headline('每项预算不能丢')
 groups=o['categories']
 vals=[(z['label'],money(z['amount']),col) for z,col in zip(groups,[GOLD,BLUE,RED,BROWN,TEAL,'#97A56E','#93A7B2','#B9A07E',DARK])]
 b.mini_legend(vals,3,11.8)
 top=sorted(groups[1]['items'],key=lambda q:q['subtotal'],reverse=True)[:3]
 note('设备大项示例：'+'；'.join(z['name']+' '+money(z['subtotal']) for z in top)+'。')
 note('月租'+money(o['monthly_rent'])+'；面积及合同是假设。若接手价含已可用设备、押金/装修，逐项扣重叠。低/标准/高档见横向对照。')
 end()
 # 3 vertically integrated chain includes opening, order, margin, actual cash and short-term exit.
 start(k+'3',ch(k),'从一单到月账，再到现金',f"标准基准，第12月；开业筹{money(o['initial_funding'])}，其中{money(o['account_reserve'])}留在账户。",co)
 b.rect(M,b.y,CW,62,ICE)
 b.fit(f"{whole(c['realized_orders'])} 单/日  ×  {m['days']}天",M+10,b.y+9,CW-20,23,16,NAVY,'b')
 b.txt(f"假设需求{whole(c['desired_orders'])}，模拟完成{whole(c['realized_orders'])}；两人各{c['partner_daily_hours_each']:g}小时",M+10,b.y+38,CW-20,11.8,MUTED,'r',16);b.y+=70
 # 3 line channel table, explicit prices and unit contribution
 rows=[]
 for each in m['channel']:
  u=each['unit'];rows.append([each['label'],f"{whole(each['daily_orders'])}单",yuan(u['list_ticket']),yuan(u['contribution'])])
 b.table(['渠道','约日单','标价/单','扣变动后'],rows,[96,72,86,88],12.8)
 # actual income, itemized monthly costs with compact arithmetic
 variable=m['variable_cost'];fixed=m['fixed_cost']+m['staff_change_cost'];net=m['net_sales'];op=m['operating_profit'];cash=m['cash_flow'];con=m['order_contribution']
 chainrow('净销售收入',ym(net),f"标价{ym(m['order_value_listed'])}－券{ym(m['merchant_discount'])}－退{ym(m['refund_allowance'])}",BLUE)
 chainrow('扣订单变动成本',ym(con),'减原料、损耗、包装、平台配送等 '+ym(variable),TEAL)
 chainrow('经营结余',ym(op),'再减固定及调整费 '+ym(fixed),TEAL if op>=0 else RED)
 chainrow('经营净现金',ym(cash),'再扣库存/应收变化、维修 '+ym(op-cash),TEAL if cash>=0 else RED)
 note(f"正常月固定费用{money(m['fixed_cost'])}：租金{money(tval(m['fixed_items'],'rent'))}、其他{money(m['fixed_cost']-tval(m['fixed_items'],'rent')-tval(m['fixed_items'],'staff_payroll'))}、员工{money(tval(m['fixed_items'],'staff_payroll'))}；两位工资0。收入与订单为近似汇总，原始计算未舍入。")
 # one line final meaning (fit y)
 b.tag('不是每个月都赚这个数',f"第12月保本约{whole(m['break_even_order_daily'])}单/日；首年平均每月{money(yrs['annual'][0]['avg_monthly_profit'])}；半年退出两位累计{loss(ex['total_net_investor_loss'])}。",co,LEAF)
 end()
 # 4 long-term
 start(k+'4',ch(k),'三年经营，钱回到哪里？','经营结余、现金流、两人分到手的钱是三件不同的事。',co)
 # cumulative 36 month
 months=yrs['monthly'];a=[z['cumulative_business_cashflow'] for z in months]
 b.headline('累计经营现金流 vs 开门支付或占用')
 b.chart([('累计经营净现金',a,co),('开业实付或占用',[o['start_spent_or_tied']]*36,GOLD)],132)
 b.table(['期间','每月平均结余','两人年分配'],[[f"第{z['year']}年",money(z['avg_monthly_profit']),money(z['distributed_to_partners'])] for z in yrs['annual']],[76,142,124],13.3)
 b.metricline([('36月经营净现金',money(yrs['business_cashflow_36']),'店铺累计现金产生'),('每人累计分配',money(yrs['each_distribution']),'两人各半；非工资')],LEAF)
 b.row('现金覆盖开业付款',recovery_label(yrs['deployed_recovery_month']))
 b.row('现金覆盖全部筹资',recovery_label(yrs['all_funding_recovery_month']))
 note(f"经营末账户留存 {money(yrs['cash_36'])}；额外筹资 {money(yrs['additional_capital'])}。分配要求先满足储备；这些是模型结果，非已拿回投资。")
 end()
 # 5 exit; narrative day vs actual loss same page
 start(k+'5',ch(k),'做不下去，真正损失是多少？','标准基准第6个月清算。如果没有实际合同和清算估值，只能给条件测算。',co)
 b.headline('关店当天：账户、回收、费用')
 # formula row direct, sign in words to avoid negative sign confusion
 b.metricline([('店内现金',money(ex['remaining_cash']),'退出前'),('资产回收',money(ex['asset_recovery_total']),'押金、设备、货款'),('退出费用',money(ex['exit_cost_total']),'租约、结清、清场')],GRAY)
 b.row('当天净需追加',money(ex['net_exit_payment_needed']),'先垫后收可能需要 '+money(ex['exit_day_bridge_before_recovery']),RED if ex['net_exit_payment_needed']>0 else TEAL)
 b.headline('两位合伙人的总账')
 items=[('最初筹资＋后来追加',ex['initial_funding']+ex['additional_capital_before_exit']+ex['net_exit_payment_needed']),('减已经分到的钱',-ex['cumulative_distributions']),('减关店拿回的钱',-ex['returned_cash_at_exit'])]
 b.waterfall(items,'累计终局损失／两位合计',ex['total_net_investor_loss'],loss_mode=True)
 b.note('每位若按50/50：'+loss(ex['loss_per_partner'])+'；当天净追加并不等于累计损失。')
 b.table(['退出时点','全店净损失/收益','每位若各半'],[[f"{z['exit_month']}月",loss(z['total_net_investor_loss']),loss(z['loss_per_partner'])] for z in x['exit']],[78,144,120],13)
 note('回收值、退租、设备变卖、库存与员工清算均为假设；不是亏损上限。偏弱市场另见后表。')
 end()
# comparative and field validation
start('cross','05 / 同条件比较','不能只看能赚多少钱','先把三档开业金额及面积放在一起：低/标/高是规模与合同组合，不是市场好坏。基准需求、混合渠道。')
b.table(['方式','低投入','标准','高投入'],[[SN[k],*[money(z['initial_funding'])+'\n'+whole(z['area_m2'])+'㎡' for z in x['comparisons']['investment']]] for k,x in R.items()],[108,78,78,78],12.6)
b.headline('标准档：钱是否被固定锁住？')
for k,x in R.items():
 o=x['opening'];y=b.y;b.txt(k+'  '+SN[k],M,y,CW*.58,13.8,INK,'b',19);b.right(money(o['initial_funding']),W-M,y,15.5,INK)
 b.rect(M,y+23,CW,13,GRAY);a=o['start_spent_or_tied']/o['initial_funding'];b.rect(M,y+23,CW*a,13,GOLD);b.rect(M+CW*a,y+23,CW*(1-a),13,TEAL);b.y+=47
note('橙色已付/占用；绿色账户备用金。低档的低转让费用假设确有房东直租或可复用设施，不等于找到了可租门面。')
end()
start('unit_compare','05 / 同条件比较','每单留下的钱，差别在哪里？','第12月，标准投入、基准需求。商品标价和扣除变动费用后的余额；不含月房租和固定人力。')
b.headline('线下订单 · 元/单')
rows=[]
for k,x in R.items():
 u=x['month12']['channel'][0]['unit'];rows.append([SN[k],yuan(u['list_ticket']),yuan(u['food_cost']),yuan(u['packaging']+u['payment_fee']+u['tax_budget']+u['host_fee']),yuan(u['contribution'])])
b.table(['模式','售价','食材损耗','其余','余额'],rows,[94,58,68,60,62],11.8)
b.headline('美团订单 · 元/单（淘宝基准合同假设相同）')
rows=[]
for k,x in R.items():
 u=x['month12']['channel'][1]['unit'];rows.append([SN[k],yuan(u['list_ticket']),yuan(u['food_cost']),yuan(u['platform_fee']+u['delivery_fee']),yuan(u['contribution'])])
b.table(['模式','标价','食材损耗','平台+运','余额'],rows,[94,58,68,64,58],11.5)
b.note('外卖另扣商家券、预计退款、包装与税费等。两平台合同真实费率未验证；每种模式的全部金额与完整逐单数学见互动附件。')
end()
start('margin','05 / 同条件比较','毛利、营业结余和现金，都不是一回事','以第12月A为例，把每一层的钱怎么变少画清楚。以净销售收入为起点，不重复计算商家券。')
x=R['A']['month12']
food=tval(x['variable_items'],'food_consumption')
b.waterfall([('净销售收入',x['net_sales']),('食材含正常损耗',-food),('其他订单变动成本',-(x['variable_cost']-food)),('固定营业与调整费',-(x['fixed_cost']+x['staff_change_cost']))],'经营结余（非可分配）',x['operating_profit'])
b.headline('五种模式：食材毛利率与经营结余')
rows=[]
for k,z in R.items():
 m=z['month12'];g=(m['net_sales']-tval(m['variable_items'],'food_consumption'))/m['net_sales'];rows.append([SN[k],perc(g),money(m['operating_profit']),money(m['cash_flow'])])
b.table(['模式','食材毛利率','经营结余','经营净现金'],rows,[101,85,78,78],12.4)
note('这里的食材毛利仅扣食材与损耗，后面还要付包装、平台配送、月租、人手等。经营结余再扣周转变化和维修得到净现金；会计摊销另在原始数据。')
end()
start('fixed_compare','05 / 同条件比较','每月还有哪些固定账单？','第12月标准基准。金额包含租金、管理费、水电基础、其他运营、门店和平台推广、员工完整雇主成本。')
for k,x in R.items():
 m=x['month12'];b.headline(k+'  '+SN[k])
 b.note('房租 '+money(tval(m['fixed_items'],'rent'))+' · 物业 '+money(tval(m['fixed_items'],'property_fee'))+' · 水电 '+money(tval(m['fixed_items'],'utilities_fixed'))+' · 其他 '+money(tval(m['fixed_items'],'other_fixed')))
 b.note('门店推广 '+money(tval(m['fixed_items'],'store_marketing'))+' · 平台推广 '+money(tval(m['fixed_items'],'platform_marketing'))+' · 员工 '+money(tval(m['fixed_items'],'staff_payroll'))+' ｜ 合计 '+money(m['fixed_cost']))
 b.line(M,b.y-4,W-M,b.y-4,LINE,.7)
note('两人亲自经营工资均0元；真实水电管理费、平台推广合同及员工需按实际报价更新。')
end()
start('profit_compare','05 / 同条件比较','市场变化，比模式名称更重要','投入不变（标准档）、混合渠道。首年平均每月结余，均未扣两位合伙人工资。')
vals=[[z['y1_avg_monthly_profit'] for z in x['comparisons']['demand']] for x in R.values()]
colors=[[INK,*[RED if z<0 else TEAL for z in a]] for a in vals]
b.table(['经营方式','偏弱','基准','偏好'],[[SN[k],*[money(z) for z in row]] for k,row in zip(R,vals)],[108,78,78,78],12.9,colors)
b.headline('如何读这张表？')
b.bullets([('偏弱：','客单、需求偏弱；原料和损耗承压；竞争更早进入。'),('基准：','成熟需求与价格假设；相邻竞争会分流。'),('偏好：','价格与客流均较有利，但产能不一定跟得上。不是概率预测。')])
b.tag('钱不足的时候不必继续烧','模型假设继续三年，会记录需要额外投入的资金；实际可以缩小规模、调整品类或退出。不要把未来三年均值当成每月工资。',RED,ROSE)
end()
start('compare_channels','05 / 同条件比较','做外卖多了，首年会怎样？','保持标准投资和市场基准，总需求不自动新增。外卖比例不同，但厨房产能是同一个。')
rows=[[SN[k],*[money(z['y1_avg_monthly_profit']) for z in x['comparisons']['channel']]] for k,x in R.items()]
b.table(['经营方式','全现场','混合','外卖较多'],rows,[108,78,78,78],13.1)
b.headline('两平台费率差一点，一年差多少？')
a=[i for i in F['platform_asymmetry_tests'] if i['mode']=='A' and i['field']=='delivery_cost']
if len(a)>=2:
 b.metricline([('美团单侧多2元配送',money(a[0]['y1_delta']),'首年月均结余变化'),('闪购单侧多2元配送',money(a[1]['y1_delta']),'首年月均结余变化')],ICE)
b.para('相同假设不代表真实两平台收费一样。应向各商户后台核对订单、优惠承担、配送、技术、退款和账期，再单独重算。合规前提下E才可启用外卖。',14.8)
source('淘宝闪购商户交易服务协议',SRC['tb']);source('美团招商规则',SRC['mt']);end()
start('stress_evidence','05 / 真实证据怎样改变账','看见新信息，就要改一笔账','这一次不只是新增数据，还把新证据的经营含义放进条件测试。保持其他假设不变，并不把案例直接当本地平均值。')
d0=R['D']['years']['annual'][0]['avg_monthly_profit']
b.headline('D：园区公共食堂替代10–14元')
rr=[('原模型现场客单16元',d0,TEAL,''),('假设压至14元',COND['D_canteen_price_14']['y1_avg_profit'],GOLD,''),('假设压至12元',COND['D_canteen_price_12']['y1_avg_profit'],RED,'')]
b.barrows(rr,True)
b.tag('为什么变？','外面已有低价食堂。售价降低没有自动让买来的食材变便宜，按原食材绝对成本不变重算。',GOLD,PALE)
b.headline('E：另一方退租，租金谁承担？')
e0=R['E']['years']['annual'][0]['avg_monthly_profit']
b.barrows([('标准场地费3,000',e0,TEAL,''),('若承担7,000元',COND['E_occupancy_7000']['y1_avg_profit'],RED,''),('若承担整租13,000元',COND['E_partner_leaves_13000']['y1_avg_profit'],RED,'')],True)
note('图中都是首年平均月经营结余；共享案例来自深圳龙华，非新和真实合作报价。食堂价格也不等于店铺必须卖同价。')
end()
start('people_stress','05 / 经营能力','会不会做菜，就是一笔投资变量','规模越大，技能和产能越可能决定实际收益。D标准基准，若必须聘专业厨师，另做独立条件测算。')
s=next(z for z in R['D']['skilled_special_cases'] if z['tier']=='base' and z['scenario']=='base')
b.metricline([('两位能做专业热厨',money(s['funding_base']),'开业筹资'),('必须聘专业厨师',money(s['funding_skilled']),'开业筹资')],LEAF)
b.table(['关键数字','两位有技能','需要员工'],[['首年月均结余',money(s['y1_avg_profit_base']),money(s['y1_avg_profit_skilled'])],['半年累计退出损失',loss(s['m6_loss_base']),loss(s['m6_loss_skilled'])],['首人完整雇主预算','0元','11,600元/月']],[148,97,97],13.0)
b.para('两人的工资为0并不等于所有技能免费。需要专业员工时，岗位工资、法定负担、休息、峰时和客户服务都要纳入；不能假定两个人无限工作。')
b.image(A/'scenario_partners.jpg','岗位情景示意（生成），并非经营者实拍。',123)
g=next(z for z in R['D']['comparisons']['demand'] if z['scenario']=='good');b.tag('规模不同，人手不同',f"D较好市场标准档模拟最多聘{g['staff_max']}名员工；聘员和额外完整雇主支出由订单、技能、峰时及设备约束决定。",GOLD,PALE)
end()
start('time_cost','05 / 经营能力','不计老板工资，但时间不是免费','以下按两人各半分配、首年工作时长模拟，计算已分现金与本人实际工时的关系。不是员工工资或可保证的收益。')
rows=[]
for k,x in R.items():
 y=x['years']['annual'][0];rows.append([SN[k],whole(y['partner_hours_each'])+'时',yuan(y['actual_distribution_per_partner_hour'])])
b.table(['模式','每位首年工时','每小时已分配'],rows,[137,105,100],13.0)
b.image(A/'scenario_partners.jpg','两人经营生成情景；实际工时和技能需亲自核验。',118)
b.tag('两个人到底够不够','标准档只作两人基准；如果高峰拥堵、设备不够或专业技能缺失，就按工资与额外可交付订单决定是否聘人。')
b.note('钱按现金分配口径；还可能有账户留存和未回收资金。不是经营结余折算劳动小时，也不是建议压低自身报酬。')
end()
start('compete','05 / 敏感与竞争','同一种生意，为什么有人活下来？','竞争者模仿、价格内卷、原料变化、客户回购都可能改变贡献额。')
b.headline('A标准：只变一个数字的首年月均结余变化')
se=[v for v in F['sensitivity'] if v['mode']=='A']
keys=['潜在需求少20%','线下售价低10%','食材采购贵10%','每月租金贵20%','两平台商家配送每单贵2元']
bar=[]
for key in keys:
 z=next((x for x in se if x['test'].startswith(key)),None)
 if z:bar.append((key,z['y1_monthly_profit_delta'],RED,''))
b.barrows(bar,True)
b.para('基础盘是品质与卫生、稳定供货、速度、消费者信任；对手压价时要用真实每单余额重新算，而不是盲目跟价。',14.6)
b.tag('V4实质模型纠正','旧版单因素降价联动了食材成本，新版固定采购成本的元数再计算。基准135组合原模型不变，只有同因素测试纠正。',GOLD,PALE)
end()
start('weak_exit','05 / 退出对照','如果市场偏弱，多久退出代价不同？','标准投入＋混合渠道＋偏弱市场。以下单位万元；正数是净损失，负数是净收益，非损失上限。')
b.table(['方式','3月','6月','12月','24月'],[[SN[k],*[f"{z['total_net_investor_loss']/10000:.1f}" for z in x['weak_exits']]] for k,x in R.items()],[90,63,63,63,63],11.6)
b.headline('如何看退出，不只是看当初多少钱')
b.para('已经付出的装修与净转让、可退押金、设备残值、未结库存/应收、清场、租约、员工结清、追加和已分配现金必须同一结算口径。',15)
b.tag('能退出，不代表能拿回本金','短租或合租的实际合同决定能否继续；若资产回收拖延还需短期过桥垫付。取得书面合同、清算报价再改退出参数。',RED,ROSE)
end()
start('verify','06 / 从研究到经营','还缺什么？先低成本验证。','不替读者做决定。用小额、合法的实测处理影响最大的未知，而不是先交高额转让费。')
# step path
for i,(t,d) in enumerate([('01  房源和合规','找3类公共商业街段，同条件各问3个真实合同、转让明细、外摆、排烟、用电。查土地规划与房东同意、经营许可。'),('02  实际商品与顾客','合法实地菜单核价；成年人及家庭自愿匿名了解早餐、加餐和复购，记录交易，不跟踪未成年人。'),('03  两位亲自试做','合规场地低成本小菜单试卖，记录每单售价、食材、包装、报损、峰时出餐、工作时间。'),('04  外卖账与退出','核两平台商户合同及实际结算、保证金、广告费、账期及退款；以书面退出责任和真实回收报价校准。')]):
 y=b.y;b.circle(M+12,y+14,12,TEAL if i%2==0 else GOLD);b.txt(str(i+1),M+8,y+5,14,13,WHITE,'b',17)
 b.txt(t,M+31,y+1,CW-31,16,INK,'b',21);b.y=b.txt(d,M+31,y+27,CW-31,14.1,MUTED,'r',20)+15
 if i<3:b.line(M+12,y+27,M+12,b.y+4,LINE,2)
b.tag('再更新模型','真实需求、现行租约、报价及费用 → 替换参数 → 复算同样135种条件 → 独立审计 → 再决定是否投资。')
end()
start('operations','06 / 经营与5P','把5P变成每天能执行的事','不是只有产品和价格。两个人、供应商、场地、运营知识，都是这门生意的一部分。')
for tit,body in [('Product 商品','少SKU，配方、分量、卫生、可追溯、明确配料与有效期；同一菜品定期观察实际回购。'),('Price 价格','每笔现场和线上净售价分别扣报损、包装、配送以及促销；单品剩余不足就不能靠规模救。'),('Place 地方','合规用途、租期与总开办资金、水电烟道、交接、客群和渠道。不是只选学校附近。'),('Promotion 推广','招牌、社区口碑、合规试吃及线上页面，用投入÷真实新客、真实复购验证；不买虚假好评。'),('People 人','与顾客清楚沟通；两位合伙人约定股权、分工、加钱、分配、请假、退伙及退出责任；有技能缺口就预算招聘。')]:
 y=b.y;b.txt(tit,M,y,CW,16,TEAL,'b',21);b.y=b.txt(body,M,y+24,CW,14.0,MUTED,'r',19.4)+12;b.line(M,b.y-4,W-M,b.y-4,LINE,.6)
b.tag('供货与安全','至少两家可追溯合规的供应渠道；入货批次检查、温控、效期、清洁、日库存、发现问题停售。实际报价和合同不以网上单价替代。')
end()
start('limits','06 / 证据等级','哪些已知道，哪些还不知道？','这份报告的公开材料与模型彼此关联，但不是实地签约或经营流水。')
b.bullets([('新增本地证据','13份抽检原表；137条新和样品、32受检主体；新和连锁公开自提83项近期价格；2026小学预算；新挂牌正文和剩余租期；深圳共享租赁及园区食堂。'),('新增条件测试','短租到期、两项真实挂牌价、食堂压低客单、共享租金与合租方退出、不同平台单侧费率。基准模型保留，不为了符合直觉故意抬高。'),('仍然不知道','真实门店销售、当地客流与转化、全量在营菜单/计费、实际租约、设备安装成交、实际组织产能和家庭购买比例。'),('工具访问记录','电脑可操作但只连接云端Linux；MacBook/OpenCLI未连接。大众点评搜索进入APP二维码登录；美团、淘宝后台现行本地合同无法获得。没有冒充已登录。')])
b.tag('为什么不直接排名','所有模式的风险来自自己的资金、手艺、渠道、业务条件。本报告只给客观证据和情景，不推荐唯一经营选择。')
end()
start('sources','06 / 原始出处','资料从哪里来（1/2）','重要原始材料可点击；完整明细、来源日期及证据等级在附带研究工程。')
for lab,key in [('福海街道官方概况','gov'),('福新小学2026部门预算','newbudget'),('鹏晖学校官方目录','middle'),('全国儿童早餐地点研究','meal'),('福海园区食堂10—14元报道','canteen'),('新和KFC第三方自提菜单','kfc'),('市监2025年12月抽检通告','check1'),('市监2026年第7期通告','check2'),('新和园区企业公开报告','keyto'),('深圳7-Eleven现场走访价','7eleven'),('新和越师傅公开消费个案','vietnam'),('32㎡米粉剩租及挂牌','rent32'),('五区35㎡挂牌','rent35'),('新福园25㎡早餐店广告','rent25'),('76㎡快餐铺广告','rent76'),('新和土地整备采购公告','planning')]:source(lab,SRC[key])
end()
start('sources2','06 / 原始出处','资料从哪里来（2/2）')
for lab,key in [('深圳共享租赁报道','share'),('深圳罗湖独立档口案例','stall'),('食品经营许可答复','permit'),('深圳小餐饮布局标准','layout'),('深圳最新最低工资通知','wage'),('网络餐饮监管规定','deliverylaw'),('美团商户规则','mt'),('淘宝闪购交易服务协议','tb'),('淘宝闪购配送技术服务协议','tbdelivery'),('完整市场竞争记录及监管样本','competitor'),('铺租、采购成本和运营','property'),('客群、产品和替代研究','customer'),('完整项目与财务方法','repo')]:source(lab,SRC[key])
b.tag('如何复算','研究工程含全部原始链接、结构数据、135个组合/36个月、540个退出、附加条件测试与财务生成脚本。互动情景模拟器另附。')
end()
# photo provenance and credit. Each used V4 source clickable; V2 sources detailed in package.
start('photo_sources','06 / 图像来源','真实照片与经营示意分开','本次新增授权照片库（部分作参考未入正文）。图像仅作商业/公共设施背景，不能证明客流、在营及销量。')
for fn in ['xinhe_bus_terminal_2026.jpg','xinhe_seafood_market_2026_a.jpg','nearby_snack_haoye_2024.jpg','nearby_snack_sku_haoye_2024.jpg','nearby_noodle_haoye_2024.jpg','nearby_chicken_haoye_2024.jpg','nearby_mcdonalds_2026_a.jpg','nearby_mcdonalds_food_2026.jpg']:
 p=PHOTO4[fn];b.note(p['caption']+'｜'+p['author']+'｜'+p['license']);source('原图/许可（版面裁切）',p['source_url'])
note('另有V2邻近真实照片：全部源文件、地点、日期、作者及许可见工程 v2/assets/PHOTO_MANIFEST.json。6幅经营照片为生成示意，并不是当地真实商铺。')
b.finish()
start('photo_sources2','06 / 图像来源','邻近历史照片，出处在这里','原图均非当前新和门店观察。照片保留来源及许可；版面缩放或裁切。')
used=['qiaohe_market.jpg','tongtai_foodstreet_05.jpg','baozi_food.jpg','sandwich_combo.jpg','qiaohe_street.jpg','tongtai_foodstreet_01.jpg','tongtai_booth.jpg']
for fn in used:
 a=PH[fn];b.note(a['caption']+' | '+a['author']+' / '+a['license']);source('原图与授权',a['source_url'])
b.note('生成情景图片不含实际商户；真实店名、菜单价格及抽检来自公开证据，不以生成影像作实证。')
b.finish(final=True)
ov=b.save()
if ov:sys.exit(2)
