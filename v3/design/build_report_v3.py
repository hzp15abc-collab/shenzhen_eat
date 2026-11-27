"""Build the V3 reader-facing mobile report. Only use the frozen, reproducible scenario outputs."""
from pathlib import Path
import json,sys,csv,math
from pdf_engine import *
ROOT=Path(__file__).resolve().parents[2]
V=ROOT/'v3'; OUT=ROOT/'deliverables'/'深圳宝安福海新和社区早餐与休闲零食市场调研及商业可行性分析报告_V3_手机版.pdf'
D=json.loads((V/'models/report_data_v3.json').read_text())
S={x['mode']:x for x in D['selected']}; CASE={x['case_id']:x for x in D['summary']}; IN=D['inputs']
MTH={(x['mode'],x['month']):x for x in D['monthly_selected']}
EX={(x['mode'],x['exit_month']):x for x in D['exit_selected']}
PH={x['filename']:x for x in json.loads((ROOT/'v2/assets/PHOTO_MANIFEST.json').read_text())}
AS=ROOT/'v2/assets'
# Broad Chinese charset supports dynamic report values and all reader-facing narrative.
charset=set(Path(__file__).read_text()+Path(__file__).with_name('pdf_engine.py').read_text()+json.dumps(PH,ensure_ascii=False)+''.join(chr(n) for n in range(32,127))+'㎡·→↓↗−×÷≈%–—／')
b=Book(OUT,''.join(charset),V/'design'/'fonts')
NAMES={'A':'传统早餐','B':'特色便携早餐','C':'早餐＋零食','D':'多时段餐饮','E':'分时合作／店中店'}
SHORT={'A':'传统早餐','B':'特色早餐','C':'早餐＋零食','D':'多时段餐饮','E':'分时合作'}
PAL={'A':GREEN,'B':BLUE,'C':'#A96D49','D':'#7A617E','E':'#78917A'}
MIX='标准投入 · 线下＋外卖 · 基准需求'
REPO='https://github.com/hzp15abc-collab/shenzhen_eat'
def p(key,ch,title,lead=None): b.start(key,ch,title,lead)
def end(): b.footer()
def photo(fn,h=155,extra=''):
 a=PH[fn]; b.image(AS/fn,a['caption']+'；'+a['author']+'，'+a['license']+'，裁切。'+extra,a['source_url'],h)
def amt(x):return money(x,2)
def exact(x):return money(x,exact=True)
def pc(x):return f'{x*100:.1f}%'.replace('.0%','%')
def pay(m):return f'第{int(m)}月' if m else '36个月内未回收'
def ls(x):return ('净亏'+amt(x)) if x>=0 else '净赚'+amt(-x)
def sem(x):return RED if x<0 else GREEN
def ccase(m,t='base',c='mixed',s='base'):return CASE[f'{m}_{t}_{c}_{s}']
def jump(label,comment,target):
 y=b.y;b.rect(22,y,CW,67,PAPER);b.txt(label,34,y+9,16,INK,'bold');b.text(comment,34,y+34,CW-44,12.7,MUTED,'reg',17);b.right('→',W-32,y+12,17,EARTH);b.link((22,y,W-22,y+67),target=target);b.y+=75
def sources(l):b.source(l)
SRC={
'market':'https://www.baoan.gov.cn/xxgk/jgk/jdbsc/content/post_12887016.html',
'primary':'https://www.sz.gov.cn/school/ba/baqxx/content/post_9457858.html',
'middle':'https://www.sz.gov.cn/school/ba/jnygz/content/post_9457237.html',
'income':'https://www.sz.gov.cn/zfgb/2026/gb1416/content/post_12848555.html',
'meal':'https://cnki.istiz.org.cn/kcms/detail/detailall.aspx?dbcode=CJFQ&dbname=CJFD2025&filename=xiws202505008',
'rent1':'https://m.shangpu5.com/zhuanrang/show-12955.html',
'rent2':'https://sz.shangpu5.com/zhuanrang/show-7656.html',
'rent3':'https://m.shangpu5.com/zhuanrang/show-16367.html',
'rent4':'https://sz.sydc.anjuke.com/sp-zhuan/dt69-st3266/',
'price':'https://hk.trip.com/moments/detail/bao-an-district-2015100-156845124/',
'mt':'https://123.meituan.com/serve/web/business/167?moduleMenuCode=0',
'tb':'https://terms.alicdn.com/legal-agreement/terms/b_platform_service_agreement/20230320103053372/20230320103053372.html',
'wage':'https://hrss.sz.gov.cn/tzgg/content/post_12954870.html',
'jobs':'https://www.58.com/ppeseoll30587/',
'medical':'https://hsa.sz.gov.cn/gkmlpt/content/12/12567/post_12567884.html',
'sba':'https://bec.www.sba.gov/breakevenpointcalculator',
'cost':'https://github.com/hzp15abc-collab/shenzhen_eat/blob/main/v3/research/COSTS.md',
'delivery':'https://github.com/hzp15abc-collab/shenzhen_eat/blob/main/v3/research/DELIVERY.md',
'model':'https://github.com/hzp15abc-collab/shenzhen_eat/blob/main/v3/models/MODEL_SPEC.md',
}
# 01 Cover
b.start('cover','封面')
b.rect(0,6,W,300,INK)
b.text('市场观察  /  投资测算  /  退出账本',22,26,CW,13.5,'#DAE7DC','bold',19)
b.text('深圳宝安福海新和社区',22,63,CW,23,'#EBD6BA','bold',29)
b.text('早餐与休闲零食\n市场调研及\n商业可行性分析报告',22,104,CW,30,WHITE,'serif',39)
b.text('给第一次考虑做餐饮的两位合伙人',22,250,CW,15,'#E5E8DB','reg',22)
b.y=323
photo('qiaohe_street.jpg',192,'邻近商圈历史街景，不是新和三区当前照片。')
b.title('先看街坊，再算生意。')
b.para('卖什么、租哪类铺、要准备多少钱、两个人够不够、什么时候能回钱、不做了会亏多少。',17)
b.small('第三版 · 手机阅读版｜2026年11月27日\n公开资料研究＋条件模拟；不替读者决定开哪种店。')
end()
p('toc','阅读导航','从哪一页开始？','先弄懂全局，再跳到你感兴趣的模式。每页底部可返回目录。')
for a,desc,k in [('01  商业全景','一眼看懂五种生意的资金、利润和风险','overview'),('02  街坊和商圈','人群、竞争、报价、产品与铺位','market1'),('03  做生意的账','装修、员工、外卖与经营规则','cost1'),('04  五种模式分解','逐种看开业、出餐、利润、回本与退出','modetoc'),('05  横向比较','投入档、需求情境、竞争与渠道压力','compare1'),('06  调查清单与来源','哪些已证实，哪些必须亲自问清楚','verify1')]:jump(a,desc,k)
end()
p('overview','01  商业全景','开业要准备多少钱？','下面用同一套条件看五种模式。钱不仅要够开张，也要够周转。')
b.bars([(k+'  '+SHORT[k],s['initial_funding'],PAL[k]) for k,s in S.items()])
b.call('比较口径','标准投入、基准市场、75%现场＋25%外卖，两位合伙人工资均为0元。资金含装修设备、进场费、押金、首批货和约3个月固定支出储备。')
b.small('都是假设预算，不是房东或装修公司的正式报价。共享档尚无合作报价。')
end()
p('overview2','01  商业全景','哪些钱能留下？','第一年平均每月经营结余，已扣当月全部模型经营成本，不扣两位合伙人工资。')
b.bars([(k+'  '+SHORT[k],s['y1_avg_monthly_profit'],sem(s['y1_avg_monthly_profit'])) for k,s in S.items()])
b.call('别把经营结余当作自己的工资','店里留下的钱还要应付库存、外卖未到账、维修和备用金。之后才可能给合伙人分钱。D经营时间长，两人各约10小时／营业日，需实测。')
end()
p('overview3','01  商业全景','半年后如果不做了？','同样条件下，第6个月关店，把可退押金、设备折价、清场费用和已收回的钱一起算。')
b.bars([(k+'  '+SHORT[k],s['exit_m6_total_net_investor_loss'],RED if s['exit_m6_total_net_investor_loss']>=0 else GREEN) for k,s in S.items()])
b.call('这不是最大损失','这是模型中的累计净损失。合同违约、无法结清、设备卖不掉、租期变化等可能让实际损失更大。详见各模式的退出账。',ROSE)
end()
p('readmode','01  商业全景','一份报告，三种数','不要把看得见的资料、估出来的预算和真的经营流水混成一件事。')
b.item('已找到的公开信息','公开挂牌、官方规则、街道资料、招聘广告和少量价格实例。逐条注明出处。')
b.item('为了算账的假设','铺面积、成交价格、日订单、出餐时间、利润、损耗和平台费用都按情境设定，等待现场证据替换。',EARTH)
b.item('目前仍然未知','实时本地菜单、真实客流、家庭早餐购买比例、实际租约、平台商家账单、门店真实营业额。',RED)
b.call('所有财务图表均是条件测算','同一个模型跑了135种组合、4,860个月份和540个退场计算。数字约取至十元或百元，原始表保留精度。')
end()
# 02 Market
p('market1','02  街坊与商圈','这里不只是学生市场。','新和在福海街道，社区消费、产业与工作场所需求交织。学校只是其中一部分。')
photo('qiaohe_market.jpg',165,'邻近片区历史街景。')
b.metrics([('福海管理人口','约53万','街道口径，不是单铺客流'),('工矿商贸企业','4,500余家','产业与社区需求并存')])
b.para('住宅区看便利程度和回头客；产业商业区看上下班、午间和工作餐；办公和交通商业看便携与速度。统计不能代替门口实测。',15.9)
sources([('福海街道机构概况（2026）',SRC['market'])]);end()
p('school','02  街坊与商圈','两所学校，需求不能直接相加。')
b.item('福新小学','公开旧目录：公办小学，旧资料记载不提供住宿、配餐。2022年预算为36班、1,798名学生，不是当前在校人数。')
b.item('鹏晖中英文学校','公开旧目录：民办九年一贯制，旧资料记载不提供住宿、堂食。当前供餐安排待核，不能用学校类型推算家庭收入。')
b.call('口径很重要','家庭在家吃、学校供餐、社区外买和成人通勤是不同需求。实际走读、家长接送、独立通勤及外购比例均未获得。不由学生规模推算销量，也不记录儿童行踪。')
sources([('福新小学官方旧目录',SRC['primary']),('鹏晖中英文学校官方旧目录',SRC['middle'])]);end()
p('demand','02  街坊与商圈','早餐到底在哪里吃？','全国跨地区营养调查（2019—2021年，6—17岁，52,535人）的主要早餐地点。仅作背景，不是本地比例。')
# visual percentages
x=22
for val,co in [(66.3,GREEN),(25.8,BLUE),(7.9,EARTH)]:b.rect(x,b.y,CW*val/100,27,co);x+=CW*val/100
b.y+=40
for lab,val,co in [('家中','66.3%',GREEN),('学校','25.8%',BLUE),('其他','7.9%',EARTH)]:b.row(lab,val,'全国样本',co)
b.para('这告诉我们：要研究谁愿意在外面买、买什么、为什么重复来，而不是看到附近有学校就把学生算成顾客。')
b.small('2025深圳全市人均可支配收入84,945元／年，仅全市背景。新和家庭收入及早餐实际预算仍未知。')
sources([('全国调查摘要',SRC['meal']),('深圳2025统计公报',SRC['income'])]);end()
p('group','02  街坊与商圈','四类顾客、四种买单理由','同一个门面可以做不同人的生意，但不能把同一个人重复计入客流。')
b.item('家庭与学龄消费','家长看卫生、配料、价格；孩子喜欢口味和方便。先测咸甜搭配、低糖饮品、分量；不用高糖刺激反复购买。')
b.item('社区住户','早餐、带回家的粥粉面、周末及日常补货；关心稳定品质和熟悉价格。')
b.item('上班族与产业工人','时间紧、拿了就走、饱腹和性价比。食堂、便利店和工作餐是替代品。')
b.item('办公与通勤成人','便携早餐、午后小食、线上预约、短时间取餐；对效率和品质更敏感。')
b.call('不能从宏观人口倒推订单','真实需求通过成人或家庭自愿匿名调查、实际付费试销和复购记录来补。')
end()
p('zones','02  街坊与商圈','四类铺段，各有自己的账。','这是一张商圈选择框架，不是四个位置的实测排名。')
photo('qiaohe_restaurants.jpg',127,'邻近街坊沿街商业。')
b.item('社区住宅商业','复购潜力；需看门面能见度、用途及住户需求。')
b.item('二区成熟商街','餐饮选择多，熟铺与闲时共享机会需谈；竞争、转让费可能更高。')
b.item('产业商业','富桥、新兴等成人工作餐需求；企业食堂和工厂假期影响。')
b.item('办公及交通商业','便携、特色产品机会；租金、便利店替代和时段波动。')
end()
p('comp','02  街坊与商圈','竞争对手不只有早餐店。','已有公开店铺线索：前版26条商户名，V3补充公开索引、实际转让广告及价格个案。不是在营普查。')
photo('qiaohe_noodle.jpg',136,'邻近真实面食店门面。')
b.item('直接竞争','潮州早餐、包子、汤包、肠粉、粉面、粥；速度、口味、价格各不同。',GREEN)
b.item('跨品类替代','便利店、快餐、手抓饼与茶饮、法棍、家庭及校内供餐；抢的是同一顿饭。',BLUE)
b.item('经营好坏尚未知','点评数、平台销量标签、店员自述均不能证明利润；本轮没有拿到真实账本。',RED)
end()
p('product','02  街坊与商圈','产品不是越多越好。','先做清楚主力商品、组合和能否重复购买；品类潜力要用真实售价、工时与损耗验证。')
photo('sandwich_combo.jpg',129,'深圳同类产品样本，非新和店。')
b.item('传统：稳定刚需','包点、粥、蛋、豆浆、粉面。配成约6—10元组合测试。')
b.item('特色：有理由付溢价','饭团、三明治、法棍、日式或西式便携早餐；试10—16元价带，注意冷藏损耗。')
b.item('零食：有复购但占库存','常温包装零食、水、牛奶、少糖饮品；小份轻食。试家庭认可与库存周转。')
b.small('以上价格都是试销价带，不是本地实价。新和越师傅消费个案：法棍＋蛋21元、鸡腿卷8元、蒜香片3元。')
sources([('2026年11月10日用户消费记录',SRC['price'])]);end()
p('rent','02  街坊与商圈','租金低，不代表接手便宜。','本轮找到22条去重挂牌：新和14条，相邻7条，宽区1条；4条有完整详情正文。都是卖方广告，不是成交。')
b.row('32㎡ 米粉店','月租 3,040元','转让费4.2万元；新和公开索引')
b.row('42㎡ 黄焖鸡','月租 5,000元','转让费11万元；二区详情')
b.row('45㎡ 饺子馆','月租 4,500元','转让费面议；一区详情')
b.row('100㎡ 自助快餐','月租 5,000元','转让费15.5万元；二区详情')
b.call('同样80㎡也差很大','新和二区公开索引：牛杂店7,600元/月、茶饮店16,300元/月。未核在租、餐饮许可、签约日期和条件，不可算片区成交均价。')
sources([('42㎡黄焖鸡挂牌',SRC['rent1']),('100㎡自助快餐挂牌',SRC['rent2']),('45㎡饺子馆挂牌',SRC['rent3']),('32㎡米粉挂牌索引',SRC['rent4'])]);end()
p('rent2','02  街坊与商圈','一个42㎡店面，怎么算进场钱？','卖方详情写着月租5,000元、转让11万元、剩余租期12个月。')
b.flow([('转让费（挂牌）','11万元','可能含已有装修、设备或转租权益。',SAND),('首月租金（挂牌）','5,000元','另假设两个月押金10,000元。',ICE),('尚未重新装修、购买设备','12.5万元','转让＋首租＋假设押金，尚未核重叠。',LIGHT)])
b.call('合同先于装修','只为收回11万元转让费，12个月平均每月需9,167元可回收资金。先查房东同意、剩余租期、续约、设备清单与押金归属。不要再重复支付已含资产。',ROSE)
sources([('卖方详情原文',SRC['rent1'])]);end()
# 03 Cost and operations
p('cost1','03  做生意的账','开店的钱分成三袋。','不是一笔钱全花掉。同一个门面，预算高低取决于租约、可复用资产、面积和设备。')
b.flow([('第一袋：买店的能力','一次性花费','装修、设备、净转让费、证照准备与开业。',SAND),('第二袋：被占住的钱','有机会回来','租房押金、平台保证金、库存。',ICE),('第三袋：留在账户的钱','周转储备','模型以约3个月固定支出为储备目标，不是永久成本。',LIGHT)])
b.call('别把转让费重复计入','广告可能含设备、装修、租金或押金。模型未确认资产组成，转让暂按净进场费、设备另购。真正签约时要按清单扣重叠。')
end()
p('cost2','03  做生意的账','装修、设备，不能只写一个总数。','深圳2026供应商公开报价存在不同施工范围。报价广告不是实际合同。')
b.metrics([('30㎡轻饮店 半包例','2.6万元','全案展示例4.2万元'),('轻餐施工广告','800—1,500元/㎡','不同标准与包含项')])
b.item('30㎡传统早餐示例','标准档装修3.3万元，按1,100元/㎡预算。含基础施工、水电、排烟等规划项目，既有条件需实际看铺。')
b.item('设备逐项预算','蒸制设备、冷柜、加热灶、工作台、水槽、收银、消毒、封口、运输安装均计。公开蒸柜报价约1,598元仅是单个产品价格。')
b.call('本报告没有为了显得真实故意抬高预算','5种业务、3档设备和装修逐项数量×单价；清单及原报价在研究包。实际排烟整改和消防等若超出预算，必须重算。')
sources([('装修及设备来源与逐项预算',SRC['cost'])]);end()
p('people','03  做生意的账','两个人不开工资，也要算体力。','假设两位合伙人共同做生意，工资账为0。做多久、会不会做、忙时够不够，不能省略。')
b.item('合伙人一：制作与品质','备货、加工、食材温控、出餐标准、清洁、损耗。')
b.item('合伙人二：接单与经营','收银、顾客沟通、标签、包装、进货、平台、核账；高峰也参与制作。')
b.item('两个人的协作','不能同时开多条复杂生产线；一个人请假、采购、休息时都要有替班计划。')
b.metrics([('普通店员完整月预算','7,200元','标准情境；范围5,800—8,800元'),('专业厨师月预算','1.08—1.25万','另按技能压力测试')])
b.small('福海招聘广告有4,000—5,000元店员、8,000—9,000元厨师。深圳2026最低工资2,700元/月；雇主社保公积金、补贴等另外计。')
sources([('深圳最低工资官方通知',SRC['wage']),('公开招聘索引',SRC['jobs'])]);end()
p('capacity','03  做生意的账','不是顾客多了，就多请人。','高峰人手和设备是共同上限。多一位员工，也不一定多卖够他的工资。')
b.flow([('两位合伙人','各8.5小时','以A为例；全天有效售卖工时700人分钟，已扣杂务。',ICE),('忙时真正可用','234人分钟','每单约2.4人分钟，约62%订单集中于忙段。',SAND),('两人模拟上限','约157单/日','234 ÷ (2.4 × 62%)；设备上限390单/日。',LIGHT)])
b.call('增加一位员工','标准完整月成本7,200元。若每单剩3元、每月26天，要多卖约92单/日才覆盖工资；实际加人提升可能不到这个数。')
end()
p('platform','03  做生意的账','外卖是另一条渠道，不是另一间店。','两位合伙人、同一厨房、同一出餐能力。模型用一个总订单池拆开，不把线上再加一次。')
b.item('美团外卖','公开入驻FAQ：开店申请免费，实际技术及配送等费用随服务方案变化。历史公开技术费6%—8%，不等于门店现行合同。')
b.item('淘宝闪购','淘宝／支付宝相关入口（原饿了么生态）按实际后台归属，不能重复算三条渠道；公开合同有交易、履约及物流等费用。')
b.item('不是顾客付多少就到手多少','商家券、退款、技术费、配送费、包装、原料和广告都影响盈利。')
b.call('本轮没有取得当地实际账单','两平台基准费率故意设相同，用7%技术费、4元商家承担配送费作试算；不能据此说哪个平台更便宜。')
sources([('美团官方商户FAQ',SRC['mt']),('淘宝闪购商户协议公开入口',SRC['tb'])]);end()
p('channel','03  做生意的账','三种渠道组合，是三种生意。')
for lab,on,dl in [('只做线下',100,0),('线下＋外卖',75,25),('外卖较多',40,60)]:
 b.title(lab)
 b.rect(22,b.y,CW*on/100,23,GREEN);b.rect(22+CW*on/100,b.y,CW*dl/100,23,BLUE) if dl else None
 b.y+=30;b.small(f'现场 {on}%   ·   外卖 {dl}%（其中两平台各半）')
b.call('开通外卖也需要额外的钱','一次性开业准备费、平台保证金、包装和设备；每个月推广，订单内商家折扣、退款、平台与配送费。基准保证金美团0、闪购1,000元只是预算。')
b.small('不给补贴永远存在、线上自动增加新客、月销量等未经验证的假设背书。E共享模式须先确认独立许可及平台审核。')
end()
p('people2','03  做生意的账','五件事决定店能否持续做。','把5P翻译成每天要做的事。')
for lab,body in [('Product｜商品','几款主力、组合价、卫生与营养、可复制口味、出餐和损耗。'),('Price｜价格','单个商品卖价与整单贡献；优惠后能不能赚钱。'),('Place｜地方','餐饮用途、物业水电排烟、租期、普遍可达性、共享分时合同。'),('Promotion｜推广','门面招牌、社区口碑、成人消费者试吃、外卖页面；小预算验证实际复购，不买虚假好评。'),('People｜人','顾客类型、两位老板的技能、增员成本、股权分工、休假及决策约定。')]:b.item(lab,body)
b.call('供应链','至少两家可追溯供应商；食品经营资质、收货温控、有效期、清洁和每日报损必须执行。')
end()
# 04 Each model full causal narrative.
p('modetoc','04  五种经营模式','想看哪一种？','每个模式都从一间具体规模的店、订单、每月利润、三年现金和退出算起。')
for k,x in S.items():jump(k+'  '+NAMES[k],f"标准面积{x['area_m2']:.0f}㎡，开业筹资{amt(x['initial_funding'])}",k+'1')
b.call('比较口径保持一致','标准档、基准需求、混合渠道；两位合伙人工资均为0。不是五项投资建议。')
end()

INTRO={
'A':('粥粉面、包点、豆浆与蛋','吃得惯、买得快','qiaohe_congee.jpg','面点、蒸制、粥品与快出餐；集中备料、菜单少，分开定价，注意早间等候和剩货。','适合检验基础餐的稳定性、速度和价值感。客单不高，单日订单和损耗影响很大。'),
'B':('饭团、三明治、法棍等便携餐','多一点特色，能否多卖几元','sandwich_combo.jpg','便携主食＋蛋白质＋饮品，先测3—5款；不把昂贵新品或新颖包装等同持久复购。','能承受较高定价取决于味道和便利；材料冷藏、损耗、外卖包装都会吃掉差额。'),
'C':('传统早餐＋包装零食、饮品','同一顾客能不能顺手多买一点','tongtai_snack.jpg','食品标签、库存保质期与早餐制作分开；饮水、少糖、常温小食和便捷加餐；不要只追高毛利零食。','货架占用、低周转与临期损耗可能抵销新增销售；同一订单的加购不能再算新增顾客。'),
'D':('早餐、简餐、下午茶或轻晚餐','租一天的店，能否多做几个时段','tongtai_foodstreet_05.jpg','共享基础食材、错峰备货；不同时段要独立测试菜单和人力。夜餐或宵夜不是本模型保证覆盖。','两人各10小时／营业日的强度很高；热厨技能、设备和轮班可能需要增员，不能假设全日全天候营业。'),
'E':('闲时共享档口／店中店','不用独立租整间店的另一种经营','tongtai_booth.jpg','借鉴现成档口的低占用思路，限定时段、少品类。真实共享业主尚无报价，也没有合作成立证据。','必须独立核验许可、房东同意、用电/清洁、收益分成、库存保管和平台门址；未获许可不启用外卖。')}
for k,s in S.items():
 ch='04  '+k+'｜'+NAMES[k]; name,why,fn,desc,lim=INTRO[k];m=MTH[k,12];x=EX[k,6];inp=IN['market'][k]['base'];st=IN['startup'][k]['base'];lb=IN['labor'][k]['base']
 p(k+'1',ch,why,name)
 photo(fn,159,'仅作业态或产品形态参考，不是本案拟租铺。')
 b.metrics([('标准面积',f"{s['area_m2']:.0f}㎡",'假设的业务规模'),('开业资金',amt(s['initial_funding']),'包括留存周转金')])
 b.para(desc,15.5);b.call('最大的约束',lim)
 b.small(MIX+'。后续各页保持同一情境。');end()
 p(k+'2',ch,'准备开门，要把钱带够。','标准档：装修设备逐项预算，转让费暂按净权益进场费，押金和储备不是已花完的成本。')
 parts=[('装修',s['fitout'],EARTH),('设备',s['equipment'],BLUE),('转让费',s['transfer'],RED),('开业杂费',s['preopening'],COLORS[3]),('外卖开通',s['delivery_setup'],GREEN),('租房押金',s['lease_deposit'],COLORS[4]),('平台保证金',s['platform_deposit'],COLORS[7]),('首批货',s['opening_inventory'],COLORS[5]),('现金储备',s['reserve'],INK)]
 b.hero('第0月需筹资金（两位合计）',amt(s['initial_funding']),f"各承担约 {amt(s['initial_funding']/2)}（假设各半）")
 b.stack(parts,columns=3)
 b.small(f"实际支付或占用 {amt(s['initial_opening_outlay'])}，留下 {amt(s['reserve'])} 周转；月租 {amt(m['rent'])}。平台合同及资产组成未核。")
 end()
 p(k+'3',ch,'同一模式，换铺面多少钱？','低／标／高是投入情景，不是好坏排名；它们可以遇到同样的市场，也可能遇到不同租约。')
 b.bars([(lab,ccase(k,t)['initial_funding'],co,f"{ccase(k,t)['area_m2']:.0f}㎡ · 月租{amt(IN['market'][k][t]['rent'])} · 转让{amt(ccase(k,t)['transfer'])}") for t,lab,co in [('low','低投入',GREEN),('base','标准投入',BLUE),('high','高投入',EARTH)]])
 b.title('标准设备的部分明细')
 items=sorted(st['equipment_items'],key=lambda z:z['subtotal'],reverse=True)[:3]
 for z in items:b.small(f"{z['name']}  {z['qty']}×{z['unit_price']:,.0f}元 ＝ {z['subtotal']:,.0f}元")
 b.call('什么时候要重算','低档假定可合法复用设施、无需顶手费；高档若真有可用原设备就扣重复。现有装修、施工和共享条件以书面合同为准。')
 end()
 p(k+'4',ch,'订单从哪里来？','第12个月的条件算例。没有实测店前总人流，不使用学生人数或平台评分估订单。')
 b.flow([('日等效商业接触机会（假设）',f"{m['addressable_opportunities']:,.0f}人次",f"新客与老客互斥，综合转化约{pc(m['conversion'])}。此处不是实际人流。",ICE),('考虑季节、爬坡、竞争后',order(m['desired_total_daily'])+'/日',f"开业爬坡{pc(m['ramp'])}，季节{pc(m['season'])}，竞争保留{pc(m['competition'])}；总订单在渠道间分。",SAND),('能实际完成的订单',order(m['realized_daily'])+'/日',f"现场约{order(m['actual_onsite_daily'])}，外卖约{order(m['actual_delivery_daily'])}；未完成约{order(m['lost_daily_orders'])}。",LIGHT)])
 b.small(f"两位各{m['partner_daily_work_hours_each']:g}小时／营业日，本月{m['days']}天，合计{m['partner_total_hours_month']:.0f}人小时；雇员{m['paid_staff']}名。高峰{m['peak_person_min']:.0f}人分钟，设备约{m['equipment_capacity_day']:.0f}单/日。")
 b.call('复购不是再次乘销量','老客占比在需求池中变化，成熟客户回流已包含在转化里。真实复购率未测，不能重复相加。')
 end()
 p(k+'5',ch,'一单的钱，分别留下多少？','第12月单笔售价与成本。每个数字都是模型预算，不是平台真实订单。')
 for c,lab in [('onsite','现场'),('meituan','美团外卖'),('taobao','淘宝闪购')]:
  get=lambda field:m[f'{c}_{field}_per_order']
  val=get('list_ticket'); cont=get('contribution')
  b.title(lab+' · 标价 '+yuan(val))
  cats=[('优惠退款',get('discount')+get('refund'),EARTH),('食材含损耗',get('food_cost'),BLUE),('包装',get('packaging'),COLORS[3]),('平台＋配送',get('platform_fee')+get('delivery_fee'),RED),('支付／分成／税费',get('payment_fee')+get('host_fee')+get('tax_budget'),COLORS[4]),('每单剩下',cont,GREEN)]
  b.stack([z for z in cats if abs(z[1])>.0001],total=val,columns=3)
  if c!='onsite':b.small(f"技术费 {yuan(get('platform_fee'))}；配送 {yuan(get('delivery_fee'))}；券 {yuan(get('discount'))}；退款 {yuan(get('refund'))}。")
 b.small('剩下的是用来付房租等固定费用的钱，还不是利润。两平台实际合同未知，基准费率刻意设相同。')
 end()
 p(k+'6',ch,'一个月实际能留下多少钱？','第12个月（较成熟月份），不是第1年平均。')
 b.metrics([('本月完成',order(m['total_orders']),f"{m['days']}营业日"),('净销售额',amt(m['recognized_revenue']),'减商家券及退款后')])
 b.small(f"现场约{order(m['onsite_orders'])}×{yuan(m['onsite_revenue_per_order'])}；美团及闪购各约{order(m['meituan_orders'])}×{yuan(m['meituan_revenue_per_order'])}。")
 b.bridge([('货品净销售额',m['recognized_revenue'],''),('食材（含损耗）',-m['food_consumption'],''),('包装＋平台＋配送',-(m['packaging_cost']+m['platform_tech_fee']+m['merchant_delivery_cost']),''),('支付／共享／税费预算',-(m['payment_fee']+m['host_fee']+m['tax_risk_allowance']),''),('每月固定支出',-m['total_fixed_cost'],''),('人手调整费',-m['staff_change_cost'],'')],m['operating_profit'],'本月经营结余',compact=True)
 b.small(f"每日保本约 {order(m['break_even_daily_orders'])}：{amt(m['total_fixed_cost'])} ÷ {yuan(m['contribution_per_order'])} ÷ {m['days']}天。两位工资为0元。")
 end()
 p(k+'7',ch,'赚的钱不一定都在账户里。','上一页固定支出和资金周转继续拆开。')
 b.stack([('月租',m['rent'],EARTH),('物业',m['property_fee'],BLUE),('基础水电',m['utilities_fixed'],COLORS[3]),('其他运营',m['other_fixed'],COLORS[4]),('门店推广',m['store_marketing'],COLORS[5]),('平台推广',m['platform_marketing'],RED),('员工雇主费',m['staff_payroll'],GREEN)],columns=3)
 b.small(f"固定支出{amt(m['total_fixed_cost'])}，老板工资0。如聘员则按人数计完整工资预算；本情境本月{m['paid_staff']}名。")
 b.bridge([('经营结余',m['operating_profit'],''),('库存资金变化',-m['inventory_change'],''),('平台应收变化',-m['receivables_change'],''),('设备维护投入',-m['maintenance_capex'],'')],m['business_cashflow'],'本月经营现金净流量',compact=True)
 b.small(f"近似会计利润（含假设摊销）{amt(m['accounting_profit'])}；现金储备目标{amt(m['required_cash_reserve'])}，本月可分配示例每位{amt(m['distribution_per_partner'])}，不是每月固定提款。")
 end()
 p(k+'8',ch,'三年后，回本了没有？','36个月持续模拟；如果钱不足，会记录必要追加，非建议一直撑下去。')
 arr=[MTH[k,i]['cumulative_business_cashflow'] for i in range(1,37)]
 b.lineplot([('累计经营现金流',arr,PAL[k]),('开门时实际支出或占用',[s['initial_opening_outlay']]*36,EARTH)],None,height=148)
 b.metrics([('首年均月结余',amt(s['y1_avg_monthly_profit']),'不扣老板工资'),('第二年均月结余',amt(s['y2_avg_monthly_profit']),'含竞争和成本增长')])
 b.row('第三年均月结余',amt(s['y3_avg_monthly_profit']))
 b.row('覆盖开业支付',pay(s['capital_recovery_month']),'不含留存初始备用金')
 b.row('覆盖全部筹资',pay(s['all_funding_recovery_month']),'含备用金及追加资金')
 b.small('回本是累计经营净现金覆盖投入的测算，不是老板已经拿回同额现金。')
 end()
 p(k+'9',ch,'两位最后可以分多少钱？','按每季、没有累计补款时，才取超出3个月固定支出储备的50%；两位各半仅举例。')
 b.metrics([('36月累计经营净现金',amt(s['cumulative_business_cashflow']),'不是累计分红'),('累计需追加',amt(s['total_capital_calls']),'经营缺口才投入')])
 b.bars([(str(i)+'年  两位合计分配',s[f'y{i}_distributed_to_partners'],GREEN) for i in (1,2,3)])
 b.row('三年合计分配／每位',amt(s['partner_distribution_each']))
 b.row('第36月账户留存',amt(s['cash_balance_m36']),'含营运储备，不等于可自由分红')
 b.call('两位老板的工时没有付工资','如果希望将本人的时间换成市场薪酬，要另做机会成本对比。这里按需求只计算真正支付的工资；不要把两人分配当员工薪资。')
 end()
 p(k+'10',ch,'如果经营半年就退出？','把清算日收支和之前的经营一起看。基准情境，第6个月。')
 b.metrics([('退出当天总费用',amt(x['exit_cost_total']),'租约、清场、杂费、员工结清'),('资产回收估计',amt(x['asset_recovery_total']),'押金、旧设备、存货、应收')])
 b.small(f"当天店里原有现金 {amt(x['remaining_cash'])}。若回收延迟，先垫付 {amt(x['exit_day_bridge_before_recovery'])}；回收后净追加 {amt(x['net_exit_payment_needed'])}。")
 b.bridge([('开业筹资',x['initial_funding'],''),('累计追加',x['additional_capital_before_exit'],''),('退出净追加',x['net_exit_payment_needed'],''),('减已经分到手的钱',-x['cumulative_distributions'],''),('减退出退回的钱',-x['returned_cash_at_exit'],'')],x['total_net_investor_loss'],'两位合计累计净损失',compact=True,loss_mode=True)
 b.small(f"若各承担50%，每位 {ls(x['loss_per_partner'])}。净损失为负即净赚；回收率、退租和违约费用均是假设，不代表损失上限。")
 end()
 p(k+'11',ch,'什么时候退出，代价不同。','同样标准投入、混合渠道和基准需求，在第3、6、12、24月分别结清。')
 for i in (3,6,12,24):
  xx=EX[k,i];b.row(f'第{i}个月退出',ls(xx['total_net_investor_loss']),f"每位{ls(xx['loss_per_partner'])}；净追加{amt(xx['net_exit_payment_needed'])}",RED if xx['total_net_investor_loss']>0 else GREEN)
 b.small(f"第6月回收拆分：租房押金{amt(x['lease_deposit_recovery'])}、平台保证金{amt(x['platform_deposit_recovery'])}、设备{amt(x['equipment_recovery'])}、库存{amt(x['stock_recovery'])}、应收{amt(x['receivable_recovery'])}。")
 b.small(f"退场费用：租约{amt(x['lease_exit_charge'])}、员工{amt(x['staff_exit_cost'])}、清场{amt(x['clearance'])}、杂费{amt(x['unsettled_misc'])}。")
 b.call('设备与押金不一定卖得出或退得回','基准房租押金回收75%、设备初始58%并按月份递减、存货50%，装修与转让回收暂为0；退租按合同情景计算。核实后重新跑。',ROSE)
 end()
# 05 Comparative dimensions
for idx,keys in enumerate(['ABC','DE']):
 p('compare1' if idx==0 else 'compare1b','05  横向比较','市场好坏，差多少？'+(' 上' if idx==0 else ' 下'),'标准投入＋混合渠道：首年平均月经营结余。不是预测或概率。')
 for k in keys:
  b.title(k+'  '+SHORT[k]);vals=[ccase(k,s=ss)['y1_avg_monthly_profit'] for ss in ('bad','base','good')]
  b.metrics([('偏弱',amt(vals[0]),'情景'),('基准',amt(vals[1]),'情景'),('较好',amt(vals[2]),'情景')])
 if idx==1:b.call('同一模式，不同市场','弱市场可能持续失血；好市场仍受人手与设备的限制。投入档与市场好坏应独立比较。')
 end()
p('compare2','05  横向比较','各模式真正的保本门槛。','标准混合基准，第12个月；订单要超过静态保本量，店才有经营结余。')
for k,s in S.items():
 m=MTH[k,12]
 b.row(k+'  '+SHORT[k],f"约{m['break_even_daily_orders']:.0f}单/日",f"模拟完成{m['realized_daily']:.0f}单/日；每单余{yuan(m['contribution_per_order'])}",GREEN if m['realized_daily']>=m['break_even_daily_orders'] else RED)
b.call('固定开支 ÷ 单笔贡献 ÷ 营业天数','算不出保本单量时，先看每单贡献是否为正，再谈规模。保本门槛不是客流量；还需预留现金。')
end()
for idx,keys in enumerate(['ABC','DE']):
 p('compare3' if idx==0 else 'compare3b','05  横向比较','更多外卖，利润怎样？'+(' 上' if idx==0 else ' 下'),'标准投入、基准市场，每月经营结余的首年平均。总需求不自动增长。')
 for k in keys:
  b.title(k+'  '+SHORT[k]);vals=[ccase(k,c=c)['y1_avg_monthly_profit'] for c in ('onsite','mixed','delivery_heavy')]
  b.metrics([('全现场',amt(vals[0]),'100%现场'),('混合',amt(vals[1]),'25%外卖'),('外卖较多',amt(vals[2]),'60%外卖')])
 if idx==1:b.call('外卖获客不是免费的','真实外卖增量必须实测，再按实际费用、额外包装和接单时间重新计算。')
 end()
p('compare4','05  横向比较','亏损会不会要继续投入？','标准投入、混合渠道、偏弱市场。下面是若仍持续经营36个月，预计必须再筹的资金。')
b.bars([(k+'  '+SHORT[k],ccase(k,s='bad')['total_capital_calls'],RED) for k in S])
b.call('不是越投入越好','现金断裂时可停业、调整或退出。持续36个月是假设的压力测试，不是经营承诺；停得早和停得晚的损失不同。')
end()
for idx,keys in enumerate(['ABC','DE']):
 p('weak_exit'+str(idx),'05  横向比较','市场偏弱，退出代价'+(' 上' if idx==0 else ' 下'),'标准投入、混合渠道；偏弱市场。如果在不同月份卖设备、清算关店，预计两位合计净损失。')
 for k in keys:
  b.title(k+'  '+SHORT[k]);weak=ccase(k,s='bad')
  for i in (3,6,12,24):
   yy=b.y;b.txt(f'第{i}月',22,yy,14.5,MUTED,'bold');v=weak[f'exit_m{i}_total_net_investor_loss'];b.right(ls(v),W-22,yy,16,RED if v>0 else GREEN);b.line(22,yy+28,W-22,yy+28);b.y+=33
 if idx==1:b.call('早退或晚退的代价不同','净损失计已投、追加、回收和分配，不等于单看哪天拿不出钱，也不是最大可能亏损。')
 end()
p('compare5','05  横向比较','竞争复制了你的产品怎么办？','三种情景都考虑竞争分流、成本变化、季节和开业爬坡。以下为模型的假定冲击，不是已知会发生的事件。')
b.item('偏弱情景','原料价与损耗承压，售价与日订单低；第7月起模拟竞争分流17%，年租金上升5%。',RED)
b.item('基准情景','第19月起模拟竞争分流7%，年租金增3%，食材等进价增2.5%。',BLUE)
b.item('较好情景','需求、价格较好、损耗下降；第25月起竞争分流3%，年租金增2%。',GREEN)
b.call('复购不是护城河的口号','卫生、口味稳定、供货、效率、口碑与组织管理才是长期因素。若大家都降价，要同时改竞争份额和真实贡献，不能仅改日订单。')
end()
p('hiring','05  横向比较','规模变大，两位伙伴可能不够。','模型按季度评估是否需要付费员工，比较额外单量能否覆盖完整雇主支出。')
example=ccase('D',s='good')
b.metrics([('D标准档较好市场',f"{example['staff_max']}名",'模拟最多同时雇员'),('第12月实际日单',order(example['m12_realized_daily']),'受共同人力与设备约束')])
b.row('首年员工费用',amt(example['y1_staff_payroll']))
b.row('第二年员工费用',amt(example['y2_staff_payroll']))
b.para('普通岗位招聘样本与雇主成本已计入。不具备热厨能力则还需按专业厨师预算、重新排班，可能降低现金结余。')
b.call('不能无条件把两人的劳动力当无限','模型的投入、雇佣和产能是假设；真实工作时长、服务压力和休息须实地验证。合伙人请假、专技缺失也要重算。')
end()
p('skilled','05  横向比较','如果两位不会掌勺呢？','D多时段餐饮，标准投入＋混合渠道＋基准市场。用额外专业厨师完整月成本11,600元另跑一次。')
cook=list(csv.DictReader(open(V/'models/skilled_cook_sensitivity_v3.csv',encoding='utf-8-sig')))[1]
b.metrics([('两位具备热厨能力',amt(float(cook['funding_base'])),'开业筹资'),('需聘专业厨师',amt(float(cook['funding_skilled'])),'开业筹资')])
b.row('首年每月结余｜不聘',amt(float(cook['y1_avg_profit_base'])))
b.row('首年每月结余｜聘厨师',amt(float(cook['y1_avg_profit_skilled'])),'每月平均',RED)
b.row('第6月退出损失｜不聘',amt(float(cook['m6_loss_base'])))
b.row('第6月退出损失｜聘厨师',amt(float(cook['m6_loss_skilled'])),'两位合计',RED)
b.call('经营能力就是财务参数','是否真的需要厨师、能不能轮班，是一项投资条件，不能只以房租和客单决定。')
end()
p('sensitivity','05  横向比较','哪几个数字值得先核实？','A标准混合基准，逐一改变一个条件，首年平均月经营结余相对原值的变化。其他参数保持不动。')
with open(V/'models/sensitivity_v3.csv',encoding='utf-8-sig') as fh:sens={r['test']:float(r['y1_monthly_profit_delta']) for r in csv.DictReader(fh) if r['mode']=='A'}
b.bars([(lab,sens[key],sem(sens[key])) for key,lab in [('潜在需求少20%','日需求少20%'),('线下售价低10%','现场售价低10%'),('食材采购贵10%','采购贵10%'),('每月租金贵20%','租金贵20%'),('两平台商家配送每单贵2元','外卖配送每单贵2元')]])
b.small('每条变化是相对基准每月结余，不是五个冲击叠加。完整54项单因素试算见研究包。')
end()
p('competition','05  横向比较','投资之前，还要做哪几道题？','不要只看收入，逐项确认经营方式是否能成立。')
b.item('分时合作是否真的可签？','书面同意、经营许可、独立收款、用电排烟、清洁交割、食材和库存、分成、损坏责任、退出。')
b.item('供货与餐饮管理','进货追溯、库存盘点、食材温控、日报损、设备清洁、固定配方、代班；做一个小菜单，让两个伙伴先练顺。')
b.item('合伙协议与知识','各出多少钱、股权及分红、岗位与工时、是否加钱、借款、亏损承担、退伙估值、谁签字、税务与合同责任。')
b.item('推广要有账','试营业前后真实留存、现场及平台独立订单、一次自付活动预算与复购收益；区分销售额、毛利、获客成本。')
end()
# 06 Evidence and next actions
p('verify1','06  现场验证与来源','先把这几件未知变成事实。','此版桌面调研并非实地经营验证；让现场报价和小规模实测替换假设，才会更接近自己的生意。')
b.item('一：找3类可租铺','每类至少3个同条件书面报价：租期、押金、顶手费、可复用资产、排烟/消防/电容/上下水、物业水电。')
b.item('二：验证商品价格和选择','每个主要品类至少5个可比菜单；记录同店规格、渠道、优惠、包装。成人与家庭自愿匿名调查，不采集孩子行踪。')
b.item('三：付费小批试销','在合规资质与场地，实测日订单、每单耗时、平均客单、报损、重复交易及外卖处理。工作日周末都测。')
b.item('四：真正的外卖合同','让美团、淘宝闪购分别出技术费、配送、优惠承担、保证金、账期和退款示例；共享档必须核验主体。')
end()
p('verify2','06  现场验证与来源','哪些来源已经真的查过？','可以直接打开来源。详细资料、22条挂牌和全部参数在研究包。')
for label,url in [('福海街道：区域概况',SRC['market']),('深圳2025统计公报',SRC['income']),('两校：福新小学',SRC['primary']),('两校：鹏晖中英文',SRC['middle']),('全国早餐地点研究',SRC['meal']),('新和42㎡转让详情',SRC['rent1']),('新和100㎡转让详情',SRC['rent2']),('新和45㎡转让详情',SRC['rent3']),('越式早餐消费个案',SRC['price']),('深圳最低工资官方文件',SRC['wage']),('深圳医疗保险缴费通知',SRC['medical']),('美团官方入驻FAQ',SRC['mt']),('淘宝商户公开协议',SRC['tb']),('通用盈亏平衡公式（SBA）',SRC['sba'])]:sources([(label,url)])
b.call('查询边界','网站公开页／索引可取，第三方详情有访问验证；未获得本地实时平台菜单或商家合同，不写成已有数据。')
end()
p('verify3','06  现场验证与来源','如何阅读完整算账材料？','电脑里打开可复算模型，手机上看图和比较。报告的条件、证据、场景与计算逐层对应。')
b.item('135种组合','5种经营方式 × 3档投入 × 3个渠道组合 × 3个市场情景。')
b.item('4,860个月份记录','每种组合36个月；订单量、售价、成本、员工、库存、平台回款、现金、分配。')
b.item('540种退出情景','每个组合分别在第3、6、12、24月退出，包含清算日净补款、先垫后收、回收和累计损失。')
b.item('真实照片如何用','照片为有授权的邻近福海历史街景或深圳同类产品实拍。并非今天在新和拍摄；每处有作者、时间、许可与原图链接。')
sources([('完整研究、流程、模型与复算说明',REPO),('详细财务口径',SRC['model'])]);end()
p('photo1','06  现场验证与来源','照片原始出处（1/2）','本报告未把生成图用作现场照片。真实照片保留原图出处；版面使用裁切。')
used=['qiaohe_street.jpg','qiaohe_market.jpg','qiaohe_restaurants.jpg','qiaohe_noodle.jpg','qiaohe_congee.jpg','sandwich_combo.jpg','tongtai_snack.jpg','tongtai_foodstreet_05.jpg','tongtai_booth.jpg']
for fn in used[:5]:
 a=PH[fn];b.small(a['caption']+'｜'+a['author']+'｜'+a['license'])
 sources([('原始照片',a['source_url']),('许可条款',a['license_url'])])
end()
p('photo2','06  现场验证与来源','照片原始出处（2/2）')
for fn in used[5:]:
 a=PH[fn];b.small(a['caption']+'｜'+a['author']+'｜'+a['license'])
 sources([('原始照片',a['source_url']),('许可条款',a['license_url'])])
b.call('从这里开始做自己的账','先把报价、试销、人工、合同数据填进模型，再比较五种方式。开哪种、不做哪种，由两位合伙人结合自己的经验、现金与风险承受力决定。')
b.footer(final=True)
ov=b.save()
if ov:sys.exit(2)
