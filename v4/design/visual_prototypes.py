"""V4同题三套手机样稿，基线取V3冻结模型。可复算的版式实验，不是V4最终数据。

运行: python shenzhen_eat/v4/design/visual_prototypes.py
输出: v4/prototypes/style_*.pdf + 宽390/360/430的PNG。版式工具可供最终报告改造。
"""
from pathlib import Path
import io,json,re,math
from PIL import Image,ImageOps,ImageDraw
import fitz
from fontTools import subset
from fontTools.ttLib import TTFont

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'v4/prototypes'
AS=ROOT/'v2/assets'
W,H=390,844
MODEL=json.loads((ROOT/'v3/models/report_data_v3.json').read_text())
S=MODEL['selected']; A=next(s for s in S if s['mode']=='A')
M12=next(s for s in MODEL['monthly_selected'] if s['case_id']==A['case_id'] and s['month']==12)
E=next(s for s in MODEL['exit_selected'] if s['case_id']==A['case_id'] and s['exit_month']==6)
PHOTO={p['filename']:p for p in json.loads((AS/'PHOTO_MANIFEST.json').read_text())}
NAMES={'A':'传统早餐','B':'便携轻食','C':'早餐＋零食','D':'多时段餐饮','E':'分时共用'}
SC={"journal":dict(bg='#F5F1E9',ink='#1F2926',mute='#59625A',accent='#A64D31',light='#D8BD92',blue='#436C73',green='#2D6F59',red='#AC4D42',paper='#FFFFFF',line='#D7CCBB'),
"flow":dict(bg='#F2F7F6',ink='#102D40',mute='#496572',accent='#DE7E30',light='#F6D89D',blue='#326D8A',green='#288378',red='#B34B38',paper='#FFFFFF',line='#CBDAD8'),
"receipt":dict(bg='#F8F7F3',ink='#252527',mute='#63615D',accent='#315C7A',light='#E9DAB9',blue='#315C7A',green='#395E4C',red='#B54930',paper='#FFFFFF',line='#D7D5CC')}
def color(s):
    s=s.lstrip('#');return tuple(int(s[i:i+2],16)/255 for i in (0,2,4))
def fmt(v): return f'{round(v):,}'
def wan(v): return f'{v/10000:.2f}万'
def kv(v): return f'{v:,.0f}元'
def money_ratio(v,total): return v/total if total else 0
def mix(a,b,u):
    return tuple(x*(1-u)+y*u for x,y in zip(color(a),color(b)))
def prepare_fonts():
    fp=OUT/'prototype_fonts'; fp.mkdir(parents=True,exist_ok=True)
    txt=Path(__file__).read_text()+'→←↓↑•×÷±㎡¥元万0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ,.%（）／：；−'
    path='/usr/share/fonts/opentype/noto/'
    F={}
    for n,fn in [('reg','NotoSansCJK-Regular.ttc'),('bold','NotoSansCJK-Bold.ttc'),('serif','NotoSerifCJK-Bold.ttc')]:
        dest=fp/(n+'.otf')
        f=TTFont(path+fn,fontNumber=2); o=subset.Options(retain_gids=True)
        ss=subset.Subsetter(options=o);ss.populate(text=''.join(set(txt)));ss.subset(f);f.save(dest)
        F[n]=(str(dest),fitz.Font(fontfile=str(dest)))
    return F
class Canvas:
    def __init__(self,style,fonts):
        self.c=SC[style]; self.style=style; self.fonts=fonts; self.doc=fitz.open();self.p=None;self.errors=[]
    def start(self):
        self.p=self.doc.new_page(width=W,height=H)
        for name,(f,_) in self.fonts.items():self.p.insert_font(fontname=name,fontfile=f)
        self.rect(0,0,W,H,self.c['bg'])
    def resolve(self,c):return color(self.c.get(c,c))
    def rect(self,x,y,w,h,c,edge=None,line=.6): self.p.draw_rect(fitz.Rect(x,y,x+w,y+h),color=self.resolve(edge) if edge else None,fill=self.resolve(c),width=line)
    def line(self,x,y,x2,y2,c='line',w=.8):self.p.draw_line((x,y),(x2,y2),color=self.resolve(c),width=w)
    def circle(self,x,y,r,c,edge=None,width=1):self.p.draw_circle((x,y),r,color=self.resolve(edge) if edge else None,fill=self.resolve(c),width=width)
    def poly(self,pts,c,edge=None,width=.5):
        q=self.p.new_shape();q.draw_polyline([fitz.Point(x,y) for x,y in pts]+[fitz.Point(*pts[0])]);q.finish(fill=self.resolve(c),color=self.resolve(edge) if edge else None,width=width,closePath=True);q.commit()
    def arrow(self,x,y,x2,y2,c='mute',w=1.6):
        self.line(x,y,x2,y2,c,w);a=math.atan2(y2-y,x2-x);self.poly([(x2,y2),(x2-7*math.cos(a-.4),y2-7*math.sin(a-.4)),(x2-7*math.cos(a+.4),y2-7*math.sin(a+.4))],c)
    def measure(self,s,size,font):return self.fonts[font][1].text_length(str(s),fontsize=size)
    def wrap(self,text,w,size,font):
        out=[]
        for l in str(text).split('\n'):
            tokens=re.findall(r'[+−-]?\d[\d,]*(?:\.\d+)?(?:万|万元|元|㎡|单|月|小时|%)?|[A-Za-z][A-Za-z0-9.\-]*|.',l)
            cur=''
            for t in tokens:
                if cur and self.measure(cur+t,size,font)>w:
                    if t in '，。；：、！？）】%' and len(cur)>1:
                        out.append(cur[:-1]);cur=cur[-1]+t
                    else:out.append(cur);cur=t
                else:cur+=t
            out.append(cur)
        return out
    def text(self,s,x,y,w=348,size=14,color_='ink',font='reg',lh=None,align='left',maxlines=None):
        lines=self.wrap(s,w,size,font);lh=lh or size*1.35
        if maxlines is not None and len(lines)>maxlines:self.errors.append((len(self.doc),str(s),len(lines),maxlines))
        for l in lines:
            xx=x if align=='left' else x+w-self.measure(l,size,font) if align=='right' else x+(w-self.measure(l,size,font))/2
            if xx<-.5 or xx+self.measure(l,size,font)>W+.5:self.errors.append((len(self.doc),'x over',l,xx))
            if y+size>H:self.errors.append((len(self.doc),'y over',l,y))
            self.p.insert_text((xx,y+size*.93),l,fontname=font,fontsize=size,color=self.resolve(color_))
            y+=lh
        return y
    def big(self,s,x,y,w,size=34,c='ink',align='left'):
        size=min(size,w/self.measure(s,1,'bold'))
        return self.text(s,x,y,w,size,c,'bold',size*1.16,align,1)
    def image(self,fn,x,y,w,h,cover=True):
        im=Image.open(AS/fn).convert('RGB')
        if cover:im=ImageOps.fit(im,(round(w*3),round(h*3)),Image.Resampling.LANCZOS)
        else:im.thumbnail((round(w*3),round(h*3)),Image.Resampling.LANCZOS)
        b=io.BytesIO();im.save(b,format='JPEG',quality=92,optimize=True)
        self.p.insert_image(fitz.Rect(x,y,x+w,y+h),stream=b.getvalue())
    def photo_caption(self,fn,x,y,w,short):
        h=self.text(short,x,y,w,10.1,'mute',lh=13)
        self.p.insert_link(dict(kind=fitz.LINK_URI,from_=fitz.Rect(x,y,x+w,h),uri=PHOTO[fn]['source_url'])) if False else None
        self.p.insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(x,y,x+w,h),'uri':PHOTO[fn]['source_url']})
        return h
    def footer(self,n,note='示范数据取V3冻结模型 · 非V4最终结论'):
        self.line(20,805,370,805)
        self.text(note,20,815,320,9.7,'mute',lh=12,maxlines=1)
        self.text(f'{n:02}',343,814,27,11.3,'accent','bold',align='right')
    def header(self,tag,title,subtitle=None):
        self.text(tag,20,18,350,11,'accent','bold')
        y=self.text(title,20,43,350,29,'ink','serif',35)
        if subtitle:self.text(subtitle,20,y+8,350,13.2,'mute',lh=18.2)
        return y+8
    def band(self,x,y,w,h,v,total,c):
        self.rect(x,y,w,h,'line');self.rect(x,y,max(1,w*v/total),h,c)
    def stack(self,x,y,w,h,values,colors):
        total=sum(values)
        for a,c in zip(values,colors):
            ww=w*a/total;self.rect(x,y,ww,h,c);x+=ww
    def rule(self,y,c='line'): self.line(20,y,370,y,c)
    def save(self,path):
        self.doc.set_metadata({'title':f'V4 同题样板 {self.style}', 'subject':'以V3冻结数据测试手机叙事版式，不代表V4最终研究'})
        self.doc.save(path,garbage=4,deflate=True)
        if self.errors:print(self.style,'INPUT LAYOUT WARN',self.errors)

# --------------------------------------------------------------
# A: editorial field notes. Image-first, warm scene, editorial typography.
def a1(d):
    d.start()
    d.image('qiaohe_street.jpg',0,0,390,235)
    d.rect(0,0,390,39,'ink');d.text('现场笔记  /  福海新和 · 商圈篇',20,10,350,12,'paper','bold')
    d.rect(0,187,390,48,'ink');d.text('社区餐饮，是街坊的日常。',20,198,350,20,'paper','bold',maxlines=1)
    d.photo_caption('qiaohe_street.jpg',20,241,350,'桥和路周边，2023年8月实拍（非新和三区当下实景）')
    d.text('新和要看三类需求，不只学校。',20,265,350,19,'ink','bold')
    # physical relation as blocks + connective lines; position meaningless and labeled.
    d.line(194,319,194,370,'accent',1.8);d.line(68,319,322,319,'accent',1.8)
    for i,(x,n,t) in enumerate([(24,'居民','早餐、便利'),(150,'园区','通勤、简餐'),(276,'学校家庭','日常补给')]):
        d.circle(x+45,319,24,'light');d.text(n,x,307,90,11.2,'ink','bold',align='center',maxlines=1)
        d.text(t,x,341,90,11.8,'mute',align='center',maxlines=1)
    d.rect(129,369,132,38,'ink');d.text('新和社区',129,378,132,14,'paper','bold',align='center')
    d.text('关系示意；客群可重叠，不表示方位、人数或实际客流',20,414,350,10.4,'mute')
    d.image('qiaohe_noodle.jpg',20,442,169,107);d.image('tongtai_snack.jpg',201,442,169,107)
    d.text('现制餐饮',20,551,169,15,'ink','bold');d.text('零食与便利',201,551,169,15,'ink','bold')
    d.photo_caption('qiaohe_noodle.jpg',20,573,169,'桥和路 2023.08')
    d.photo_caption('tongtai_snack.jpg',201,573,169,'同泰广场 2024.06')
    d.rect(20,602,350,115,'paper')
    d.text('公开价格线索，别误读成普遍售价',32,612,326,14.5,'accent','bold')
    d.text('越师傅｜法棍＋蛋21元、鸡腿卷8元（单个用户记录，2026.11.10）',32,638,326,13,'ink',lh=18)
    d.text('宝安肠粉｜4至10元（区级报道，非新和菜单）',32,681,326,13,'ink',lh=18)
    d.text('新和本地公开挂牌：32㎡米粉店，月租3,040元，转让4.2万元（广告，未核成交）。',20,731,350,13.5,'ink','bold',lh=18.5)
    d.text('先核真实菜单、成人顾客需求与租约，再给投资数字。',20,776,350,11.7,'accent','bold')
    d.footer(1,'来源：V3市场MR12、V3P01/03；图片可点击')
def a2(d):
    d.start()
    d.header('算一笔完整的账  /  A · 传统早餐','14.15万要花在哪？','基准情景 · 30㎡ · 两位合伙人 · 工资0元。')
    d.text('不是14.15万全部花掉。',20,126,350,17,'ink','bold')
    x=20;y=158
    parts=[A['initial_opening_outlay'],A['reserve']]
    d.stack(x,y,350,20,parts,['accent','light'])
    d.big(wan(A['initial_opening_outlay']),20,185,180,28,'accent');d.big(wan(A['reserve']),223,185,146,28,'ink')
    d.text('开门实际付款及占用',20,222,182,12,'mute');d.text('留在账户备用',223,222,146,12,'mute')
    d.text('主要付款：转让4.2万、装修3.3万、设备2.25万。',20,237,350,11,'mute')
    d.rule(254)
    d.image('baozi_food.jpg',20,265,113,121)
    d.photo_caption('baozi_food.jpg',20,390,113,'前海湾站同类包点，2024.09')
    d.text('第12月：约123单/日',147,267,223,17,'ink','bold')
    d.text('现场约92单 × 8.5元\n外卖约31单 × 15元',147,296,223,15,'ink',lh=22)
    d.text('每单可用于固定支出：\n现场4.84元 / 外卖2.30元',147,347,223,12.5,'mute',lh=18)
    d.text('两人各8.5小时／0雇员（备餐与接单交付分工示意）',20,416,350,11.6,'ink')
    d.text('27营业日约3,319单；两外卖平台各半。日保本约71单。',20,433,350,11.6,'ink')
    d.text('标价3.36万 − 商家券622 − 退款118 ≈ 净收入3.29万',20,450,350,11.8,'accent','bold')
    d.text('一个月的钱如何变化',20,474,350,17,'ink','bold')
    # data-accurate nested pathway, visual consecutive balances
    vals=[('订单净收入',M12['recognized_revenue'],'ink'),('扣食材损耗、包装、平台等',M12['order_contribution'],'blue'),('扣房租等固定支出8,110元',M12['operating_profit'],'green'),('再扣周转变化及维护',M12['business_cashflow'],'green')]
    maxv=vals[0][1]
    for i,(lab,v,c) in enumerate(vals):
        y=505+i*50
        d.text(lab,20,y,237,12.7,'mute','bold');d.big(kv(v),256,y-1,114,17,c,'right')
        d.rect(20,y+23,350,13,'line');d.rect(20,y+23,350*v/maxv,13,c)
        if i<3:d.arrow(20+350*v/maxv,y+37,20+350*vals[i+1][1]/maxv,y+48,'mute',1)
    d.text('第12月经营净现金 5,570元；不等于能立即分光。',20,715,350,13,'ink','bold')
    d.rect(20,744,350,48,'ink');d.text('首年月均经营结余2,653元\n36个月累计经营净现金11.77万',31,751,330,13.6,'paper','bold',lh=18.5)
    d.footer(2)
def a3(d):
    d.start()
    d.header('退出账  /  A · 传统早餐','做了半年，再关门。','同一投入与市场基准：第6个月清算。')
    d.rect(0,125,390,116,'ink')
    d.text('两位合伙人合计累计净损失',20,140,350,13.5,'paper')
    d.big(wan(E['total_net_investor_loss']),20,164,350,42,'paper')
    d.text('各承担约5.05万元（按各半出资示范）',20,213,350,13,'paper')
    d.text('当天还要再掏多少钱？',20,256,350,17.5,'ink','bold')
    d.big(kv(E['net_exit_payment_needed']),20,281,100,32,'green')
    d.text('因为可用现金与回收资产，在模型中大于清算费用。',129,283,241,13,'mute',lh=18)
    d.text('什么钱还能拿回来？',20,342,350,16.5,'ink','bold')
    cash=E['remaining_cash'];rec=E['asset_recovery_total'];cost=E['exit_cost_total'];r=E['returned_cash_at_exit']
    d.stack(20,371,350,20,[cash,rec],['blue','green'])
    d.text(f'账上现金 {wan(cash)}  ＋  资产回收 {wan(rec)}',20,397,350,13,'ink','bold')
    d.arrow(195,419,195,438,'mute')
    d.rect(20,444,350,48,'paper');d.text('扣清算费',30,456,160,13,'mute');d.big(kv(cost),202,453,156,23,'red','right')
    d.text(f'最终退回 {wan(r)}；此前已分 {fmt(E["cumulative_distributions"])} 元',20,506,350,13,'ink','bold')
    d.text('最初筹款14.15万，减退回与此前分款＝累计损失。',20,534,350,11.8,'mute')
    d.rule(563)
    d.text('五种模式，同样第6个月退出',20,576,350,17,'ink','bold')
    gmax=max(s['exit_m6_total_net_investor_loss'] for s in S)
    for i,s in enumerate(S):
        y=610+i*34
        d.text(s['mode']+' '+NAMES[s['mode']],20,y,105,11.8,'ink','bold')
        d.rect(129,y+3,152,9,'line');d.rect(129,y+3,s['exit_m6_total_net_investor_loss']/gmax*152,9,'red' if s['mode']=='A' else 'light')
        d.big(wan(s['exit_m6_total_net_investor_loss']),285,y-2,85,15,'red','right')
    d.text('这些是同条件模型情景，不是实付损失或经营排名。',20,784,350,11.2,'mute')
    d.footer(3)
# --------------------------------------------------------------
# B: causal flow; shapes/lines represent actual relations, not a card stack.
def b1(d):
    d.start()
    d.header('市场关系图  /  区域与竞争','这片商圈，需求从哪来？','新和与相邻区域分开；周边照片不等于本地普查。')
    # Three layered context lines, diagram labelled schematic.
    d.image('qiaohe_market.jpg',20,132,350,155)
    d.photo_caption('qiaohe_market.jpg',20,293,350,'桥头市场，2023年8月实拍；仅相邻片区参照')
    d.rect(20,320,350,196,'paper')
    for x,lab,sub in [(42,'居民家庭','日常餐食'),(155,'园区职工','通勤简餐'),(268,'学校家庭','日常补给')]:
        d.circle(x+40,355,27,'light')
        d.text(lab,x,345,80,11.8,'ink','bold',align='center',maxlines=1)
        d.text(sub,x,390,80,10.7,'mute',align='center',maxlines=1)
        d.arrow(x+40,407,195,444,'blue',1.4)
    d.rect(112,444,166,47,'ink')
    d.text('新和社区（目标）',112,456,166,14.5,'paper','bold',align='center')
    d.text('客群可能重合；不是地理地图、客流测量或学校动线。',27,499,336,10.3,'mute')
    d.text('竞争不是只有早餐店',20,535,350,18,'ink','bold')
    for i,(fn,note,desc) in enumerate([('qiaohe_noodle.jpg','现制餐饮','宝安肠粉4至10元：区级报道，非新和菜单。'),('tongtai_snack.jpg','轻食与零售替代','越师傅法棍＋蛋21元、鸡腿卷8元：单次记录。')]):
        y=569+i*78;d.image(fn,20,y,101,60);d.text(note,132,y,238,14,'ink','bold');d.text(desc,132,y+23,238,12,'mute',lh=16)
        d.photo_caption(fn,20,y+61,103,'桥和路 2023.08' if i==0 else '同泰 2024.06')
    d.rect(20,731,350,60,'light')
    d.text('租金不能替代总进场成本',31,738,328,15,'ink','bold')
    d.text('新和32㎡米粉：月租3,040元，转让4.2万；公开挂牌未核成交。',31,761,328,12.3,'ink',lh=16)
    d.footer(1,'来源：V3市场MR12、V3P01/03；图片可点击')
def b2(d):
    d.start()
    d.header('统一算账图  /  A · 传统早餐','钱怎样从筹款走到现金？','标准档 · 两人亲自做 · 第12月基准 · 工资0元')
    # Connected amount flow with split / merge; all arrow meanings labelled.
    d.rect(20,120,350,67,'ink')
    d.text('两位合伙人筹款（开业资金）',31,128,328,12.8,'paper')
    d.big(wan(A['initial_funding']),31,148,328,29,'paper')
    d.arrow(195,187,195,204,'blue')
    d.line(98,208,292,208,'blue',1.6); d.arrow(98,208,98,221,'blue');d.arrow(292,208,292,221,'blue')
    for x,v,lab,co in [(20,A['initial_opening_outlay'],'付款及占用','accent'),(214,A['reserve'],'账户储备','green')]:
        d.big(wan(v),x,223,156,26,co,'center');d.text(lab,x,254,156,12.7,'mute','bold',align='center')
    d.text('主体付款：转让4.2万＋装修3.3万＋设备2.25万',20,271,350,10.8,'mute')
    d.rule(287)
    d.text('模拟做单（约123单/日 × 27天）',20,290,350,15,'ink','bold')
    # Channel lines proportional to actual order count; widths show mix.
    d.rect(20,318,350,24,'line')
    on=M12['actual_onsite_daily'];dl=M12['actual_delivery_daily'];tot=on+dl
    d.rect(20,318,350*on/tot,24,'blue');d.rect(20+350*on/tot,318,350*dl/tot,24,'accent')
    d.text(f'现场 {round(on)}单/日',26,322,240,12.6,'paper','bold')
    d.text(f'外卖 {round(dl)}',20+350*on/tot+2,322,85,10.9,'paper','bold',align='center')
    d.text('现场8.5元/单→贡献4.84元；外卖15元→2.30元',20,350,350,12.2,'ink')
    d.text('两人各8.5小时／0雇员；备餐与接单交付。日保本约71单',20,370,350,11.2,'ink')
    d.text('标价3.36万 − 商家券622 − 退款118 ≈ 净收入3.29万',20,388,350,11.4,'accent','bold')
    d.arrow(195,403,195,416,'blue')
    # cash chain "bridge" arranged with values and varying width.
    nums=[('净销售额',M12['recognized_revenue'],None,'ink'),('扣订单变动费',M12['order_contribution'],M12['recognized_revenue']-M12['order_contribution'],'blue'),('扣固定支出',M12['operating_profit'],M12['total_fixed_cost'],'green'),('扣库存/应收变化及维护',M12['business_cashflow'],M12['operating_profit']-M12['business_cashflow'],'green')]
    for i,(lab,v,sub,co) in enumerate(nums):
        y=423+i*75
        d.rect(20,y,350,59,'paper')
        d.text(lab,31,y+5,195,12,'mute','bold');d.big(kv(v),181,y+3,177,24,co,'right')
        if sub is not None:d.text('−'+kv(sub),31,y+32,195,11.4,'red')
        d.rect(31,y+46,326,5,'line');d.rect(31,y+46,326*v/nums[0][1],5,co)
        if i<3:d.arrow(195,y+60,195,y+73,'blue',1.4)
    d.text('首年月均经营结余2,653元；36月净经营现金11.77万。',20,721,350,13.2,'ink','bold',lh=18)
    d.rect(20,754,350,35,'light');d.text('不能把第12月的结余当成年均，也不能全数分光。',30,762,330,12.2,'ink','bold')
    d.footer(2)
def b3(d):
    d.start()
    d.header('退出因果图  /  A · 传统早餐','退出那天，和最终亏损','不是一回事。相同标准、混合渠道、基准市场；第6个月。')
    # A genuine diverging balance split.
    d.rect(20,124,350,64,'ink');d.text('最初筹款',31,132,190,13,'paper');d.big(wan(E['initial_funding']),31,150,328,30,'paper')
    d.arrow(195,188,195,207,'blue')
    d.text('如果退出，手头还剩多少现金？',20,211,350,15,'ink','bold')
    d.rect(20,242,169,73,'paper');d.big(wan(E['remaining_cash']),29,252,151,26,'blue');d.text('账上可用现金',29,287,151,12.8,'mute')
    d.rect(201,242,169,73,'paper');d.big(wan(E['asset_recovery_total']),210,252,151,26,'green');d.text('可回收资产',210,287,151,12.8,'mute')
    d.arrow(104,315,195,336,'blue');d.arrow(285,315,195,336,'blue')
    d.rect(20,340,350,52,'light');d.text('关闭费用 8,500元',31,349,328,15.5,'ink','bold')
    d.text('租赁解约、清理、未结杂费；员工0。',31,370,328,11.8,'mute')
    d.arrow(195,392,195,410,'blue')
    d.rect(20,413,350,62,'paper');d.text('当天净追加',31,424,153,13.3,'mute','bold');d.big('0元',190,419,168,29,'green','right');d.text('退回两人3.89万，回收未必能同日到账。',31,449,328,11.7,'mute')
    d.arrow(195,475,195,494,'blue')
    d.rect(20,498,350,75,'ink');d.text('扣除累计已分1,645元，最终损失',31,506,328,12.9,'paper');d.big(wan(E['total_net_investor_loss']),31,528,328,32,'paper')
    d.text('相同第6个月：其他模式怎样？',20,587,350,16.8,'ink','bold')
    gmax=max(s['exit_m6_total_net_investor_loss'] for s in S)
    for i,s in enumerate(S):
        y=620+i*33
        d.text(NAMES[s['mode']],20,y-2,112,11.8,'mute','bold')
        d.rect(138,y+3,146,2,'line'); xx=138+146*s['exit_m6_total_net_investor_loss']/gmax
        d.circle(xx,y+4,5,'red' if s['mode']=='A' else 'blue')
        d.big(wan(s['exit_m6_total_net_investor_loss']),291,y-5,79,15,'red' if s['mode']=='A' else 'ink','right')
    d.text('回收估值和费用均为模型假设，不代表最高风险。',20,787,350,10.9,'mute')
    d.footer(3)
# --------------------------------------------------------------
# C: decision-focused notebook; annotated expense ledger and editorial photos.
def c1(d):
    d.start()
    d.rect(0,0,390,104,'accent')
    d.text('决策笔记 / 新和社区',20,15,350,12,'paper','bold')
    d.text('先看：你的顾客是谁？',20,42,350,25,'paper','serif',maxlines=1)
    d.image('qiaohe_market.jpg',20,122,228,146)
    d.image('qiaohe_noodle.jpg',257,122,113,70)
    d.image('tongtai_snack.jpg',257,198,113,70)
    d.photo_caption('qiaohe_market.jpg',20,274,228,'桥头市场 2023.08 实拍')
    d.photo_caption('qiaohe_noodle.jpg',257,270,113,'桥和路 2023.08')
    d.photo_caption('tongtai_snack.jpg',257,283,113,'同泰 2024.06')
    d.text('照片来自周边，不能当作本地普查。便利零售也是替代。',20,301,350,11.7,'mute','bold')
    # matrix as a task-oriented list, clear boundaries but not table cards.
    d.text('买什么，取决于什么场景',20,329,350,19,'ink','bold')
    for i,(n,why,prod) in enumerate([('居民家庭','日常、价格、复购','包点、饭团、粥'),('园区职工','便捷、工作日需求','主食、可携简餐'),('学校家庭','日常补给、便利','包点、奶和饮品')]):
        y=366+i*71;d.text(f'0{i+1}',20,y,34,13,'accent','bold');d.text(n,59,y,310,15,'ink','bold');d.text(why+' → '+prod,59,y+24,310,12.5,'mute');d.rule(y+61)
    d.text('看到两个真实信号',20,592,350,18,'ink','bold')
    d.rect(20,624,350,78,'paper');d.text('价格',30,634,58,14,'accent','bold');d.text('越师傅法棍＋蛋21元、鸡腿卷8元（本地单用户记录）；宝安肠粉4至10元（区级报道）。',94,634,265,12.5,'ink',lh=17)
    d.rect(20,712,350,66,'paper');d.text('租铺',30,721,58,14,'accent','bold');d.text('新和32㎡米粉店：租3,040元/月，转让4.2万（广告；未核成交）。',94,721,265,12.5,'ink',lh=17)
    d.footer(1,'来源：V3市场MR12、V3P01/03；图示非实测')
def c2(d):
    d.start()
    d.rect(0,0,390,100,'accent')
    d.text('传统早餐 / 完整决策链',20,16,350,11.8,'paper','bold')
    d.text('一张票据，看懂回钱逻辑',20,43,350,24,'paper','serif',maxlines=1)
    d.text('30㎡ · 两位合伙人自己经营 · 工资0元 · 标准档',20,115,350,13,'mute')
    d.image('baozi_food.jpg',20,143,101,93)
    d.photo_caption('baozi_food.jpg',20,240,101,'前海湾同类包点\n2024.09')
    d.text('初始筹款',136,145,234,13,'mute','bold');d.big(wan(A['initial_funding']),136,165,234,30,'accent')
    d.text(f'付款及占用{wan(A["initial_opening_outlay"])}，备用{wan(A["reserve"])}',136,207,234,12.4,'ink',lh=17.8)
    d.text('转让4.2万＋装修3.3万＋设备2.25万',136,244,234,10.6,'mute')
    # A receipt: no repeated cards; exact values and gridded reading.
    d.rect(20,272,350,359,'paper')
    d.text('第12月营业流水',31,283,328,17,'ink','bold')
    d.text('27个营业日，约123单/日，共3,319单。',31,310,328,12.4,'mute')
    d.text('现场约92单/日 × 8.5元，外卖31单 × 15元。',31,331,328,12.4,'mute')
    d.text('标价33,600 − 券622 − 退款118（约数，元）',31,349,328,11.8,'accent','bold')
    d.line(31,367,359,367,'line',1.2)
    rows=[
      ('净销售额',M12['recognized_revenue'],'ink'),
      ('− 订单变动费用',M12['recognized_revenue']-M12['order_contribution'],'red'),
      ('= 订单贡献',M12['order_contribution'],'accent'),
      ('− 房租等固定支出',M12['total_fixed_cost'],'red'),
      ('= 经营结余',M12['operating_profit'],'green'),
      ('− 周转净变化及维护',M12['operating_profit']-M12['business_cashflow'],'red'),
      ('= 经营净现金',M12['business_cashflow'],'green'),
    ]
    for i,(lab,v,c) in enumerate(rows):
        y=375+i*35
        d.text(lab,31,y,183,13.6,'ink','bold' if i in [0,2,4,6] else 'reg')
        d.big(kv(v),215,y-1,144,19,c,'right');d.line(31,y+28,359,y+28,'line',.6)
    d.text('两人各8.5小时／0雇员；备餐与接单交付。日保本约71单。',20,638,350,11.2,'ink')
    d.text('渠道贡献：现场4.84元/单；美团和闪购各2.30元/单。',20,656,350,12.2,'ink',lh=17)
    d.rule(692)
    d.text('首年与三年不能混着算',20,704,350,16.5,'ink','bold')
    d.big(kv(A['y1_avg_monthly_profit']),20,734,164,25,'green')
    d.big(wan(A['cumulative_business_cashflow']),204,734,166,25,'green','right')
    d.text('首年月均经营结余',20,765,168,12,'mute');d.text('三年累计经营净现金',190,765,180,12,'mute',align='right')
    d.footer(2)
def c3(d):
    d.start()
    d.rect(0,0,390,105,'accent')
    d.text('决策笔记 / 退出与比较',20,15,350,12,'paper','bold')
    d.text('先问自己能承受多少损失。',20,43,350,24,'paper','serif',maxlines=1)
    d.text('A传统早餐 · 标准档 · 第6个月退出 · 基准市场',20,121,350,13,'mute')
    # owner cash trail with big value + equation
    d.big(wan(E['total_net_investor_loss']),20,156,350,43,'red')
    d.text('两位累计净损失，不是退出当天再付的金额。',20,208,350,14.2,'ink','bold')
    d.rect(20,243,350,191,'paper')
    for i,(lab,v,co) in enumerate([('最初出资',E['initial_funding'],'ink'),('− 此前已分款',E['cumulative_distributions'],'green'),('− 清算后退回',E['returned_cash_at_exit'],'green'),('= 最终净损失',E['total_net_investor_loss'],'red')]):
        y=257+i*42;d.text(lab,31,y,180,14,'ink','bold');d.big(kv(v),195,y-1,164,19,co,'right');d.rule(y+33)
    d.text('退回怎么算？',20,454,350,17.5,'ink','bold')
    d.text(f'账上现金 {fmt(E["remaining_cash"])} ＋资产回收 {fmt(E["asset_recovery_total"])}\n− 清算费 {fmt(E["exit_cost_total"])} ＝约 {fmt(E["returned_cash_at_exit"])} 元。',20,482,350,13.3,'ink',lh=21)
    d.rect(20,538,350,41,'light');d.text('退出当天净追加0元；实际到账时点与违约金额待核。',30,547,330,12.3,'ink','bold')
    d.text('五模式累计损失对照（半年）',20,600,350,16.5,'ink','bold')
    for i,s in enumerate(S):
        y=635+i*30;d.text(s['mode']+'  '+NAMES[s['mode']],20,y,165,12.3,'mute','bold')
        d.big(wan(s['exit_m6_total_net_investor_loss']),190,y-2,180,17,'red' if s['mode']=='A' else 'ink','right');d.rule(y+25)
    d.text('情景模拟，不代表实际成交或最高风险。',20,788,350,11,'mute')
    d.footer(3)

def main():
    fonts=prepare_fonts()
    for style,pages in [('journal',[a1,a2,a3]),('flow',[b1,b2,b3]),('receipt',[c1,c2,c3])]:
        d=Canvas(style,fonts)
        for p in pages:p(d)
        fn=OUT/f'style_{style}.pdf';d.save(fn)
        check=fitz.open(fn)
        for i,p in enumerate(check):
            for width in [360,390,430]:
                pix=p.get_pixmap(matrix=fitz.Matrix(width/W,width/W),alpha=False)
                pix.save(OUT/f'style_{style}_{i+1}_{width}.png')
        print(style, 'pages',len(check),'extractable_chars',sum(len(p.get_text()) for p in check),'errors',d.errors)
    # Same topic across three approaches in separate images meaningful at reader size.
    for i in range(1,4):
        files=[OUT/f'style_{s}_{i}_390.png' for s in ['journal','flow','receipt']]
        ims=[Image.open(f) for f in files]; w=390*3+40;h=844+25
        canvas=Image.new('RGB',(w,h),'#dddddd'); dr=ImageDraw.Draw(canvas)
        for j,(im,s) in enumerate(zip(ims,['A JOURNAL','B FLOW','C RECEIPT'])):
            canvas.paste(im,(j*(390+10)+10,0));dr.text((j*(390+10)+10,848),s,fill='black')
        canvas.save(OUT/f'V4_same_topic_{i}_compare.png')
if __name__=='__main__':main()
