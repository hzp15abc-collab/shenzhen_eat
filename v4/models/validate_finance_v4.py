#!/usr/bin/env python3
"""Independent arithmetic and invariance checks, no importing producer code."""
import csv, json, math, hashlib
from pathlib import Path
P=Path(__file__).resolve().parent; V3=P.parents[1]/'v3'/'models'
a=json.loads((V3/'report_data_v3.json').read_text());b=json.loads((P/'report_data_v4.json').read_text())
n=0
def E(x,y,s,atol=1e-4):
 global n
 n+=1
 if not math.isclose(float(x),float(y),rel_tol=1e-10,abs_tol=atol):raise ValueError(s,x,y)
def ok(x,s):
 global n
 n+=1
 if not x:raise ValueError(s)
for key in ['summary','selected','monthly_selected','exit_selected','all_exits','monthly_compact','unit_economics','inputs']:
 ok(a[key]==b[key],key+' canonical data invariance')
ok(hashlib.sha256((V3/'report_data_v3.json').read_bytes()).hexdigest()==b['v4_meta']['source_report_sha256'],'v3 baseline hash')
S={r['case_id']:r for r in b['summary']};M={(r['case_id'],r['month']):r for r in b['monthly_compact']};X={(r['case_id'],r['exit_month']):r for r in b['all_exits']}
ok(len(S)==135 and len(M)==4860 and len(X)==540,'baseline cardinality')
for csvfile,index,keys,idx in [('summary_v3.csv',S,['initial_funding','initial_opening_outlay','reserve','y1_avg_monthly_profit','y2_avg_monthly_profit','y3_avg_monthly_profit','total_capital_calls','cumulative_distributions','cash_balance_m36'],('case_id',)),('monthly_v3.csv',M,['recognized_revenue','operating_profit','business_cashflow','cumulative_business_cashflow','retained_cash','additional_capital','distributed_to_partners','paid_staff','total_fixed_cost'],('case_id','month')),('exit_v3.csv',X,['asset_recovery_total','exit_cost_total','total_net_investor_loss','net_exit_payment_needed','returned_cash_at_exit'],('case_id','exit_month'))]:
 with (V3/csvfile).open(encoding='utf-8-sig') as f:
  for r in csv.DictReader(f):
   key=r[idx[0]] if len(idx)==1 else (r[idx[0]],int(r[idx[1]]));x=index[key]
   for k in keys:E(r[k],x[k],csvfile+' '+str(key)+' '+k)
for mode,z in b['reader'].items():
 o=z['opening'];c=z['capacity'];m=z['month12'];y=z['years'];case=z['case_id']
 E(o['start_spent_or_tied']+o['account_reserve'],o['initial_funding'],mode+' start')
 E(sum(i['amount'] for i in o['categories']),o['initial_funding'],mode+' source sums')
 for g in o['categories']:
  if g.get('items'):E(sum(i['subtotal'] for i in g['items']),g['amount'],mode+' '+g['key'])
 E(sum(ch['daily_orders'] for ch in m['channel']),m['daily']['orders'],mode+' order count')
 E(sum(ch['orders_month']*ch['unit']['revenue'] for ch in m['channel']),m['net_sales'],mode+' revenue')
 E(sum(ch['orders_month']*ch['unit']['contribution'] for ch in m['channel']),m['order_contribution'],mode+' contribution')
 for ch in m['channel']:
  u=ch['unit'];E(u['list_ticket']-u['discount']-u['refund'],u['revenue'],mode+' unit revenue')
  E(u['revenue']-sum(u[k] for k in ('food_cost','packaging','platform_fee','delivery_fee','payment_fee','host_fee','tax_budget')),u['contribution'],mode+' unit contribution')
 E(m['net_sales']-sum(i['amount'] for i in m['variable_items'])-sum(i['amount'] for i in m['fixed_items'])-m['staff_change_cost'],m['operating_profit'],mode+' op result')
 E(sum(i['signed_amount'] for i in m['cash_trace']),m['cash_flow'],mode+' cash')
 E(sum(i['signed_amount'] for i in m['cash_balance_trace']),m['retained_cash'],mode+' cash balance')
 E(m['daily']['operating_profit']*m['days'],m['operating_profit'],mode+' daily')
 E(c['partner_salary'],0,mode+' owner salary')
 E(c['paid_staff']*c['loaded_wage_per_staff'],c['staff_payroll'],mode+' paid salary')
 E(c['peak_actual_orders_per_hour']*(c['peak_minutes']/60),c['realized_orders']*c['peak_share'],mode+' peak run')
 E(min(c['desired_orders'],c['day_limit_service_orders'],c['day_limit_peak_orders'],c['day_limit_equipment_orders']),c['realized_orders'],mode+' min bottleneck')
 E(sum(x['business_cashflow'] for x in y['annual']),y['business_cashflow_36'],mode+' years')
 E(sum(x['each_distribution'] for x in y['annual']),y['each_distribution'],mode+' payout')
 for r in y['annual']:E(r['actual_distribution_per_partner_hour']*r['partner_hours_each'],r['each_distribution'],mode+' owner time diagnostic')
 for e in z['exit']+z['weak_exits']:
  E(sum(i['amount'] for i in e['recovery_items']),e['asset_recovery_total'],mode+' exit assets')
  E(sum(i['amount'] for i in e['exit_cost_items']),e['exit_cost_total'],mode+' exit costs')
  E(max(0,e['exit_cost_total']-e['remaining_cash']-e['asset_recovery_total']),e['net_exit_payment_needed'],mode+' exit day')
  E(max(0,e['remaining_cash']+e['asset_recovery_total']-e['exit_cost_total']),e['returned_cash_at_exit'],mode+' exit cash back')
  E(sum(i['signed_amount'] for i in e['loss_trace']),e['total_net_investor_loss'],mode+' cumulative loss')
  E(e['total_net_investor_loss']/2,e['loss_per_partner'],mode+' each loss')
  E(e['total_net_investor_loss'],X[(e['case_id'],e['exit_month'])]['total_net_investor_loss'],mode+' canonical exit')
ok(len(b['conditional_tests'])==11,'11 evidence-linked what-if tests')
for t in b['conditional_tests']:
 r=b['reader'][t['mode']]
 if 'price' in t:
  E(t['m12_on_list_ticket'],t['price'],t['key']+' target price')
  E(t['m12_on_food_cost'],r['month12']['channel'][0]['unit']['food_cost'],t['key']+' hold ingredient yuan')
 if 'fitout_delta' in t:
  E(t['funding_delta'],t['fitout_delta'],t['key']+' one-off new capital')
  E(t['m6_loss_delta'],t['fitout_delta'],t['key']+' fitout no recovery')
  E(t['y1_avg_profit_delta'],0,t['key']+' no operating change')
 if 'lease_end' in t:
  z=t['lease_end'];E(z['net_transfer_month_equivalent']*t['lease_months'],t['transfer']-t.get('transfer_credit',0),t['key']+' lease duration')
  ok(z['exit_loss_if_no_early_charge']<=z['loss_base_early_charge'],t['key']+' no early charge')
ok(len(b['platform_asymmetry_tests'])==30,'30 asymmetric platform tests')
for mode in 'ABCDE':
 for field in ('delivery_cost','commission_rate','merchant_discount_rate'):
  x=[r for r in b['platform_asymmetry_tests'] if r['mode']==mode and r['field']==field]
  ok(len(x)==2,mode+' per channel '+field)
  E(x[0]['y1_delta'],x[1]['y1_delta'],mode+' symmetric costs base, unknown actual ranking '+field)
ok(len(b['sensitivity'])==54,'sensitivity count')
ok(len(b['sensitivity_corrections'])==5,'five documented corrected price probes')
# Corrections must make repricing more adverse with ingredients held constant.
for t in b['sensitivity_corrections']:ok(t['new_y1_delta']<t['old_y1_delta'],t['mode']+' corrected price pressure')
print(f'PASS: {n} independent CSV/JSON invariance, cash, capacity, per-channel arithmetic, conditions and sensitivity checks; no canonical V3 values changed.')
