#!/usr/bin/env python3
"""Spot-audit actual PDF extracted text and internal navigation against generated scenarios."""
import fitz,json,glob,math,re
from pathlib import Path
R=Path(__file__).resolve().parents[2]
pdf=fitz.open(next((R/'deliverables').glob('*V3_手机版.pdf')))
idx={x['id']:x['page'] for x in json.load(next((R/'deliverables').glob('*V3_手机版.index.json')).open())}
data=json.load((R/'v3/models/report_data_v3.json').open())
S={x['mode']:x for x in data['selected']}; C={x['case_id']:x for x in data['summary']}; M={(x['mode'],x['month']):x for x in data['monthly_selected']}; E={(x['mode'],x['exit_month']):x for x in data['exit_selected']}
checked=0
def check(cond,label):
 global checked
 checked+=1
 assert cond,label
def read(key):return re.sub(r'\s+','',pdf[idx[key]].get_text())
def has(key,val):
 check(val.replace(' ','') in read(key),(key,val))
def money(v):
 neg='−' if v<0 else '';v=abs(v)
 if v>=10000: return neg+format(v/10000,'.2f').rstrip('0').rstrip('.')+'万元'
 if v>=100: return neg+format(round(v/10)*10,',.0f')+'元'
 return neg+format(v,',.0f')+'元'
def count(v):return format(round(v),',.0f')+'单'
def yuan(v):return format(v,'.2f').rstrip('0').rstrip('.')+'元'
def profit(v):return ('净亏' if v>=0 else '净赚')+money(abs(v))
has('cover','深圳宝安福海新和社区早餐与休闲零食市场调研及商业可行性分析报告')
check(len(idx)==len(pdf)==96,'page count')
for i,p in enumerate(pdf):
 ls=[x for x in p.get_links() if x['kind']==fitz.LINK_GOTO]
 check(any(x['from'].y0>790 and x['from'].x0<100 and x['page']==idx['toc'] for x in ls),('return link',i))
 check(any(x['from'].y0>790 and x['from'].x0>250 and x['page']==(idx['toc'] if i==len(pdf)-1 else i+1) for x in ls),('next link',i))
 check(p.get_text().strip().endswith(f'{i+1:02}'),('page number',i))
for k in 'ABCDE':
 check(any(x['kind']==fitz.LINK_GOTO and x['page']==idx[k+'1'] for x in pdf[idx['modetoc']].get_links()),('mode navigation',k))
 s=S[k];m=M[k,12];e=E[k,6]
 # Overall financial snapshots and five per-mode derivations
 for page,val in [('overview',s['initial_funding']),('overview2',s['y1_avg_monthly_profit']),('overview3',e['total_net_investor_loss'])]:
  has(page,money(val))
 for f in ('initial_funding','fitout','equipment','transfer','preopening','delivery_setup','lease_deposit','platform_deposit','opening_inventory','reserve','initial_opening_outlay'):
  has(k+'2',money(s[f]))
 for t in ('low','base','high'):
  has(k+'3',money(C[f'{k}_{t}_mixed_base']['initial_funding']))
 for f in ('desired_total_daily','realized_daily','actual_onsite_daily','actual_delivery_daily','lost_daily_orders'):
  has(k+'4',count(m[f]))
 for ch in ('onsite','meituan','taobao'):
  for f in ('list_ticket','food_cost','packaging','contribution'):
   has(k+'5',yuan(m[f'{ch}_{f}_per_order']))
  if ch!='onsite':
   for f in ('platform_fee','delivery_fee','discount','refund'):
    has(k+'5',yuan(m[f'{ch}_{f}_per_order']))
 for f in ('recognized_revenue','food_consumption','total_fixed_cost','operating_profit'):
  has(k+'6',money(m[f]))
 has(k+'6',count(m['total_orders']));has(k+'6',count(m['break_even_daily_orders']))
 has(k+'7',money(m['business_cashflow']))
 for f in ('y1_avg_monthly_profit','y2_avg_monthly_profit','y3_avg_monthly_profit','cumulative_business_cashflow','initial_opening_outlay'):
  has(k+'8',money(s[f]))
 for f in ('cumulative_business_cashflow','total_capital_calls','partner_distribution_each','cash_balance_m36'):
  has(k+'9',money(s[f]))
 for f in ('exit_cost_total','asset_recovery_total','remaining_cash','exit_day_bridge_before_recovery','net_exit_payment_needed','initial_funding','additional_capital_before_exit','cumulative_distributions','returned_cash_at_exit','total_net_investor_loss'):
  has(k+'10',money(e[f]))
 for t in (3,6,12,24):
  x=E[k,t]
  for val in (profit(x['total_net_investor_loss']),profit(x['loss_per_partner']),money(x['net_exit_payment_needed'])):
   has(k+'11',val)
  weak=C[f'{k}_base_mixed_bad']['exit_m'+str(t)+'_total_net_investor_loss']
  has('weak_exit0' if k in 'ABC' else 'weak_exit1',profit(weak))
 for f in ('lease_deposit_recovery','platform_deposit_recovery','equipment_recovery','stock_recovery','receivable_recovery','lease_exit_charge','staff_exit_cost','clearance','unsettled_misc'):
  has(k+'11',money(e[f]))
 for sc in ('bad','base','good'):
  has('compare1' if k in 'ABC' else 'compare1b',money(C[f'{k}_base_mixed_{sc}']['y1_avg_monthly_profit']))
 for route in ('onsite','mixed','delivery_heavy'):
  has('compare3' if k in 'ABC' else 'compare3b',money(C[f'{k}_base_{route}_base']['y1_avg_monthly_profit']))
print('PASS',checked,'actual PDF text, amounts and navigation checks')
