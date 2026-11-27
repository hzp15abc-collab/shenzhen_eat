#!/usr/bin/env python3
"""Conditional sensitivity: D needs one qualified heat-kitchen cook when partners lack skills.
Canonical 135 scenario set remains unchanged (partners assumed qualified).
Based on labor_capacity.json skilled benchmark 11,600 RMB loaded monthly; not a job quote.
Only first paid role is skilled, each additional employee retains ordinary employer-cost scenario.
"""
import csv,json
from pathlib import Path
import model_v3 as m
orig_labor=m.get_labor
orig_fixed=m.fixed
def labor(mode,tier):
 d=orig_labor(mode,tier)
 if mode=='D':d['min_staff']=max(1,d['min_staff'])
 return d
def fixed(mode,tier,strategy,sc,month,staff):
 r=orig_fixed(mode,tier,strategy,sc,month,staff)
 if mode=='D' and staff:
  year=(month-1)//12
  sk=11600*m.MARKET_SCENARIOS[sc]['wage']*(1+m.MARKET_SCENARIOS[sc]['wage_growth'])**year
  r['staff_payroll']+=sk-m.wage(tier,sc,year)
 return r
p=Path(__file__).resolve().parent
rows=[]
for tier,sc in [('low','base'),('base','base'),('base','good'),('high','base'),('high','good')]:
 m.get_labor=orig_labor;m.fixed=orig_fixed
 _,b,_=m.simulate('D',tier,'mixed',sc)
 m.get_labor=labor;m.fixed=fixed
 _,r,_=m.simulate('D',tier,'mixed',sc)
 rows.append(dict(case_id=b['case_id'],tier=tier,scenario=sc,qualified_owner_assumption='partners can perform D kitchen tasks; ordinary paid staff only if economic',
  sensitivity='one qualified paid cook required; first role loaded 11600/month plus ordinary additional staff',staff_max_base=b['staff_max'],staff_max_skilled=r['staff_max'],
  funding_base=b['initial_funding'],funding_skilled=r['initial_funding'],y1_avg_profit_base=b['y1_avg_monthly_profit'],y1_avg_profit_skilled=r['y1_avg_monthly_profit'],
  y2_avg_profit_base=b['y2_avg_monthly_profit'],y2_avg_profit_skilled=r['y2_avg_monthly_profit'],cashflow36_base=b['cumulative_business_cashflow'],cashflow36_skilled=r['cumulative_business_cashflow'],
  m6_loss_base=b['exit_m6_total_net_investor_loss'],m6_loss_skilled=r['exit_m6_total_net_investor_loss'],
  capital_recovery_base=b['capital_recovery_month'],capital_recovery_skilled=r['capital_recovery_month'],additional_capital_skilled=r['total_capital_calls']))
m.get_labor=orig_labor;m.fixed=orig_fixed
m.write_csv(p/'skilled_cook_sensitivity_v3.csv',rows)
(p/'skilled_cook_sensitivity_v3.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
for row in rows:print(row['case_id'],round(row['funding_skilled']),round(row['y1_avg_profit_skilled']),round(row['y2_avg_profit_skilled']),round(row['m6_loss_skilled']),row['staff_max_skilled'])
