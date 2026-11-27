"""V3 mobile editorial PDF composition. All charts draw from actual values; vector + embedded Noto CJK."""
from pathlib import Path
import fitz,io,math,re,json
from PIL import Image,ImageOps
from fontTools import subset
from fontTools.ttLib import TTFont
W,H=390,844; M=22; CW=W-2*M
BG='#FAF6EF'; PAPER='#FFFFFF'; INK='#183B35'; MUTED='#52645C'; GREEN='#24745C'; LIGHT='#E4EEE4'; EARTH='#92613F'; SAND='#F1E3CE'; RED='#A14635'; ROSE='#F2DFD7'; NAVY='#223D50'; BLUE='#3D7894'; ICE='#E1EDF0'; LINE='#D8D6CA'; CHARCOAL='#21352E'; WHITE='#FFFFFF'
COLORS=[EARTH,BLUE,GREEN,'#C28B50','#738D74','#B9B6A0','#A64836','#90ADB2']
def rgb(h):
 h=h.lstrip('#');return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
def money(v,prec=1,sign=False,exact=False):
 v=float(v);neg=v<0;v=abs(v);p=('−' if neg else '+' if sign else '')
 if exact:return p+f'{v:,.0f}元'
 if v>=10000:
  return p+f'{v/10000:.{prec}f}'.rstrip('0').rstrip('.')+'万元'
 if v>=100:return p+f'{round(v/10)*10:,.0f}元'
 return p+f'{v:,.0f}元'
def cashword(v,prec=1):return ('亏约' if v<0 else '赚约')+money(abs(v),prec)
def order(v):return f'{round(float(v)):,.0f}单'
def yuan(v):return f'{float(v):.2f}'.rstrip('0').rstrip('.')+'元'
class Book:
 def __init__(self,out,charset,font_dir):
  self.out=Path(out);self.doc=fitz.open();self.fonts={};self.pages=[];self.links=[];self.ind={};self.p=None;self.y=0;self.chapter='';self.code=''; self.over=[]
  font_dir=Path(font_dir);font_dir.mkdir(exist_ok=True,parents=True)
  fr=Path('/usr/share/fonts/opentype/noto')
  for name,f in [('reg','NotoSansCJK-Regular.ttc'),('bold','NotoSansCJK-Bold.ttc'),('serif','NotoSerifCJK-Bold.ttc')]:
   target=font_dir/(name+'.otf');font=TTFont(fr/f,fontNumber=2);sub=subset.Subsetter(options=subset.Options(retain_gids=True));sub.populate(text=charset);sub.subset(font);font.save(target);self.fonts[name]=(str(target),fitz.Font(fontfile=str(target)))
 def rect(self,x,y,w,h,c,stroke=None):
  self.p.draw_rect(fitz.Rect(x,y,x+w,y+h),fill=rgb(c),color=rgb(stroke) if stroke else None,width=.6)
 def line(self,x,y,x2,y2,c=LINE,width=.8):
  self.p.draw_line((x,y),(x2,y2),color=rgb(c),width=width)
 def circle(self,x,y,r,c,stroke=None):self.p.draw_circle((x,y),r,fill=rgb(c),color=rgb(stroke) if stroke else None,width=.5)
 def wrap(self,s,w,size,font='reg'):
  res=[]
  for para in str(s).split('\n'):
   cur=''
   toks=re.findall(r'[+-−]?\d[\d,]*(?:\.\d+)?(?:万元|元/月|元|万|单/日|单|个月|月|年|%|㎡|分钟|秒|小时)?|[A-Za-z][A-Za-z0-9.\-]*|.',para)
   for tok in toks:
    if cur and self.fonts[font][1].text_length(cur+tok,fontsize=size)>w:
     if tok in '，。；：、！？）】%％' and len(cur)>1:
      res.append(cur[:-1]);cur=cur[-1]+tok
     else:res.append(cur);cur=tok
    else:cur+=tok
   if cur:res.append(cur)
   elif not para:res.append('')
  return res
 def th(self,s,w,size,font='reg',lh=None):return len(self.wrap(s,w,size,font))*(lh or size*1.43)
 def text(self,s,x,y,w=CW,size=16.0,color=INK,font='reg',lh=None):
  lh=lh or size*1.43
  for q in self.wrap(s,w,size,font):
   self.p.insert_text((x,y+size*.96),q,fontname=font,fontsize=size,color=rgb(color))
   y+=lh
  return y
 def txt(self,s,x,y,size,color=INK,font='reg'):return self.text(s,x,y,W-x-5,size,color,font,size*1.22)
 def right(self,s,x,y,size,color=INK,font='bold'):
  width=self.fonts[font][1].text_length(str(s),fontsize=size)
  self.txt(s,x-width,y,size,color,font)
 def link(self,rect,target=None,url=None):self.links.append((self.p.number,rect,target,url))
 def start(self,key,chapter,title=None,lead=None,dark=False):
  self.p=self.doc.new_page(width=W,height=H);self.code=key;self.chapter=chapter
  for k,(ff,_) in self.fonts.items():self.p.insert_font(fontname=k,fontfile=ff)
  self.rect(0,0,W,H,INK if dark else BG);self.rect(0,0,W,6,EARTH if dark else GREEN)
  self.pages.append({'id':key,'page':self.p.number,'chapter':chapter,'title':title or ''})
  self.ind[key]=self.p.number
  self.y=22
  if title:
   self.y=self.text(chapter,M,self.y,CW,12.5,EARTH,'bold',17)+9
   size=29
   w=self.fonts['serif'][1].text_length(title,fontsize=size)
   if w>CW:
    fit=size*CW/w
    size=max(25,min(29,fit)) if fit>=25 else 26
   lines=self.wrap(title,CW,size,'serif')
   if len(lines)>1 and len(lines[-1])<=3 and len(lines[-2])>6:
    tail=lines[-2][-4:]+lines[-1];lines[-2]=lines[-2][:-4];lines[-1]=tail
   self.y=self.text('\n'.join(lines),M,self.y,CW,size,INK,'serif',size*1.23)+10
   if lead:self.y=self.text(lead,M,self.y,CW,16.8,MUTED,'reg',23.5)+15
  return self
 def title(self,s):self.y=self.text(s,M,self.y,CW,17.6,INK,'bold',24)+5
 def para(self,s,size=16.2,c=INK,gap=8):self.y=self.text(s,M,self.y,CW,size,c,'reg',size*1.45)+gap
 def small(self,s):self.y=self.text(s,M,self.y,CW,12.7,MUTED,'reg',18)+8
 def call(self,label,body,c=LIGHT):
  hh=self.th(body,CW-26,14.1,'reg',19.8)+40
  self.rect(M,self.y,CW,hh,c);self.rect(M,self.y,4,hh,GREEN if c==LIGHT else RED if c==ROSE else EARTH)
  self.text(label,M+14,self.y+9,CW-28,13.3,GREEN if c==LIGHT else RED if c==ROSE else EARTH,'bold',18)
  self.text(body,M+14,self.y+29,CW-28,14.1,INK,'reg',19.8);self.y+=hh+10
 def hero(self,label,value,sub='',c=INK):
  vh=self.th(value,CW-30,33,'bold',39);lh=self.th(label,CW-30,14,'reg',19);sh=self.th(sub,CW-30,13.8,'reg',19)
  hh=lh+vh+sh+28;self.rect(M,self.y,CW,hh,c)
  y=self.text(label,M+15,self.y+10,CW-30,14,'#E5E9E2','reg',19)
  y=self.text(value,M+15,y+1,CW-30,33,WHITE,'bold',39)
  self.text(sub,M+15,y+2,CW-30,13.8,'#E5E9E2','reg',19);self.y+=hh+11
 def metrics(self,items):
  n=len(items);ww=(CW-(n-1)*8)/n
  def fit_value(value):
   sz=25 if len(value)<=8 else 21
   measured=self.fonts['bold'][1].text_length(value,fontsize=sz)
   return min(sz, max(13.8,sz*(ww-20)/max(1,measured)))
  hh=0
  for label,value,detail in items:
   sz=fit_value(value)
   hh=max(hh,self.th(label,ww-20,13.0,'bold',18)+self.th(value,ww-20,sz,'bold',sz*1.15)+self.th(detail,ww-20,12.6,'reg',17)+32)
  for i,(label,value,detail) in enumerate(items):
   x=M+i*(ww+8);self.rect(x,self.y,ww,hh,LIGHT if i%2==0 else ICE)
   t=self.text(label,x+10,self.y+10,ww-20,13.0,MUTED,'bold',18)
   sz=fit_value(value)
   t=self.text(value,x+10,t+4,ww-20,sz,RED if value.startswith('−') else INK,'bold',sz*1.15)
   self.text(detail,x+10,t+4,ww-20,12.6,MUTED,'reg',17)
  self.y+=hh+12
 def row(self,label,value,sub='',color=INK):
  left=153;vl=CW-left-8;ys=self.y
  a=self.text(label,M,ys,left,15,MUTED,'bold',20)
  b=self.text(value,M+left+8,ys,vl,20,color,'bold',25)
  if sub:b=self.text(sub,M+left+8,b+1,vl,12.6,MUTED,'reg',17)
  yy=max(a,b)+8;self.line(M,yy,W-M,yy);self.y=yy+10
 def item(self,label,body,co=GREEN):
  self.circle(M+5,self.y+9,4,co)
  self.y=self.text(label,M+17,self.y,CW-17,16.5,INK,'bold',22)
  self.y=self.text(body,M+17,self.y+2,CW-17,15.3,INK,'reg',22)+12
 def image(self,path,caption,url=None,h=160):
  im=Image.open(path).convert('RGB');im=ImageOps.fit(im,(int(CW*2.5),int(h*2.5)),Image.Resampling.LANCZOS);b=io.BytesIO();im.save(b,format='JPEG',quality=90,optimize=True)
  self.p.insert_image(fitz.Rect(M,self.y,W-M,self.y+h),stream=b.getvalue());self.y+=h+5;yy=self.y
  self.y=self.text(caption,M,self.y,CW,11.8,MUTED,'reg',16)+9
  if url:self.link((M,yy,W-M,self.y),url=url)
 def stack(self,items,total=None,columns=2):
  # items label, value, color; nonnegative partition; visual sum exact
  total=total if total is not None else sum(v for _,v,_ in items);total=max(total,1)
  x=M
  for lab,v,co in items:
   w=CW*max(0,v)/total
   if w>0:self.rect(x,self.y,w,19,co);x+=w
  self.y+=31
  ww=CW/columns
  # each item number and label are own text line, no tiny wide tables
  for i in range(0,len(items),columns):
   hh=0
   for j,(lab,v,co) in enumerate(items[i:i+columns]):
    xx=M+j*ww;self.circle(xx+4,self.y+9,3.7,co)
    yy=self.text(lab,xx+12,self.y,ww-17,12.4,MUTED,'reg',17)
    yy=self.text(money(v,2) if v>=1000 else yuan(v),xx+12,yy,ww-17,14.7,INK,'bold',19)
    hh=max(hh,yy-self.y)
   self.y+=hh+7
 def bars(self,items,maxval=None,unit='money'):
  # caption and bar each row; sign encoded by color plus label
  maxval=maxval or max(abs(v) for _,v,*_ in items) or 1
  for label,v,*more in items:
   color=more[0] if more else (GREEN if v>=0 else RED)
   note=more[1] if len(more)>1 else ''
   y0=self.y;self.txt(label,M,y0,14.7,MUTED,'bold')
   display=money(v,2) if unit=='money' else order(v) if unit=='order' else f'{v:,.0f}'
   self.right(display,W-M,y0,17,INK if v>=0 else RED)
   self.rect(M,y0+27,CW,11,SAND);self.rect(M,y0+27,max(1,CW*abs(v)/maxval),11,color)
   self.y=y0+47
   if note:self.y=self.text(note,M,self.y,CW,12.3,MUTED,'reg',17)+3
 def flow(self,steps):
  for i,(label,val,sub,co) in enumerate(steps):
   hh=max(self.th(label,CW-24,13.6,'bold',18)+self.th(sub,CW-24,12.5,'reg',17)+self.th(val,CW-24,25,'bold',29)+26,70)
   self.rect(M,self.y,CW,hh,co)
   yy=self.text(label,M+12,self.y+9,CW-24,13.6,MUTED,'bold',18)
   yy=self.text(val,M+12,yy+2,CW-24,25,INK,'bold',29)
   self.text(sub,M+12,yy+1,CW-24,12.5,MUTED,'reg',17)
   self.y+=hh
   if i<len(steps)-1:self.txt('↓',W/2-6,self.y+1,15,EARTH,'bold');self.y+=23
  self.y+=10
 def bridge(self,steps,final,final_label='经营结余',compact=False,loss_mode=False):
  # steps [name, delta, explanation]; visual waterfall horizontal running balance
  run=0;bounds=[0];rs=[]
  for label,v,desc in steps:
   a=run;run+=v;rs.append((label,v,desc,a,run));bounds.append(run)
  lo=min(0,min(bounds));hi=max(0,max(bounds));span=max(1,hi-lo)
  for label,v,desc,a,b in rs:
   y=self.y;self.txt(label,M,y,14.2,MUTED,'bold')
   co=(RED if v>0 else GREEN) if loss_mode else (GREEN if v>=0 else RED)
   self.right(money(v,2,sign=True),W-M,y,16.2,co,'bold')
   x0=M+CW*(min(a,b)-lo)/span;w=CW*abs(b-a)/span
   self.rect(M,y+24,CW,8,SAND);self.rect(x0,y+24,max(.8,w),8,co)
   yy=y+38
   if desc and not compact:yy=self.text(desc,M,yy,CW,12.2,MUTED,'reg',17)+4
   self.y=yy+3
  hh=60
  self.rect(M,self.y,CW,hh,(RED if final>0 else INK) if loss_mode else (INK if final>=0 else RED))
  self.txt(final_label,M+12,self.y+7,13.4,WHITE,'reg')
  self.right(money(final,2),W-M-12,self.y+28,24,WHITE,'bold');self.y+=hh+10
 def lineplot(self,series,labels,zero=True,height=160):
  # series list (name,(monthly values),color)
  vs=[v for _,arr,_ in series for v in arr];lo=min(vs+[0]);hi=max(vs+[0]);span=max(1,hi-lo);x=M+10;w=CW-20;y=self.y+13
  self.rect(M,self.y,CW,height+46,PAPER)
  for i in range(3):
   yy=y+height*i/2;self.line(x,yy,x+w,yy,LINE,.6)
  if zero:self.line(x,y+height*hi/span,x+w,y+height*hi/span,RED,1.1)
  for name,a,co in series:
   for k in range(len(a)-1):
    self.line(x+w*k/(len(a)-1),y+height*(hi-a[k])/span,x+w*(k+1)/(len(a)-1),y+height*(hi-a[k+1])/span,co,1.6)
  self.txt('第1月',x,y+height+6,11.8,MUTED);self.right('第36月',x+w,y+height+6,11.8,MUTED,'reg')
  self.y+=height+55
  for name,a,co in series:
   self.circle(M+5,self.y+8,4,co);self.txt(name,M+16,self.y,13.6,MUTED,'bold')
   self.right(money(a[-1],2),W-M,self.y,15.7,INK if a[-1]>=0 else RED)
   self.y+=26
  self.y+=7
 def source(self,items):
  for label,url in items:
   yy=self.y;self.y=self.text(label+' ↗',M,self.y,CW,12.0,EARTH,'bold',16)+3
   if url:self.link((M,yy,W-M,self.y),url=url)
 def footer(self,final=False):
  if self.y>779:self.over.append((self.code,round(self.y,1)))
  self.line(M,789,W-M,789,LINE)
  self.txt('目录',M,799,13.1,EARTH,'bold');self.link((M,794,M+65,824),target='toc')
  self.right('返回目录' if final else '下一页 →',W-M,799,13.1,EARTH,'bold');self.link((W-110,794,W-M,825),target='toc' if final else ('next',self.p.number))
  self.txt('深圳 · 福海新和 / 市场调研',M,825,9.2,MUTED)
  self.right(f'{self.p.number+1:02}',W-M,825,10.3,MUTED)
 def save(self):
  for i,coords,target,url in self.links:
   if url: self.doc[i].insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(*coords),'uri':url})
   else:
    d=i+1 if isinstance(target,tuple) else self.ind.get(target)
    if d is not None and d<len(self.doc):self.doc[i].insert_link({'kind':fitz.LINK_GOTO,'from':fitz.Rect(*coords),'page':d,'to':fitz.Point(0,0)})
  toc=[];seen=set()
  for row in self.pages:
   if row['chapter'] not in seen:
    seen.add(row['chapter']);toc.append([1,row['chapter'],row['page']+1])
  self.doc.set_toc(toc)
  self.doc.set_metadata({'title':'深圳宝安福海新和社区早餐与休闲零食市场调研及商业可行性分析报告','author':'Shenzhen Eat 商业研究','subject':'V3｜桌面研究及情景模拟'})
  self.doc.save(self.out,garbage=4,deflate=True)
  self.out.with_suffix('.index.json').write_text(json.dumps(self.pages,ensure_ascii=False,indent=2))
  print('pages',len(self.doc),'overflows',self.over,'file',self.out)
  return self.over
