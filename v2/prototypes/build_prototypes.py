"""A/B/C same-content PDF page prototype experiment: A ReportLab, B and C PyMuPDF.
Photos are intentionally placeholders: photo-sourcing research is separate.
This is a tool/typography demonstration, not the final report.
"""
from pathlib import Path
import fitz, json, time, re, math
from fontTools.ttLib import TTFont
from fontTools import subset
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.colors import HexColor
from PIL import Image

root=Path(__file__).resolve().parent
W,H=390,844
M=24
CONTENT={
 'head':['这里是一门什么生意？','开一间传统早餐店','到底要准备多少钱？'],
 'tag':['认识新和','模式 A · 传统中式早餐','模拟数据 · 基准情景'],
 'intro':['街坊的早餐，不只来自学生。','包点、粥、鸡蛋和豆饮。','这是创业资金，不是保证赚钱。'],
 'pic':['图片位｜当地街区实景待核实','图片位｜早餐店和产品实景待核实','数据页｜无需装饰性照片'],
 'p1a':'附近学校以外，社区居民、老师、家长和园区员工，也可能成为固定顾客。',
 'p1b':'两校家庭有不同消费需求，但校内用餐、家里做早餐、单位食堂，都可能替代街边早餐。',
 'p1c':'先问真实顾客每天买几次、多少钱，再看铺。不要把整个街道的人口都算成顾客。',
 'p2a':'一家20至35平方米的外带店，主食做成简单套餐，让顾客买完就走。',
 'p2b':'早餐套餐可以从6至11元做起测试。真正价格取决于本地竞品、食材与家长接受度。',
 'p2c':'难点不是把菜单做丰富，而是高峰期能否快速交付，以及能否保持新鲜、卫生和复购。',
 'p3a':'约13万元',
 'p3b':'启动资金（含装修、押金、设备、备货及周转储备）',
 'p3c':'4,500元',
 'p3d':'每月租金假设',
 'p3e':'约180单',
 'p3f':'正常月每天保本',
 'p3g':'第一年平均每月亏约2,400元',
 'p3h':'这里已经计算老板本人劳动的参考工资。不是实际门店数据，不表示每个月都亏同样的钱。',
 'src':['来源：深圳市政府公开学校目录、福海街道资料（V1研究 M01–M10）','经营原型与价格为待验证的模型假设，不是当地实测','模型：A基准情景（V1模型 summary.csv）'],
 'foot':'新和社区餐饮创业指南 · 手机样稿',
 'pages':['01 / 03','02 / 03','03 / 03'],
 'nav':['下一页：看看传统早餐店','下一页：算算这门生意','回到第一页']
}
# Glyph coverage from all actual copy, punctuation, and numbers.
def collect(x):
 if isinstance(x,dict):return '\n'.join(map(collect,x.values()))
 if isinstance(x,list):return '\n'.join(map(collect,x))
 return str(x)
CHARSET=collect(CONTENT)+'商圈模式资金开店真实照片来源简明结论一个要点每页三种参考样稿阅读漂亮白色黑色茶绿不止是学生20至35平方米6至11元套餐¥￥0123456789,.%/·→—-｜'
FONT_ROOT=Path('/usr/share/fonts/opentype/noto')
fonts={}
def subset_font(name,ttc):
 p=root/(name+'.otf')
 t=TTFont(FONT_ROOT/ttc,fontNumber=2)
 s=subset.Subsetter(options=subset.Options(retain_gids=True));s.populate(text=CHARSET);s.subset(t);t.save(p)
 fonts[name]=(p,fitz.Font(fontfile=str(p)))
for name,src in [('regular','NotoSansCJK-Regular.ttc'),('bold','NotoSansCJK-Bold.ttc'),('serif','NotoSerifCJK-Bold.ttc')]:
 subset_font(name,src)

def rgb(c):
 c=c.lstrip('#'); return tuple(int(c[i:i+2],16)/255 for i in (0,2,4))
class Fitz:
 """Native PDF: selectable, embedded Simplified Chinese fonts."""
 def __init__(self,path):self.doc=fitz.open();self.path=path;self.pending=[]
 def new(self):self.p=self.doc.new_page(width=W,height=H);self.p.set_rotation(0);[self.p.insert_font(fontname=n,fontfile=str(v[0])) for n,v in fonts.items()]
 def rect(self,x,y,w,h,color):self.p.draw_rect(fitz.Rect(x,y,x+w,y+h),fill=rgb(color),color=None,overlay=True)
 def line(self,x1,y1,x2,y2,c,w=1):self.p.draw_line((x1,y1),(x2,y2),color=rgb(c),width=w)
 def txt(self,x,y,s,size,c,font='regular'):
  assert fonts[font][1].text_length(s,fontsize=size) <= W-x+1.0,(s,size,x)
  self.p.insert_text((x,y+size),s,fontname=font,fontsize=size,color=rgb(c))
 def length(self,s,size,font):return fonts[font][1].text_length(s,fontsize=size)
 def link(self,rect,target):self.pending.append((self.p.number,rect,target))
 def save(self):
  for p,rect,target in self.pending:self.doc[p].insert_link({'kind':fitz.LINK_GOTO,'from':fitz.Rect(*rect),'page':target})
  self.doc.set_toc([[1,'认识新和',1],[1,'传统早餐店',2],[1,'投资与保本',3]]);self.doc.save(self.path,garbage=4,deflate=True)

class RL:
 """ReportLab CID fonts, stable and lighter but no native modern bold/serif distinction."""
 def __init__(self,path):
  pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
  self.c=Canvas(str(path),pagesize=(W,H),pageCompression=1);self.i=-1
 def new(self):
  if self.i>=0:self.c.showPage()
  self.i+=1;self.c.bookmarkPage('page'+str(self.i))
  self.c.addOutlineEntry(['认识新和','传统早餐店','投资与保本'][self.i],'page'+str(self.i),0)
 def rect(self,x,y,w,h,color):
  self.c.setFillColor(HexColor(color));self.c.rect(x,H-y-h,w,h,stroke=0,fill=1)
 def line(self,x1,y1,x2,y2,c,w=1):
  self.c.setStrokeColor(HexColor(c));self.c.setLineWidth(w);self.c.line(x1,H-y1,x2,H-y2)
 def txt(self,x,y,s,size,c,font='regular'):
  assert self.length(s,size,font)<=W-x+1.0,(s,x,size)
  self.c.setFillColor(HexColor(c));self.c.setFont('STSong-Light',size);self.c.drawString(x,H-y-size,s)
 def length(self,s,size,font):return pdfmetrics.stringWidth(s,'STSong-Light',size)
 def link(self,rect,target):
  x1,y1,x2,y2=rect;self.c.linkRect('章节跳转','page'+str(target),Rect=(x1,H-y2,x2,H-y1),relative=0,thickness=0)
 def save(self):self.c.showPage();self.c.save()

def wrap(b,text,width,size,font='regular'):
 out=[]
 for para in text.split('\n'):
  line=''
  for ch in para:
   if line and b.length(line+ch,size,font)>width:
    out.append(line);line=ch
   else:line+=ch
  out.append(line)
 return out

def para(b,x,y,text,width,size,c,font='regular',leading=None):
 leading=leading or size*1.52
 for l in wrap(b,text,width,size,font):
  b.txt(x,y,l,size,c,font);y+=leading
 return y

def picbox(b,y,h,txt,design):
 x=M;w=W-2*M
 b.rect(x,y,w,h,design['photo'])
 # abstract placeholder geometry, deliberately not photo or claimed local scene
 for i in range(5):
  hh=25+i*7;b.rect(x+20+i*40,y+h-hh-44,23,hh,design['shape'])
 b.line(x+16,y+h-44,x+w-16,y+h-44,design['line'])
 b.txt(x+12,y+h-31,txt,13,design['muted'],'regular')

def label(b,x,y,t,d):b.txt(x,y,t,13,d['accent'],'bold')
def navigation(b,i,d):
 b.line(M,775,W-M,775,d['line'])
 b.txt(M,785,CONTENT['nav'][i],14,d['accent'],'bold')
 b.link((M,778,W-M,814),(i+1)%3)
 b.txt(M,823,CONTENT['foot'],9.5,d['muted'])
 b.txt(330,823,CONTENT['pages'][i],9,d['muted'])

def render(design,key,pdf):
 b=pdf;d=design
 for i in range(3):
  b.new();b.rect(0,0,W,H,d['bg'])
  b.rect(0,0,W,8,d['accent'])
  if key=='C' and i<2:
   # Photo-forward magazine composition: lead with the photograph and then the question.
   label(b,M,24,CONTENT['tag'][i],d)
   picbox(b,50,205,CONTENT['pic'][i],d)
   h=para(b,M,273,CONTENT['head'][i],W-2*M,d['h1'],d['ink'],d['titlefont'],d['h1']*1.25)
   h=para(b,M,h+4,CONTENT['intro'][i],W-2*M,18,d['muted'],'regular',25)
  else:
   label(b,M,27,CONTENT['tag'][i],d)
   h=para(b,M,53,CONTENT['head'][i],W-2*M,d['h1'],d['ink'],d['titlefont'],d['h1']*1.25)
   h=para(b,M,h+4,CONTENT['intro'][i],W-2*M,18,d['muted'],'regular',25)
  if i==0:
   if key!='C':picbox(b,153,190,CONTENT['pic'][i],d)
   y=358 if key=='C' else 354
   b.txt(M,y,'不止是学生',22,d['accent'],'bold')
   y=para(b,M,y+40,CONTENT['p1a'],W-2*M,17,d['ink'])
   y=para(b,M,y+18,CONTENT['p1b'],W-2*M,17,d['ink'])
   b.rect(M,y+15,W-2*M,99,d['panel'])
   para(b,M+14,y+27,CONTENT['p1c'],W-2*M-28,15,d['ink'])
  elif i==1:
   if key!='C':picbox(b,153,190,CONTENT['pic'][i],d)
   y=358 if key=='C' else 354
   b.txt(M,y,'20至35平方米',25,d['accent'],'bold')
   y=para(b,M,y+40,CONTENT['p2a'],W-2*M,17,d['ink'])
   b.line(M,y+12,W-M,y+12,d['line'])
   b.txt(M,y+29,'6至11元 / 套餐',23,d['accent'],'bold')
   y=para(b,M,y+67,CONTENT['p2b'],W-2*M,17,d['ink'])
   b.rect(M,y+12,W-2*M,99,d['panel'])
   para(b,M+14,y+24,CONTENT['p2c'],W-2*M-28,15,d['ink'])
  else:
   y=142
   b.rect(M,y,W-2*M,153,d['dark'])
   b.txt(M+18,y+17,CONTENT['p3a'],d['metric'],d['onDark'],'bold')
   para(b,M+18,y+91,CONTENT['p3b'],W-2*M-36,15,d['onDark'])
   y=317
   if key=='A':
    for metric,title in [(CONTENT['p3c'],CONTENT['p3d']),(CONTENT['p3e'],CONTENT['p3f'])]:
     b.rect(M,y,W-2*M,75,d['panel']);b.txt(M+13,y+8,metric,25,d['accent'],'bold');b.txt(M+13,y+44,title,15,d['muted']);y+=86
   else:
    # Vertical cards; one thought per row, no wide table.
    for metric,title in [(CONTENT['p3c'],CONTENT['p3d']),(CONTENT['p3e'],CONTENT['p3f'])]:
     b.txt(M,y,metric,27,d['accent'],'bold');b.txt(M,y+38,title,15,d['muted']);b.line(M,y+66,W-M,y+66,d['line']);y+=86
   y+=20
   b.txt(M,y,CONTENT['p3g'],20,d['risk'],'bold')
   y=para(b,M,y+37,CONTENT['p3h'],W-2*M,16,d['ink'],leading=25)
  para(b,M,715,CONTENT['src'][i],W-2*M,11,d['muted'],leading=17)
  navigation(b,i,d)
 b.save()

designs={
'A':{'bg':'#FBF6ED','ink':'#1C3329','muted':'#5b6c62','accent':'#287457','photo':'#dde6d9','shape':'#adc5b1','line':'#cadbd1','panel':'#e7f1e7','dark':'#dcece1','onDark':'#205a44','risk':'#A34B35','titlefont':'regular','h1':29,'metric':43},
'B':{'bg':'#FFFFFF','ink':'#253547','muted':'#526879','accent':'#1F5C75','photo':'#dbe8ed','shape':'#b0ced9','line':'#bfd1da','panel':'#e4edf0','dark':'#253547','onDark':'#fcfdf4','risk':'#A34B35','titlefont':'bold','h1':29,'metric':44},
'C':{'bg':'#F6F2E8','ink':'#163F3A','muted':'#5b554b','accent':'#7C5C38','photo':'#e7dfcf','shape':'#cfb89b','line':'#dad1bf','panel':'#f3e8d7','dark':'#443829','onDark':'#fff7e4','risk':'#b1492c','titlefont':'serif','h1':28,'metric':44},
}
metrics={}
for key,d in designs.items():
 name={'A':'A_reportlab_cards','B':'B_pymupdf_editorial','C':'C_pymupdf_photo_led'}[key]
 path=root/(name+'.pdf')
 start=time.perf_counter()
 render(d,key,RL(path) if key=='A' else Fitz(path))
 t=time.perf_counter()-start
 f=fitz.open(path); m={'path':str(path.name),'bytes':path.stat().st_size,'generate_seconds':round(t,3),'pages':len(f),'links':sum(len(p.get_links()) for p in f),'toc':len(f.get_toc()),'size_pt':[f[0].rect.width,f[0].rect.height]}
 m['checks']=[]
 for i,pg in enumerate(f):
  txt=pg.get_text();bad=[]
  for block in pg.get_text('blocks'):
   if min(block[0],block[1])<-0.5 or block[2]>W+.5 or block[3]>H+.5:bad.append(block[:4])
  exact=[CONTENT['head'][i],CONTENT['intro'][i]]
  if i==2:exact+=['约13万元','4,500元','约180单','第一年平均每月亏约2,400元']
  # Ignore spaces introduced by PDF extraction.
  loose=re.sub(r'\s+','',txt)
  m['checks'].append({'page':i+1,'text_chars':len(txt),'missing_expected':[word for word in exact if re.sub(r'\s+','',word) not in loose],'out_of_page_blocks':bad,'replacement_char_count':txt.count('�')})
  for w in [360,390,430]:
   pix=pg.get_pixmap(matrix=fitz.Matrix(w/W,w/W),alpha=False)
   pix.save(root/f'{name}_p{i+1}_{w}px.png')
 f.close();metrics[name]=m
(root/'benchmark_metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2))
print(json.dumps(metrics,ensure_ascii=False,indent=2))
