"""Three phone report concepts with identical fictional illustrative model.
A: street editorial, B: finance explainer, C: field decision notebook.
Does not consume V3 final model inputs; all amounts explicitly labelled example.
"""
from pathlib import Path
import fitz, json, re, time, statistics, io
from PIL import Image, ImageOps, ImageDraw
from fontTools.ttLib import TTFont
from fontTools import subset
P=Path(__file__).resolve().parent; V3=P.parent; ROOT=V3.parent
W,H=390,844; M=22; CW=W-2*M
COLORS={
 'A': {'bg':'#FBF5E9','ink':'#263C33','sub':'#56645B','accent':'#8F563B','panel':'#EBE8D8','soft':'#F5E5CF','dark':'#304A3D','risk':'#A94432','green':'#416E55','line':'#D8D0BE','blue':'#5C8790','white':'#FFFDF7'},
 'B': {'bg':'#F7FAFA','ink':'#1D3448','sub':'#4D6273','accent':'#246779','panel':'#DFEEF0','soft':'#E9F0F5','dark':'#20394E','risk':'#A84A37','green':'#276C64','line':'#CDDBDF','blue':'#638CA4','white':'#FFFFFF'},
 'C': {'bg':'#F3F2E6','ink':'#243C35','sub':'#4F6458','accent':'#526E4F','panel':'#E1E8D4','soft':'#EAE0C8','dark':'#334D42','risk':'#A44535','green':'#516E46','line':'#D3D9C5','blue':'#6A8A96','white':'#FFFDF4'},
}
NAMES={'A':'A_街坊纪实','B':'B_财经图解','C':'C_店主决策笔记'}
PHOTO=ROOT/'v2/assets/qiaohe_street.jpg'; PM=json.load(open(ROOT/'v2/assets/PHOTO_MANIFEST.json'))[0]
CAPTION='宝安福海桥和路，2023年8月实拍。邻近商业参照，非新和三区。'
FUND=[('装修','4.5万',45000),('设备','2.8万',28000),('转让费','4.2万',42000),('押金','1万',10000),('备货','0.6万',6000),('外卖开通','0.2万',2000),('杂费','0.5万',5000),('备用金','5万',50000)]
assert sum(t[2] for t in FUND)==188000
MODEL={'onsite':{'orders':100,'ticket':9,'costs':[('食材',3.2),('包装',0.5),('支付等',0.2)],'contrib':5.1},
'delivery':{'orders':60,'ticket':14,'costs':[('商家优惠',2),('平台及配送',3),('食材',4),('包装',1.2),('其他比例费',0.3)],'contrib':3.5},
'fixed':[('租金',5000),('水电',2000),('其他固定支出',2800)],'days':27}
start=188000; topup=10000; cash=42000; recovery=22000; closing=9000
loss=start+topup-(cash+recovery-closing); assert loss==143000
assert abs(27*(100*5.1+60*3.5)-9800-9640)<1e-8
ROOTFONT=Path('/usr/share/fonts/opentype/noto')
F={}
charset=Path(__file__).read_text()+CAPTION+str(FUND)+str(MODEL)+str(PM)+'0123456789%━—＋－×·→≤＝①②③④元万单月￥¥'
for name,file in [('reg','NotoSansCJK-Regular.ttc'),('bold','NotoSansCJK-Bold.ttc'),('serif','NotoSerifCJK-Bold.ttc')]:
 out=P/(name+'.otf')
 ft=TTFont(ROOTFONT/file,fontNumber=2); s=subset.Subsetter(options=subset.Options(retain_gids=True));s.populate(text=charset);s.subset(ft);ft.save(out)
 F[name]=(str(out),fitz.Font(fontfile=str(out)))
def rgb(h):h=h.lstrip('#');return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
def rect(p,x,y,w,h,c,stroke=None):p.draw_rect(fitz.Rect(x,y,x+w,y+h),fill=rgb(c),color=rgb(stroke) if stroke else None,width=.6)
def line(p,x1,y1,x2,y2,c,w=.8):p.draw_line((x1,y1),(x2,y2),color=rgb(c),width=w)
def dot(p,x,y,r,c):p.draw_circle((x,y),r,color=None,fill=rgb(c))
def wrap(s,w,sz,f):
 a=[]
 for pp in str(s).split('\n'):
  l=''
  for ch in re.findall(r'\d[\d,]*(?:\.\d+)?(?:万元|元/单|元/月|元|万|单/日|单|个月|月|年|%|㎡|秒|小时)?|[A-Za-z][A-Za-z0-9.\-]*|.',pp):
   if l and F[f][1].text_length(l+ch,fontsize=sz)>w:
    a.append(l);l=ch
   else:l+=ch
  if l:a.append(l)
 return a
def text(p,s,x,y,w,sz,c,f='reg',lh=None,align='left'):
 lh=lh or sz*1.43
 for l in wrap(s,w,sz,f):
  ww=F[f][1].text_length(l,fontsize=sz);xx=x+(w-ww if align=='right' else (w-ww)/2 if align=='center' else 0)
  assert xx>=-1 and xx+ww<=W+1,(s,ww,xx,sz)
  p.insert_text((xx,y+sz*.96),l,fontname=f,fontsize=sz,color=rgb(c));y+=lh
 return y
def tt(p,s,x,y,w,sz,c,f='reg',align='left'):return text(p,s,x,y,w,sz,c,f,sz*1.28,align)
def photo(p,x,y,w,h,d,full=False):
 im=Image.open(PHOTO).convert('RGB')
 im=ImageOps.fit(im,(int(w*2.2),int(h*2.2)),method=Image.Resampling.LANCZOS)
 b=io.BytesIO();im.save(b,'JPEG',quality=91)
 p.insert_image(fitz.Rect(x,y,x+w,y+h),stream=b.getvalue())
 yy=text(p,CAPTION,x,y+h+6,w,11.4,d['sub'],lh=16)
 yy=text(p,'JMUAIANWNC 3366688 · CC BY-SA 4.0（裁切，原图）',x,yy,w,10.7,d['accent'],'bold',15)
 p.insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(x,yy-15,x+w,yy),'uri':PM['source_url']})
 return yy
def chapter(p,tag,title,lead,d,style):
 rect(p,0,0,W,H,d['bg']);rect(p,0,0,W,5,d['accent'])
 y=tt(p,tag,M,20,CW,12.3,d['accent'],'bold')+10
 y=tt(p,title,M,y,CW,27,d['ink'],'serif' if style=='A' else 'bold')+10
 y=text(p,lead,M,y,CW,16,d['sub'],'reg',23)+12
 return y
def footer(p,n,d,style):
 line(p,M,789,W-M,789,d['line']);t='示例演算，非实测或最终财务结果'
 tt(p,t,M,800,CW,11.1,d['sub'],'bold')
 tt(p,'V3 视觉样稿  '+style+'  |  '+str(n)+'/3',M,824,CW/2,9.8,d['sub'])
 tt(p,'总览 ←' if n>1 else '样稿仅供评审',M+CW/2,824,CW/2,10.2,d['accent'],'bold','right')
def labelval(p,label,value,x,y,w,d,color=None):
 tt(p,label,x,y,w,13.5,d['sub'],'bold');tt(p,value,x,y+22,w,27,color or d['ink'],'bold')
def note(p,s,y,d):
 hh=len(wrap(s,CW-24,13.5,'reg'))*19+24
 rect(p,M,y,CW,hh,d['soft']);text(p,s,M+12,y+11,CW-24,13.5,d['ink'],'reg',19)
 return y+hh+9
def arrow(p,x,y,d):
 line(p,x,y,x,y+13,d['accent'],1.5)
 p.draw_polyline([(x-4,y+8),(x,y+13),(x+4,y+8)],color=rgb(d['accent']),width=1.5)
def boxline(p,y,label,value,desc,d,fill=None):
 rect(p,M,y,CW,61,fill or d['panel'])
 tt(p,label,M+12,y+7,188,14,d['sub'],'bold')
 tt(p,value,M+205,y+5,CW-217,22,d['ink'],'bold','right')
 tt(p,desc,M+12,y+35,CW-24,12.8,d['sub'])
 return y+70
def sections_board(p,y,d):
 # Exposure to capacity, independently derived and no double counts
 y=tt(p,'订单先过两道关',M,y,CW,17,d['ink'],'bold')+7
 x=M; w=(CW-12)/2
 for i,(label,value,caption) in enumerate([('假设每日需求','180单','不是测得的客流'),('实际接单上限','160单','两位合伙人的假设产能')]):
  xx=x+i*(w+12);rect(p,xx,y,w,85,d['panel'])
  tt(p,label,xx+10,y+9,w-20,13,d['sub'],'bold')
  tt(p,value,xx+10,y+29,w-20,22,d['ink'],'bold')
  text(p,caption,xx+10,y+58,w-20,11.3,d['sub'],lh=15)
 y+=96
 return y
def budget_chart(p,y,d):
 # Eight inputs, all parts of 188000. Two line rows, explicit amounts.
 y=tt(p,'18.8万元，是这样凑出来的',M,y,CW,16.8,d['ink'],'bold')+7
 palette=[d['accent'],d['blue'],d['risk'],d['green'],d['sub'],d['dark'],'#BCB6A0',d['panel']]
 x=M
 for (lbl,amount,v),co in zip(FUND,palette):
  ww=CW*v/188000;rect(p,x,y,ww,15,co,d['line']);x+=ww
 y+=22
 for i,(lbl,v,n) in enumerate(FUND):
  xx=M+(i%2)*(CW/2); yy=y+(i//2)*25
  dot(p,xx+4,yy+9,3.8,palette[i])
  tt(p,lbl,xx+15,yy,69,12.5,d['sub'],'bold');tt(p,v,xx+83,yy,CW/2-91,13.5,d['ink'],'bold','right')
 return y+108
def budget_ledger(p,y,d):
 # Compact same-data ledger used by A & C. No less information than B.
 y=tt(p,'开业投入与备用金的组成',M,y,CW,14.2,d['ink'],'bold')+2
 for i,(lbl,v,n) in enumerate(FUND):
  xx=M+(i%2)*(CW/2);yy=y+(i//2)*19
  tt(p,lbl,xx,yy,75,12.6,d['sub'])
  tt(p,v,xx+83,yy,CW/2-92,13,d['ink'],'bold','right')
 return y+80
def overview(p,d,s):
 y=chapter(p,'01　先看结论｜示例','两个人开店，\n先把三笔账说清','需要多少钱、一天卖多少单、一个月能留下多少钱？',d,s)
 if s=='A':
  y=photo(p,M,y,CW,91,d)+8
  rect(p,M,y,CW,83,d['dark']);tt(p,'开业和备用金合计',M+12,y+8,CW-24,13,d['white'],'bold')
  tt(p,'18.8万元',M+12,y+28,CW-24,31,d['white'],'bold')
  tt(p,'其中备用金5万元，不是已经花掉的钱。',M+12,y+62,CW-24,11.9,d['white']);y+=94
  y=budget_ledger(p,y,d)
  y=sections_board(p,y,d)
  y=boxline(p,y,'正常月经营结余','9,640元','27个营业日；合伙人工资为0。',d)
  y=note(p,'先验证订单和设备工位，再决定是否增聘。',y,d)
 elif s=='B':
  y=budget_chart(p,y,d)
  y=sections_board(p,y,d)
  y=boxline(p,y,'正常月经营结余','9,640元','27个营业日；合伙人工资为0。',d,fill=d['panel'])
  # Same imagery with concise nearby provenance.
  y=photo(p,M,y,CW,94,d)+10
  y=note(p,'先验证订单和设备工位，再决定是否增聘。',y,d)
 else:
  y=photo(p,M,y,CW,102,d)+6
  for idx,(title,v,desc) in enumerate([('① 要准备多少钱','18.8万元','其中5万元备用金仍留在账上。'),('② 一天最多接多少单','160单','需求180单，仅按假设产能接单。'),('③ 正常月剩多少','9,640元','27天营业；合伙人工资为0。')]):
   y=boxline(p,y,title,v,desc,d)
   if idx<2:arrow(p,W/2,y-5,d);y+=8
  y=budget_ledger(p,y,d)
  y=note(p,'先验证订单和设备工位，再决定是否增聘。',y,d)
 assert y<=780,('overview',s,y)
def channel_bar(p,y,title,ticket,costs,contrib,d,s):
 # labeled cost components and proportional composition; no duplicate fee assumptions
 y=tt(p,title+' / 每单',M,y,CW,17,d['ink'],'bold')+5
 tt(p,'顾客商品价'+f'{ticket:g}'+'元',M,y,CW/2,13.4,d['sub'],'bold')
 tt(p,'留下'+f'{contrib:g}'+'元',M+CW/2,y,CW/2,17,d['green'],'bold','right');y+=24
 cols=[d['accent'],d['risk'],d['blue'],d['sub'],d['dark'],d['green']]
 x=M
 for j,(lbl,v) in enumerate(costs+[('每单留下',contrib)]):
  col=d['green'] if lbl=='每单留下' else cols[j]
  ww=CW*v/ticket;rect(p,x,y,ww,20,col,d['bg']);x+=ww
 y+=26
 for j,(lbl,v) in enumerate(costs):
  xx=M+(j%2)*CW/2;yy=y+(j//2)*23
  dot(p,xx+4,yy+8,3.8,cols[j]);tt(p,lbl,xx+13,yy,95,12.5,d['sub'])
  tt(p,f'{v:g}元',xx+102,yy,CW/2-108,13,d['ink'],'bold','right')
 return y+((len(costs)+1)//2)*23+5
def waterfall(p,y,steps,d,scale_min=0):
 # Running total, horizontal axis from zero. Labels exact with connectors.
 step_h=52; maxv=max(max(prev,nxt) for label,prev,nxt,delta in steps)
 base=M+128; ww=CW-128; scale=ww/maxv
 for i,(label,prev,nxt,delta) in enumerate(steps):
  yy=y+i*step_h
  tt(p,label,M,yy,120,13.7,d['sub'],'bold')
  tt(p,delta,M,yy+20,120,16,d['ink'],'bold')
  xx=base+min(prev,nxt)*scale;bw=abs(nxt-prev)*scale
  fill=d['dark'] if i in (0,len(steps)-1) else (d['risk'] if nxt>prev else d['green'])
  rect(p,base,yy+13,ww,13,d['panel'])
  rect(p,xx,yy+13,max(bw,2),13,fill)
  if i<len(steps)-1:
   line(p,base+nxt*scale,yy+26,base+nxt*scale,yy+step_h+13,d['sub'],.6)
  tt(p,f'{nxt:.1f}万',base,yy+29,ww,11.6,d['sub'],'reg','right')
 return y+len(steps)*step_h
def economics(p,d,s):
 y=chapter(p,'02　钱从哪来｜示例','外卖流水高，\n未必留下更多钱','同一店、同一产能；线下和外卖分开算每一单。',d,s)
 if s in ('A','B'):
  y=channel_bar(p,y,'线下',9,MODEL['onsite']['costs'],5.1,d,s)+6
  y=channel_bar(p,y,'外卖',14,MODEL['delivery']['costs'],3.5,d,s)+4
 else:
  for title,m in [('线下',MODEL['onsite']),('外卖',MODEL['delivery'])]:
   y=tt(p,title+' / 每单',M,y,CW,16.8,d['ink'],'bold')+7
   rect(p,M,y,CW,33,d['panel'])
   tt(p,'商品价 '+f"{m['ticket']:g}元",M+10,y+7,155,14,d['ink'],'bold')
   tt(p,'留下 '+f"{m['contrib']:g}元",M+170,y+5,CW-181,16,d['green'],'bold','right');y+=36
   # Each component appears on same line, receipt style (two items per row)
   for j,(label,v) in enumerate(m['costs']):
    xx=M+(j%2)*CW/2; yy=y+(j//2)*22
    tt(p,'－'+label,xx,yy,111,12.5,d['sub'])
    tt(p,f'{v:g}元',xx+115,yy,CW/2-121,12.7,d['ink'],'bold','right')
   y+=((len(m['costs'])+1)//2)*22+11
 y=tt(p,'把单笔结余，变成一个月的账',M,y,CW,17,d['ink'],'bold')+6
 # simple monthly logic diagram
 rect(p,M,y,CW,72,d['panel']);tt(p,'线下100单×5.1元  ＋  外卖60单×3.5元',M+10,y+8,CW-20,14,d['ink'],'bold')
 tt(p,'每日留下720元  ×  27个营业日',M+10,y+39,CW-20,14,d['ink'])
 y+=72
 arrow(p,W/2,y+2,d);y+=20
 tt(p,'月订单贡献',M,y,CW/2,13.5,d['sub'],'bold')
 tt(p,'19,440元',M+CW/2,y,CW/2,17,d['ink'],'bold','right');y+=30
 tt(p,'固定开支（租金5,000、水电2,000、其他2,800）',M,y,CW,12.7,d['sub']);y+=25
 rect(p,M,y,CW,53,d['dark']);tt(p,'经营结余',M+10,y+16,131,17,d['white'],'bold')
 tt(p,'9,640元/月',M+130,y+9,CW-140,25,d['white'],'bold','right');y+=63
 y=text(p,'两位合伙人工资均为0。这还不是能直接分掉的钱；先留够周转金，才能考虑分配。',M,y,CW,13.4,d['sub'],'reg',19)
 assert y<=780,('economics',s,y)
def exit_page(p,d,s):
 y=chapter(p,'03　失败代价｜示例','退出时，究竟亏多少钱？','假如开了6个月仍不合适：把实际投进去的钱、收得回的钱分开。',d,s)
 if s=='A':
  rect(p,M,y,CW,102,d['dark']);tt(p,'两人合计损失（示例）',M+13,y+10,CW-26,14.7,d['white'],'bold')
  tt(p,'14.3万元',M+13,y+34,CW-26,34,d['white'],'bold');tt(p,'均分约7.15万元／人（假设各半出资）',M+13,y+76,CW-26,12.4,d['white']);y+=114
  steps=[('开业资金','18.8万元'),('再投入','＋1万元'),('退回的账上现金','－4.2万元'),('设备、押金及库存','－2.2万元'),('退出清场及结账','＋0.9万元')]
  for label,v in steps:
   tt(p,label,M,y,CW/2+18,15,d['sub']);tt(p,v,M+CW/2+18,y,CW/2-18,16,d['ink'],'bold','right')
   line(p,M,y+27,W-M,y+27,d['line']);y+=32
 elif s=='B':
  y=tt(p,'资金损失桥  /  每一步看余下损失',M,y,CW,17,d['ink'],'bold')+8
  st=[('开业资金',0,18.8,'18.8万'),('追加投入',18.8,19.8,'＋1万'),('账上现金',19.8,15.6,'－4.2万'),('资产可回收',15.6,13.4,'－2.2万'),('退出还须支付',13.4,14.3,'＋0.9万'),('合计损失',0,14.3,'14.3万')]
  y=waterfall(p,y,st,d)+12
  rect(p,M,y,CW,66,d['dark']);tt(p,'每位合伙人（各半示例）',M+12,y+7,CW-24,13.1,d['white'],'bold')
  tt(p,'7.15万元',M+12,y+29,CW-24,25,d['white'],'bold');y+=78
 else:
  y=tt(p,'先看两边，再减一减',M,y,CW,17,d['ink'],'bold')+8
  rect(p,M,y,CW,78,d['panel']);tt(p,'两人实际投入',M+11,y+9,198,14,d['sub'],'bold');tt(p,'19.8万',M+204,y+5,CW-215,23,d['ink'],'bold','right')
  tt(p,'开业18.8万 ＋ 后续1万',M+11,y+43,CW-22,14.5,d['sub'])
  y+=89;arrow(p,W/2,y-2,d);y+=16
  rect(p,M,y,CW,117,d['soft']);tt(p,'退出能拿回多少现金？',M+11,y+9,CW-22,16,d['ink'],'bold')
  tt(p,'账上4.2万 ＋ 残值2.2万',M+11,y+36,CW-22,14,d['ink'])
  tt(p,'－ 退租清场等0.9万 ＝ 5.5万',M+11,y+63,CW-22,14.5,d['ink'],'bold')
  y+=127;arrow(p,W/2,y-3,d);y+=16
  rect(p,M,y,CW,77,d['dark']);tt(p,'19.8万－5.5万＝实际损失',M+9,y+8,CW-18,13.5,d['white'])
  tt(p,'14.3万元',M+9,y+28,CW-18,29,d['white'],'bold');y+=87
  y=tt(p,'若各半出资，约每人亏7.15万元。',M,y,CW,14.5,d['sub'])+12
 y=note(p,'账上4.2万已包含追加投入和经营亏损的影响。不能把1.8万累计亏损又加一次；本例未分红。',y,d)
 # 9k paid from 42k or recoverable cash; do not claim liabilities all same-day
 y=text(p,'本例账上资金足以支付退出费，当天无需另筹钱。真实情况要看合同、残值及未结费用。',M,y,CW,13.2,d['sub'],lh=18)
 assert y<=780,('exit',s,y)
metrics={}
for s,d in COLORS.items():
 doc=fitz.open();t0=time.perf_counter()
 for n,func in enumerate([overview,economics,exit_page],1):
  p=doc.new_page(width=W,height=H)
  for k,(f,_) in F.items():p.insert_font(fontname=k,fontfile=f)
  func(p,d,s);footer(p,n,d,s)
  if n>1:p.insert_link({'kind':fitz.LINK_GOTO,'from':fitz.Rect(W/2,817,W-M,840),'page':0})
 doc.set_toc([[1,'决策总览',1],[1,'单笔账与月结余',2],[1,'退出损失',3]])
 path=P/(NAMES[s]+'.pdf');doc.save(path,garbage=4,deflate=True);doc.close();q=fitz.open(path)
 mm={'file':path.name,'pages':len(q),'page_size':[W,H],'seconds':round(time.perf_counter()-t0,2),'bytes':path.stat().st_size,'checks':[]}
 for j,p in enumerate(q):
  spans=[x for b in p.get_text('dict')['blocks'] if b['type']==0 for l in b['lines'] for x in l['spans'] if x['text'].strip()]
  overflow=[x['text'] for x in spans if x['bbox'][0]<-1 or x['bbox'][1]<-1 or x['bbox'][2]>W+1 or x['bbox'][3]>H+1]
  sz=[x['size'] for x in spans for _ in x['text']];mm['checks'].append({'page':j+1,'median_font_pt':round(statistics.median(sz),2),'overflow':overflow,'replacement':p.get_text().count('�')})
  for width in [360,390,430]:
   pix=p.get_pixmap(matrix=fitz.Matrix(width/W,width/W),alpha=False);pix.save(P/(s+f'_p{j+1}_{width}.png'))
 metrics[s]=mm
# side-by-side comparisons 390px exact width with labels
sheet=Image.new('RGB',(3*390+36,3*860+26),'#E1DED3');draw=ImageDraw.Draw(sheet)
for col,s in enumerate(COLORS):
 for j in range(1,4):
  im=Image.open(P/(s+f'_p{j}_390.png'));sheet.paste(im,(col*402+6,(j-1)*860+23));draw.text((col*402+8,(j-1)*860+4),s+' / '+str(j),fill='black')
sheet.save(P/'V3_same_content_comparison_390.jpg',quality=91)
(P/'benchmark_metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2))
print(json.dumps(metrics,ensure_ascii=False,indent=2))
