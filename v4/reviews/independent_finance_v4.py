#!/usr/bin/env python3
"""Read-only numeric audit of untouched V3 baseline + V4 reader data. No model imports."""
import csv,json,math,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
m3=ROOT/'v3/models';m4=ROOT/'v4/models'
read=lambda f:list(csv.DictReader(f.open(encoding='utf-8-sig')))
j=lambda f:json.loads(f.read_text())
old=j(m3/'report_data_v3.json');v=j(m4/'report_data_v4.json')
checks=0;errors=[]
def check(cond,label):
 global checks
 checks+=1
 if not cond: errors.append(label)
def near(a,b,label,tol=.003):
 try: check(math.isclose(float(a),float(b),rel_tol=1e-9,abs_tol=tol),label)
 except (ValueError,TypeError):check(a==b,label)
def field(a,k,b,other=None):
 near(a[k],b[other or k],k)
def fsum(r,ks):return sum(float(r[k]) for k in ks)
for key in ('summary','selected','monthly_selected','exit_selected','all_exits','monthly_compact','unit_economics','inputs'):
 check(old[key]==v[key], 'V3 exact semantic data preserved '+key)
# Sensitivities intentionally changed, unlike core matrix; five mistaken food-price
# linkages repaired and 5 wording-only online growth explanations clarified.
original=old['sensitivity']; revised=v['sensitivity']
check(len(original)==len(revised)==54,'sensitivity row count')
diff_price=diff_label=0
for a,b in zip(original,revised):
 if a==b:continue
 check(a['mode']==b['mode'],'sensitivity same mode')
 if a['test']=='线下售价低10%':
  diff_price+=1
  check('原食材绝对成本不变' in b['test'],'corrected sensitivity label')
  check(b['y1_monthly_profit']<a['y1_monthly_profit'],'no artificial food cost reduction')
  check(b['y1_monthly_profit_delta']<a['y1_monthly_profit_delta'],'larger single-factor negative effect')
 elif a['test']=='另发掘20%线上增量且线下无流失':
  diff_label+=1
  check({k:v for k,v in a.items() if k!='test'}=={k:v for k,v in b.items() if k!='test'},'online delta only changed label')
 else: check(False,'unexpected sensitivity change')
check(diff_price==5 and diff_label==5,'exact 5+5 sensitivity revisions')
check(v['v4_meta']['source_report_sha256']==hashlib.sha256((m3/'report_data_v3.json').read_bytes()).hexdigest(),'V3 SHA256')
cases={r['case_id']:r for r in read(m3/'summary_v3.csv')}
monthly={(r['case_id'],int(r['month'])):r for r in read(m3/'monthly_v3.csv')}
exits={(r['case_id'],int(r['exit_month'])):r for r in read(m3/'exit_v3.csv')}
check(len(cases)==135,'135 cases')
check(len(monthly)==4860,'4860 months')
check(len(exits)==540,'540 exits')
for mode,r in v['reader'].items():
 case=r['case_id']; s=cases[case]; month=monthly[case,12]
 check(case==f'{mode}_base_mixed_base',case+' baseline')
 o=r['opening'];near(o['initial_funding'],s['initial_funding'],case+' start funds')
 near(o['initial_funding'],o['start_spent_or_tied']+o['account_reserve'],case+' start split')
 near(o['start_spent_or_tied'],s['initial_opening_outlay'],case+' spent')
 near(o['account_reserve'],s['reserve'],case+' reserve')
 near(sum(x['amount'] for x in o['categories']),o['initial_funding'],case+' categories')
 near(o['initial_each_50_50']*2,o['initial_funding'],case+' each')
 for x in o['categories']:
  near(sum(float(a['subtotal']) for a in x['items']),x['amount'],case+' '+x['key'])
  if x['key'] not in ('reserve',):near(x['amount'],s[x['key']],case+' '+x['key']+' summary')
 cap=r['capacity']
 check(cap['partner_count']==2 and cap['partner_salary']==0,case+' 2 partners/zero salary')
 near(cap['total_service_min_day'],cap['partner_service_min_day']+cap['paid_staff']*cap['staff_service_add_min_day_each'],case+' staff capacity')
 near(cap['staff_payroll'],cap['paid_staff']*cap['loaded_wage_per_staff'],case+' loaded wage')
 near(cap['realized_orders'],month['realized_daily'],case+' realized')
 check(cap['realized_orders'] <= min(cap['desired_orders'],cap['day_limit_service_orders'],cap['day_limit_peak_orders'],cap['day_limit_equipment_orders'])+1e-7,case+' min constraints')
 M=r['month12'];day=M['daily'];days=M['days']; near(days,month['days'],case+' days')
 near(day['orders']*days,month['total_orders'],case+' daily orders')
 near(day['sales']*days,M['net_sales'],case+' daily sales')
 near(day['operating_profit']*days,M['operating_profit'],case+' daily operating')
 near(M['net_sales'],month['recognized_revenue'],case+' sales')
 near(M['net_sales'],M['order_value_listed']-M['merchant_discount']-M['refund_allowance'],case+' net sales')
 for ch in M['channel']:
  k=ch['key'];u=ch['unit'];near(u['list_ticket']-u['discount']-u['refund'],u['revenue'],case+' channel rev '+k)
  near(u['food_sold']+u['food_waste'],u['food_cost'],case+' food '+k)
  near(u['revenue']-sum(u[x] for x in ('food_cost','packaging','platform_fee','delivery_fee','payment_fee','host_fee','tax_budget')),u['contribution'],case+' contribution '+k)
  near(ch['monthly_revenue'],u['revenue']*ch['orders_month'],case+' total revenue '+k)
  near(ch['monthly_contribution'],u['contribution']*ch['orders_month'],case+' total contrib '+k)
  near(ch['orders_month'],month[k+'_orders'],case+' CSV orders '+k)
  near(ch['monthly_revenue'],month[k+'_revenue_total'],case+' CSV sales '+k)
 near(sum(c['monthly_revenue'] for c in M['channel']),M['net_sales'],case+' sum channels')
 near(sum(c['monthly_contribution'] for c in M['channel']),M['order_contribution'],case+' sum contributions')
 near(sum(x['amount'] for x in M['variable_items']),M['variable_cost'],case+' variable')
 near(sum(x['amount'] for x in M['fixed_items']),M['fixed_cost'],case+' fixed')
 near(M['net_sales']-M['variable_cost']-M['fixed_cost']-M['staff_change_cost'],M['operating_profit'],case+' operating')
 near(M['operating_profit'],month['operating_profit'],case+' CSV operating')
 near(M['accounting_profit_approx'],M['operating_profit']-M['amortization'],case+' accrual')
 near(sum(x['signed_amount'] for x in M['cash_trace']),M['cash_flow'],case+' cash')
 near(M['cash_flow'],month['business_cashflow'],case+' CSV cash')
 near(sum(x['signed_amount'] for x in M['cash_balance_trace']),M['retained_cash'],case+' bank balance')
 near(M['retained_cash'],month['retained_cash'],case+' CSV balance')
 near(M['distribution_per_partner']*2,M['distributed_to_partners'],case+' split')
 near(M['fixed_cost']/M['contribution_per_order']/days,M['break_even_order_daily'],case+' break-even')
 yrs=r['years']; near(yrs['additional_capital'],s['total_capital_calls'],case+' add capital')
 near(yrs['starting_funding']+yrs['additional_capital'],yrs['all_funding_with_calls'],case+' total funds')
 near(yrs['invested_each']*2,yrs['all_funding_with_calls'],case+' owner investment')
 near(yrs['each_distribution']*2,yrs['total_distribution'],case+' owner distribution')
 for ann in yrs['annual']:
  a=ann['year']
  for x in ('recognized_revenue','operating_profit','business_cashflow','additional_capital','distributed_to_partners','avg_monthly_profit','avg_daily_orders'):
   near(ann[x],s[f'y{a}_{x}'],case+' year '+str(a)+x)
 prev=o['account_reserve']
 for mon in yrs['monthly']:
  n=mon['month']; base=monthly[case,n]
  near(mon['retained_cash'],prev+mon['business_cashflow']+mon['additional_capital']-mon['distributed_to_partners'],case+' month'+str(n))
  for x in ('days','realized_daily','recognized_revenue','operating_profit','business_cashflow','distributed_to_partners','retained_cash','additional_capital','paid_staff'):
   near(mon[x],base[x],case+' month '+str(n)+x)
  prev=mon['retained_cash']
 near(yrs['cash_36'],prev,case+' yr3 bank')
 for e in r['exit']+r['weak_exits']:
  label=e['case_id']+' exit '+str(e['exit_month']); raw=exits[e['case_id'],e['exit_month']]
  near(sum(x['amount'] for x in e['recovery_items']),e['asset_recovery_total'],label+' recovery')
  near(sum(x['amount'] for x in e['exit_cost_items']),e['exit_cost_total'],label+' costs')
  near(max(0,e['exit_cost_total']-e['remaining_cash']-e['asset_recovery_total']),e['net_exit_payment_needed'],label+' net extra')
  near(max(0,e['exit_cost_total']-e['remaining_cash']),e['exit_day_bridge_before_recovery'],label+' bridge')
  near(max(0,e['remaining_cash']+e['asset_recovery_total']-e['exit_cost_total']),e['returned_cash_at_exit'],label+' returned')
  near(sum(x['signed_amount'] for x in e['loss_trace']),e['total_net_investor_loss'],label+' investment loss')
  near(e['initial_opening_outlay']-e['cumulative_business_cashflow']-e['asset_recovery_total']+e['exit_cost_total'],e['total_net_investor_loss'],label+' second identity')
  near(e['total_net_investor_loss'],raw['total_net_investor_loss'],label+' CSV loss')
  near(e['loss_per_partner']*2,e['total_net_investor_loss'],label+' per owner')
 for axis,rows in r['comparisons'].items():
  check(len(rows)==3,case+axis)
  for c in rows:
   target=cases[f"{mode}_{c['tier']}_{c['strategy']}_{c['scenario']}"]
   for x in ('initial_funding','reserve','initial_opening_outlay','y1_avg_monthly_profit','m12_realized_daily','m12_break_even_daily_orders','total_capital_calls','partner_distribution_each','exit_m6_total_net_investor_loss','exit_m12_total_net_investor_loss','exit_m24_total_net_investor_loss'):
    near(c[x],target[x],case+axis+x)
# Additional condition tests — only independently check identified visible identities/deltas,
# not claim full solver reproduction unless exact fields are exported.
conditionals=v.get('conditional_tests',[])
check(len(conditionals)==11,'11 named V4 conditions')
for t in conditionals:
 label=t['key']; r=v['reader'][t['mode']]; o=r['opening']; M=r['month12']; s=cases[r['case_id']]
 near(t['initial_funding'],t['opening_spent']+t['reserve'],label+' funding split')
 near(t['funding_delta'],t['initial_funding']-o['initial_funding'],label+' funding delta')
 near(t['y1_avg_profit_delta'],t['y1_avg_profit']-float(s['y1_avg_monthly_profit']),label+' y1 delta')
 near(t['m6_loss_delta'],t['m6_loss']-float(s['exit_m6_total_net_investor_loss']),label+' m6 delta')
 if 'rent' in t:
  rentd=t['rent']-o['monthly_rent']; net_transfer=t.get('transfer',o['transfer_listed_budget'])-t.get('transfer_credit',0)
  near(t['opening_spent']-o['start_spent_or_tied'],rentd*o['deposit_months']+net_transfer-o['transfer_budget'],label+' rent/deposit/transfer')
  near(t['reserve']-o['account_reserve'],rentd*3,label+' reserve')
  near(t['y1_avg_profit_delta'],-rentd,label+' year1 rent effect')
 if 'fitout_delta' in t:
  near(t['funding_delta'],t['fitout_delta'],label+' only exhaust replacement')
  near(t['y1_avg_profit_delta'],0,label+' exhaust not operating expense')
 if 'price' in t:
  on=M['channel'][0]['unit']; delta=t['price']-on['list_ticket']
  near(t['m12_on_food_cost'],on['food_cost'],label+' absolute ingredient cost held')
  near(t['m12_net_sales']-M['net_sales'],delta*M['channel'][0]['orders_month'],label+' sales change')
  expected=delta*M['channel'][0]['orders_month']*(1-on['payment_fee']/on['revenue']-on['tax_budget']/on['revenue']-on['host_fee']/on['revenue'])
  near(t['m12_profit']-M['operating_profit'],expected,label+' profit change after proportional fees')
 if 'lease_end' in t:
  e=t['lease_end']
  near(e['net_transfer_month_equivalent'],(t['transfer']-t.get('transfer_credit',0))/t['lease_months'],label+' lease amortization')
  near(e['exit_loss_if_no_early_charge'],t['opening_spent']-e['business_cashflow_cumulative']-e['recovered_assets']+e['closing_cost_no_early_charge'],label+' lease end loss')
asym=v.get('platform_asymmetry_tests',[])
check(len(asym)==30,'30 single platform tests')
for t in asym:
 label=t['mode']+' '+t['channel']+' '+t['field'];r=v['reader'][t['mode']]; M=r['month12']; s=cases[r['case_id']]; unit=next(x for x in M['channel'] if x['key']==t['channel'])
 near(t['m12_delta'],t['m12_operating_profit']-M['operating_profit'],label+' delta operating')
 near(t['y1_delta'],t['y1_avg_monthly_profit']-float(s['y1_avg_monthly_profit']),label+' delta year')
 if abs(t['m12_daily_orders']-M['daily']['orders'])<1e-7 and t['field']=='delivery_cost':
  near(t['m12_delta'],-t['test_delta']*unit['orders_month'],label+' independently computed delivery delta')
print('checks',checks,'failures',len(errors))
for e in errors[:20]:print(e)
raise SystemExit(1 if errors else 0)
