#!/usr/bin/env python3
"""Independently check final PDF structure, amounts and key labels from freeze JSON. No import of report code."""
from pathlib import Path
import fitz,hashlib,json,glob,re,sys
ROOT=Path(__file__).resolve().parents[2]; V=ROOT/'v4'
pdf=next((ROOT/'deliverables').glob('*V4_手机图解版.pdf'))
idx=json.loads(pdf.with_suffix('.index.json').read_text()); D=fitz.open(pdf)
data=json.loads((V/'models/report_data_v4.json').read_text()); R=data['reader']
keys={x['key']:x['page']-1 for x in idx}; checks=0;errors=[]
def ok(condition,why):
 global checks
 checks+=1
 if not condition:errors.append(why)
def norm(x):return re.sub(r'\s','',str(x)).replace('－','−')
text={k:norm(D[n].get_text()) for k,n in keys.items()}
def contains(key,*vals):
 for v in vals:ok(norm(v) in text[key],key+' missing '+str(v))
def contains_amount(key,n):
 ok(any(norm(f) in text[key] for f in (money(n),f'{round(float(n)):,}元',f'{round(float(n))}元')),key+' missing amount '+str(n))
def money(n):
 n=float(n);sg='−' if n<0 else '';a=abs(n)
 if a>=10000:return sg+f'{a/10000:.2f}'.rstrip('0').rstrip('.')+'万'
 return sg+f'{round(a):,}'+'元'
def loss(n):return ('亏' if n>=0 else '净赚')+money(abs(n))
def whole(n):return f'{round(float(n)):,}'
def yuan(n):return f'{float(n):.2f}'.rstrip('0').rstrip('.')+'元'
def recovery(n):return '第'+str(n)+'月' if n is not None else '36月内未覆盖'
ok(len(D)==len(idx),'index count')
ok(len(keys)==len(idx),'unique keys')
bounds=[];repl=[];links=0;img_pages=0
for i,p in enumerate(D):
 ok(p.rect.width==390 and p.rect.height==844,'phone '+str(i+1))
 if p.get_images():img_pages+=1
 if '�' in p.get_text():repl.append(i+1)
 for blk in p.get_text('dict')['blocks']:
  if blk.get('type')!=0:continue
  for ln in blk['lines']:
   for sp in ln['spans']:
    r=fitz.Rect(sp['bbox'])
    if r.x0<-.3 or r.y0<-.3 or r.x1>390.3 or r.y1>844.3: bounds.append((i+1,sp['text'],list(r)))
 for li in p.get_links():
  links+=1
  if li['kind']==fitz.LINK_GOTO:ok(0<=li.get('page',-1)<len(D),'internal '+str(i+1))
  ok(li['from'].intersects(p.rect),'link rectangle '+str(i+1))
# Check actual destination wiring of both navigation pages and standard footer links.
for k,dest in [('toc',['area','rent','work','modes','cross','verify']),('modes',[m+'1' for m in 'ABCDE']),('overview',[m+'1' for m in 'ABCDE'])]:
 pl=D[keys[k]].get_links();pages={l['page'] for l in pl if l['kind']==fitz.LINK_GOTO}
 for a in dest:ok(keys[a] in pages,'navigation '+k+' -> '+a)
for i,p in enumerate(D):
 dest={l['page'] for l in p.get_links() if l['kind']==fitz.LINK_GOTO}
 ok(keys['toc'] in dest,'return contents '+str(i+1))
 if i<len(D)-1:ok(i+1 in dest,'next page '+str(i+1))
ok(not bounds,'span bounds '+str(bounds[:3]))
ok(not repl,'replacement code points '+str(repl))
contains('cover','深圳宝安福海新和社区','早餐与休闲零食','市场调研及','商业可行性分析报告')
contains('school','福新小学','鹏晖中英文学校','133万元','未知')
contains('competition','137条','32个主体')
contains('price','2026年11月26日','83个商品')
contains('rent','32㎡', '3,040', '4.2万', '7月')
contains('work','0元','7,200元/月')
for k,r in R.items():
 o=r['opening'];c=r['capacity'];M=r['month12'];Y=r['years'];e=r['exit'][1]
 contains('overview',money(o['initial_funding']),money(Y['annual'][0]['avg_monthly_profit']),loss(e['total_net_investor_loss']))
 contains(k+'1',whole(o['area'])+'㎡',f"{c['partner_daily_hours_each']:g}小时/人",whole(c['paid_staff'])+'人')
 contains(k+'2',money(o['initial_funding']),money(o['start_spent_or_tied']),money(o['account_reserve']))
 for x in o['categories']:contains(k+'2',money(x['amount']))
 contains(k+'3',whole(M['daily']['orders'])+'单/日',str(M['days'])+'天',whole(M['break_even_order_daily'])+'单/日',money(Y['annual'][0]['avg_monthly_profit']))
 for a in ('net_sales','order_contribution','operating_profit','cash_flow'):contains_amount(k+'3',M[a])
 for ch in M['channel']:
  contains(k+'3',yuan(ch['unit']['list_ticket']),yuan(ch['unit']['contribution']))
 contains(k+'4',money(Y['business_cashflow_36']),money(Y['each_distribution']),money(Y['cash_36']),money(Y['additional_capital']))
 for a in Y['annual']:contains(k+'4',money(a['avg_monthly_profit']),money(a['distributed_to_partners']))
 contains(k+'5',money(e['remaining_cash']),money(e['asset_recovery_total']),money(e['exit_cost_total']),money(e['net_exit_payment_needed']),loss(e['total_net_investor_loss']))
 for ex in r['exit']: contains(k+'5',loss(ex['total_net_investor_loss']),loss(ex['loss_per_partner']))
 for comp in r['comparisons']['investment']:contains('cross',money(comp['initial_funding']),whole(comp['area_m2'])+'㎡')
 for comp in r['comparisons']['channel']:contains('compare_channels',money(comp['y1_avg_monthly_profit']))
 for comp in r['comparisons']['demand']:contains('profit_compare',money(comp['y1_avg_monthly_profit']))
print('PDF',pdf.name,'pages',len(D),'sha256',hashlib.sha256(pdf.read_bytes()).hexdigest())
print('pages with raster images',img_pages,'links',links,'checks',checks,'errors',len(errors))
for e in errors:print(e)
if bounds:print('invalid text spans',bounds[:12])
