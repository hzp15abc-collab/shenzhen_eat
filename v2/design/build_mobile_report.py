"""Mobile-first reader edition. Source data independent of display rounding."""
from pathlib import Path
import json,csv,re,math,io,os,copy
import fitz
from fontTools.ttLib import TTFont
from fontTools import subset
from PIL import Image,ImageOps
HERE=Path(__file__).resolve().parent; V2=HERE.parent; ROOT=V2.parent
OUT=ROOT/'deliverables'/'Shenzhen_Eat_手机商业指南_V2.pdf'
W,H=390,844; M=24; CW=W-2*M; LIMIT=778
BG='#FBF6ED'; INK='#183832'; DIM='#52655D'; ACC='#94613B'; DARK='#203C34'; PALE='#E8EBDD'; SAND='#F2E4CF'; PAPER='#FFFDF8'; BRICK='#9C4634'; ROSE='#F4DDD3'; BLUE='#263E52'; LINE='#D7D6C7'; OLIVE='#60765C'; WHITE='#FFFFFF'
DATA=json.load(open(HERE/'editorial_content.json'))
SC=DATA['source_catalog']; entries=copy.deepcopy(DATA['pages'])
MOD=json.load(open(ROOT/'models/model_results.json'))['modes']
raw=list(csv.DictReader(open(ROOT/'models/summary.csv',encoding='utf-8-sig')))
R={(r['mode'],r['scenario']):r for r in raw}
monthly=list(csv.DictReader(open(ROOT/'models/monthly.csv',encoding='utf-8-sig')))
NAMES={'A':'传统早餐','B':'特色早餐','C':'早餐＋零食','D':'全天组合','E':'分时合作'}
def val(a,k,s='base'): return float(R[a,s][k] or 0)
def amount(n,prec=1):
 n=abs(n)
 if n>=10000:return f'{n/10000:.{prec}f}'.rstrip('0').rstrip('.')+'万元'
 if n>=100:return f'{round(n/10)*10:,.0f}元'
 return f'{round(n):,}元'
def sign_amount(n,prec=1):return ('赚约' if n>=0 else '亏约')+amount(n,prec)
def page(id,section,title,lead,metrics=[],body=[],note='',sources=[],layout='text'):
 return {'id':id,'section':section,'title':title,'lead':lead,'metrics':metrics,'body':body,'note':note,'sources':sources,'layout':layout}
def met(label,value,context=''):return {'label':label,'value':value,'context':context}
def para(title,text):return {'title':title,'text':text}
# Enrich comparison; keep exact values in model. This is a reader guide, not a re-estimated model.
extra={
 27:[page('27a','钱到底怎么算','每天能卖够单，为什么还是可能亏？','以传统早餐A为例，模型成熟营业日约212单，比首年保本约179单多。但这不代表全年每天都客满。',
  [met('成熟营业日假设','约212单','不是当地测到的客流'),met('首年正常保本门槛','约179单','含老板劳动成本')],
  [para('开业需要时间','刚开始客人少，复购要慢慢积累；租金和固定开支却从开业就发生。'),para('客群会变化','寒暑假、春节、工作日与周末、雨天都会影响需求；居民、园区和学校家庭能否互补要实际验证。'),para('同行会分流','价格和竞争一变，每单留的钱及每日订单都可能下降。')],
  '所以必须看36个月的账户余额，而不是只拿最好的一天乘以30天。',['MODEL','M14'],'text')],
 23:[page('23a','钱到底怎么算','不开张的时候，哪些钱照样要付？','房租之外，工资、水电、物业和日常运营，还有老板自己的时间。这里是首年基准每月固定支出的估算。',
  [met(a+' '+NAMES[a],amount(val(a,'basic_monthly_fixed')),f"场地费{MOD[a]['lease_cash']:,}元；雇员{MOD[a]['staff_loaded']:,}元；老板工资{MOD[a]['owner_labor']:,}元") for a in NAMES],
  [],'不含按销量变化的食材、损耗、包装及分成。全部是模型假设；真正租约和人工需实报实算。',['MODEL'],'money_chart')],
 24:[page('24a','钱到底怎么算','卖100元，扣下食材还剩多少？','这是毛利而不是净利润。不同菜单的原料和损耗差别很大。',
  [met(a+' '+NAMES[a],f"约{val(a,'normal_gross_margin')*100:.0f}元",f"再扣包装、费率、税费预算等后约{val(a,'normal_contribution_margin')*100:.0f}元") for a in NAMES],
  [],'以上以100元销售额演示，来自首年基准菜单成本模型，并非当地同行毛利实测。剩余金额还要付房租、人工、水电等固定支出。',['MODEL'],'gross')],
 28:[page('28a','三年会怎样','同样开三年，哪一年才缓过来？','基准模拟：大数字是第2年平均每月结果；右侧对比第1年、第3年。均已计老板劳动，未扣折旧。',
  [met(a+' '+NAMES[a],sign_amount(val(a,'year2_operating_profit')/12),f"第1年{sign_amount(val(a,'year1_operating_profit')/12)}\n第3年{sign_amount(val(a,'year3_operating_profit')/12)}") for a in NAMES],
  [],'每个数是该年12个月的平均结果，不表示月月相同；亏损、淡季与竞争按月在沙盘中模拟。',['MODEL'],'money_chart')],
 30:[page('30a','三年会怎样','三年里，账户上的钱怎样变化？','基准情景，从开业留在账上的备用金开始。每条线代表一个模式的逐月现金余额。',[],[],
  '红线是0元：跌破即出现资金缺口，而不是建议继续追投。全部为假设。',['MODEL'],'sparks')]
}
# Plain-language and accuracy refinements.
for e in entries:
 if e['id']==19:e['title']='20平方米，一天能做多少单？'
 if e['id']==18:
  e['lead']='做生意先问五件事：卖什么、卖多少钱、在哪里卖、怎么让人知道、谁来做。'
  for b in e['body']: b['title']=b['title'].split('（')[0]
 if e['id']==20:e['body'][0]['text']='自己做也要算工资。深圳2026年9月起最低月工资2700元；实际用人成本还要核实工时、社保和报价。';e['note']=''
 if e['id']==24:e['metrics'][2]['label']='每单真正能拿去付房租人工的钱';e['metrics'][2]['context']='再扣包装、比例费用和税费预算'
 if e['id']==22:e['title']='12万元转让费，得赚多少才能补回来？'
 if e['id']==23:e['title']='开店要花的钱，和要准备的钱不同';e['lead']='包括开业支出与三个月备用金的五种起步预算（基准模拟）。下方条形中绿色代表备用金。'
 if e['id']==27:e['lead']='数字说明目标难度，不是实测订单。浅色条＝成熟营业日订单假设；棕色条＝每日保本门槛。'
 if e['id']==25:
  e['title']='老板赚到的工资，不等于投资回报';e['metrics'][0]['label']='没给自己算工资前，每月经营结余';e['metrics'][0]['context']='不是全部可提款的现金'
 if e['id']==28:
  e['title']='生意做三年，钱会多还是少？';e['lead']='三个可能情景下，36个月经营净现金。已算老板工资、库存变化和设备维护，还没扣开业投入。'
  for a,mm in zip('ABCDE',e['metrics']):
   vv=val(a,'total_free_cash');bb=val(a,'total_free_cash','bad');gg=val(a,'total_free_cash','good')
   mm['value']=('净进账约' if vv>=0 else '净流出约')+amount(vv)
   mm['context']='不顺：流出约'+amount(bb)+'\n顺利：进账约'+amount(gg)
 if e['id']==32:
  for mm in e['metrics']:mm['value']=mm['value'].replace('约','约亏')
  e['body'][1]['text']='如果把资金拿去做别的，也有机会成本。模型以6%的年折现率测试，基准三年清算时仅E略为正（约3300元），其余为负；不代表实际可赚。'
 if e['id']==6:
  e['body'].append(para('学校收费也只是参考','公办小学目录记载免费；鹏晖旧收费文件列小学每学期4100至5400元、初中5500元。不是当前收费或学生家庭收入。'))
 if e['id']==4:
  e['body'][2]['text']='旧官方目录记载两校均不提供住宿，现时情况待确认。学校供餐、家中自备和外购的实际比例未知；人数绝不等于订单。'
 if e['id']==31:
  e['metrics'][0]['value']='少约4.8万元';e['metrics'][1]['value']='少约10.3万元';e['metrics'][2]['value']='约赚1,700元'
 if e['layout']=='mode':
  for mm in e['metrics']:
   if mm['label']=='正常成熟营业日保本订单':mm['label']='首年正常成本下，每日保本';mm['context']='非当地实测，也不保证全年盈利'
  a='ABCDE'[e['id']-12];e['body'][2]['text']=e['body'][2]['text'].rstrip('。；')+'；场地费假设'+format(MOD[a]['lease_cash'],',')+'元/月。'
  e['note']='基准模拟，非实测；36个月内未收回开业支出（不含备用金）。'
  if a=='E':e['note']='基准模拟：第24个月仅覆盖开业支出约1.56万元（不含备用金）。共享须合法。'
# Real photo captions: source links and credits taken from verified manifest file once available.
# All near-site photos explicitly not from exact core site; do not infer present operation.
PH={
 'qiaohe_street.jpg':('福海桥和路沿街商铺，2023年8月实拍。仅周边参照，非新和三区。','JMUAIANWNC 3366688','CC BY-SA 4.0'),
 'qiaohe_market.jpg':('福海桥头菜肉市场，2023年8月实拍。仅周边参照。','JMUAIANWNC 3366688','CC BY-SA 4.0'),
 'qiaohe_congee.jpg':('福海桥和路砂锅粥店，2023年8月实拍。历史门面，非当前经营证明。','JMUAIANWNC 3366688','CC BY-SA 4.0'),
 'qiaohe_noodle.jpg':('福海桥和路潮汕面馆，2023年8月实拍。周边同类店型。','JMUAIANWNC 3366688','CC BY-SA 4.0'),
 'qiaohe_bakery.jpg':('福海桥和路蛋挞店，2023年8月实拍。周边同类门店。','JMUAIANWNC 3366688','CC BY-SA 4.0'),
 'qiaohe_restaurants.jpg':('福海桥和路沿街门店，2023年8月实拍。非新和三区商户盘点。','JMUAIANWNC 3366688','CC BY-SA 4.0'),
 'tongtai_foodstreet_05.jpg':('福海桥头同泰时代广场沿街餐饮，2024年6月实拍。周边参照。','NGAON32 Hongam','CC0'),
 'tongtai_snack.jpg':('福海桥头同泰时代广场零食店，2024年6月实拍。仅店型参照。','NGAON32 Hongam','CC0'),
 'tongtai_booth.jpg':('福海桥头同泰时代广场小摊位，2024年6月实拍。仅小空间参照，并非已确认可分租。','NGAON32 Hongam','CC0'),
 'generated_shared.jpg':('AI生成的写实厨房场景示意，非新和实拍，也非已核实合作铺。','AI生成','生成示意'),
 'generated_portable.jpg':('AI生成的便携早餐小店示意，非真实门店或实际新和场景。','AI生成','生成示意'),
 'generated_breakfast.jpg':('AI生成的早餐摊示意，非真实新和门店。','AI生成','生成示意'),
 'generated_snacks.jpg':('AI生成的零食陈列场景示意，非真实新和门店。','AI生成','生成示意')
}
# Load verified photos from agent manifest if present; fallback captions are overridden by manifest.
manifest_path=V2/'assets'/'PHOTO_MANIFEST.json'
manifest={}
if manifest_path.exists():
 x=json.load(open(manifest_path))
 if isinstance(x,list): manifest={str(item.get('file') or item.get('filename') or item.get('local_file')):item for item in x}
 elif isinstance(x,dict):
  items=x.get('photos',x)
  if isinstance(items,list):manifest={str(item.get('file') or item.get('filename') or item.get('local_file')):item for item in items}
  else:manifest=items
# explicit product photo labels with source details taken from manifest when available
PH.update({
 'baozi_food.jpg':('南山前海湾站包点，2024年9月实拍。餐品参照，非新和。','HHAFOL Moratim LUNG','CC0'),
 'sandwich.jpg':('真实三明治照片，餐品参考；非当地实际菜单。','见图片来源页','见图片来源页'),
 'sandwich_combo.jpg':('福田连城新天地三明治餐品，2024年3月实拍。非新和。','Mam 302 iGRean','CC0')})
PH_MAP={1:'qiaohe_street.jpg',3:'qiaohe_market.jpg',7:'qiaohe_restaurants.jpg',10:'baozi_food.jpg',12:'qiaohe_noodle.jpg',13:'sandwich_combo.jpg',14:'tongtai_snack.jpg',15:'qiaohe_congee.jpg',16:'generated_shared.jpg',20:'tongtai_booth.jpg'}
# Keep photos first; fallback if no licensed material is available.
for k,v in list(PH_MAP.items()):
 if not (V2/'assets'/v).exists(): PH_MAP[k]= 'generated_portable.jpg' if k==13 else 'generated_breakfast.jpg'
# sequence with a separate linked contents screen
seq=[]
for e in entries:
 seq.append(e)
 if e['id']==2:seq.append(page('toc','阅读地图','想看哪一段？','点下面任一问题，直接跳到对应章节。',[],[],'每页底部都可以回目录。也可以像电子书一样一页页往下读。',[],'toc'))
 seq.extend(extra.get(e['id'],[]))
# concise candidate record appendices (real leads, no data duplication)
comp=[]
for L in (ROOT/'research/02_competition.md').read_text().splitlines():
 a=[i.strip() for i in L.strip('|').split('|')]
 if len(a)==4 and re.match(r'^[ABC] \[S',a[3]):comp.append(a)
for i in range(0,len(comp),9):
 part=comp[i:i+9]
 seq.append(page(f'comp{i//9+1}','查资料','找到的商户记录（'+str(i//9+1)+'）','以下是已去重的公开候选名字和区域，并不是当前营业确认或完整普查。',[],[para(a[0],a[1]+' · '+a[3]) for a in part], 'A＝官方或交叉确认；B＝单个目录/体验；C＝待核线索。实际经营状况应现场核实。',[],'list'))
# rental lead appendix: preserve all 11
rents=list(csv.DictReader(open(ROOT/'evidence/competition_rental_samples.csv',encoding='utf-8-sig')))
# examine columns generically and extract selected key values
def rent_record(r):
 vals=list(r.values());return para(str(vals[0]),' · '.join(str(v) for v in vals[1:4]))
# Explicit data copied from V1 evidence table, no claim of current available space.
rentlines=[('新和三区朵拉国际社区','30㎡ · 1,180元/月，餐饮条件未知'),('新和五区卤味铺','28㎡ · 1,600元/月，广告称可明火'),('新和茂华优选广场附近','40㎡ · 3,000元/月，百货转让'),('新和二区精酿店','20㎡ · 3,300元/月，转让费待谈'),('新和二区临街底商','45㎡ · 6,100元/月，未明示餐饮'),('新和新兴工业区','100㎡ · 6,050元/月，转让报价12.8万元'),('新和二区悦盛三路','100㎡ · 10,000元/月，烤鱼小炒'),('新和二区饮品店','80㎡ · 16,300元/月，转让费待谈'),('邻近桥头商业铺','50㎡ · 4,000元/月'),('邻近桥和路早餐铺','30㎡ · 8,860元/月'),('邻近塘尾包点店','120㎡ · 7,400元/月')]
for i in range(0,len(rentlines),6):
 seq.append(page(f'rent{i//6+1}','查资料','全部租赁挂牌线索（'+str(i//6+1)+'）','2026年11月27日检索，八条目标社区加三条邻近对照。不是成交价。',[],[para(a,b) for a,b in rentlines[i:i+6]],'详情页存在访问验证限制，必须问房东确认在租状态、用途、面积、转让费和租约。',['R01','R02','R03','R04','R05','R06','R07','R08','R09'],'list'))
# Append photo provenance and full source list in compact phone-native screens.
usedphotos=list(dict.fromkeys(PH_MAP.values()))
# Source manifest can contain direct url attributes; exact URLs loaded from agent output
for i in range(0,len(usedphotos),4):
 seq.append(page(f'photo{i//4+1}','查资料','照片从哪里来？（'+str(i//4+1)+'）','每张图均注明地域和时间。真实照片仅作历史街区或同类店型参照；生成图单独标记。',[],[], '照片在报告中为适配手机版式作缩放/裁切；原始照片许可见各条。',[],'photosources'))
 seq[-1]['photo_keys']=usedphotos[i:i+4]
codes=[k for k in SC if SC[k].get('urls')]
for i in range(0,len(codes),6):
 seq.append(page(f'src{i//6+1}','查资料','公开资料索引（'+str(i//6+1)+'）','点下方资料标题，可直接打开原始网页。研究检索日期为2026年11月27日。',[],[],'部分页面可能更新、失效或要求正常验证。更多计算与背景详见完整研究工程。',[],'sources'))
 seq[-1]['source_keys']=codes[i:i+6]
# font subset uses original CFF glyph IDs and all text to avoid missing/misrendered Chinese.
font_dir=V2/'design'/'fonts';font_dir.mkdir(exist_ok=True)
charset=open(__file__,encoding='utf8').read()+json.dumps(seq,ensure_ascii=False)+json.dumps(SC,ensure_ascii=False)+json.dumps(PH,ensure_ascii=False)+json.dumps(manifest,ensure_ascii=False)+'0123456789+-−.·%¥￥／—，。、（）…→'
F={}
rootfont=Path('/usr/share/fonts/opentype/noto')
for label,file in [('reg','NotoSansCJK-Regular.ttc'),('bold','NotoSansCJK-Bold.ttc'),('serif','NotoSerifCJK-Bold.ttc')]:
 target=font_dir/(label+'.otf'); ft=TTFont(rootfont/file,fontNumber=2); sub=subset.Subsetter(options=subset.Options(retain_gids=True));sub.populate(text=charset);sub.subset(ft);ft.save(target);F[label]=(str(target),fitz.Font(fontfile=str(target)))
def rgb(h):h=h.lstrip('#');return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
def wrap(s,w,size,font='reg'):
 out=[]
 for pp in str(s).split('\n'):
  a=''
  for ch in re.findall(r'\d[\d,]*(?:\.\d+)?(?:万元|元/月|元|万|单/日|单|个月|月|年|%|㎡|秒|小时)?|[A-Za-z][A-Za-z0-9.\-]*|.',pp):
   if a and F[font][1].text_length(a+ch,fontsize=size)>w:
    # keep punctuation with preceding char when possible
    if ch in '，。；：、！？）】%％' and len(a)>1:out.append(a[:-1]);a=a[-1]+ch
    else:out.append(a);a=ch
   else:a+=ch
  if a:out.append(a)
 return out
def height(s,w,size,font='reg',lh=None):return len(wrap(s,w,size,font))*(lh or size*1.44)
doc=fitz.open()
pending=[]; sections={}; actual=[]; used_set=set()
def rect(p,x,y,w,h,color,stroke=None):
 p.draw_rect(fitz.Rect(x,y,x+w,y+h),fill=rgb(color),color=rgb(stroke) if stroke else None,width=.6,overlay=True)
def line(p,x,y,x2,y2,color=LINE,width=.8):p.draw_line((x,y),(x2,y2),color=rgb(color),width=width)
def text(p,s,x,y,w=CW,size=16.5,color=INK,font='reg',lh=None):
 lh=lh or size*1.44
 for r in wrap(s,w,size,font):
  p.insert_text((x,y+size*.96),r,fontname=font,fontsize=size,color=rgb(color))
  y+=lh
 return y
def tline(p,s,x,y,size,color=INK,font='reg'):
 return text(p,s,x,y,W-x-6,size,color,font,size*1.26)
def hyperlink(p,rect_,*,target=None,url=None):
 pending.append((p.number,rect_,target,url))
def new(e,continuation=False):
 p=doc.new_page(width=W,height=H)
 for k,(f,_) in F.items():p.insert_font(fontname=k,fontfile=f)
 rect(p,0,0,W,H,BG);rect(p,0,0,W,6,DARK)
 actual.append({'page':p.number,'id':e['id'],'section':e['section'],'title':e['title'],'continuation':continuation})
 if e['section'] not in sections:sections[e['section']]=p.number
 return p
def caption(p,key,y):
 # Actual media page source is clickable; complete source details in appendix.
 c=PH[key][0]
 y=text(p,c,M,y,CW,11.7,DIM,lh=16.1)
 y2=text(p,'图源及授权 / 点击查看',M,y+1,CW,10.8,ACC,font='bold',lh=14)
 hyperlink(p,(M,y,W-M,y2+1),target='photo'+str(usedphotos.index(key)//4+1))
 return y2+9
def photo(p,key,y,h=153):
 f=V2/'assets'/key
 im=Image.open(f).convert('RGB')
 # cover crop performed solely for editorial page layout; source unchanged.
 im=ImageOps.fit(im,(int(CW*2.4),int(h*2.4)),method=Image.Resampling.LANCZOS,centering=(.5,.51))
 b=io.BytesIO();im.save(b,format='JPEG',quality=89,optimize=True)
 p.insert_image(fitz.Rect(M,y,W-M,y+h),stream=b.getvalue())
 used_set.add(key)
 return caption(p,key,y+h+6)
def header(p,e,photo_key=None,cont=False):
 y=21
 y=text(p,e['section']+(' · 续读' if cont else ''),M,y,CW,12.5,ACC,'bold',17)+10
 if photo_key:y=photo(p,photo_key,y,105 if e['layout']=='mode' else 139 if e['id']==20 else 168)
 title=e['title']
 if cont:title='接着看：'+e['title']
 size=27 if len(title)<22 else 25.4
 y=text(p,title,M,y,CW,size,INK,'serif',size*1.28)+10
 if not cont:y=text(p,e['lead'],M,y,CW,17,DIM,'reg',25)+13
 return y
def footer(p,e,last=False):
 line(p,M,789,W-M,789,LINE)
 tline(p,'目录',M,799,13,ACC,'bold');hyperlink(p,(M,795,M+68,823),target='toc')
 tline(p,'下一页 →' if not last else '返回目录',W-101,799,13,ACC,'bold')
 if not last:hyperlink(p,(W-115,795,W-M,824),target=('next',p.number))
 else:hyperlink(p,(W-115,795,W-M,824),target='toc')
 tline(p,'新和 · 开店指南',M,825,9.3,DIM)
 tline(p,f'{p.number+1:02}',W-53,825,10,DIM,'bold')
def note_block(p,s,y,small=False):
 if not s:return y
 size=13.2 if small else 14.1;hh=height(s,CW-24,size,lh=size*1.42)+31
 rect(p,M,y,CW,hh,SAND);rect(p,M,y,3,hh,ACC)
 text(p,'读这页请留意',M+12,y+8,CW-24,11.8,ACC,'bold',15)
 y2=text(p,s,M+12,y+24,CW-24,size,INK,lh=size*1.42)
 return y+hh+10
def bodyblock(p,b,y,check=False,compact=False):
 sz=16.2 if compact else 16.6
 title=b['title'];body=b['text']
 if check:
  rect(p,M,y+4,16,16,PAPER,ACC); x=M+28; w=CW-28
 else:x=M;w=CW
 y=text(p,title,x,y,w,16.3,INK,'bold',23)
 y=text(p,body,x,y+2,w,sz,INK,'reg',24)
 line(p,x,y+6,W-M,y+6,LINE,.6)
 return y+16
def metricblock(p,m,y,big=False,compact=False):
 label=m['label'];v=m['value'];ctx=m['context']
 risk=('亏' in v or '流出' in v or '少约' in v or v.startswith('-') or '缺口' in v and '无' not in v or '未回本' in v)
 cc=BRICK if risk else INK
 if big:
  h1=height(label,CW-30,13.2,'reg',18)
  size=33 if len(v)<8 else 29
  h2=height(v,CW-30,size,'bold',size*1.16)
  h3=height(ctx,CW-30,13.8,'reg',18)
  hh=16+h1+h2+h3+9
  rect(p,M,y,CW,hh,DARK)
  yy=text(p,label,M+15,y+8,CW-30,13.2,'#F4EBDD','reg',18)
  yy=text(p,v,M+15,yy+2,CW-30,size,WHITE,'bold',size*1.16)
  text(p,ctx,M+15,yy+1,CW-30,13.8,'#E7EADD','reg',18)
  return y+hh+12
 if compact:
  # value left, label + context right, two-column row, not a table.
  vw=154; gap=9
  vn=21 if len(v)<10 else 17.2
  hval=height(v,vw,vn,'bold',vn*1.22)
  hr=height(label,CW-vw-gap-8,14.2,'bold',19)+height(ctx,CW-vw-gap-8,12.1,'reg',17)+3
  hh=max(hr,hval)+12
  text(p,v,M,y+4,vw,vn,cc,'bold',vn*1.22)
  y2=text(p,label,M+vw+gap,y,CW-vw-gap,14.2,DIM,'bold',19)
  text(p,ctx,M+vw+gap,y2+2,CW-vw-gap,12.1,DIM,'reg',17)
  line(p,M,y+hh-3,W-M,y+hh-3,LINE,.7)
  return y+hh+8
 # editorial amount tile with direct context
 labelh=height(label,CW,14.6,'bold',20)
 vsize=24 if len(v)<13 else 20.5
 vh=height(v,CW,vsize,'bold',vsize*1.15)
 ch=height(ctx,CW,13.9,'reg',19)
 yy=text(p,label,M,y,CW,14.6,DIM,'bold',20)
 yy=text(p,v,M,yy+2,CW,vsize,cc,'bold',vsize*1.15)
 yy=text(p,ctx,M,yy+3,CW,13.9,DIM,'reg',19)
 line(p,M,yy+6,W-M,yy+6,LINE,.7)
 return yy+14
def source_ref(p,e,y):
 if e.get('sources'):
  c=[s for s in e['sources'] if s in SC and SC[s].get('urls')]
  if c:
   target='src'+str((codes.index(c[0])//6)+1)
   y2=text(p,'资料来源 · 点此查看',M,y,CW,11.7,ACC,'bold',16)
   hyperlink(p,(M,y,W-M,y2+2),target=target)
  else:y2=text(p,'数字来自原始财务模拟（可复算工程）',M,y,CW,11.7,DIM,'reg',16)
  return y2
 return y
def draw_cover(p,e):
 rect(p,0,0,W,H,DARK);rect(p,0,0,W,7,ACC)
 y=text(p,'深圳宝安 · 福海新和社区',M,28,CW,14.5,'#F0D9B7','bold',21)+10
 y=text(p,'在新和，开一家\n能养活自己的小店？',M,y,CW,36,WHITE,'serif',43)+13
 y=text(p,'一份给第一次做生意的人看的开店指南',M,y,CW,17,'#F2E4CE','reg',25)+12
 # Full photo with explicit annotation; adjacent commercial scene, not target core.
 f=V2/'assets'/PH_MAP[1];im=Image.open(f).convert('RGB')
 im=ImageOps.fit(im,(840,630),method=Image.Resampling.LANCZOS);buf=io.BytesIO();im.save(buf,format='JPEG',quality=90)
 p.insert_image(fitz.Rect(M,y,W-M,y+250),stream=buf.getvalue());used_set.add(PH_MAP[1]);y+=256
 yy=y;y=text(p,PH[PH_MAP[1]][0]+' · 图源见照片页',M,y,CW,12.1,'#EBDCC2','reg',17)+15
 hyperlink(p,(M,yy,W-M,y),target='photo1')
 y=text(p,'五种做法｜三年经营账｜如何小成本验证',M,y,CW,17.2,WHITE,'bold',25)+11
 y=text(p,'不是一份告诉你“哪家店一定赚钱”的报告。是把选择、投入、风险和条件说明白。',M,y,CW,16.2,'#F0E5D5','reg',24)+14
 y=text(p,'2026年11月27日 · 桌面研究与模拟',M,y,CW,12.3,'#E3D9C6','reg',18)
 tline(p,'开始阅读 →',M,786,18,'#FFFFFF','bold');hyperlink(p,(M,778,W-M,831),target=2)
def draw_toc(p,e,y):
 groups=[('看懂这个地方','学校、住户和真正会花钱的人',3),('看看同行','现有门店、房租和地段',7),('选择做什么','五种开店方式',10),('怎么经营','人员、设备和供应链',18),('签约之前','铺面、证照与转让费',21),('钱到底怎么算','启动资金、每单毛利与保本',23),('三年会怎样','回本、竞争与退出',28),('开始前怎么试','低成本市场验证',33),('查资料','商户、房源、照片与来源','comp1')]
 for j,(label,desc,target) in enumerate(groups):
  yy=y; text(p,f'{j+1:02}',M,yy,36,17,ACC,'bold',23)
  yy=text(p,label,M+40,yy,CW-48,16.7,INK,'bold',23); yy=text(p,desc,M+40,yy,CW-48,13.4,DIM,'reg',19)
  line(p,M,yy+4,W-M,yy+4,LINE);hyperlink(p,(M,y,W-M,yy+6),target=target);y=yy+12
 return y
def draw_stacked(p,e,y):
 colors=[OLIVE,ACC,BRICK];parts=[66.3,25.8,7.9];xx=M
 for co,v in zip(colors,parts):rect(p,xx,y,CW*v/100,25,co);xx+=CW*v/100
 y+=36
 for m,co in zip(e['metrics'],colors):
  rect(p,M,y+8,9,9,co);tline(p,m['label'],M+17,y,15,DIM,'bold')
  text(p,m['value'],W-M-75,y-3,75,21,INK,'bold',27);y+=32
 return y+9
def draw_sparks(p,e,y):
 maxabs=max(abs(float(r['cash_balance'])) for r in monthly if r['scenario']=='base')/10000
 for a in NAMES:
  arr=[float(r['cash_balance'])/10000 for r in monthly if r['mode']==a and r['scenario']=='base'];end=arr[-1]
  yy=text(p,a+' '+NAMES[a],M,y,CW,14.8,INK,'bold',21)
  text(p,'第36月：'+('余额' if end>=0 else '缺口')+amount(end*10000),M+165,y,CW-165,13.1,INK if end>=0 else BRICK,'bold',18)
  plot_y=yy+3;h=46
  # common y scale for comparable cash lines
  lo=-maxabs;hi=maxabs;zero=plot_y+h/2;line(p,M,zero,W-M,zero,BRICK,.65)
  for i in range(len(arr)-1):
   x1=M+CW*i/35;x2=M+CW*(i+1)/35
   y1=plot_y+h*(hi-arr[i])/(hi-lo);y2=plot_y+h*(hi-arr[i+1])/(hi-lo)
   line(p,x1,y1,x2,y2,OLIVE if min(arr[i],arr[i+1])>=0 else BRICK,1.7)
  y=plot_y+h+13
 text(p,'第1月',M,y,CW,11.5,DIM);text(p,'第36月',W-M-46,y,46,11.5,DIM)
 return y+22
def draw_money_chart(p,e,y):
 if e['layout']=='gross':
  for i,m in enumerate(e['metrics']):
   a='ABCDE'[i]; gross=val(a,'normal_gross_margin'); contr=val(a,'normal_contribution_margin')
   y=text(p,m['label'],M,y,CW,14.6,DIM,'bold',21)
   y=text(p,m['value'],M,y-1,CW,22,INK,'bold',27)
   rect(p,M,y,CW,9,SAND);rect(p,M,y,CW*gross,9,ACC);rect(p,M,y,CW*contr,9,OLIVE)
   y=text(p,m['context'],M,y+14,CW,12.7,DIM,'reg',18)+6
  return y
 if e['id'] in [23,26,27,28,32]:
  for i,m in enumerate(e['metrics']):
   a='ABCDE'[i]
   if e['id']==23:
    y=metricblock(p,m,y,compact=True)-5
    frac=val(a,'total_funding')/max(val(x,'total_funding') for x in NAMES);reserve=val(a,'reserve')/max(val(x,'total_funding') for x in NAMES)
    rect(p,M,y-2,CW,6,SAND);rect(p,M,y-2,CW*frac,6,ACC);rect(p,M,y-2,CW*reserve,6,OLIVE);y+=8
   elif e['id']==26:
    y=metricblock(p,m,y,compact=True)-6
    n=val(a,'year2_operating_profit');mx=max(abs(val(x,'year2_operating_profit')) for x in NAMES)
    line(p,W/2,y-3,W/2,y+6,LINE,.7);ww=(CW/2)*abs(n)/mx
    rect(p,W/2 if n>=0 else W/2-ww,y-2,ww,5,OLIVE if n>=0 else BRICK);y+=8
   elif e['id']==27:
    y=metricblock(p,m,y,compact=True)-4
    mx=max(val(x,'normal_mature_orders_day') for x in NAMES)
    rect(p,M,y-2,CW*val(a,'normal_mature_orders_day')/mx,6,PALE);rect(p,M,y-2,CW*val(a,'reference_be_orders_per_day')/mx,6,ACC);y+=8
   else:
    y=metricblock(p,m,y,compact=True)
  return y
 for m in e['metrics']:y=metricblock(p,m,y,compact=True)
 return y
def photosource(p,key,y):
 info=manifest.get(key,{})
 # match filenames through basename if manifest used relative paths
 if not info:
  for a,it in manifest.items():
   if Path(str(a)).name==key:info=it;break
 desc=PH[key][0]; author=info.get('author') or info.get('photographer') or PH[key][1]; lic=info.get('license') or PH[key][2]
 url=info.get('source_url') or info.get('source_page') or info.get('url') or info.get('file_page')
 if isinstance(url,list):url=url[0] if url else None
 y=text(p,desc,M,y,CW,15,INK,'bold',21)
 y=text(p,'作者：'+str(author)+'｜授权：'+str(lic),M,y+2,CW,12.8,DIM,'reg',18)
 if url and isinstance(url,str) and url.startswith('http'):
  yy=text(p,'查看原始照片',M,y+3,135,13,ACC,'bold',18);hyperlink(p,(M,y,M+134,yy+2),url=url)
  license_url=info.get('license_url')
  if license_url:
   text(p,'查看使用许可',M+168,y+3,CW-168,13,ACC,'bold',18);hyperlink(p,(M+168,y,W-M,yy+2),url=license_url)
  y=yy
 else:
  y=text(p,'生成示意，无真实地点或店铺来源' if key.startswith('generated') else '原始链接见照片清单（随完整工程交付）',M,y,CW,12.5,DIM,'reg',18)
 line(p,M,y+6,W-M,y+6,LINE);return y+16
def render_sources(p,e,y):
 for s in e.get('source_keys',[]):
  info=SC[s];title=info['title'].strip()
  yy=text(p,title,M,y,CW,14,INK,'reg',20)
  yy=text(p,'打开原始资料 →',M,yy+1,CW,12.3,ACC,'bold',18)
  hyperlink(p,(M,y,W-M,yy+3),url=info['urls'][0])
  line(p,M,yy+5,W-M,yy+5,LINE);y=yy+12
 return y
# Continuations are created only when necessary rather than making text tiny.
def draw_content(e):
 p=new(e)
 if e['layout']=='cover':draw_cover(p,e);return
 y=header(p,e,None if e['layout']=='toc' else PH_MAP.get(e['id']))
 if e['layout']=='toc':
  y=draw_toc(p,e,y)
 elif e['layout']=='sources':
  y=render_sources(p,e,y)
 elif e['layout']=='photosources':
  for k in e['photo_keys']:y=photosource(p,k,y)
 elif e['layout']=='sparks':y=draw_sparks(p,e,y)
 elif e['id']==5:y=draw_stacked(p,e,y)
 elif e['id']==17:
  for i,(a,b,co) in enumerate([('多卖出的那一份','新增收入',PALE),('每份多花的钱','食材、包装等',SAND),('多开门才出现的钱','人工、设备等',ROSE)]):
   rect(p,M,y,CW,48,co);text(p,('＋' if i==0 else '－')+' '+a,M+12,y+7,CW-24,16.8,INK,'bold',22);text(p,b,M+12,y+29,CW-24,12.3,DIM,'reg',16);y+=54
  y+=7
 elif e['layout'] in ['money_chart','gross','scenario']:
  y=draw_money_chart(p,e,y)
 elif e['layout']=='mode':
  # One big decision number, then two compact key numbers.
  if e['metrics']:
   y=metricblock(p,e['metrics'][0],y,big=True)
   for m in e['metrics'][1:]:y=metricblock(p,m,y,compact=True)
 elif e['metrics']:
  if len(e['metrics'])>=3:
   for m in e['metrics']:y=metricblock(p,m,y,compact=True)
  else:
   for m in e['metrics']:y=metricblock(p,m,y,compact=True)
 # Regular text, split when necessary, not by shrinking text.
 for b in e['body']:
  if e['layout']=='mode':
   bh=height(b['title']+'：'+b['text'],CW,15.8,'reg',22)+10
  elif e['layout']=='list':
   bh=height(b['title'],CW,14.7,'bold',20)+height(b['text'],CW,12.8,'reg',18)+15
  else:
   ww=CW-28 if e['layout']=='checklist' else CW
   bh=height(b['title'],ww,16.3,'bold',23)+height(b['text'],ww,16.2 if e['layout']=='mode' else 16.6,'reg',24)+18
  if y+bh>LIMIT-8:
   footer(p,e);p=new(e,True);y=header(p,e,None,True)
  if e['layout']=='mode':
   y=text(p,b['title']+'：'+b['text'],M,y,CW,15.8,INK,'reg',22)+5
  elif e['layout']=='list':
   y=text(p,b['title'],M,y,CW,14.7,INK,'bold',20)
   y=text(p,b['text'],M,y+2,CW,12.8,DIM,'reg',18);line(p,M,y+4,W-M,y+4,LINE);y+=12
  else:y=bodyblock(p,b,y,e['layout']=='checklist',e['layout']=='mode')
 if e['layout']=='mode':
  # keep the assumption and payback qualifier visible on the same screen
  y+=3;yy=text(p,e['note'],M,y,CW,12.7,DIM,'reg',17)
  c=[ss for ss in e['sources'] if ss in SC and SC[ss].get('urls')]
  if c:hyperlink(p,(M,y,W-M,yy+4),target='src'+str(codes.index(c[0])//6+1))
  if yy>LIMIT:print('MODE NOTE OVERFLOW',e['id'],p.number+1,yy)
  footer(p,e);return
 if e['note']:
  nh=height(e['note'],CW-24,13.2,'reg',18.75)+43
  if y+nh>LIMIT-18:
   footer(p,e);p=new(e,True);y=header(p,e,None,True)
  y=note_block(p,e['note'],y,True)
 if e.get('sources'):
  if y+20>LIMIT:footer(p,e);p=new(e,True);y=header(p,e,None,True)
  y=source_ref(p,e,y+1)
 if y>LIMIT+1: print('OVERFLOW',e['id'],p.number+1,round(y,1))
 footer(p,e,last=e is seq[-1])
for e in seq:draw_content(e)
# internal targets point to first physical page of content unit
target_index={}
for q in actual:
 if q['id'] not in target_index:target_index[q['id']]=q['page']
for idx,coords,target,url in pending:
 if url:link={'kind':fitz.LINK_URI,'from':fitz.Rect(*coords),'uri':url}
 else:
  if isinstance(target,tuple):dest=idx+1
  else:dest=target_index.get(target)
  if dest is None or dest>=len(doc):continue
  link={'kind':fitz.LINK_GOTO,'from':fitz.Rect(*coords),'page':dest,'to':fitz.Point(0,0)}
 doc[idx].insert_link(link)
bookmarks=[]
for sec,pno in sections.items():bookmarks.append([1,sec,pno+1])
doc.set_toc(bookmarks)
doc.set_metadata({'title':'深圳新和社区｜手机商业指南 V2','author':'Shenzhen Eat 研究项目','subject':'早餐与轻餐饮商业可行性（桌面研究及模拟）'})
doc.save(OUT,garbage=4,deflate=True)
(HERE/'page_index.json').write_text(json.dumps({'pages':actual,'photo_files':list(used_set),'section_pages':sections},ensure_ascii=False,indent=2))
print('Built',OUT,len(doc),'pages; photographs',len(used_set))
