#!/usr/bin/env python3
"""Independent V3 output audit; no import of the model implementation."""
import csv,json,hashlib,math,itertools
from pathlib import Path
from collections import defaultdict,Counter
P=Path(__file__).resolve().parents[1]
def load(f): return json.load(open(f))
def read(f): 
    with open(f, encoding='utf-8-sig',newline='') as h:return list(csv.DictReader(h))
def num(r,k):return float(r[k])
M=P/'models'; E=P/'evidence'
monthly=read(M/'monthly_v3.csv'); summary=read(M/'summary_v3.csv'); exits=read(M/'exit_v3.csv'); units=read(M/'unit_economics_v3.csv')
inputs=load(M/'model_inputs_v3.json'); raw={f.stem:load(f) for f in E.glob('*.json')}; report=load(M/'report_data_v3.json')
counts=Counter(); fails=[]; deviations=defaultdict(float)
def ok(label,condition,loc):
    counts[label]+=1
    if not condition: fails.append((label,loc))
def near(label,x,y,loc,atol=.002):
    delta=abs(float(x)-float(y)); deviations[label]=max(delta,deviations[label]);ok(label,delta<=atol,(loc,x,y))
cases=set('_'.join(item) for item in itertools.product('ABCDE',('low','base','high'),('onsite','mixed','delivery_heavy'),('bad','base','good')))
ok('case matrix',len(summary)==len(cases)==135 and {r['case_id'] for r in summary}==cases,'summary')
ok('monthly unique matrix',len(monthly)==4860 and {(r['case_id'],int(r['month'])) for r in monthly}==set(itertools.product(cases,range(1,37))),'monthly')
ok('exit unique matrix',len(exits)==540 and {(r['case_id'],int(r['exit_month'])) for r in exits}==set(itertools.product(cases,(3,6,12,24))),'exit')
ok('unit unique matrix',len(units)==135 and len({(r['mode'],r['tier'],r['scenario'],r['channel']) for r in units})==135,'units')
for f,v in inputs['input_status'].items():ok('source input SHA',v['used'] and v['sha256']==hashlib.sha256((E/f).read_bytes()).hexdigest(),f)
for mode,tier in itertools.product('ABCDE',('low','base','high')):
    cost=raw['startup_costs'][mode][tier]
    for name in ('area_m2','fitout','equipment','opening_inventory','preopening','delivery_setup','property_fee','utilities_fixed','other_fixed','marketing_fixed','equipment_capacity_day'):
        near('source cost mapping',cost[name],inputs['startup'][mode][tier][name],(mode,tier,name))
    for aggregate,items in (('fitout','fitout_items'),('equipment','equipment_items'),('opening_inventory','inventory_items'),('preopening','preopening_items'),('delivery_setup','delivery_setup_items')):
        near('source cost sum',cost[aggregate],sum(a['subtotal'] for a in cost[items]),(mode,tier,aggregate))
    for field in ('rent','deposit_months'):
        near('rent mapping',raw['market_assumptions']['modes'][mode][field][tier],inputs['market'][mode][tier][field],(mode,tier,field))
    near('rent transfer mapping',raw['market_assumptions']['modes'][mode]['transfer'][tier],inputs['market'][mode][tier]['transfer_quote'],(mode,tier))
    for field in ('open_days_30','partner_daily_hours','available_service_person_min','onsite_person_min_per_order','delivery_person_min_per_order','added_staff_service_min_day','peak_minutes','peak_share','peak_partner_person_min','peak_staff_person_min'):
        near('labor mapping',raw['labor_capacity']['modes'][mode][field],inputs['labor'][mode][tier][field],(mode,tier,field))
for platform,tier,scenario in itertools.product(('meituan','taobao'),('low','base','high'),('bad','base','good')):
    for field in ('commission_rate','delivery_cost','merchant_discount_rate','refund_rate','marketing_month','deposit','settlement_days'):
        near('platform mapping',raw['delivery_params']['platforms'][platform][field][scenario],inputs['platform'][platform][scenario][tier][field],(platform,tier,scenario,field))
for mode in 'ABCDE':
    for a,b in [('delivery_ticket','delivery_ticket'),('delivery_food_rate','food_cost_rate'),('delivery_pack','delivery_packaging')]:
        near('delivery basket mapping',inputs['unit_inputs'][mode][a],raw['delivery_params']['modes'][mode][b],(mode,a,b))
sm={r['case_id']:r for r in summary}; mm={(r['case_id'],int(r['month'])):r for r in monthly}; ex={(r['case_id'],int(r['exit_month'])):r for r in exits}
assets=['fitout','equipment','transfer','preopening','delivery_setup','lease_deposit','platform_deposit','opening_inventory']
fixed=['rent','property_fee','utilities_fixed','other_fixed','store_marketing','platform_marketing','staff_payroll','owner_salary']
variable=['food_consumption','packaging_cost','platform_tech_fee','merchant_delivery_cost','payment_fee','host_fee','tax_risk_allowance']
cvar=['food_cost','packaging','platform_fee','delivery_fee','payment_fee','host_fee','tax_budget']
rec=['lease_deposit_recovery','platform_deposit_recovery','equipment_recovery','stock_recovery','receivable_recovery','transfer_recovery','fitout_recovery']
charges=['lease_exit_charge','staff_exit_cost','clearance','unsettled_misc']
S=lambda r,keys:sum(num(r,k) for k in keys)
for case,s in sm.items():
    near('startup outlay sum',num(s,'initial_opening_outlay'),S(s,assets),case)
    near('startup total fund',num(s,'initial_funding'),S(s,['initial_opening_outlay','reserve']),case)
    near('transfer distinct',num(s,'transfer'),max(0,num(s,'transfer_quote')-num(s,'transfer_bundle_credit')),case)
    prev_cash=num(s,'reserve'); previous_inv=num(s,'opening_inventory'); previous_rec=0; previous_staff=0; cumcf=cumcalls=cumpay=0
    for month in range(1,37):
        r=mm[case,month];loc=(case,month); sc=r['scenario'];yr=(month-1)//12
        l=inputs['labor'][r['mode']][r['tier']]; staff=num(r,'paid_staff')
        ok('two owners zero pay',num(r,'owner_salary')==0 and num(r,'partner_count')==2,loc)
        ok('staff integer bounds',staff.is_integer() and l['min_staff']<=staff<=l['max_staff'],loc)
        if month%3!=1: near('quarterly staff',staff,previous_staff,loc)
        near('full loaded wage payroll',num(r,'staff_payroll'),num(r,'loaded_wage_per_staff')*staff,loc,atol=.0005)
        near('staff change cost',num(r,'staff_change_cost'),700*max(0,staff-previous_staff)+1200*max(0,previous_staff-staff),loc)
        near('partner working time',num(r,'partner_total_hours_month'),2*num(r,'days')*l['partner_daily_hours'],loc)
        near('person time linked staff',num(r,'available_person_min'),l['available_service_person_min']+staff*l['added_staff_service_min_day'],loc)
        near('peak time linked staff',num(r,'peak_person_min'),l['peak_partner_person_min']+staff*l['peak_staff_person_min'],loc)
        near('actual order total',num(r,'total_orders'),num(r,'realized_daily')*num(r,'days'),loc)
        near('order partition onsite+delivery',num(r,'realized_daily'),S(r,['actual_onsite_daily','actual_delivery_daily']),loc)
        near('order partition 3 channels',num(r,'total_orders'),S(r,['onsite_orders','meituan_orders','taobao_orders']),loc)
        act=num(r,'actual_onsite_daily')*l['onsite_person_min_per_order']+num(r,'actual_delivery_daily')*l['delivery_person_min_per_order']
        near('independent actual person time',num(r,'actual_person_min'),act,loc,.001)
        near('peak actual person time',num(r,'peak_actual_person_min'),act*l['peak_share'],loc,.001)
        ok('hard capacity',act<=num(r,'available_person_min')+.001 and act*l['peak_share']<=num(r,'peak_person_min')+.001 and num(r,'realized_daily')<=min(num(r,'equipment_capacity_day'),num(r,'desired_total_daily'))+.001,loc)
        near('unserved orders',num(r,'lost_daily_orders'),num(r,'desired_total_daily')-num(r,'realized_daily'),loc)
        if r['strategy']=='onsite':
            ok('offline no online orders',num(r,'meituan_orders')==num(r,'taobao_orders')==num(r,'platform_marketing')==0,loc)
        for ch in ('onsite','meituan','taobao'):
            g=lambda k:num(r,ch+'_'+k+'_total')
            near('channel net meal revenue',g('revenue'),g('list_ticket')-g('discount')-g('refund'),(loc,ch))
            near('channel direct food',g('food_cost'),g('sold_food')+g('food_waste'),(loc,ch))
            near('channel contribution',g('contribution'),g('revenue')-sum(g(k) for k in cvar),(loc,ch))
            near('channel settlement',g('settlement'),g('revenue')-g('platform_fee')-g('delivery_fee'),(loc,ch))
            for key in ('list_ticket','discount','refund','revenue','sold_food','food_waste','food_cost','packaging','platform_fee','delivery_fee','payment_fee','host_fee','tax_budget','settlement','contribution'):
                # CSV per order rounded 5 dec places. For monthly large sums allow order count x rounding.
                near('unit to total',g(key),num(r,ch+'_'+key+'_per_order')*num(r,ch+'_orders'),(loc,ch,key),.000006*(1+num(r,ch+'_orders'))+.0002)
        near('recognized revenue',num(r,'recognized_revenue'),num(r,'order_value_listed')-num(r,'discounts')-num(r,'refund_allowance'),loc)
        near('food cost',num(r,'food_consumption'),S(r,['food_sold','food_waste']),loc)
        near('contribution',num(r,'order_contribution'),num(r,'recognized_revenue')-S(r,variable),loc)
        near('fixed costs',num(r,'total_fixed_cost'),S(r,fixed),loc)
        near('operating profit',num(r,'operating_profit'),num(r,'order_contribution')-S(r,['total_fixed_cost','staff_change_cost']),loc)
        near('accounting profit',num(r,'accounting_profit'),num(r,'operating_profit')-num(r,'amortization'),loc)
        near('inventory net change',num(r,'inventory_change'),num(r,'inventory_balance')-previous_inv,loc)
        near('receivable net change',num(r,'receivables_change'),num(r,'receivables')-previous_rec,loc)
        near('cashflow',num(r,'business_cashflow'),num(r,'operating_profit')-S(r,['inventory_change','receivables_change','maintenance_capex']),loc)
        near('capital need',num(r,'additional_capital'),max(0,-prev_cash-num(r,'business_cashflow')),loc)
        near('cash opening before calls',num(r,'balance_before_capital_call'),prev_cash+num(r,'business_cashflow'),loc)
        near('cash closing',num(r,'retained_cash'),prev_cash+S(r,['business_cashflow','additional_capital'])-num(r,'distributed_to_partners'),loc)
        near('distribution per owner',num(r,'distribution_per_partner'),num(r,'distributed_to_partners')/2,loc)
        if month%3: near('quarterly distribution',num(r,'distributed_to_partners'),0,loc)
        cumcf+=num(r,'business_cashflow');cumcalls+=num(r,'additional_capital');cumpay+=num(r,'distributed_to_partners')
        near('cumulative cashflow',num(r,'cumulative_business_cashflow'),cumcf,loc)
        near('cumulative capital',num(r,'cumulative_additional_capital'),cumcalls,loc)
        near('cumulative distribution',num(r,'cumulative_distributions'),cumpay,loc)
        if cumcalls>.001:near('distribution blocked post-call',num(r,'distributed_to_partners'),0,loc)
        prev_cash=num(r,'retained_cash');previous_inv=num(r,'inventory_balance');previous_rec=num(r,'receivables');previous_staff=staff
        if (case,month) in ex:
            e=ex[case,month];assets_back=S(e,rec);exit_bill=S(e,charges)
            near('exit cash source',num(e,'remaining_cash'),prev_cash,loc)
            near('exit asset accounts',num(e,'asset_recovery_total'),assets_back,loc)
            near('exit bill accounts',num(e,'exit_cost_total'),exit_bill,loc)
            near('exit net payment',num(e,'net_exit_payment_needed'),max(0,exit_bill-prev_cash-assets_back),loc)
            near('exit bridge',num(e,'exit_day_bridge_before_recovery'),max(0,exit_bill-prev_cash),loc)
            near('exit return',num(e,'returned_cash_at_exit'),max(0,prev_cash+assets_back-exit_bill),loc)
            near('exit net loss A',num(e,'total_net_investor_loss'),num(s,'initial_funding')+cumcalls+num(e,'net_exit_payment_needed')-cumpay-num(e,'returned_cash_at_exit'),loc)
            near('exit net loss B',num(e,'total_net_investor_loss'),num(s,'initial_opening_outlay')-cumcf-assets_back+exit_bill,loc)
            for name,src in [('loss_per_partner','total_net_investor_loss'),('cash_payment_per_partner','net_exit_payment_needed'),('bridge_per_partner','exit_day_bridge_before_recovery')]:
                near('exit 50-50 split',num(e,name),num(e,src)/2,loc)
    near('summary cumulative cashflow',num(s,'cumulative_business_cashflow'),cumcf,case)
    near('summary final cash',num(s,'cash_balance_m36'),prev_cash,case)
    near('summary payouts',num(s,'cumulative_distributions'),cumpay,case)
    near('summary calls',num(s,'total_capital_calls'),cumcalls,case)
    for year in range(1,4):
        for field in ('recognized_revenue','total_orders','operating_profit','accounting_profit','business_cashflow','additional_capital','distributed_to_partners','staff_payroll'):
            near('summary annual sum',num(s,f'y{year}_{field}'),sum(num(mm[case,m],field) for m in range((year-1)*12+1,year*12+1)),(case,year,field))
# Ensure the report generator is reading the same model output, not stale/hand-entered copies.
def compare_json(label,jrow,crow,loc):
    for k,v in jrow.items():
        assert k in crow, (label,k,loc)
        if isinstance(v,(float,int)) and not isinstance(v,bool):
            near(label,v,num(crow,k),(loc,k),.000011)
        elif v is None: ok(label,crow[k]=='',(loc,k))
        else: ok(label,str(v)==crow[k],(loc,k))
ok('report summary covers all cases',len(report['summary'])==135 and {r['case_id'] for r in report['summary']}==cases,'report')
ok('report monthly covers all months',len(report['monthly_compact'])==4860 and {(r['case_id'],r['month']) for r in report['monthly_compact']}==set(mm),'report')
ok('report exits cover all exits',len(report['all_exits'])==540 and {(r['case_id'],r['exit_month']) for r in report['all_exits']}==set(ex),'report')
ok('report selected is five standard mixed baseline cases',{r['case_id'] for r in report['selected']}=={m+'_base_mixed_base' for m in 'ABCDE'},'report')
for r in report['summary']: compare_json('report summary matches csv',r,sm[r['case_id']],r['case_id'])
for r in report['selected']: compare_json('report selected matches csv',r,sm[r['case_id']],r['case_id'])
for r in report['monthly_compact']+report['monthly_selected']: compare_json('report monthly matches csv',r,mm[r['case_id'],r['month']],(r['case_id'],r['month']))
for r in report['all_exits']+report['exit_selected']: compare_json('report exit matches csv',r,ex[r['case_id'],r['exit_month']],(r['case_id'],r['exit_month']))
uk={(r['mode'],r['tier'],r['scenario'],r['channel']):r for r in units}
for r in report['unit_economics']: 
    key=(r['mode'],r['tier'],r['scenario'],r['channel']); compare_json('report unit matches csv',r,uk[key],key)
ok('report and model inputs consistent',report['inputs']==inputs,'report')
for label in sorted(counts):
    print(f'{label}: {counts[label]} checks; max rounding delta={deviations.get(label,0):.7g}')
print('TOTAL',sum(counts.values()),'FAILURES',len(fails))
for f in fails[:30]:print('FAIL',f)
assert not fails
