"""Reader-first editorial atlas. Original vector graphics + reusable captions, source links and phone geometry."""
from pathlib import Path
import fitz,io,re,math
from PIL import Image,ImageOps
from fontTools import subset
from fontTools.ttLib import TTFont
W,H=390,844; M=24; CW=W-48
PAPER='#FFFCF7'; WHITE='#FFFFFF'; INK='#1C3233'; DARK='#143B37'; MUTED='#546562'; TEAL='#167769'; LEAF='#DDEDE1'; GOLD='#C38E40'; PALE='#F5E8CC'; BROWN='#886348'; RED='#B54D37'; ROSE='#FAE3DD'; NAVY='#244458'; BLUE='#2B7794'; ICE='#E3EFF4'; LINE='#DFE1D8'; GRAY='#E9EAE4'; GRAYINK='#6C766F'; YELLOW='#F4C676'
PAL={'A':'#32806C','B':'#397C9D','C':'#B9774D','D':'#826A92','E':'#788D5E'}
def rgb(x):
 x=x.lstrip('#');return tuple(int(x[i:i+2],16)/255 for i in (0,2,4))
def money(n,p=2):
 n=float(n);sign='−' if n<0 else '';a=abs(n)
 if a>=10000:return sign+f'{a/10000:.{p}f}'.rstrip('0').rstrip('.')+'万'
 return sign+f'{round(a):,}'+'元'
def whole(n):return f'{round(float(n)):,}'
def yuan(n):return f'{float(n):.2f}'.rstrip('0').rstrip('.')+'元'
def perc(n):return f'{float(n)*100:.1f}%'.replace('.0%','%')
def loss(n):return ('亏'+money(n)) if n>=0 else '净赚'+money(-n)
class Atlas:
 def __init__(self,output,charset,fontdir):
  self.out=Path(output);self.d=fitz.open();self.p=None;self.fs={};self.idx={};self.pages=[];self.links=[];self.warn=[];self.y=0;self.pagekey=''
  fd=Path(fontdir);fd.mkdir(parents=True,exist_ok=True)
  for k,name in [('r','NotoSansCJK-Regular.ttc'),('b','NotoSansCJK-Bold.ttc'),('s','NotoSerifCJK-Bold.ttc')]:
   path=fd/(k+'.otf');f=TTFont(Path('/usr/share/fonts/opentype/noto')/name,fontNumber=2)
   sub=subset.Subsetter(options=subset.Options(retain_gids=True));sub.populate(text=charset);sub.subset(f);f.save(path);self.fs[k]=(path,fitz.Font(fontfile=str(path)))
 def rect(self,x,y,w,h,c,stroke=None,rad=0):
  self.p.draw_rect(fitz.Rect(x,y,x+w,y+h),fill=rgb(c),color=rgb(stroke) if stroke else None,width=.6)
 def line(self,x,y,x2,y2,c=LINE,width=1,dash=False):
  self.p.draw_line(fitz.Point(x,y),fitz.Point(x2,y2),color=rgb(c),width=width,dashes='[3 3] 0' if dash else None)
 def circle(self,x,y,r,c,stroke=None):
  self.p.draw_circle(fitz.Point(x,y),r,fill=rgb(c),color=rgb(stroke) if stroke else None,width=.7)
 def textwidth(self,t,size=15,font='r'):return self.fs[font][1].text_length(str(t),fontsize=size)
 def wrap(self,s,w,size,font='r'):
  ls=[]
  for q in str(s).split('\n'):
   t=''
   for a in re.findall(r'[−+]?\d[\d,.]*(?:万元|万|元|份|单|个月|月|㎡|人次|小时|分钟|%|年)?|[A-Za-z][A-Za-z0-9.-]*|.',q):
    if t and self.textwidth(t+a,size,font)>w:
     if a in '，。；：、！？”）】%' and len(t)>2:ls.append(t[:-1]); t=t[-1]+a
     else:ls.append(t);t=a
    else:t+=a
   ls.append(t)
  return ls
 def h(self,s,w,size=15,font='r',lh=None):return len(self.wrap(s,w,size,font))*(lh or size*1.45)
 def txt(self,s,x,y,w=CW,size=15,color=INK,font='r',lh=None):
  lh=lh or size*1.42
  for q in self.wrap(s,w,size,font):
   if self.textwidth(q,size,font)>w+.5:self.warn.append((self.pagekey,'textwidth',q,w,size))
   self.p.insert_text((x,y+size*.96),q,fontsize=size,fontname=font,color=rgb(color));y+=lh
  return y
 def right(self,s,x,y,size=14,color=INK,font='b',maxw=None):
  v=str(s);ww=self.textwidth(v,size,font)
  if maxw and ww>maxw:size=max(10.5,size*maxw/ww);ww=self.textwidth(v,size,font)
  return self.txt(v,x-ww,y,ww+1,size,color,font,size*1.18)
 def fit(self,s,x,y,w,size=25,minsize=15,color=INK,font='b'):
  v=str(s);sz=min(size,max(minsize,size*w/max(1,self.textwidth(v,size,font))));return self.txt(v,x,y,w,sz,color,font,sz*1.2)
 def img(self,path,x,y,w,h,focus=(.5,.5)):
  im=Image.open(path).convert('RGB');im=ImageOps.fit(im,(int(w*2.4),int(h*2.4)),Image.Resampling.LANCZOS,centering=focus)
  arr=io.BytesIO();im.save(arr,format='JPEG',quality=88,optimize=True);self.p.insert_image(fitz.Rect(x,y,x+w,y+h),stream=arr.getvalue())
 def link(self,rect,target=None,url=None):self.links.append((self.p.number,tuple(rect),target,url))
 def start(self,key,chapter,title=None,kicker=None,accent=TEAL,background=PAPER,light=False):
  self.p=self.d.new_page(width=W,height=H);self.pagekey=key;self.idx[key]=self.p.number;self.pages.append({'key':key,'chapter':chapter,'title':title or '', 'page':self.p.number+1})
  self.accent=accent;self.bg=background;self.light=light
  for k,(pp,_) in self.fs.items():self.p.insert_font(fontname=k,fontfile=str(pp))
  self.rect(0,0,W,H,background);self.rect(0,0,7,H,accent);self.rect(24,23,32,3,accent)
  self.txt(chapter,64,17,CW-40,11.5,WHITE if light else accent,'b',15)
  self.y=47
  if title:
   size=29 if len(title)<=14 else 27
   if self.textwidth(title,size,'s')>CW and self.textwidth(title,25,'s')<=CW:size=25
   self.y=self.txt(title,M,self.y,CW,size,WHITE if light else INK,'s',size*1.25)+10
   if kicker:self.y=self.txt(kicker,M,self.y,CW,15.2,'#DCE9DE' if light else MUTED,'r',21)+12
  return self
 def finish(self,final=False):
  if self.y>780:self.warn.append((self.pagekey,'cursor',round(self.y,1)))
  co='#CFDDD6' if self.light else LINE;tc='#DCE9DE' if self.light else MUTED;self.line(M,791,W-M,791,co,.7)
  self.txt('目录',M,803,50,12.2,tc,'b',16);self.link((M,796,M+56,827),target='toc')
  self.right(f'{self.p.number+1:02}',W-M,803,12.5,tc)
  if not final:self.txt('下一页 →',W-124,803,76,11.6,tc,'b',16);self.link((W-133,798,W-48,828),target=('next',))
  self.txt('深圳 · 福海新和 / 2026.11',M+57,826,210,8.8,tc,'r',11)
 def para(self,s,size=15.3,color=INK,gap=9):
  self.y=self.txt(s,M,self.y,CW,size,color,'r',size*1.46)+gap
 def caption(self,s,url=None):
  yy=self.y;self.y=self.txt(s,M,self.y,CW,11.3,MUTED,'r',15.6)+6
  if url:self.link((M,yy,W-M,self.y),url=url)
 def headline(self,label):
  self.y=self.txt(label,M,self.y,CW,17.0,INK,'b',22)+5
 def tag(self,label,body,color=TEAL,bg=LEAF):
  hh=20+self.h(body,CW-24,14.0,'r',19.2)+22
  self.rect(M,self.y,CW,hh,bg);self.rect(M,self.y,4,hh,color)
  y=self.txt(label,M+12,self.y+9,CW-24,13.2,color,'b',18)
  self.txt(body,M+12,y+2,CW-24,14.0,INK,'r',19.2);self.y+=hh+9
 def note(self,s):self.y=self.txt(s,M,self.y,CW,12.3,MUTED,'r',17.5)+7
 def bullets(self,items):
  for a,b in items:
   self.circle(M+4,self.y+8,3.2,self.accent);yy=self.txt(a,M+14,self.y,CW-14,15.2,INK,'b',20);self.y=self.txt(b,M+14,yy+2,CW-14,14.1,MUTED,'r',19.5)+8
 def image(self,path,caption,h=180,url=None,focus=(.5,.5)):
  self.img(path,M,self.y,CW,h,focus);self.y+=h+5;self.caption(caption,url)
 def photo_split(self,photos,h=118):
  n=len(photos);w=(CW-(n-1)*5)/n;ys=self.y;maxy=0
  for i,(path,caption,link) in enumerate(photos):
   x=M+i*(w+5);self.img(path,x,ys,w,h);yy=self.txt(caption,x,ys+h+5,w,10.5,MUTED,'r',14)
   if link:self.link((x,ys+h,x+w,yy),url=link)
   maxy=max(maxy,yy)
  self.y=maxy+8
 def pill(self,label,x,y,c=TEAL,bg=LEAF):
  ww=self.textwidth(label,11.2,'b')+16;self.rect(x,y,ww,22,bg);self.txt(label,x+8,y+3,ww-16,11.2,c,'b',15);return ww
 def metricline(self,items,bg=None):
  n=len(items);ww=(CW-8*(n-1))/n
  yh=max(self.h(a,ww-12,12,'b',16)+self.h(c,ww-12,12,'r',16)+47 for a,b,c in items)
  for i,(a,b,c) in enumerate(items):
   x=M+i*(ww+8)
   if bg:self.rect(x,self.y,ww,yh,bg)
   else:self.line(x,self.y,x+ww,self.y,self.accent,2)
   self.txt(a,x+6,self.y+9,ww-12,12,MUTED,'b',16)
   y=self.fit(b,x+6,self.y+30,ww-12,27,15,RED if str(b).startswith('−') else INK,'b')
   self.txt(c,x+6,y+4,ww-12,12,MUTED,'r',16)
  self.y+=yh+8
 def row(self,a,b,sub='',color=INK):
  w=CW*.52
  y1=self.txt(a,M,self.y,w-6,14.7,MUTED,'b',20);y2=self.right(b,W-M,self.y,16.6,color,'b',CW-w)
  yy=max(y1,y2)
  if sub:yy=self.txt(sub,M,yy+2,CW,12.7,MUTED,'r',17)
  self.line(M,yy+5,W-M,yy+5,LINE,.7);self.y=yy+13
 def stack(self,items,total=None,h=21):
  tot=total if total else sum(q[1] for q in items);tot=max(tot,.1);xx=M
  for lab,val,co in items:
   ww=CW*max(val,0)/tot
   if ww>0:self.rect(xx,self.y,ww,h,co);xx+=ww
  self.y+=h+8
 def mini_legend(self,items,n=2,size=12.6):
  w=CW/n; maxy=self.y
  for i,(lab,val,col) in enumerate(items):
   j=i%n;x=M+j*w
   if j==0:y=maxy
   self.circle(x+4,y+7,3.3,col); yy=self.txt(lab,x+13,y,w-19,size,MUTED,'r',size*1.37)
   yy=self.fit(val,x+13,yy+2,w-18,18,13,INK,'b')
   maxy=max(maxy,yy+7)
  self.y=maxy+4
 def source(self,lab,url):
  yy=self.y;self.y=self.txt(lab+' ↗',M,self.y,CW,11.5,TEAL,'b',16)+5
  if url:self.link((M,yy,W-M,self.y),url=url)
 def band(self,label,value,body='',c=DARK):
  hh=32+self.h(body,CW-30,13,'r',18)+44
  self.rect(M,self.y,CW,hh,c)
  self.txt(label,M+14,self.y+10,CW-28,13,'#E2EBDD','b',18); yy=self.fit(value,M+14,self.y+32,CW-28,32,20,WHITE,'b')
  self.txt(body,M+14,yy+3,CW-28,13,'#E2EBDD','r',18);self.y+=hh+9
 def table(self,headers,rows,widths=None,fs=13.5,colors=None):
  widths=widths or [CW/len(headers)]*len(headers)
  x=M
  for h,w in zip(headers,widths):
   self.rect(x,self.y,w,26,DARK);self.txt(h,x+6,self.y+5,w-12,11.4,WHITE,'b',15);x+=w
  self.y+=26
  for i,row in enumerate(rows):
   hh=max(self.h(t,w-12,fs,'r',fs*1.38) for t,w in zip(row,widths))+13;x=M
   for j,(t,w) in enumerate(zip(row,widths)):
    co=colors[i][j] if colors else INK;self.rect(x,self.y,w,hh,WHITE if i%2 else '#F4F5EE')
    sz=fs;vl=str(t)
    if self.textwidth(vl,sz,'r')>w-12 and re.fullmatch(r'[-−+]?\d[\d,.]*(?:万|元|单|㎡|月)?',vl):sz=max(10.7,sz*(w-12)/self.textwidth(vl,sz,'r'))
    self.txt(t,x+6,self.y+7,w-12,sz,co,'b' if j==0 else 'r',sz*1.38);x+=w
   self.y+=hh
  self.y+=8
 def steps(self,steps):
  for i,(label,val,detail,c) in enumerate(steps):
   # visual vertical chain, one cross-page concept
   hh=max(65,self.h(detail,CW-126,13,'r',18)+34)
   self.circle(M+14,self.y+23,13,c)
   self.txt(str(i+1),M+10,self.y+15,12,12.5,WHITE,'b',14)
   self.line(M+14,self.y+38,M+14,self.y+hh+7,LINE,2) if i<len(steps)-1 else None
   self.txt(label,M+35,self.y+4,CW-35,13.0,MUTED,'b',18)
   self.fit(val,M+35,self.y+24,CW-45,25,17,INK,'b')
   self.y+=hh
   if detail:self.y=self.txt(detail,M+35,self.y-2,CW-35,12.3,MUTED,'r',17.8)+8
 def barrows(self,rows,signed=False):
  vmax=max(abs(v) for _,v,_,_ in rows) or 1
  for a,v,co,sub in rows:
   y=self.y;self.txt(a,M,y,CW*.6,14.2,INK,'b',19);self.right(money(v),W-M,y,16.4,RED if v<0 else INK,'b',CW*.4)
   self.rect(M,y+24,CW,8,GRAY);self.rect(M,y+24,CW*abs(v)/vmax,8,co)
   self.y=y+36
   if sub:self.y=self.txt(sub,M,self.y,CW,11.7,MUTED,'r',16)+4
 def waterfall(self,rows,final_label,value,loss_mode=False):
  # amount text and running-balance bars (not values alone)
  cur=0;vals=[0]
  for _,v in rows:cur+=v;vals.append(cur)
  lo=min(vals);hi=max(vals);span=max(hi-lo,1);cur=0
  for label,v in rows:
   y=self.y;end=cur+v;c=(RED if v>0 else TEAL) if loss_mode else (TEAL if v>=0 else RED)
   self.txt(label,M,y,CW*.59,13.6,MUTED,'b',18);self.right(('+' if v>0 else '')+money(v),W-M,y,14.6,c,'b',CW*.4)
   self.rect(M,y+22,CW,8,GRAY);self.rect(M+CW*(min(cur,end)-lo)/span,y+22,max(1,CW*abs(v)/span),8,c);cur=end;self.y+=36
  bg=ROSE if ((loss_mode and value>0) or (not loss_mode and value<0)) else LEAF
  self.rect(M,self.y,CW,56,bg);self.txt(final_label,M+10,self.y+7,CW-20,13.2,MUTED,'b',18)
  self.right(loss(value) if loss_mode else money(value),W-M-10,self.y+26,24,RED if bg==ROSE else DARK,'b',CW-20)
  self.y+=65
 def chart(self,series,h=130):
  a=[v for _,vals,_ in series for v in vals];lo=min(a+[0]);hi=max(a+[0]);span=max(hi-lo,1);x=M+5;yy=self.y;ww=CW-10
  self.rect(M,yy,CW,h+31,WHITE)
  for frac in (0,.5,1):self.line(x,yy+7+h*frac,x+ww,yy+7+h*frac,LINE,.5)
  self.line(x,yy+7+h*(hi-0)/span,x+ww,yy+7+h*(hi-0)/span,RED,1,dash=True)
  for name,vals,co in series:
   for i in range(len(vals)-1):
    x0=x+ww*i/(len(vals)-1);x1=x+ww*(i+1)/(len(vals)-1);y0=yy+7+h*(hi-vals[i])/span;y1=yy+7+h*(hi-vals[i+1])/span
    self.line(x0,y0,x1,y1,co,1.7)
  self.txt('第1月',x,yy+11+h,88,10.6,MUTED);self.right('第36月',x+ww,yy+11+h,10.6,MUTED,'r')
  self.y=yy+h+39
  for name,vals,co in series:
   self.circle(M+5,self.y+8,4,co);self.txt(name,M+14,self.y,CW*.63,12.4,MUTED,'b',17);self.right(money(vals[-1]),W-M,self.y,13.9,INK,'b',CW*.36);self.y+=23
 def nav(self,label,detail,target):
  y=self.y;self.rect(M,y,CW,61,WHITE,LINE);self.txt(label,M+12,y+8,CW-60,15.8,INK,'b',21);self.txt(detail,M+12,y+31,CW-60,12.3,MUTED,'r',17);self.right('→',W-M-12,y+18,19,self.accent);self.link((M,y,W-M,y+61),target=target);self.y+=68
 def save(self):
  for src,rect,tar,url in self.links:
   if url:self.d[src].insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(rect),'uri':url})
   else:
    dst=src+1 if isinstance(tar,tuple) else self.idx.get(tar)
    if dst is not None and dst<len(self.d):self.d[src].insert_link({'kind':fitz.LINK_GOTO,'from':fitz.Rect(rect),'page':dst,'to':fitz.Point(0,0)})
  seen=set();toc=[]
  for p in self.pages:
   if p['chapter'] not in seen:seen.add(p['chapter']);toc.append([1,p['chapter'],p['page']])
  self.d.set_toc(toc);self.d.set_metadata({'title':'深圳宝安福海新和社区早餐与休闲零食市场调研及商业可行性分析报告','author':'Shenzhen Eat','subject':'V4 · 市场研究与经营条件模拟'})
  self.d.save(self.out,garbage=4,deflate=True)
  import json;self.out.with_suffix('.index.json').write_text(json.dumps(self.pages,ensure_ascii=False,indent=2))
  print('PAGES',len(self.d),'WARNINGS',self.warn)
  return self.warn
