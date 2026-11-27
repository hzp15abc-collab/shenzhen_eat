#!/usr/bin/env python3
"""V4 reader-facing causal layer, all values CNY. No mutation to frozen V3.
The source baseline remains verified V3 conditional scenarios. New observed
facts can affect a specific scenario only if a documented evidence overlay
supplies a comparable quote with scope. Conditional offer/fee tests are
explicitly separate from the standard baseline. All math uses exact floats
until display. Run: python v4/models/build_finance_v4.py
"""
import json, csv, math, hashlib, importlib.util
from pathlib import Path
from copy import deepcopy

P=Path(__file__).resolve().parent
V4=P.parent
V3=P.parents[1]/'v3'
OUT=P/'report_data_v4.json'
RD=V3/'models/report_data_v3.json'
BASE=json.loads(RD.read_text())
COST=json.loads((V3/'evidence/startup_costs.json').read_text())
LABOR=json.loads((V3/'evidence/labor_capacity.json').read_text())
MARKET=json.loads((V3/'evidence/market_assumptions.json').read_text())
DELIVERY=json.loads((V3/'evidence/delivery_params.json').read_text())
MR={r['id']:r for r in csv.DictReader((V3/'evidence/market_rent.csv').open(encoding='utf-8-sig'))}
INPUT=BASE['inputs']
S={s['mode']:s for s in BASE['selected']}
M={s['mode']:[m for m in BASE['monthly_selected'] if m['mode']==s['mode']] for s in BASE['selected']}
X={s['mode']:[x for x in BASE['exit_selected'] if x['mode']==s['mode']] for s in BASE['selected']}
U={(r['mode'],r['tier'],r['scenario'],r['channel']):r for r in BASE['unit_economics']}
SC={x['case_id']:x for x in BASE['summary']}
MODE_META={
 'A':{'name':'传统早餐','role1':'备料、蒸制、热食质量','role2':'收银、盛装、打包与补台','risk':'高峰拥堵；低毛利怕损耗；提前备料及卫生'},
 'B':{'name':'特色便携早餐','role1':'冷热分区、组装、压烤','role2':'收银、包装、订单核对','risk':'新品复购、短保库存、冷链及标准化'},
 'C':{'name':'早餐＋休闲零食','role1':'热食备餐与补货','role2':'收银、陈列、包装与库存','risk':'多SKU的资金与临期；淡时段是否真增加需求'},
 'D':{'name':'多时段餐饮','role1':'热厨、批次生产与食品安全','role2':'前台收银、包装、洗消与交接','risk':'专业热厨门槛；工时长、跨时段产能与休息'},
 'E':{'name':'分时合作／店中店','role1':'少SKU预备、加热','role2':'收款、打包、交接清洁','risk':'独立许可和房东同意；设备、库存与钱款归属'},
}
START_GROUPS=[
 ('fitout','装修/店面工程','fitout_items','已付或占用'),
 ('equipment','设备与工器具','equipment_items','已付或占用'),
 ('transfer','转让/净进场费',None,'已付或占用'),
 ('preopening','开业准备','preopening_items','已付或占用'),
 ('delivery_setup','外卖开通物料','delivery_setup_items','已付或占用'),
 ('lease_deposit','租房押金',None,'已付或占用'),
 ('platform_deposit','平台保证金',None,'已付或占用'),
 ('opening_inventory','首批货/原料','inventory_items','已付或占用'),
 ('reserve','账户周转储备',None,'账上现金'),
]
VAR_FIELDS=[
 ('food_consumption','食材含损耗'),('packaging_cost','包装'),('platform_tech_fee','平台技术费'),('merchant_delivery_cost','商家承担配送'),
 ('payment_fee','线下支付费用'),('host_fee','共享方分成'),('tax_risk_allowance','税费预算（非税率结论）')]
FIX_FIELDS=[
 ('rent','房租'),('property_fee','管理费'),('utilities_fixed','水电基础'),
 ('other_fixed','其他运营'),('store_marketing','门店推广'),('platform_marketing','平台推广'),
 ('staff_payroll','受雇员工全部雇主成本'),('owner_salary','两位合伙人工资（排除）')]
CHANNELS={'onsite':'线下','meituan':'美团外卖','taobao':'淘宝闪购'}
count=0
def eq(a,b,label,tol=1e-6):
 global count
 count+=1
 if not math.isclose(a,b,rel_tol=1e-10,abs_tol=tol):
  raise AssertionError((label,a,b))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def items(row,fields):
 return [{'key':k,'label':v,'amount':row[k]} for k,v in fields]
def opening(mode,s):
 tier=s['tier']; market=INPUT['market'][mode][tier]; cost=COST[mode][tier]; 
 cats=[]
 for key,name,detail,status in START_GROUPS:
  x={'key':key,'label':name,'amount':s[key],'kind':status}
  if detail:
   x['items']=cost[detail]
   eq(sum(d['subtotal'] for d in x['items']),x['amount'],mode+' '+key)
  elif key=='transfer':
   x['items']=[{'name':'转让报价预算（非指定挂牌实付款）','subtotal':s['transfer_quote']},{'name':'已证实可替代资产扣减（未获清单按零）','subtotal':-s['transfer_bundle_credit']}]
  elif key=='lease_deposit':
   x['items']=[{'name':'租金×假设押金月数','qty':market['deposit_months'],'unit_price':market['rent'],'subtotal':s[key]}]
  elif key=='platform_deposit':
   x['items']=[{'name':CHANNELS[ch]+'保证金预算','subtotal':INPUT['platform'][ch][s['scenario']][tier]['deposit']} for ch in ('meituan','taobao')]
  elif key=='reserve':
   x['items']=[{'name':'首月固定支出×3（仅留账，不是费用）','unit_price':s['reserve']/3,'qty':3,'subtotal':s[key]}]
  if 'items' in x:eq(sum(d['subtotal'] for d in x['items']),x['amount'],mode+' '+key)
  cats.append(x)
 eq(sum(c['amount'] for c in cats if c['key']!='reserve'),s['initial_opening_outlay'],mode+' opening spend')
 eq(sum(c['amount'] for c in cats),s['initial_funding'],mode+' starting total')
 return {'area':s['area_m2'],'monthly_rent':market['rent'],'deposit_months':market['deposit_months'],
         'transfer_budget':s['transfer'],'transfer_listed_budget':s['transfer_quote'],
         'transfer_credit':s['transfer_bundle_credit'],'start_spent_or_tied':s['initial_opening_outlay'],
         'account_reserve':s['reserve'],'initial_funding':s['initial_funding'],'initial_each_50_50':s['initial_funding']/2,
         'ref_listings':[MR[x] for x in market['source_ids'] if x in MR],'setup_context':cost['setup_context'],
         'evidence_status':cost['evidence_status'],'categories':cats,
         'note':'所有金额为条件预算；刊登租金/转让不是成交，需核实用途和是否含可回用设备、装修、押金。实际签合同前更新。'}
def unit_trace(mode,row,c):
 u=U[(mode,'base','base',c)]
 units={'list_ticket':u['list_ticket'],'discount':u['discount'],'refund':u['refund'],'revenue':u['revenue'],
    'food_sold':u['sold_food'],'food_waste':u['food_waste'],'food_cost':u['food_cost'],'packaging':u['packaging'],
    'platform_fee':u['platform_fee'],'delivery_fee':u['delivery_fee'],'payment_fee':u['payment_fee'],'host_fee':u['host_fee'],'tax_budget':u['tax_budget'],
    'settlement':u['settlement'],'settlement_days':u['settlement_days'],'contribution':u['contribution']}
 eq(u['list_ticket']-u['discount']-u['refund'],u['revenue'],mode+' '+c+' unit net')
 eq(u['revenue']-sum(u[k] for k in ('food_cost','packaging','platform_fee','delivery_fee','payment_fee','host_fee','tax_budget')),u['contribution'],mode+' '+c+' unit contribution')
 q=row[c+'_orders']; out={'key':c,'label':CHANNELS[c],'daily_orders':q/row['days'],'orders_month':q,'unit':units,'monthly_list_value':q*u['list_ticket'],'monthly_revenue':q*u['revenue'],'monthly_contribution':q*u['contribution']}
 eq(out['monthly_revenue'],row[c+'_revenue_total'],mode+' '+c+' monthly')
 return out
def day_capacity(mode,row):
 l=INPUT['labor'][mode]['base']; meta=MODE_META[mode]
 c=INPUT['startup'][mode]['base']
 # Peak applies to shared total order pool; labor work requirement per order
 # is weighted by desired mix, and all channels constrained proportionally.
 blended=(row['work_demand_person_min']/row['desired_total_daily'])
 peak_capacity=row['peak_person_min']/(l['peak_share']*blended)
 service_capacity=row['available_person_min']/blended
 equipo=row['equipment_capacity_day']
 eq(min(row['desired_total_daily'],peak_capacity,service_capacity,equipo),row['realized_daily'],mode+' capacity')
 n=row['paid_staff']; peaks=l['peak_minutes']
 return {'partner_count':2,'partner_salary':0,'role1':meta['role1'],'role2':meta['role2'],
  'partner_daily_hours_each':l['partner_daily_hours'],'partner_month_hours_each':row['partner_total_hours_month']/2,
  'both_daily_hours':2*l['partner_daily_hours'],'daily_fixed_chores_breaks_both_min':LABOR['modes'][mode]['fixed_work_and_breaks_min'],
  'partner_service_min_day':l['available_service_person_min'],'staff_service_add_min_day_each':l['added_staff_service_min_day'],
  'total_service_min_day':row['available_person_min'],'actual_person_min':row['actual_person_min'],
  'onsite_person_min_per_order':l['onsite_person_min_per_order'],'delivery_person_min_per_order':l['delivery_person_min_per_order'],
  'blended_person_min_per_order':blended,'peak_minutes':peaks,'peak_share':l['peak_share'],
  'peak_partner_min':l['peak_partner_person_min'],'peak_total_min':row['peak_person_min'],
  'peak_used_min':row['peak_actual_person_min'],'peak_actual_orders_per_hour':row['realized_daily']*l['peak_share']/(peaks/60),
  'peak_capacity_orders_per_hour':row['peak_person_min']/blended/(peaks/60),
  'day_limit_service_orders':service_capacity,'day_limit_peak_orders':peak_capacity,'day_limit_equipment_orders':equipo,
  'desired_orders':row['desired_total_daily'],'realized_orders':row['realized_daily'],'lost_orders':row['lost_daily_orders'],'bottleneck':row['bottleneck'],
  'paid_staff':n,'loaded_wage_per_staff':row['loaded_wage_per_staff'],'staff_payroll':row['staff_payroll'],
  'technical_risk':meta['risk'],'note':'工作/休息及高峰时长为经营规划假设；不等同实测，不是学校时间。两位老板无工资成本，但每人实际时间投入仍然列示。'}
def month_trace(mode,rows):
 r=rows[11]; prev=rows[10]; days=r['days']
 channels=[unit_trace(mode,r,c) for c in CHANNELS]
 fixed=items(r,FIX_FIELDS); var=items(r,VAR_FIELDS)
 eq(sum(t['monthly_revenue'] for t in channels),r['recognized_revenue'],mode+' revenue channel sum')
 eq(sum(t['monthly_contribution'] for t in channels),r['order_contribution'],mode+' contribution channel sum')
 eq(sum(t['amount'] for t in var),r['recognized_revenue']-r['order_contribution'],mode+' variable sum')
 eq(sum(t['amount'] for t in fixed),r['total_fixed_cost'],mode+' fixed sum')
 steps=[{'key':'recognized_revenue','label':'净销售收入','signed_amount':r['recognized_revenue']}]+[{'key':t['key'],'label':t['label'],'signed_amount':-t['amount']} for t in var+fixed]+[{'key':'staff_change_cost','label':'人事调整支出','signed_amount':-r['staff_change_cost']}]
 eq(sum(t['signed_amount'] for t in steps),r['operating_profit'],mode+' monthly op')
 cf=[{'key':'operating_profit','label':'经营结余','signed_amount':r['operating_profit']},
     {'key':'inventory_change','label':'库存占用变动','signed_amount':-r['inventory_change']},
     {'key':'receivables_change','label':'平台回款占用变动','signed_amount':-r['receivables_change']},
     {'key':'maintenance_capex','label':'维护设备开支','signed_amount':-r['maintenance_capex']}]
 eq(sum(t['signed_amount'] for t in cf),r['business_cashflow'],mode+' cash bridge')
 bal=[{'key':'prev_balance','label':'月初账户现金','signed_amount':prev['retained_cash']},
     {'key':'business_cashflow','label':'当月经营现金流','signed_amount':r['business_cashflow']},
     {'key':'capital_call','label':'追加投入','signed_amount':r['additional_capital']},
     {'key':'distribution','label':'两人已分配','signed_amount':-r['distributed_to_partners']}]
 eq(sum(t['signed_amount'] for t in bal),r['retained_cash'],mode+' cash balance')
 eq(r['recognized_revenue']/days,sum(t['daily_orders']*t['unit']['revenue'] for t in channels),mode+' daily rev')
 daily={'orders':r['realized_daily'],'list_sales':r['order_value_listed']/days,'sales':r['recognized_revenue']/days,'variable_cost':sum(t['amount'] for t in var)/days,
        'contribution':r['order_contribution']/days,'fixed_share':r['total_fixed_cost']/days,
        'staff_change_share':r['staff_change_cost']/days,'operating_profit':r['operating_profit']/days}
 eq(daily['sales']-daily['variable_cost']-daily['fixed_share']-daily['staff_change_share'],daily['operating_profit'],mode+' daily profit')
 return {'month':12,'calendar':r['calendar'],'days':days,'daily':daily,'channel':channels,
   'demand':{'normal_total_daily':r['normal_total_daily'],'addressable_opportunities':r['addressable_opportunities'],'returning_share':r['returning_share'],
     'conversion':r['conversion'],'ramp':r['ramp'],'season':r['season'],'competition':r['competition'],'desired_total_daily':r['desired_total_daily'],'realized_daily':r['realized_daily']},
   'net_sales':r['recognized_revenue'],'order_value_listed':r['order_value_listed'],'merchant_discount':r['discounts'],'refund_allowance':r['refund_allowance'],
   'variable_cost':sum(t['amount'] for t in var),'variable_items':var,'order_contribution':r['order_contribution'],'fixed_items':fixed,
   'fixed_cost':r['total_fixed_cost'],'staff_change_cost':r['staff_change_cost'],'operating_profit':r['operating_profit'],'accounting_profit_approx':r['accounting_profit'],'amortization':r['amortization'],
   'operating_trace':steps,'cash_trace':cf,'cash_flow':r['business_cashflow'],'cash_balance_trace':bal,'retained_cash':r['retained_cash'],
   'required_cash_reserve':r['required_cash_reserve'],'distributed_to_partners':r['distributed_to_partners'],'distribution_per_partner':r['distribution_per_partner'],
   'break_even_order_daily':r['break_even_daily_orders'],'break_even_cash_daily':r['break_even_cash_daily_orders'],'contribution_per_order':r['contribution_per_order'],
   'cash_note':'成熟月 M12 为一月经营示例，不是首年均月结余；全年经过开业爬坡、淡旺季与竞争假设。月结余不是两人已收到的钱。'}
def years(s,rows):
 annual=[]
 for y in (1,2,3):
  d={k:s[f'y{y}_{k}'] for k in ['recognized_revenue','total_orders','operating_profit','accounting_profit','business_cashflow','additional_capital','distributed_to_partners','staff_payroll','avg_monthly_profit','avg_daily_orders','avg_monthly_each_distribution']}
  d['year']=y;d['each_distribution']=d['distributed_to_partners']/2
  seg=rows[(y-1)*12:y*12]
  d['partner_hours_both']=sum(r['partner_total_hours_month'] for r in seg)
  d['partner_hours_each']=d['partner_hours_both']/2
  d['operating_surplus_per_partner_hour']=d['operating_profit']/d['partner_hours_both']
  d['actual_distribution_per_partner_hour']=d['distributed_to_partners']/d['partner_hours_both']
  annual.append(d)
 eq(sum(x['business_cashflow'] for x in annual),s['cumulative_business_cashflow'],s['mode']+' year cum')
 eq(sum(x['distributed_to_partners'] for x in annual),s['cumulative_distributions'],s['mode']+' distribution cum')
 return {'annual':annual,'monthly':[{k:r[k] for k in ('month','calendar','days','realized_daily','recognized_revenue','operating_profit','business_cashflow','cumulative_business_cashflow','distributed_to_partners','cumulative_distributions','retained_cash','additional_capital','paid_staff')} for r in rows],
   'starting_funding':s['initial_funding'],'all_funding_with_calls':s['total_funding_with_calls'],
   'additional_capital':s['total_capital_calls'],'cash_36':s['cash_balance_m36'],'business_cashflow_36':s['cumulative_business_cashflow'],
   'total_distribution':s['cumulative_distributions'],'each_distribution':s['partner_distribution_each'],'invested_each':s['total_funding_with_calls']/2,
   'deployed_recovery_month':s['capital_recovery_month'],'all_funding_recovery_month':s['all_funding_recovery_month'],
   'first_cash_gap':s['cash_shortfall_month'],'max_paid_staff':s['staff_max'],
   'total_partner_hours_each':sum(r['partner_total_hours_month'] for r in rows)/2,
   'distribution_per_partner_hour_36':s['cumulative_distributions']/sum(r['partner_total_hours_month'] for r in rows),
   'note':'累计经营现金流覆盖已支付/占用和覆盖全部筹资是两个不同回收口径；都不等同把钱已分回个人。正现金余额非盈利保证。'}
def comparisons(mode):
 def pick(t,c,sc): return SC[f'{mode}_{t}_{c}_{sc}']
 def select(s):return {k:s[k] for k in ('tier','strategy','scenario','area_m2','initial_funding','reserve','initial_opening_outlay','y1_avg_monthly_profit','y2_avg_monthly_profit','y3_avg_monthly_profit','m12_realized_daily','m12_break_even_daily_orders','staff_max','cash_shortfall_month','total_capital_calls','capital_recovery_month','all_funding_recovery_month','partner_distribution_each','exit_m6_total_net_investor_loss','exit_m12_total_net_investor_loss','exit_m24_total_net_investor_loss')}
 return {'investment':[select(pick(t,'mixed','base')) for t in ('low','base','high')],
  'channel':[select(pick('base',c,'base')) for c in ('onsite','mixed','delivery_heavy')],
  'demand':[select(pick('base','mixed',sc)) for sc in ('bad','base','good')]}
def exit_trace(e):
 recovery=items(e,[('lease_deposit_recovery','租房押金'),('platform_deposit_recovery','平台保证金'),('equipment_recovery','设备残值'),('stock_recovery','库存回收'),('receivable_recovery','外卖应收'),('transfer_recovery','转让回收'),('fitout_recovery','装修回收')])
 costs=items(e,[('lease_exit_charge','租约/提前退场'),('staff_exit_cost','员工结清预算'),('clearance','清场'),('unsettled_misc','其他未结费用')])
 eq(sum(x['amount'] for x in recovery),e['asset_recovery_total'],e['case_id']+' exit assets')
 eq(sum(x['amount'] for x in costs),e['exit_cost_total'],e['case_id']+' exit costs')
 eq(e['initial_funding']+e['additional_capital_before_exit']+e['net_exit_payment_needed']-e['cumulative_distributions']-e['returned_cash_at_exit'],e['total_net_investor_loss'],e['case_id']+' investor loss')
 eq(max(0,e['exit_cost_total']-e['remaining_cash']-e['asset_recovery_total']),e['net_exit_payment_needed'],e['case_id']+' exit new')
 return {**e,'recovery_items':recovery,'exit_cost_items':costs,
  'day_trace':[{'label':'店内可用现金','signed_amount':e['remaining_cash']},{'label':'回收资产','signed_amount':e['asset_recovery_total']},{'label':'退出支出','signed_amount':-e['exit_cost_total']}],
  'loss_trace':[{'label':'原筹资金','signed_amount':e['initial_funding']},{'label':'开业后追加','signed_amount':e['additional_capital_before_exit']},{'label':'退出净再补','signed_amount':e['net_exit_payment_needed']},{'label':'已经分到','signed_amount':-e['cumulative_distributions']},{'label':'关店拿回','signed_amount':-e['returned_cash_at_exit']}]}
def load_engine():
 spec=importlib.util.spec_from_file_location('frozen_v3_readonly',V3/'models/model_v3.py')
 engine=importlib.util.module_from_spec(spec); spec.loader.exec_module(engine)
 return engine
def platform_tests():
 # Model one asymmetric platform's incremental fee. No claim that either
 # company is currently more expensive. Same demand split and other terms.
 e=load_engine(); results=[]
 for mode in S:
  base=S[mode]
  for channel in ('meituan','taobao'):
   for field,delta,label in [('delivery_cost',2,'该平台每单商家配送多2元'),('commission_rate',.03,'该平台技术费用多3个百分点'),('merchant_discount_rate',.05,'该平台商家优惠多5个百分点')]:
    obj=e.DELIVERY_RAW['platforms'][channel][field]
    orig=obj['base'];obj['base']=orig+delta
    try:
     rows,s,exits=e.simulate(mode,'base','mixed','base')
    finally:obj['base']=orig
    results.append({'mode':mode,'channel':channel,'condition':label,'field':field,'test_delta':delta,'initial_funding':s['initial_funding'],'y1_avg_monthly_profit':s['y1_avg_monthly_profit'],
      'y1_delta':s['y1_avg_monthly_profit']-base['y1_avg_monthly_profit'],'m12_operating_profit':rows[11]['operating_profit'],'m12_delta':rows[11]['operating_profit']-M[mode][11]['operating_profit'],
      'm12_daily_orders':rows[11]['realized_daily'],'capital_recovery_month':s['capital_recovery_month'],'extra_capital':s['total_capital_calls'],'m6_exit_loss':s['exit_m6_total_net_investor_loss']})
 return results

def conditional_tests():
 """New, evidence-linked what-ifs. Time/demand/actual quote not inferred."""
 e=load_engine(); results=[]
 cases=[
  dict(key='A_rent_32m_7mo',mode='A',label='32㎡米粉转让租期7个月（挂牌例）',rent=3040,transfer=42000,lease_months=7,listed_area=32,
   source='https://m.shangpu5.com/zhuanrang/show-16522.html',
   evidence='卖方广告：3040元/月，转让4.2万元，剩7个月（刊登时点不明）。并非签约、不能承诺当前剩7个月。',
   hypothesis='仅以披露租金与转让费替换A标准两项，其余按A的30㎡条件；装修设备重叠未证实，不减；到期不续另试。'),
  dict(key='A_rent_25m_12mo',mode='A',label='25㎡工业园早餐铺（挂牌例）',rent=2800,transfer=48000,lease_months=12,listed_area=25,
   source='https://m.shangpu5.com/zhuanrang/show-11195.html',
   evidence='卖方广告：新福工业园早餐店，2800元/月、4.8万元转让，剩12个月，称设备齐全。',
   hypothesis='仅替换A标准租金与转让费，非25㎡铺的完整真实预算；需核对设备/装修清单，未核不扣，另算可确证重叠。'),
  dict(key='A_rent_25m_reuse_20k',mode='A',label='25㎡挂牌＋核实2万可复用（假设）',rent=2800,transfer=48000,transfer_credit=20000,lease_months=12,listed_area=25,
   source='https://m.shangpu5.com/zhuanrang/show-11195.html',
   evidence='同一挂牌卖方称设备齐；并未取得价值清单。',
   hypothesis='若现场证实转让款内含能替代新购的2万元资产，用净进场费扣除避免双算。设备实况与残值仍须再估；仅算术敏感性。'),
  dict(key='A_full_exhaust_low',mode='A',label='排烟若需全换：8千元报价',fitout_delta=3000,
   source='https://www.zgtlhb.com/news/qyxw/61622.html',
   evidence='供应商商业文章（正文2026-05）50㎡以下排烟设备+安装8,000–12,000元广告，与A标准既有系统局部轻改5,000不完全同工序。',
   hypothesis='如现场拿到8千元同规格全换报价，以8千替换原5千（非重复加）；仅改变装修支出3000；物业允许与许可成立前提。'),
  dict(key='A_full_exhaust_high',mode='A',label='排烟若需全换：1.2万元报价',fitout_delta=7000,
   source='https://www.zgtlhb.com/news/qyxw/61622.html',
   evidence='同一供应商商业广告范围上沿，不是新和成交施工价。',
   hypothesis='若取得同规格1.2万元实际报价，替换原5千排烟，不重复计；只变装修7000。不得以增加预算代替物业/消防/排烟是否合法判断。'),
  dict(key='D_rent_76m_24mo',mode='D',label='76㎡园区快餐铺（挂牌例）',rent=5985,transfer=12000,lease_months=24,listed_area=76,
   source='https://www.shangpu5.com/zhuanrang/show-16371.html',
   evidence='福园一路76㎡快餐卖方广告：5985元/月，1.2万元转让，剩24个月，广告时点未知。',
   hypothesis='仅替换D标准70㎡的租金与转让费，其余经营、购置、人员与需求不变，不宣称此铺总资金；租期不续另试。'),
  dict(key='D_canteen_price_14',mode='D',label='食堂替代压力：现场客单压到14元',price=14,
   source='https://static.nfnews.com/content/202505/08/c11268879.html?enterColumnId=13298',
   evidence='2025-05-08 福海机器人科技园食堂报道一荤一素10元等、2荤12元、3荤14元，是其他消费选择非新和店成交价。',
   hypothesis='若D全时段现场平均客单从16降到14，食材原绝对成本不变，成交量/外卖仍同基准；不是由食堂直接证明的降价。'),
  dict(key='D_canteen_price_12',mode='D',label='食堂替代压力：现场客单压到12元',price=12,
   source='https://static.nfnews.com/content/202505/08/c11268879.html?enterColumnId=13298',
   evidence='同一食堂价格证据，非新和外部消费价。',
   hypothesis='若D现场加权客单降至12元，食材原绝对成本不变，成交量/外卖同基准；不代表所有午餐必需降价。'),
  dict(key='D_canteen_demand_minus20',mode='D',label='食堂替代：潜在订单少20%',volume_factor=.8,
   source='https://static.nfnews.com/content/202505/08/c11268879.html?enterColumnId=13298',
   evidence='园区食堂为可替代供给，替代幅度未测。',
   hypothesis='假设整体潜在订单少20%、原客单不变；20%是压力刻度，不是实测份额。'),
  dict(key='E_occupancy_7000',mode='E',label='共享场地负担升至7000元/月',rent=7000,
   source='https://finance.sina.com.cn/tech/roll/2024-11-07/doc-incvfpzf7705577.shtml',
   evidence='2024深圳民治非新和案例：主租13000元/月，午晚分租6000元，早餐主租实际负担7000元另有人力。',
   hypothesis='E固定场地成本从3000升至7000的单因素测试，其余分成/人员/需求不变；并非该主租案例完整账。合法独立许可、场地协议是前提。'),
  dict(key='E_partner_leaves_13000',mode='E',label='若承担整租13000元/月',rent=13000,
   source='https://finance.sina.com.cn/tech/roll/2024-11-07/doc-incvfpzf7705577.shtml',
   evidence='同一非新和深圳案例整租13000；南山分租户退场使共同租赁遇风险。',
   hypothesis='只针对需承担整租责任的极端情形（非所有共享租客），固定场地费压力；仍保留基准分成，属保守单项假设。')
 ]
 for d in cases:
  mode=d['mode']; orig_m=deepcopy(e.MARKET_RAW['modes'][mode]); orig_u=deepcopy(e.DELIVERY_RAW['modes'][mode]); orig_cost=deepcopy(e.COST_RAW[mode]['base'])
  mr=e.MARKET_RAW['modes'][mode]; ur=e.DELIVERY_RAW['modes'][mode]
  try:
   for key in ('rent','transfer'):
    if key in d:mr[key]['base']=d[key]
   if 'transfer_credit' in d:mr['transfer_bundle_credit']={'base':d['transfer_credit']}
   if 'fitout_delta' in d:e.COST_RAW[mode]['base']['fitout']+=d['fitout_delta']
   if 'price' in d:
    # Independent price probe: preserve absolute food cost, unlike repricing food ratio.
    old_price=e.get_market(mode,'base')['onsite_price'];old_rate=e.get_unit_inputs(mode)['onsite_food_rate']
    old_food=e.unit(mode,'base','base',0,'onsite')['food_cost']
    mr['offline_ticket_cny']['base']=d['price'];ur['onsite_food_rate']=old_rate*old_price/d['price']
    eq(e.unit(mode,'base','base',0,'onsite')['food_cost'],old_food,d['key']+' price only food hold')
   if 'volume_factor' in d:mr['mature_orders_day']['base']*=d['volume_factor']
   rows,s,ex=e.simulate(mode,'base','mixed','base')
   base=S[mode]; r12=rows[11]
   result={**d,'initial_funding':s['initial_funding'],'opening_spent':s['initial_opening_outlay'],'reserve':s['reserve'],
    'base_funding':base['initial_funding'],'funding_delta':s['initial_funding']-base['initial_funding'],
    'y1_avg_profit':s['y1_avg_monthly_profit'],'base_y1_avg_profit':base['y1_avg_monthly_profit'],
    'y1_avg_profit_delta':s['y1_avg_monthly_profit']-base['y1_avg_monthly_profit'],
    'm12_net_sales':r12['recognized_revenue'],'m12_profit':r12['operating_profit'],'m12_day_orders':r12['realized_daily'],
    'm12_break_even_daily':r12['break_even_daily_orders'],'m12_on_list_ticket':r12['onsite_list_ticket_per_order'],
    'm12_on_food_cost':r12['onsite_food_cost_per_order'],'m12_on_contribution':r12['onsite_contribution_per_order'],
    'cumulative_cashflow36_if_terms_renewed':s['cumulative_business_cashflow'],
    'capital_recovery_month_if_renewed':s['capital_recovery_month'],'all_funding_recovery_month_if_renewed':s['all_funding_recovery_month'],
    'extra_capital_if_continued':s['total_capital_calls'],'m6_loss':s['exit_m6_total_net_investor_loss'],
    'm6_loss_delta':s['exit_m6_total_net_investor_loss']-base['exit_m6_total_net_investor_loss'],'staff_max':s['staff_max']}
   if 'lease_months' in d:
    n=d['lease_months']; x=e.exit_calc(e.start_cost(mode,'base','mixed','base'),rows[n-1],'base')
    # If lease genuinely ends (not early departure), show no early-termination-rent
    # conditional variant. Other costs/residual rates still hypotheses.
    no_penalty_cost=x['exit_cost_total']-x['lease_exit_charge']; rec=x['asset_recovery_total']; cash=x['remaining_cash']
    net=max(0,no_penalty_cost-cash-rec); back=max(0,cash+rec-no_penalty_cost)
    loss=x['initial_funding']+x['additional_capital_before_exit']+net-x['cumulative_distributions']-back
    eq(loss,x['total_net_investor_loss']-x['lease_exit_charge'],d['key']+' no early termination loss')
    result['lease_end']={'month':n,'lease_remaining_at_post':n,'net_transfer_month_equivalent':s['transfer']/n,
     'business_cashflow_cumulative':rows[n-1]['cumulative_business_cashflow'],'loss_base_early_charge':x['total_net_investor_loss'],
     'exit_day_net_add_if_no_early_charge':net,'exit_day_bridge_if_no_early_charge':max(0,no_penalty_cost-cash),
     'exit_loss_if_no_early_charge':loss,'exit_returns_if_no_early_charge':back,
     'recovered_assets':rec,'closing_cost_no_early_charge':no_penalty_cost,
     'note':'假设可经营至挂牌当时剩余租期末；若真实到期退出无提前退租项，其他清场及回收仍用基准估值。无续签证据不能把36月条件当真实。'}
   results.append(result)
  finally:
   e.MARKET_RAW['modes'][mode]=orig_m; e.DELIVERY_RAW['modes'][mode]=orig_u; e.COST_RAW[mode]['base']=orig_cost
 return results


def corrected_sensitivity():
 """Correct one V3 one-factor label/calculation; canonical 135 unchanged."""
 engine=load_engine(); result=[]; fixes=[]
 for row in BASE['sensitivity']:
  x=deepcopy(row); mode=x['mode']
  if row['test']=='线下售价低10%':
   mr=engine.MARKET_RAW['modes'][mode];ur=engine.DELIVERY_RAW['modes'][mode]
   old=mr['offline_ticket_cny']['base'];price0=engine.get_market(mode,'base')['onsite_price'];rate=engine.get_unit_inputs(mode)['onsite_food_rate']
   prev_rate=ur.get('onsite_food_rate');present='onsite_food_rate' in ur
   old_food=engine.unit(mode,'base','base',0,'onsite')['food_cost']
   try:
    mr['offline_ticket_cny']['base']=old*.9;ur['onsite_food_rate']=rate/.9
    eq(engine.unit(mode,'base','base',0,'onsite')['food_cost'],old_food,mode+' corrected price food hold')
    _,sim,_=engine.simulate(mode,'base','mixed','base')
   finally:
    mr['offline_ticket_cny']['base']=old
    if present:ur['onsite_food_rate']=prev_rate
    else:ur.pop('onsite_food_rate',None)
   x=engine.sens_result(mode,'线下售价低10%（原食材绝对成本不变）',sim,S[mode])
   fixes.append({'mode':mode,'old_label':row['test'],'new_label':x['test'],'old_y1_monthly_profit':row['y1_monthly_profit'],'new_y1_monthly_profit':x['y1_monthly_profit'],'old_y1_delta':row['y1_monthly_profit_delta'],'new_y1_delta':x['y1_monthly_profit_delta'],'canonical_baseline_changed':False,'reason':'旧版单因素修改基准客单时无意联动按基准价计算的食材原成本；新版固定绝对原成本。'})
  if row['test']=='另发掘20%线上增量且线下无流失':
   x['test']='潜在总订单加20%（均为线上，线下不减少）'
  result.append(x)
 return result,fixes

def write_reader_csv(out):
 for key,name in [('conditional_tests','conditional_finance_v4.csv'),('platform_asymmetry_tests','platform_asymmetry_v4.csv'),('sensitivity','sensitivity_v4.csv'),('sensitivity_corrections','sensitivity_corrections_v4.csv')]:
  rows=[]
  for r in out[key]:
   flat={}
   for k,v in r.items():
    if isinstance(v,dict):
     for k0,v0 in v.items():flat[k+'_'+k0]=v0
    else:flat[k]=v
   rows.append(flat)
  fields=list(dict.fromkeys(k for r in rows for k in r))
  with (P/name).open('w',encoding='utf-8-sig',newline='') as f:
   w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
   w.writerows([{k:round(v,5) if isinstance(v,float) else v for k,v in r.items()} for r in rows])
def main():
 reader={}
 for mode,s in S.items():
  r=M[mode][11]
  reader[mode]={'mode':mode,'mode_name':MODE_META[mode]['name'],'case_id':s['case_id'],
   'opening':opening(mode,s),'capacity':day_capacity(mode,r),'month12':month_trace(mode,M[mode]),'years':years(s,M[mode]),
   'exit':[exit_trace(e) for e in X[mode]],'comparisons':comparisons(mode),
   'weak_exits':[exit_trace(e) for e in BASE['all_exits'] if e['case_id']==mode+'_base_mixed_bad'],
   'skilled_special_cases':[m for m in json.loads((V3/'models/skilled_cook_sensitivity_v3.json').read_text()) if mode=='D']}
 sensitivities,fixes=corrected_sensitivity()
 out={**BASE,'sensitivity':sensitivities,'sensitivity_corrections':fixes,'reader':reader,'platform_asymmetry_tests':platform_tests(),'conditional_tests':conditional_tests(),'v4_meta':{'state':'Verified V3 computational baseline retained; new local evidence separately reviewed; not measured actual local sales or merchant terms','method':'reader causal extraction, asymmetric platform sensitivity and evidence-linked property/price/occupancy condition tests','base_case':'base investment, mixed 75% offline/25% delivery, base market; 50/50 owners illustrative','source_report_sha256':sha(RD),'source_model_sha256':sha(V3/'models/model_v3.py'),
 'input_sha256':{x:sha(V3/'evidence'/x) for x in ('startup_costs.json','labor_capacity.json','market_assumptions.json','delivery_params.json')},'validation_assertions_reader':count}}
 out['v4_meta']['validation_assertions_reader']=count
 # Optional evidence decision ledger is included in final reported metadata.
 for f,key in [(V4/'evidence/finance_evidence_decisions.json','evidence_decisions'),(V4/'evidence/delivery_v4.json','delivery_evidence')]:
  if f.exists():out['v4_meta'][key]=json.loads(f.read_text())
 OUT.write_text(json.dumps(out,ensure_ascii=False),encoding='utf-8')
 write_reader_csv(out)
 # Friendly small extract for report composition: only 5 modes and common notes.
 (P/'reader_finance_v4.json').write_text(json.dumps({'reader':reader,'sensitivity':out['sensitivity'],'sensitivity_corrections':out['sensitivity_corrections'],'platform_asymmetry_tests':out['platform_asymmetry_tests'],'conditional_tests':out['conditional_tests'],'meta':out['v4_meta']},ensure_ascii=False,indent=2),encoding='utf-8')
 (P/'FINANCE_VALIDATION_V4.txt').write_text(f'PASS; {count} causal identity checks. All baseline counts: {len(BASE["summary"])} configurations, {len(BASE["monthly_compact"])} monthly rows, {len(BASE["all_exits"])} exits. 30 asymmetric platform fee sensitivity experiments, 11 evidence-linked conditional tests. 5 price sensitivity rows corrected with absolute ingredient cost fixed. V3 report SHA256 {sha(RD)}; no V3 files changed.\n',encoding='utf-8')
 print('PASS',count,'reader checks',len(out['reader']),'modes',len(out['platform_asymmetry_tests']),'platform tests')
if __name__=='__main__':main()
