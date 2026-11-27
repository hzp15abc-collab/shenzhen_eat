from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from pathlib import Path
import csv, json, math, re, html
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'deliverables'/'Shenzhen_Eat_商业可行性研究.pdf'
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
W,H=A4; M=38; CW=W-2*M
NAVY='#173D39'; GREEN='#297361'; MINT='#DDECE6'; CREAM='#F8F5ED'; AMBER='#CA833D'; PALE='#F8E5CD'; CORAL='#BF594D'; ROSE='#F5E0DB'; INK='#243B38'; MUTED='#647875'; LINE='#D9E1DB'; WHITE='#FFFFFF'
c=canvas.Canvas(str(OUT),pagesize=A4, pageCompression=1)
c.setTitle('深圳新和社区｜早餐、零食与轻餐饮商业可行性研究')
c.setAuthor('Shenzhen Eat 商业研究项目')
pg=0; y=0
def col(v): return HexColor(v)
def rect(x,t,w,h,fill=WHITE,stroke=None,r=0):
    c.setFillColor(col(fill)); c.setStrokeColor(col(stroke or fill)); c.setLineWidth(.7)
    if r:c.roundRect(x,H-t-h,w,h,r,fill=1,stroke=bool(stroke))
    else:c.rect(x,H-t-h,w,h,fill=1,stroke=bool(stroke))
def line(x1,t1,x2,t2,color=LINE,width=.8):
    c.setStrokeColor(col(color));c.setLineWidth(width);c.line(x1,H-t1,x2,H-t2)
def text(s,x,t,w=CW,size=11.4,color=INK,bold=False,leading=None):
    s=html.escape(str(s).replace('−','-').replace('–','-')).replace('\n','<br/>')
    sty=ParagraphStyle('body',fontName='STSong-Light',fontSize=size,leading=leading or size*1.47,textColor=col(color),wordWrap='CJK',spaceAfter=0,allowWidows=1,allowOrphans=1)
    p=Paragraph(s,sty); _,h=p.wrap(w,9999);p.drawOn(c,x,H-t-h)
    return h
def num(s,x,t,size=28,color=NAVY):
    c.setFillColor(col(color));c.setFont('Helvetica-Bold' if str(s).isascii() else 'STSong-Light',size);c.drawString(x,H-t-size*.82,str(s))
def image(name,x,t,w,h):
    p=ROOT/'design'/f'{name}.jpg'; c.drawImage(str(p),x,H-t-h,w,h,preserveAspectRatio=False,mask='auto')
def end():
    global pg,y
    if y>H-48: print('OVERFLOW',pg,round(y,1))
    line(M,H-39,W-M,H-39)
    text('SHENZHEN EAT  /  研究日期 2026.11.27',M,H-30,350,8,MUTED)
    c.setFont('Helvetica-Bold',9);c.setFillColor(col(GREEN));c.drawRightString(W-M,H-30-7,f'{pg:02d}')
    c.showPage()
def page(k,title,sub=''):
    global pg,y
    if pg:end()
    pg+=1
    rect(0,0,W,H,CREAM)
    rect(0,0,W,8,NAVY)
    text(k.upper(),M,29,CW,10,GREEN)
    h=text(title,M,49,CW,26,NAVY,leading=31)
    y=57+h
    if sub:y+=text(sub,M,y,CW,10.6,MUTED,leading=15)+10
    else:y+=12
    line(M,y,W-M,y);y+=15
def heading(s):
    global y
    y+=text(s,M,y,CW,15,GREEN,leading=21)+7
def para(s, size=11.4,color=INK):
    global y
    y+=text(s,M,y,CW,size,color)+9
def callout(title,body,kind='green'):
    global y
    fill,accent={'green':(MINT,GREEN),'orange':(PALE,AMBER),'red':(ROSE,CORAL),'plain':(WHITE,NAVY)}[kind]
    ht=text_measure(body,CW-34,11.1)+42
    rect(M,y,CW,ht,fill,r=9);rect(M,y,5,ht,accent,r=2)
    text(title,M+17,y+10,CW-34,13.5,accent)
    text(body,M+17,y+32,CW-34,11.1,INK)
    y+=ht+10
def text_measure(s,w,size=11.4,leading=None):
    st=ParagraphStyle('measure',fontName='STSong-Light',fontSize=size,leading=leading or size*1.47,wordWrap='CJK')
    p=Paragraph(html.escape(str(s).replace('−','-').replace('–','-')).replace('\n','<br/>'),st);return p.wrap(w,9999)[1]
def bullets(items,sz=11.3):
    global y
    for title,body in items:
        rect(M,y+5,6,6,GREEN,r=3)
        h=text(title+'｜'+body,M+15,y,CW-15,sz)
        y+=h+7
def metrics(items):
    global y
    n=len(items); w=(CW-10*(n-1))/n;h=82
    for i,(v,label,detail) in enumerate(items):
        x=M+i*(w+10);rect(x,y,w,h,WHITE,r=8); num(v,x+12,y+12,24,GREEN)
        text(label,x+12,y+38,w-24,11,NAVY);text(detail,x+12,y+55,w-24,8.3,MUTED)
    y+=h+12
def table(headers,rows,widths=None,sz=10.3):
    global y
    widths=[CW/len(headers)]*len(headers) if widths is None else [CW*v/sum(widths) for v in widths]
    allrows=[headers]+rows
    for i,row in enumerate(allrows):
        heights=[text_measure(str(s),w-14,sz if i else sz+0.2) for s,w in zip(row,widths)]
        h=max(heights)+13
        rect(M,y,CW,h,NAVY if i==0 else (WHITE if i%2 else '#EEF2EB'),r=0)
        x=M
        for s,w in zip(row,widths):
            text(str(s),x+7,y+6,w-14,sz if i else sz+.2,WHITE if i==0 else INK)
            x+=w
        y+=h
    y+=10
def barrows(items,unit='',maxv=None,sz=10.8):
    global y
    maxv=maxv or max(abs(float(v)) for _,v,_ in items)
    for label,v,disp in items:
        text(label,M,y,145,sz); x=M+153; bw=CW-153-86
        rect(x,y+4,bw,12,'#E8EDE6',r=4)
        rect(x,y+4,max(1,bw*abs(float(v))/maxv),12,GREEN if float(v)>=0 else CORAL,r=4)
        text(disp,x+bw+7,y,78,sz,NAVY)
        y+=23
    y+=8
def figure_caption(s):
    global y
    y+=text(s,M,y,CW,9,MUTED,leading=12.5)+10
def photo_strip(name,body,heading_text=None):
    global y
    image(name,M,y,178,148); rect(M+190,y,CW-190,148,WHITE,r=9)
    if heading_text:
        text(heading_text,M+204,y+12,CW-218,14,GREEN)
        text(body,M+204,y+39,CW-218,10.9)
    else:text(body,M+204,y+12,CW-218,11)
    y+=157
# load model
data=json.load(open(ROOT/'models/model_results.json'))
# adapt json summary rows or use csv
raw=list(csv.DictReader(open(ROOT/'models/summary.csv',encoding='utf-8-sig')))
def val(r,k):return float(r[k]) if r.get(k) not in ('',None) else None
def wan(v):return f'{float(v)/10000:,.1f}' if v is not None else '—'
def n0(v):return f'{round(float(v)):,}' if v is not None else '—'
def pay(v):return str(round(v))+'月' if v is not None else '未回本'
R={(r['mode'],r['scenario']):r for r in raw}; MOD=data['modes']; modes=list(MOD.keys())
name={'A':'中式外带','B':'便携早餐','C':'早餐+零食','D':'全天组合','E':'分时共享'}
# cover
pg=1;rect(0,0,W,H,NAVY); rect(0,0,W,12,AMBER)
text('SHENZHEN EAT  /  商业研究  2026',M,40,CW,13,'#D5E8DB')
text('一间小店，\n能不能成为一门生意？',M,85,CW,39,WHITE,leading=48)
text('深圳宝安 · 福海街道新和社区',M,208,CW,19,'#FADEB6')
image('street',M,258,320,285);image('food',M+332,258,CW-332,137);image('kiosk',M+332,407,CW-332,136)
rect(M,561,CW,118,'#22524C',r=8)
text('早餐 × 零食 × 轻餐饮',M+17,578,CW-34,24,WHITE)
text('五种经营模式 · 17项研究 · 36个月现金流沙盘\n给第一次做生意的人看的、可以复算的投资可行性研究',M+17,615,CW-34,13,'#D5E8DB',leading=20)
text('桌面研究与情景模拟  |  非实地审计、非收益保证',M,707,CW,11,'#D5E8DB')
text('研究更新：2026年11月27日 · 图像为创作示意，并非真实街景',M,735,CW,9.5,'#D5E8DB')
y=759
page('01 / 一眼读懂','先看结论的边界','不是帮你押注哪种生意，而是把每一种选择的条件、资金和代价放在桌面上。')
metrics([('5','候选经营模式','同一模型口径'),('36','模拟月数','2027–2029年'),('17','研究模块','证据、假设分离')])
callout('已核实：这是复合商圈','两所学校基本身份、校内供餐方式、福海街道产业与人口概况、深圳居民收入统计、全国餐饮及食品经营制度；实际指定铺位消费客流和成交率尚无现场样本。')
callout('最重要的未知：外购需求到底有多大？','家庭早餐、学校供餐、园区食堂、便利店和现有餐饮都会分走需求。附近人多不等于店前有效客流，更不等于顾客会付款。','orange')
callout('财务结果是压力测试，不是预测','五种模式都采用明确可替换的假设；基准、悲观、乐观不是概率。先用真实租约、报价、成交和损耗校准参数，才有资格谈投资。','plain')
heading('阅读路线')
table(['先看什么','读完能知道什么'],[['市场与客群（第3–6页）','人群、替代需求、商业客流'],['竞争与选址（第7–9页）','租金线索、位置与合同条件'],['产品与经营（第10–16页）','5P、菜单、时空、人、能力与合规'],['财务与下一步（第17–24页）','现金流、回本、竞争、退出、验证清单']], [1,1.7])
page('02 / 市场环境','两所学校不是全部市场','学校信息采自深圳政府公开目录与预算；旧目录并非实时学校经营情况。[M01–M06]')
table(['项目','福新小学','鹏晖中英文学校'],[
['办学性质','公办小学','民办九年一贯制（小学及初中阶段）'],['校内供餐','配餐；现时早餐供应未知','堂食；现时早餐供应未知'],['住宿','历史目录：无；2026待核','历史目录：无；2026待核'],['学生规模','2022预算：36班、1798人；2026秋招生计划8班','当前实际人数无可靠官方数据；旧招聘转载非在校规模'],['收费','目录：免费','旧收费文件：小学4100–5400/学期，初中5500元；2026待查']], [1,1.7,1.7],10.6)
heading('家庭收入不能从学费推断')
para('民办学校收费只证明一项教育支出，不能代表家庭富裕程度，也不能代表孩子零花钱。福新小学2025预算纳入午餐午休与课后服务，说明校内供餐及安排可能替代校外需求。')
photo_strip('street','同一商圈还有居民、家长、教师、企业及商户员工、通勤者。学校需求可能受假期影响，成年需求则可能在中午、周末或夜间形成补充。日订单必须由真实商业交易验证。','复合商圈，而非单一学生市场')
figure_caption('插图：虚构街区氛围，不对应真实铺位；学校规模历史信息仅作背景。')
page('03 / 区域背景','住户、园区与收入水平','街道、社区、全市不同口径必须分开。人口不能直接转换为特定门店生意。')
metrics([('53万','福海管理人口','街道官方2026概况'),('4500+','工矿商贸企业','街道官方概况'),('5.29万','新和历史人口','官方地名词典，非即时')])
heading('深圳居民消费水平（2025年，全市）')
metrics([('8.49万','年人均可支配收入','约7079元/月'),('5.35万','年人均消费支出','约4462元/月'),('29.2%','食品烟酒支出占比','并非早餐预算')])
table(['客群','购买任务','待验证价位（元）'],[
['学生家庭、家长','卫生、饱腹、方便携带','5–10 / 10–15组合'],['老师、通勤员工','快速、稳定；午餐便利','早餐7–15，简餐12–25'],['工业园从业者','性价比、出餐快','早餐5–10，简餐10–20'],['社区住户','家庭加餐与日常备餐','早餐5–15，简餐12–25'],['周边流动成人','透明价格、短等候','早餐6–15，简餐10–20']], [1,1.65,1.3],10.2)
callout('这组价格不是当地市场报价','它们是建议调研时用于校准模型的试价区间。家庭收入、交通方式、校内早餐参与比例、购买地点和频次当地均未获得可信的实测。','orange')
figure_caption('来源：[M07–M10]；以上人口、产业及收入均不可直接等于商铺客流。')
page('04 / 消费需求','早餐有三个对手：家、学校、街边','全国样本提供方向，而不是替代本地调查。2019–2021年14省级地区、52,535名6–17岁儿童调查，2025年发表。[M11]')
heading('全国样本：主要早餐地点')
x=M; bw=CW; t=y
for label,v,co in [('家中',.663,GREEN),('校内',.258,AMBER),('其他餐饮',.079,CORAL)]:
    rect(x,t,bw*v,34,co);x+=bw*v
y+=43
for label,v,co in [('家中',66.3,GREEN),('校内',25.8,AMBER),('其他外部餐饮',7.9,CORAL)]:
    rect(M,y+3,12,12,co,r=2);text(label,M+20,y,180,11);num(f'{v:.1f}%',M+220,y,15,co);y+=25
callout('不能用7.9%乘两校人数得出订单','研究地区、调查时间、家庭及学校供给不同。外食不等于到某一家店购买，更不能代表在新和当前的比例。','orange')
heading('需要验证的五个问题')
bullets([('在哪吃','家庭自备、校内/单位食堂、外购占比与购买频次'),('谁决定','家长或成人消费者是否实际付款、对健康质量的要求'),('为什么买','便捷、温度、口味、卫生、份量和价格'),('如何替代','便利店、外卖、传统早餐、工作场所供餐'),('什么时候买','以店铺匿名汇总营业时段订单为口径；不把学校上下学时刻当作订单')])
figure_caption('另有2024长三角调查及2025城市成人外出就餐研究，口径不同，详见[M12–M13]。')
page('05 / 市场容量','从人流走到收入，中间隔了四道门','用公开商业区域总体客流与匿名成交测量，不追踪个体。')
# funnel
for i,(label,detail,co) in enumerate([('商业可达人次','不等于顾客',MINT),('有购买需求','排除已用餐、食堂等',PALE),('选择本店','产品、价格、等候和竞争',MINT),('实际完成支付','按窗口产能与可售库存封顶',ROSE)]):
    w=CW-i*59;x=M+(CW-w)/2;rect(x,y,w,39,co,r=5);text(label,x+12,y+6,w-24,12,NAVY);text(detail,x+150 if w>300 else x+108,y+9,w-(162 if w>300 else 115),9.5,MUTED);y+=45
heading('月收入 = 日实际订单 × 客单价 × 营业天数')
table(['演示','悲观','基准','乐观'],[['日商业机会','600','900','1300'],['综合成交率','8%','12%','16%'],['订单/日','48','108','208'],['客单（元）','6','7','8'],['26日收入（元）','7,488','19,656','43,264']],[1.3,1,1,1])
callout('复购不是再乘一次的倍率','重复到访已包含在商业人次中。应单独统计回头客及新客的订单来源，避免重复计算；不同营业时段也不能把同一订单相加两次。')
figure_caption('演示数字全为假设，非下文财务模型成熟客流。深圳汛期与节假日会影响出勤、通行和损耗。[M14]')
# next pages competition dynamically built below
page('06 / 竞争','附近已经有什么生意？','共26个公开候选名称，非完整普查；证据等级只代表名称/位置的支持，不代表真实销量。')
metrics([('26','候选商户','跨平台去重'),('3','A级线索','品牌原站/交叉'),('23','B/C级线索','单源或聚合')])
table(['品类','公开候选样本','经营启示'],[
['包点、粉面','福海汤包、原味汤粉王、潮州早餐店、永香特色包子房','基础需求已被服务，比较真实价签、出餐和品质。'],
['快餐与简餐','林记快餐、永和自选快餐、潮味自选、梅汕烧腊','午间有竞争；新时段必须另测贡献。'],
['轻食与饮品','1点点福永新和店、快乐番薯、尊宝比萨、越式法棍','替代品有不同价格带，不能把新颖视为高复购。'],
['便利零售','美宜佳、福万家、园区便利店','品类多、购买方便；零食库存周转重要。']],[1,1.65,1.6],10.1)
callout('公开可得的经营证据很有限','1点点原始目录明确列名；快乐番薯OpenRice标注营业10:00–次日02:00，上无食评。目录不代表实时在营，更不能反推营业额。未获授权经营流水、真实利润和完整竞争店菜单。','orange')
figure_caption('完整26条候选名称、证据等级及24条来源见仓库 research/02_competition.md。[S01–S15]')
page('07 / 商铺租赁','一条街里，租金可以差十几倍','8条核心社区挂牌和3条邻近参考。本页仅展示核心区搜索索引；安居客详情验证受限，非挂牌实时可用或签约价。[R01–R09]')
rents=[('新和三区 · 30㎡',1180,'¥1,180'),('新和五区 · 28㎡',1600,'¥1,600'),('新和百货 · 40㎡',3000,'¥3,000'),('新和二区 · 20㎡',3300,'¥3,300'),('新兴工业区 · 100㎡',6050,'¥6,050'),('新和二区 · 45㎡',6100,'¥6,100'),('悦盛三路 · 100㎡',10000,'¥10,000'),('新和二区 · 80㎡',16300,'¥16,300')]
barrows(rents)
figure_caption('不同面积、用途和租约条件；不可作为同类铺位均值。最低挂牌并未确认可餐饮。')
table(['成本项','核验重点'],[['租金','实用面积、租期、递增规则、免租期、押付方式'],['转让费','设备和经营权分别定价，例：100㎡工业区挂牌12.8万元顶手'],['管理费、水电','物业费、垃圾、维修、转供电价、欠费、清洁'],['合规硬件','专用烟道、消防、上下水、电力、许可与房东书面同意']],[1,2.5])
callout('顶手费可能比租金更伤','如果12万元转让费希望24个月收回，仅这一项就要求每月多赚5000元现金。这还不包括租金、人工和利息。','red')
page('08 / 选址','四类商业地段，不凭距离拍板','以新和三区为核心，扩展到新和二区、产业商业与交通商业。下面是商业区类型示意，不是精确地图或已测客流。')
# Schematic independently labeled
for j,(title,sub,co) in enumerate([('A 住宅商业带','新和三区、远东中/东/西路片区',MINT),('B 成熟商街','新和二区、悦康/悦盛/悦昌',PALE),('C 产业商业带','富桥、新兴、福园一路',MINT),('D 办公/交通商带','宝安大道扩展参考',PALE)]):
    x=M+(j%2)*(CW/2+4);t=y+(j//2)*74;w=CW/2-4;rect(x,t,w,66,co,r=8);text(title,x+12,t+9,w-24,14,NAVY);text(sub,x+12,t+34,w-24,10,MUTED)
y+=155
table(['地段','可能适配','必须实看'],[['A 住宅带','小外带、早餐加社区零食','一般商业可达性、周末需求、烟道'],['B 成熟商街','全天组合、分时合作','同质竞争、转让费、许可及合作条款'],['C 产业带','标准早餐、午间简餐','园区食堂及真实职工订单'],['D 扩展区','便携特色、预订自提','较高租费是否由有效需求弥补']],[1,1.4,1.6],10.2)
heading('用同一把尺评分（现场再填写）')
barrows([('真实商业需求',25,'25%'),('租赁全成本',20,'20%'),('可见与易达性',15,'15%'),('餐饮硬件',15,'15%'),('竞争替代',15,'15%'),('客群与时段平衡',10,'10%')],maxv=25)
figure_caption('合规是进入评分先决条件。当前没有可靠指定铺位实测，所以不输出伪精确排名。')
page('09 / 商业模式','5P：把产品与“人”放在一起','需求端和经营者端必须匹配。即使市场有需求，不代表经营者拥有足够执行能力。')
for title,desc,accent in [
('PRODUCT  产品','少量稳定商品、实际需求、营养与卫生、质量、复购、损耗',GREEN),('PRICE  价格','透明价签；客单价减去原料、包装、报损和费率才是订单贡献',AMBER),('PLACE  地点与渠道','合规铺面及共享空间，经营时段、社区、自提与公开成人顾客渠道',GREEN),('PROMOTION  推广','可追踪开业投入、真实付费订单、自然口碑及增量利润',AMBER),('PEOPLE  人','需求端：学生家庭、家长、住户、教师和上班族；供给端：老板、合伙人、员工与合作伙伴',GREEN)]:
    h=64 if title.startswith('PEOPLE') else 56;rect(M,y,CW,h,WHITE,r=8);rect(M,y,5,h,accent,r=2);text(title,M+16,y+7,CW-32,13.5,accent);text(desc,M+16,y+29,CW-32,10.6);y+=h+8
heading('两个群体的匹配决定商业模式')
callout('顾客需要什么 × 老板能交付什么','有健康、便携、低价诉求的顾客，未必愿意为复杂新品支付溢价。老板的食品安全、制作、采购、成本管理、营销、人脉与排班决定能否长期稳定地兑现承诺。')
figure_caption('依据市场/产品/经营研究综合整理。[M11–M13；P1–P14；OP1–OP11]')
page('10 / 候选模式','先比较产品与门店组合（A–C）','所有地址、成本、售价均需验证。图示为经营方式原型，不是已存在的店铺。')
image('food',M,y,CW,170);y+=180
table(['原型','示意菜单与价格','经营条件'],[
['A 中式外带','包点/粥/蛋/豆饮，套餐6–11元','20–35㎡模型，蒸煮/保温；同质竞争、产能瓶颈。'],
['B 便携早餐','饭团/三明治+奶/饮，9–15元','15–30㎡模型，冷藏与标准化；客单和冷链风险。'],
['C 早餐+零食','早餐7–12元，较健康零食/饮3–8元','30–50㎡模型，延长时段与陈列；报废和SKU复杂性。']],[1.0,1.4,1.6],10.6)
heading('全国趋势不等于当地机会')
para('2025全国餐饮收入57,982亿元、同比+3.2%；2026连锁便利店报告显示社区门店比重提高，但单店日营收和坪效承压。基础餐饮不等于轻松赚钱；新品类须验证支付意愿、复购、损耗。[P1–P3]')
callout('产品机会是可以证伪的假设','比较传统套餐和特色便携早餐：正常价下的真实成交、出餐速度、贡献利润、退单、损耗与回购。缺少本地样本时不宣称市场空白。','orange')
page('11 / 候选模式','时间与空间也能创造生意（D–E）','全天组合与共享空间都不是天然好生意，要比较新增收入和新增成本。')
photo_strip('kiosk','早餐+简餐+下午轻食+合法夜餐。示意价：早餐6–12元、简餐13–22元、加餐6–15元、夜餐15–25元。45–80㎡模型，多岗位、厨房及合规硬件。','D 全天组合')
photo_strip('shared','把既有餐厅的闲置早餐时段或柜台作为场地。约8–20㎡共享可用区；在许可、房东和合同条件成立后开展有限菜单。固定租金、流水抽成或混合结算均可谈。','E 分时租赁 / 店中店')
heading('时间组合（示意营业时段，非学校时间）')
table(['方式','早餐','午间','下午','晚间'],[['A/B 独立外带','核心','—','—','—'],['C 早餐零食','核心','可试','轻食','可试'],['D 全天组合','核心','简餐','茶点','夜餐'],['E 分时共享','合作','原店','原店','原店']],[1.5,1,1,1,1],10.0)
callout('新增时段利润 = 新收入 × 贡献率 - 新增固定成本','设备、人力、原料和备餐有复用价值；贡献率已扣销量相关费用，另减未计入的新增班次人工、水电、清洁和设备摊销等。若该时段增量利润持续为负，多开门只会多亏。','orange')
page('12 / 产品与消费者','口味、健康和复购，不必三选一','目标是为学生家庭和成年居民提供可信赖的日常食物，避免把高糖、高盐、高脂当作商业卖点。')
photo_strip('food','学龄儿童膳食指南建议早餐在谷薯、蔬果、动物性食物、奶豆坚果四类中至少选三类；零食重视清洁及适量、优先白水。依据一般指导，不是医学个体方案。','以基础食物搭出灵活套餐')
table(['产品策略','潜力与门槛'],[['经典刚需','包点、粥、蛋、奶、豆饮；高频且易替代，关键是稳定。'],['跨品类便携','饭团、三明治、轻食、奶制品；单价可能较高，短保期引起损耗。'],['社区加餐','小份水果、酸奶、无糖饮品、包装零食；库存寿命和需求独立测试。'],['新品试验','先验证真实付费复购，而不是用网络热度或免费试吃推断销量。']],[1,2.5])
callout('家长信任如何形成？','清楚列菜单和价格，告知食材及过敏原，按许可规范制作、控制温度及保质期。可用新鲜度、口感与恰当调味提供好体验，不夸大健康功效。')
figure_caption('营养与市场方向：[P4–P9]；共享/全天外地案例仅说明模式存在：[P10–P12]。')
page('13 / 经营产能','铺面做多大，先看最慢的一环','面积假设来自经营原型与财务测算，不是法规最低面积或实测报价。[OP1–OP3]')
table(['模式','可比面积（㎡）','同时在岗/重点设备'],[['A 传统','20–35','店主+1–2；蒸柜、保温、洗消、冰箱'],['B 便携','15–30','2–3；冷藏、简化加工、包装'],['C 社区','30–50','2–3；陈列与冷藏、分区及保温'],['D 全天','45–80','2–4分班；厨房排烟与洗消、更多工位'],['E 共享','共享8–20','店主+助手；专属储存、收银、用具']],[1,1.2,2.0])
heading('示例：一个窗口 40 秒/单，70%有效利用率')
metrics([('63','单/小时','假设有效出餐'),('94','单/90分钟','单窗口近似上限'),('120','单目标','需优化或增岗')])
callout('高峰实际销售量受产能和库存共同限制','现场合法演练30单并检查错单、等待、卫生及库存；采购、冷藏、制备、加热、保温/冷藏、取餐及洗消路线要避免交叉。面积不能直接换算销售。','orange')
para('估算预算：轻型外带设备0.8–2.5万，小施工1–3万；复杂设备2.5–6万，工程3–8万。仅测试区间，真正报价看同规格、运输、安装、保修、排烟及许可。',10.3)
page('14 / People','老板、合伙人和员工：最容易被低估的人','同样的菜单、面积和租金，不同经营者的真实结果可能非常不同。')
table(['角色','关键知识体系','缺失的表现'],[['老板/店长','食品安全、制作、定价、财务、客诉和人手','忙于出餐但不会看成本或现金流'],['运营/财务合伙人','进销存、预算、供应商账期、资金及分账','流水漂亮但不知道应付与库存'],['制作/助手','标准配方、卫生、温控、备料、替班','服务质量随人员波动'],['合作店/房东','出租权、责任、设备及水电、合同','场地可用性与合作持续性不稳']],[1,1.7,1.4],10.2)
heading('按模式看最有价值的能力')
table(['A/B','C','D','E'],[['A：批量制作\nB：冷链品质','品类、库存和跨时段','多人班次、成本与复杂菜单','伙伴谈判、交接、许可与分账']],[1.1,1,1,1])
callout('先约定工资，再约定利润分红','出资比例、岗位工资、追加资金上限、亏损分担、财务授权、质量责任及退出估值应书面明确。只投资不劳动的人，不应把老板的劳动报酬也当可分利润。')
para('供应链：至少两三家同规格试购，核查合法资质、批次、价格、冷链/到货、售后、账期。先到期先售，报废按实际成本入账。',10.6)
page('15 / 合规','签租约之前，先过四道门','政策核实截至2026-11-27；具体场地和菜单须以属地主管部门审批或咨询为准。')
callout('1｜经营许可','仅预包装食品销售适用相应备案安排；热食、冷食等餐饮经营须按实际制售项目确认许可。广东2025实施细则中50㎡及以下“小餐饮”是分类，不是免证。')
callout('2｜场地硬件','检查产权用途、消防、排水、电力、卫生、专用烟道与噪声。2026年8月施行的生态环境法典第250条限制不合规场所产生油烟的餐饮项目。','orange')
callout('3｜合作关系','是否允许转租、同一场所两主体分时经营及相应许可须具体核实。不能借用他人许可证。房东书面同意、合法经营主体、清洁交接、食安和核算责任缺一不可。','red')
callout('4｜人员、食安和合同','进货查验、直接入口食品岗位人员按规定健康检查、储存温控、清洁、过敏原、异常停止销售；租约约定办证失败的解除及退押、设备归属与撤店责任。','plain')
para('深圳最低工资自2025-03-01为全日制2520元/月、非全日制23.7元/小时，属于法律下限，不是餐饮实付报价。合伙、兼职和社保成本以实际合规安排核实。',10.6)
figure_caption('官方政策：[OP1–OP11]；深圳市场监管公开咨询12315、12345，广东政务服务网。')
page('16 / 财务模型','先准备多少钱，和能赚多少是两回事','统一假设：2027年1月开业；2027–2029年36个月；五种模式，三个情景。下方金额单位万元；不是当地实付成本。')
rows=[]
for a in modes:
    r=R[a,'base'];m=MOD[a]
    rows.append([a+' '+name[a],wan(val(r,'investment')),wan(val(r,'reserve')),wan(val(r,'total_funding')),f"{m['lease_cash']:,}"])
table(['模式','开店投入','预留现金','启动资金','月租/场地费（元）'],rows,[1.4,1,1,1,1.4],10.5)
heading('开店投入的组成（基准，万元）')
table(['模式','装修+设备','转让+开业','押金+首批货'],[[a+' '+name[a],wan(MOD[a]['fitout']+MOD[a]['equipment']),wan(MOD[a]['transfer']+MOD[a]['preopening']),wan(val(R[a,'base'],'deposit')+val(R[a,'base'],'initial_stock'))] for a in modes],[1.4,1.2,1.2,1.2])
callout('为什么钱不能只够开门？','启动资金 = 开店投入（部分可回收，如押金、设备残值）+ 三个月固定成本储备。现金储备不是额外成本，但可用于覆盖初期上客慢、淡季与日常支付。','orange')
figure_caption('模型不含贷款利息；租费、转让费、装修、设备、员工成本、报损、费率、税费预算等是假设，见模型附件。')
page('17 / 财务模型','一笔订单，最后还能留下多少钱？','模型以客群、商品组合、可购买机会、新客成交、回头客成交、库存与产能逐月计算。')
table(['模式','成熟日订单*','客单（元）','毛利率','贡献率**','保本/日'],[[a+' '+name[a],n0(val(R[a,'base'],'normal_mature_orders_day')),f"{val(R[a,'base'],'normal_avg_ticket'):.2f}",f"{val(R[a,'base'],'normal_gross_margin')*100:.1f}%",f"{val(R[a,'base'],'normal_margin')*100:.1f}%",n0(math.ceil(val(R[a,'base'],'reference_be_orders_per_day')))] for a in modes],[1.4,1,1,1,1,1],9.7)
figure_caption('* 正常成熟营业日示意，不是全年日均；毛利率已扣原料及报损；** 销售减原料、损耗、包装、按比例费用、税费预算及共享抽成后的贡献率，不等于常规毛利率。保本口径为正常月固定成本含老板参考工资。')
heading('订单经济性示例：A基准')
r=R['A','base'];price=val(r,'normal_avg_ticket');margin=val(r,'normal_margin');fixed=val(r,'basic_monthly_fixed')
metrics([(f'{price:.2f}','每单收入（元）','客单价假设'),(f'{price*margin:.2f}','每单贡献（元）','扣变动支出'),(f'{fixed:,.0f}','月固定（元）','含老板工资')])
callout('毛利、利润与现金流，这三件事不同','原料和报损等先从收入扣除，得到贡献利润；再扣租金、雇员、业主工资、水电管理营销等为经营利润；会计利润另扣折旧；经营自由现金流再反映库存变化和维修资本支出。','plain')
para('客流与复购：同一个购买机会只能归为新客或回头客，不重复乘复购率。月订单受成熟度、季节性、竞争分流、成交率和每天产能共同影响。',10.6)
page('18 / 三年沙盘','基准情景：收入不等于赚钱','单位万元。经营利润已扣业主参考工资、未扣折旧；累计自由现金流已反映库存变动和维修资本支出。')
table(['模式','第1年收入','第1年经营利润','第2年经营利润','第3年经营利润'],[[a+' '+name[a],wan(val(R[a,'base'],'year1_revenue')),wan(val(R[a,'base'],'year1_operating_profit')),wan(val(R[a,'base'],'year2_operating_profit')),wan(val(R[a,'base'],'year3_operating_profit'))] for a in modes],[1.3,1.1,1.2,1.2,1.2],10.4)
heading('三年累计经营自由现金流（万元）')
barrows([(a+' '+name[a],val(R[a,'base'],'total_free_cash')/10000,wan(val(R[a,'base'],'total_free_cash'))) for a in modes])
table(['模式','资金首次缺口月','初始投入回收','额外现金缺口*（万）'],[[a+' '+name[a],n0(val(R[a,'base'],'cash_shortfall_month')),pay(val(R[a,'base'],'payback_month')),wan(val(R[a,'base'],'additional_funding_needed'))] for a in modes],[1.35,1.2,1.2,1.4],10.4)
callout('不能把这张表当推荐榜','只有E在基准假设中第24月回收开店投入，36月仍未覆盖含储备金在内的全部启动资金；其共享经营许可和合作条件也尚未成立。A–D未回本；B/C/D出现现金缺口。','orange')
figure_caption('* 若不止损且继续运营的压力测试；负余额不是允许自动新增贷款或真实经营结果。')
page('19 / 三年沙盘','如果市场好一点，或者坏一点','悲观、基准、乐观是明确假设，不是概率预测；窗口为36个月。单位万元。')
table(['模式','悲观累计自由现金','基准累计自由现金','乐观累计自由现金'],[[a+' '+name[a],wan(val(R[a,'bad'],'total_free_cash')),wan(val(R[a,'base'],'total_free_cash')),wan(val(R[a,'good'],'total_free_cash'))] for a in modes],[1.3,1.3,1.3,1.3],10.2)
heading('乐观情景的资本回收速度')
table(['模式','初始开店投入回收','全部启动资金等值回收'],[[a+' '+name[a],pay(val(R[a,'good'],'payback_month')),pay(val(R[a,'good'],'full_funding_payback_month'))] for a in modes],[1.4,1.4,1.55],10.4)
callout('悲观情景不是“最大亏损”的上限','悲观模型假设客流×0.78、成交率×0.82、售价×0.96、原料×1.08、报损×1.25、租金×1.15，竞争在第7月开始分流18%，不主动止损时五模式第5月均出现现金缺口。','red')
para('基准竞争：第19月起分流7%；乐观：第25月分流4%。年租金、工资、食材和价格按不同通胀参数增长。实际变动不一定同时发生，需逐项验证。',10.6)
page('20 / 动态沙盘','36个月资金余额：最怕先耗光现金','以下基准模型资金余额含预留现金；余额小于0是理论资金缺口，模拟继续经营仅用于压力测试。')
monthly=list(csv.DictReader(open(ROOT/'models/monthly.csv',encoding='utf-8-sig')))
def chart_series(rows, key, label='现金余额（万元）'):
    global y
    vals=[[float(r[key])/10000 for r in rows if r['mode']==a and r['scenario']=='base'] for a in modes]
    lo=min(0,min(min(v) for v in vals)); hi=max(max(v) for v in vals); lo=math.floor(lo/5)*5;hi=math.ceil(hi/5)*5
    x0=M+37;x1=W-M-14;top=y+27;bot=y+242
    rect(M,y,CW,274,WHITE,r=9)
    for i in range(6):
        vv=lo+(hi-lo)*i/5;t=bot-(vv-lo)/(hi-lo)*(bot-top)
        line(x0,t,x1,t,LINE,.6);text(f'{vv:.0f}',M+4,t-7,29,9,MUTED)
    zero=bot-(0-lo)/(hi-lo)*(bot-top);line(x0,zero,x1,zero,CORAL,1.2)
    colors=[GREEN,'#A66737','#557EAC','#B75F69','#7669A1']
    for a,v,co in zip(modes,vals,colors):
        for i in range(len(v)-1):
            px=x0+(x1-x0)*i/35;nx=x0+(x1-x0)*(i+1)/35
            py=bot-(v[i]-lo)/(hi-lo)*(bot-top);ny=bot-(v[i+1]-lo)/(hi-lo)*(bot-top)
            line(px,py,nx,ny,co,1.8)
    for a,i in zip(['1月','12月','24月','36月'],[0,11,23,35]):text(a,x0+(x1-x0)*i/35-10,bot+8,40,9,MUTED)
    text(label,M+12,y+7,CW-24,9,MUTED);y+=281
    for a,co in zip(modes,colors):
        x=M+(modes.index(a)%3)*CW/3; t=y+(modes.index(a)//3)*19;rect(x,t+3,12,5,co);text(a+' '+name[a],x+18,t,CW/3-18,10)
    y+=45
chart_series(monthly,'cash_balance')
table(['模式','第12月余额','第24月余额','第36月余额'],[[a+' '+name[a],wan(val(R[a,'base'],'year1_end_cash')),wan(val(R[a,'base'],'year2_end_cash')),wan(val(R[a,'base'],'year3_end_cash'))] for a in modes],[1.3,1,1,1])
callout('为什么不是每个月都一样？','模型给教育家庭相关消费与其他居民/职工需求不同季节系数，假期、春节、淡季波动与租金刚性叠加；成熟度和竞争亦影响订单。全部系数是情景参数，须用真实月度交易修正。','orange')
page('21 / 风险与博弈','一旦你生意好，别人也会动','竞争不是固定背景。模仿、降价、便利店鲜食、租金上调都会改变投资回报。')
heading('A模式：第2年经营利润的单因素压力测试')
sens=data['sensitivity']; ss=[s for s in sens if s['mode']=='A']; ss=sorted(ss,key=lambda z:z['year2_profit_delta'])
for s in ss[:7]:
    # compact
    d=float(s['year2_profit_delta'])/10000
    text(s['change'],M,y,255,10.4);text(f'{d:+.2f} 万',M+270,y,110,11,CORAL if d<0 else GREEN);y+=22
figure_caption('相较A基准第二年经营利润1.11万元。单因素变化，其余参数固定，非叠加预测。全部5种模式、62组压力测试在 sensitivity.csv。')
callout('价格战为什么危险？','产品变便宜时，每份收入先下降；租金、人员、耗材并不会同比下降。若为维持客流而扩大SKU、延长营业，成本和损耗还可能同步提高。','red')
heading('共享抽成也是压力变量')
para('E基准第2年经营利润约2.23万元；若合作方采用营业额10%或15%抽成，模型分别降至约0.17万元或-1.41万元，36个月均无法回本。',10.6)
bullets([('先识别','按匿名交易与经营记录比较订单、价格、贡献、损耗、复购；不把评论当销量'),('再计算','分别测成交变化、单位原料价格、必要宣传费用及竞争分流'),('再调整','缩减低贡献商品、调整时段和班次、保持食品安全与真实品质'),('最后止损','若不能用真实付费订单覆盖固定成本和老板工时，推迟扩张或按合同退出')])
page('22 / 退出与业主工时','老板赚的钱，可能只是自己的工资','经营者的劳动报酬应与资本收益分开。下面为基准情景第一年（万元）。')
table(['模式','老板参考工资/年','扣工资前经营现金收入*','扣工资后经营利润'],[[a+' '+name[a],wan(val(R[a,'base'],'year1_owner_labor')),wan(val(R[a,'base'],'year1_pre_owner_cash_income')),wan(val(R[a,'base'],'year1_operating_profit'))] for a in modes],[1.3,1.3,1.5,1.3],10.3)
figure_caption('* 经营贡献减其他固定成本，未扣老板参考工资、折旧及现金流调节项。并非老板可全部提取的分红。')
heading('若第6个月退出，会怎样？（基准假设）')
table(['模式','六个月退出净损失（万元）'],[[a+' '+name[a],wan(val(R[a,'base'],'month6_exit_loss'))] for a in modes],[1.6,1])
callout('退出损失考虑可回收项目，但不保证能变现','模型假设设备、库存、押金部分可回收，并计合同退出义务；真实损失要用租约、债务、设备回购价、拖欠费用及清仓所得重新计算。不得把假设残值当保证。','orange')
para('更加严峻的亏损可能来自长期继续亏钱、场地不适用、食品事故、合伙纠纷及无法退出的租约。悲观情景没有为这些无法量化的事件给出最坏上限。',10.6)
page('23 / 实地验证','花小钱去验证，再决定下一步','这不是让你立即选模式，而是用相同标准收集买得到、租得到、做得成的数据。')
for i,(title,body) in enumerate([('第一步 · 调查','在不同商业区做匿名总体客流/订单观察，覆盖工作日周末雨天；向50–100位自愿成年人/家庭询问外购频次、价格与替代品，结果仅作方向性。'),('第二步 · 找铺','至少三处同类租约报价，核对产权、房东、面积、租金、顶手、管理费、排烟、许可及退租条款。'),('第三步 · 试菜单','合法条件成立后，7–14天小规模真实付费测试：少量SKU，正常价；记录售出、报废、出餐和实际成本。'),('第四步 · 重算','把现场日订单、客单、贡献率、租金、工资和业主工时回填财务模型，复跑悲观/基准/乐观及竞争情景。'),('第五步 · 选择演化路线','比较继续共享、独立门店、增加品类/时段和退出。共享合规未确认之前不能销售；投入与净损失须符合可承受水平。')]):
    h=75;rect(M,y,CW,h,WHITE,r=8);rect(M+10,y+11,35,35,MINT,r=8);num(str(i+1),M+19,y+17,19,GREEN);text(title,M+55,y+9,CW-67,13.1,NAVY);text(body,M+55,y+30,CW-67,10.5);y+=h+10
callout('真实付费比“大家都说好吃”更有价值','不做个人跟踪；以匿名汇总、成年人自愿反馈与真实正常价格交易，核验足够订单是否长时间覆盖成本。')
page('24 / 工具与质量','研究方法真的改过，不是纸上流程','经实际工具对比，团队调整数据渠道；证据和财务参数可追溯。')
table(['工具','实测结果/选择'],[['Web + Exa','组合发现公开资料与候选店；原始官网/政府资料复核。'],['Firecrawl','网页及结构化搜索辅助；精确本地覆盖不足。'],['高德/百度/目录','出现同名社区、旧索引和地区混杂；只作交叉线索。'],['大众点评 / 58 / 安居客','虚拟电脑进入滑块验证；租赁详情验证受限。仅使用可读公开索引，不声称完整采集。'],['GitHub / 本地工具','查最佳实践；保留工作规范、证据、CSV和可执行Python模型。报告使用已验证的PDF生成方案。']],[1.2,2.8])
heading('研究结果的三种标签')
callout('事实 / 公开证据','原始官方、品牌与公开来源按地域、时间、口径标注。')
callout('假设 / 情景','页面上的售价、订单、租金、供应链成本与未来利润不是本地实测；模型可替换。','orange')
callout('未知 / 待实地验证','校内早餐比例、家庭真实收入、当地交通构成、指定门店客流、当前房源、竞品账本、共享许可和合作意向仍未知。','red')
figure_caption('工具竞争受来源覆盖和验证挑战影响，H02阶段条件通过而非数据已完整。详见 tooling/ 文档及独立审查。')
page('25 / 交付总结','用证据决定，不用故事决定','这份报告把17项研究、5个商业模式、财务沙盘与运营实践连接起来，是签约前可复用的分析工具。')
table(['商业选择','最应验证的条件'],[['传统中式早餐','真实订单能过保本线，出餐与采购稳定。'],['饭团/三明治','客单价和复购能抵消冷链和报损。'],['早餐+社区零食','下午/周末订单是增量，不只是把早餐收入挪到另一个时段。'],['全天餐饮','各新增时段独立贡献足以负担人手、设备、清洁和休息成本。'],['分时租赁/店中店','房东、许可、结算及食品安全责任明确，且合同能持续。']],[1.4,2.5])
heading('完整复算及研究材料')
para('同一研究项目保留各模块原文与来源、工具试验、模型脚本、36月逐月CSV、摘要及敏感性表。数据一旦改变，应重跑模型并更新结论，而不是让报告上旧数字继续沿用。')
callout('当前研究阶段的诚实结论','线上资料能够证明区域存在相关商圈、餐饮竞品和租赁线索；无法独立证明哪个铺位能达到设定订单量。所有商业选择都保留，最终以现场核验与可承受亏损决定。','green')
figure_caption('后附重要参考资料（全部来源及细节见研究文件和工具记录）。')
# additional operating breakdown
page('附录 / 每月成本','固定费用到底花在哪？','以下为各模式基准的每月初始固定成本参数（元）；不含按销量产生的食材、损耗、包装、抽成和税费预算。')
rows=[]
for a in modes:
    m=MOD[a]
    rows.append([a+' '+name[a],f"{m['lease_cash']:,}",f"{m['property_fee']:,}",f"{m['staff_loaded']:,}",f"{m['owner_labor']:,}",f"{m['utilities']+m['fixed_other']+m['marketing']:,}"])
table(['模式','场地费','物业','雇员','业主参考工资','水电+其他+推广'],rows,[1.35,1,1,1,1.12,1.4],10.0)
heading('盈利比较：实际经营成本、劳动与折旧')
table(['模式','首年月均经营利润（元）','首年月均折旧后利润（元）','第2年月均经营利润（元）'],[[a+' '+name[a],n0(val(R[a,'base'],'year1_operating_profit')/12),n0(val(R[a,'base'],'year1_accounting_profit')/12),n0(val(R[a,'base'],'year2_operating_profit')/12)] for a in modes],[1.3,1.5,1.5,1.5],10.3)
callout('为什么很忙却未必有资本收益？','上述折旧后利润已扣参考业主工资，且未考虑贷款利息、个体实际税务及突发事件。如果老板不领取工资，店面银行余额可能较好看，但这部分属于劳动所得而非资本回报。')
heading('客单价、开业上客与产能假设')
para('每个模式初期成交需要爬坡，重复顾客占比逐步提高；按照日成交能力封顶。模型用家庭相关需求与其他人群系数模拟假期，并计算回头客与新客订单，未把复购当第二重乘数。真实利润须使用店面收款、进货和费用记录。')
page('附录 / 经营数据','我们找到的26条商户候选','证据A=品牌原站或交叉确认；B=单个目录/体验记录；C=聚合线索。均不等于2026当前在营、菜单和流水已核实。')
f=(ROOT/'research/02_competition.md').read_text().splitlines()
competitors=[]
for L in f:
    if not L.startswith('| '): continue
    a=[i.strip() for i in L.strip('|').split('|')]
    if len(a)==4 and re.match(r'^[ABC] \[S',a[3]):
        competitors.append([a[0],a[1],a[3]])
table(['候选商户','公开区域','等级 / 来源'],competitors[:13],[1.6,1.8,1],9.7)
page('附录 / 经营数据','商户候选（续）','证据等级按公开列表记录；请以现场营业状态和实际价签为准。')
table(['候选商户','公开区域','等级 / 来源'],competitors[13:],[1.6,1.8,1],9.7)
figure_caption('线上目录很难覆盖城中村所有小微生意；本页不能被解释为附近店铺总数。若签约，须先现场复核。')

# source appendix glean titles and link clickable
src_items=[]
for f in sorted((ROOT/'research').glob('*.md')):
    for L in f.read_text().splitlines():
        m=re.match(r'^(?:-\s*)?(?:\[([A-Z]+\d+)\]|([A-Z]+\d+)\s)(.*)$',L)
        if not m:continue
        urls=re.findall(r'https?://[^\s;；]+',L)
        if not urls:continue
        code=m.group(1) or m.group(2); title=m.group(3).split('https://')[0].strip(' ：:;；，。')
        src_items.append((code,title,urls[0].rstrip('。；，)）')))
for start in range(0,len(src_items),10):
    page('来源 / 附录',f'公开资料与追溯索引 {start//10+1}','所有条目检索日期为2026-11-27；原始发布时间或口径按各来源注明。点击短链接打开原始资料。')
    for code,title,url in src_items[start:start+10]:
        h=max(43,text_measure(title,CW-72,10.7)+27)
        rect(M,y,CW,h,WHITE,r=6)
        text(code,M+8,y+9,44,10,GREEN);text(title,M+58,y+6,CW-68,10.7,NAVY)
        link_t=y+h-17;text('打开来源网页',M+58,link_t,CW-68,8.8,GREEN)
        c.linkURL(url,(M+58,H-(link_t+13),M+148,H-link_t+1),relative=0,thickness=0)
        y+=h+6
    figure_caption('链接页面可能更新、过期或要求验证。所有原始资料出处和详细证据等级保留在项目研究文档。')
if pg:end()
c.save()
print('PDF',OUT,'pages',pg)
