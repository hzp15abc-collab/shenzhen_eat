#!/usr/bin/env python3
"""Independently reconcile CSV outputs; tolerances cover 5-decimal serialization."""
from pathlib import Path
import csv,json,hashlib,math
from collections import defaultdict
P=Path(__file__).resolve().parent
def rows(f):return list(csv.DictReader((P/f).open(encoding='utf-8-sig')))
def f(r,k):return float(r[k] or 0)
def equal(a,b,tol=.015):
 assert abs(a-b)<tol,(a,b)
s={r['case_id']:r for r in rows('summary_v3.csv')};m=defaultdict(list)
for r in rows('monthly_v3.csv'):m[r['case_id']].append(r)
ex=rows('exit_v3.csv');u=rows('unit_economics_v3.csv');sens=rows('sensitivity_v3.csv')
assert len(s)==len(m)==135 and len(ex)==540 and len(u)==135
for cid,series in m.items():
 b=s[cid];cash=f(b,'reserve');sumcf=0;sumcall=0;sumpay=0
 equal(f(b,'initial_funding'),f(b,'reserve')+sum(f(b,k) for k in ('fitout','equipment','transfer','preopening','delivery_setup','lease_deposit','platform_deposit','opening_inventory')))
 assert len(series)==36
 for i,r in enumerate(series,1):
  assert int(r['month'])==i and f(r,'partner_count')==2 and f(r,'owner_salary')==0
  assert abs(f(r,'total_orders')-sum(f(r,k+'_orders') for k in ('onsite','meituan','taobao')))<.015
  assert f(r,'actual_person_min')<=f(r,'available_person_min')+.015 and f(r,'peak_actual_person_min')<=f(r,'peak_person_min')+.015
  assert f(r,'realized_daily')<=f(r,'equipment_capacity_day')+.015 and f(r,'realized_daily')<=f(r,'desired_total_daily')+.015
  equal(f(r,'recognized_revenue'),f(r,'order_value_listed')-f(r,'discounts')-f(r,'refund_allowance'))
  equal(f(r,'order_contribution'),f(r,'recognized_revenue')-sum(f(r,k) for k in ('food_consumption','packaging_cost','platform_tech_fee','merchant_delivery_cost','payment_fee','host_fee','tax_risk_allowance')))
  equal(f(r,'operating_profit'),f(r,'order_contribution')-f(r,'total_fixed_cost')-f(r,'staff_change_cost'))
  equal(f(r,'business_cashflow'),f(r,'operating_profit')-f(r,'inventory_change')-f(r,'receivables_change')-f(r,'maintenance_capex'))
  equal(f(r,'staff_payroll'),f(r,'paid_staff')*f(r,'loaded_wage_per_staff'))
  cash+=f(r,'business_cashflow')+f(r,'additional_capital')-f(r,'distributed_to_partners')
  sumcf+=f(r,'business_cashflow');sumcall+=f(r,'additional_capital');sumpay+=f(r,'distributed_to_partners')
  equal(cash,f(r,'retained_cash'));equal(sumcf,f(r,'cumulative_business_cashflow'))
  equal(sumcall,f(r,'cumulative_additional_capital'));equal(sumpay,f(r,'cumulative_distributions'))
 equal(sumcf,f(b,'cumulative_business_cashflow'));equal(cash,f(b,'cash_balance_m36'))
for e in ex:
 r=m[e['case_id']][int(e['exit_month'])-1]
 equal(f(e,'asset_recovery_total'),sum(f(e,k) for k in ('lease_deposit_recovery','platform_deposit_recovery','equipment_recovery','stock_recovery','receivable_recovery','transfer_recovery','fitout_recovery')))
 equal(f(e,'exit_cost_total'),sum(f(e,k) for k in ('lease_exit_charge','staff_exit_cost','clearance','unsettled_misc')))
 total=f(e,'initial_funding')+f(e,'additional_capital_before_exit')+f(e,'net_exit_payment_needed')-f(e,'cumulative_distributions')-f(e,'returned_cash_at_exit')
 equal(total,f(e,'total_net_investor_loss'))
 equal(f(e,'total_net_investor_loss'),f(e,'initial_opening_outlay')-f(e,'cumulative_business_cashflow')-f(e,'asset_recovery_total')+f(e,'exit_cost_total'))
 equal(f(e,'total_net_investor_loss')/2,f(e,'loss_per_partner'))
 equal(f(e,'remaining_cash'),f(r,'retained_cash'))
p=json.loads((P/'model_inputs_v3.json').read_text())
for k,v in p['input_status'].items():
 assert v['used'] and v['sha256']==hashlib.sha256((P.parent/'evidence'/k).read_bytes()).hexdigest()
assert len(sens)>=50
print('PASS: independent CSV check',len(s),'cases',sum(map(len,m.values())),'months',len(ex),'exits',len(u),'unit snapshots',len(sens),'one-factor tests; source hashes match.')
