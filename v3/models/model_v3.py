#!/usr/bin/env python3
"""Shenzhen Eat V3, auditable 36-month scenario model (RMB).
Models inputs as scenarios, not observations/forecasts. All money RMB.
No partners' salaries. Two partners, paid staff selected quarterly subject to capacity.
Standard library Python 3; optional openpyxl output.
"""
import calendar, csv, json, math, statistics, hashlib
from pathlib import Path
from itertools import product
from copy import deepcopy
P=Path(__file__).resolve().parent
E=P.parent/'evidence'
SCENARIOS=('bad','base','good')
TIERS=('low','base','high')
CHANNELS=('onsite','mixed','delivery_heavy')
MONTHS=36
EXIT_MONTHS=(3,6,12,24)
START_YEAR=2027
MODES={'A':'传统早餐','B':'特色便携早餐','C':'早餐＋零食','D':'多时段餐饮','E':'分时合作/店中店'}
TAX_ALLOWANCE=.015  # Budget only; no statutory tax claim.
MAINT_RATE=.008
POST_RESERVE_MONTHS=3
# Models are explicitly assumptions; actual local conversion / footfall unavailable.
DEFAULT_MARKET={
 'A':dict(rent=[3000,5000,8500],transfer=[0,42000,110000],expo=1800,conversion=.105,onsite_price=8.5,school_share=.48),
 'B':dict(rent=[2800,4500,7500],transfer=[0,42000,100000],expo=1500,conversion=.10,onsite_price=11.5,school_share=.42),
 'C':dict(rent=[4000,6500,10000],transfer=[0,60000,120000],expo=1900,conversion=.105,onsite_price=9.3,school_share=.36),
 'D':dict(rent=[6500,10000,16000],transfer=[0,100000,155000],expo=2600,conversion=.09,onsite_price=13.5,school_share=.23),
 'E':dict(rent=[1500,3000,5000],transfer=[0,0,0],expo=1250,conversion=.10,onsite_price=8.0,school_share=.42),
}
# Fallbacks only, overwritten by v3/evidence JSON if agents return documented values.
DEFAULT_SIZE={'A':[20,30,40],'B':[18,28,38],'C':[30,45,60],'D':[45,70,95],'E':[8,12,20]}
DEFAULT_EQUIP_CAP={'A':[260,390,550],'B':[220,360,500],'C':[280,420,550],'D':[220,420,600],'E':[160,250,340]}
DEFAULT_COST={
 'A':[[14000,18000,2500,3500],[30000,28000,4500,5000],[60000,48000,7000,8000]],
 'B':[[13000,17000,2500,3500],[28000,24000,4500,5000],[57000,43000,6500,8000]],
 'C':[[24000,23000,5000,4000],[49000,35000,8000,7000],[90000,65000,13000,11000]],
 'D':[[40000,38000,5500,6000],[91000,62000,9000,10000],[150000,102000,16000,16000]],
 'E':[[3000,5000,1800,2000],[6000,12000,2500,3000],[15000,23000,5000,5500]],
}
DEFAULT_LABOR={
 # All service minutes net of prep/cleanup/rest: two partner roster.
 # Peak resource constraint is independent of all-day throughput and equipment.
 'A':dict(open_days_30=26,partner_daily_hours=8.0,available_service_person_min=520,onsite_person_min_per_order=2.4,delivery_person_min_per_order=3.2,added_staff_service_min_day=285,peak_minutes=150,peak_share=.68,peak_partner_person_min=240,peak_staff_person_min=90,min_staff=0,max_staff=[1,2,3]),
 'B':dict(open_days_30=26,partner_daily_hours=8.0,available_service_person_min=500,onsite_person_min_per_order=2.6,delivery_person_min_per_order=3.4,added_staff_service_min_day=285,peak_minutes=150,peak_share=.60,peak_partner_person_min=235,peak_staff_person_min=90,min_staff=0,max_staff=[1,2,3]),
 'C':dict(open_days_30=26,partner_daily_hours=8.5,available_service_person_min=610,onsite_person_min_per_order=2.4,delivery_person_min_per_order=3.1,added_staff_service_min_day=285,peak_minutes=180,peak_share=.55,peak_partner_person_min=285,peak_staff_person_min=110,min_staff=0,max_staff=[1,2,3]),
 'D':dict(open_days_30=26,partner_daily_hours=9.0,available_service_person_min=650,onsite_person_min_per_order=3.1,delivery_person_min_per_order=3.9,added_staff_service_min_day=285,peak_minutes=300,peak_share=.60,peak_partner_person_min=340,peak_staff_person_min=140,min_staff=0,max_staff=[2,4,5]),
 'E':dict(open_days_30=26,partner_daily_hours=6.5,available_service_person_min=425,onsite_person_min_per_order=2.5,delivery_person_min_per_order=3.3,added_staff_service_min_day=270,peak_minutes=120,peak_share=.65,peak_partner_person_min=210,peak_staff_person_min=75,min_staff=0,max_staff=[1,1,2]),
}
# Market scenario assumptions explicitly distinct from initial investment tier.
MARKET_SCENARIOS={
 'bad':dict(demand=.70,price=.96,ingredient=1.08,waste=1.22,wage=1.08,rent_growth=.05,price_growth=0,input_growth=.04,other_growth=.035,wage_growth=.05,competition_at=7,competition_loss=.17),
 'base':dict(demand=1,price=1,ingredient=1,waste=1,wage=1,rent_growth=.03,price_growth=.015,input_growth=.025,other_growth=.025,wage_growth=.04,competition_at=19,competition_loss=.07),
 'good':dict(demand=1.27,price=1.04,ingredient=.96,waste=.82,wage=1,rent_growth=.02,price_growth=.02,input_growth=.02,other_growth=.02,wage_growth=.035,competition_at=25,competition_loss=.03)
}
# Channel strategy splits ONE latent demand pool. No automatic incremental online demand.
# Actual online growth is a separately testable opportunity, not assumed here.
CHANNEL_DEMAND={
 'onsite':dict(onsite=1,delivery=0,mt_share=.5,label='仅线下'),
 'mixed':dict(onsite=.75,delivery=.25,mt_share=.5,label='线下＋外卖'),
 'delivery_heavy':dict(onsite=.40,delivery=.60,mt_share=.5,label='外卖占比较高'),
}
# Food sold ratios, spoilage rates and packaging illustrative from menu/cost study.
UNIT_BASE={
 'A':dict(onsite_food_rate=.35,delivery_food_rate=.36,onsite_pack=.35,delivery_pack=.90,delivery_ticket=15,waste=.05,host_rate=0),
 'B':dict(onsite_food_rate=.39,delivery_food_rate=.39,onsite_pack=.65,delivery_pack=1.20,delivery_ticket=19,waste=.07,host_rate=0),
 'C':dict(onsite_food_rate=.46,delivery_food_rate=.45,onsite_pack=.30,delivery_pack=1.00,delivery_ticket=17,waste=.05,host_rate=0),
 'D':dict(onsite_food_rate=.39,delivery_food_rate=.40,onsite_pack=.45,delivery_pack=1.60,delivery_ticket=24,waste=.06,host_rate=0),
 'E':dict(onsite_food_rate=.35,delivery_food_rate=.36,onsite_pack=.35,delivery_pack=.90,delivery_ticket=15,waste=.05,host_rate=.035),
}
PLATFORMS={
 'meituan':dict(commission_rate={'bad':.08,'base':.07,'good':.06},delivery_cost={'bad':5.5,'base':4,'good':2.5},merchant_discount_rate={'bad':.10,'base':.05,'good':.02},refund_rate={'bad':.03,'base':.01,'good':.005},marketing_month={'bad':500,'base':300,'good':200},deposit={'low':0,'base':1000,'high':2000},settlement_days=3),
 'taobao':dict(commission_rate={'bad':.08,'base':.07,'good':.05},delivery_cost={'bad':5.5,'base':4,'good':2.5},merchant_discount_rate={'bad':.10,'base':.05,'good':.02},refund_rate={'bad':.03,'base':.01,'good':.005},marketing_month={'bad':500,'base':300,'good':200},deposit={'low':0,'base':1000,'high':2000},settlement_days=3),
}
WAGES={'low':5800,'base':7200,'high':8800}
# Family-linked seasonal weights (not an observed school schedule) and adult demand.
FAMILY=(.85,.53,1,1,1,.94,.72,.70,1,.97,1,1)
OTHER=(.96,.84,1,1,1,.98,.98,.98,1,.97,1,1)
TIER_DEMAND={'low':.80,'base':1,'high':1.18}  # capture/location proxy, not measured relation.
BASE_INVENTORY_DAYS={'A':3,'B':3,'C':6,'D':4,'E':3}
INPUT_STATUS={}
def read_json(name):
 p=E/name
 if p.exists():
  try:
   x=json.loads(p.read_text()); INPUT_STATUS[name]={'used':True,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()};return x
  except Exception as e:INPUT_STATUS[name]={'used':False,'error':str(e)}
 else:INPUT_STATUS[name]={'used':False,'reason':'not found; explicit fallback retained'}
 return {}
COST_RAW=read_json('startup_costs.json')
LABOR_RAW=read_json('labor_capacity.json')
MARKET_RAW=read_json('market_assumptions.json')
DELIVERY_RAW=read_json('delivery_params.json')
def n(x,default=None):
 if isinstance(x,(int,float)):return float(x)
 if isinstance(x,str):
  try:return float(x.replace(',',''))
  except ValueError:return default
 if isinstance(x,dict):
  for k in ('value','amount','rmb','estimate','base'):
   if k in x and n(x[k]) is not None:return n(x[k])
 return default
def getv(obj,key,default=None):
 return n(obj.get(key),default) if isinstance(obj,dict) else default
def tier_value(v,tier,default=None):
 if isinstance(v,dict):return n(v.get(tier),default)
 if isinstance(v,(list,tuple)) and len(v)>=3:return n(v[TIERS.index(tier)],default)
 return n(v,default)
def scvalue(v,sc,default=None):
 if isinstance(v,dict):return n(v.get(sc),default)
 if isinstance(v,(list,tuple)) and len(v)>=3:return n(v[SCENARIOS.index(sc)],default)
 return n(v,default)
def mroot(raw):return raw.get('modes',raw) if isinstance(raw,dict) else {}
def get_market(mode,tier):
 m=deepcopy(DEFAULT_MARKET[mode]); r=mroot(MARKET_RAW).get(mode,{})
 m['rent']=tier_value(r.get('rent',r.get('rent_monthly',m['rent'])),tier,m['rent'][TIERS.index(tier)])
 m['transfer_quote']=tier_value(r.get('transfer',m['transfer']),tier,m['transfer'][TIERS.index(tier)])
 m['transfer_bundle_credit']=tier_value(r.get('transfer_bundle_credit',0),tier,0)
 m['transfer']=max(0,m['transfer_quote']-m['transfer_bundle_credit'])
 m['deposit_months']=tier_value(r.get('deposit_months',[1,2,3]),tier,[1,2,3][TIERS.index(tier)])
 m['expo']=getv(r,'reference_exposures_per_day',getv(r,'expo',m['expo']))
 m['conversion']=getv(r,'base_combined_conversion',getv(r,'conversion',m['conversion']))
 m['onsite_price']=tier_value(r.get('offline_ticket_cny',r.get('onsite_price',m['onsite_price'])),'base',m['onsite_price'])
 m['onsite_price_scenario']={sc:tier_value(r.get('offline_ticket_cny',{}),t,m['onsite_price']*MARKET_SCENARIOS[sc]['price']) for sc,t in zip(SCENARIOS,TIERS)}
 m['mature_orders_scenario']={sc:tier_value(r.get('mature_orders_day',{}),t,m['expo']*m['conversion']*MARKET_SCENARIOS[sc]['demand']) for sc,t in zip(SCENARIOS,TIERS)}
 m['source_ids']=r.get('comparable_source_ids',[])
 m['school_share']=getv(r,'school_share',m['school_share'])
 if getv(r,'mature_onsite_orders_day') is not None:
  m['conversion']=getv(r,'mature_onsite_orders_day')/m['expo']
 return m
def get_cost(mode,tier):
 k=TIERS.index(tier); x=DEFAULT_COST[mode][k]
 defaults=dict(area_m2=DEFAULT_SIZE[mode][k],fitout=x[0],equipment=x[1],opening_inventory=x[2],preopening=x[3],
    delivery_setup=2000+1000*k,property_fee=[350,700,1200][k] if mode!='E' else [150,300,500][k],
    utilities_fixed={'A':[700,1000,1500],'B':[550,850,1200],'C':[850,1450,2200],'D':[1500,2400,3800],'E':[250,450,750]}[mode][k],
    other_fixed=[500,850,1300][k],marketing_fixed=[250,400,650][k],equipment_capacity_day=DEFAULT_EQUIP_CAP[mode][k],equipment_items=[])
 root=mroot(COST_RAW).get(mode,{})
 c=root.get(tier,{}) if isinstance(root,dict) else {}
 for key,d in defaults.items():
  if key=='equipment_items':
   defaults[key]=c.get(key,d)
  else:defaults[key]=getv(c,key,d)
 return defaults
def get_labor(mode,tier):
 d=deepcopy(DEFAULT_LABOR[mode]); r=mroot(LABOR_RAW).get(mode,{})
 for k,v in d.items():
  if k=='max_staff': d[k]=int(tier_value(r.get(k,v),tier,v[TIERS.index(tier)]))
  else:d[k]=tier_value(r.get(k),tier,v)
 d['max_staff']=max(int(d['min_staff']),d['max_staff'])
 d['min_staff']=int(d['min_staff'])
 return d
def wage(tier,sc,year):
 obj=LABOR_RAW.get('wages',LABOR_RAW.get('loaded_wages',{}))
 # Gross remuneration incl employer burdens, not partners.
 v=tier_value(obj,tier,WAGES[tier])
 return v*MARKET_SCENARIOS[sc]['wage']*(1+MARKET_SCENARIOS[sc]['wage_growth'])**year
def get_platform(p,sc,tier):
 r=DELIVERY_RAW.get('platforms',{}).get(p,{})
 d=PLATFORMS[p].copy()
 out={}
 for k,v in d.items():
  if k=='deposit':out[k]=scvalue(r.get(k,v),sc,tier_value(v,tier,0))
  else:out[k]=scvalue(r.get(k,v),sc,scvalue(v,sc))
 return out
def get_unit_inputs(mode):
 d=UNIT_BASE[mode].copy()
 r=mroot(DELIVERY_RAW).get(mode,{})
 for k,v in d.items():
  d[k]=getv(r,k,v)
 d['delivery_pack']=getv(r,'delivery_packaging',d['delivery_pack'])
 d['delivery_food_rate']=getv(r,'food_cost_rate',d['delivery_food_rate'])
 return d
def unit(mode,market_sc,tier,year,channel):
 s=MARKET_SCENARIOS[market_sc]; u=get_unit_inputs(mode); m=get_market(mode,tier)
 onsite=channel=='onsite'
 ticket0=m['onsite_price'] if onsite else u['delivery_ticket']
 ticket=(m['onsite_price_scenario'][market_sc] if onsite else ticket0*s['price'])*(1+s['price_growth'])**year
 # Onsite raw ratio excludes spoilage; delivery research ratio includes normal spoilage.
 food=ticket0*(u['onsite_food_rate'] if onsite else u['delivery_food_rate']*(1-u['waste']))*s['ingredient']*(1+s['input_growth'])**year
 waste_rate=min(.30,u['waste']*s['waste']); food_consumption=food/(1-waste_rate)
 packaging=(u['onsite_pack'] if onsite else u['delivery_pack'])*(1+s['other_growth'])**year
 if onsite:
  discount=refund=tech=logistic=0;gross_receipt=ticket;payfee=ticket*.006
  settlement_days=0
 else:
  p=get_platform(channel,market_sc,tier)
  discount=ticket*p['merchant_discount_rate']
  refund=(ticket-discount)*p['refund_rate']
  gross_receipt=ticket-discount-refund
  tech=(ticket-discount)*p['commission_rate'] # conservative: refund fee reversal not assumed
  logistic=p['delivery_cost']*(1+s['other_growth'])**year
  payfee=0 # Included in tech/transaction allowance; no duplicate.
  settlement_days=p['settlement_days']
 host=gross_receipt*u['host_rate']; tax=gross_receipt*TAX_ALLOWANCE
 contrib=gross_receipt-food_consumption-packaging-tech-logistic-payfee-host-tax
 # Net settlement from platform before supplier/physical costs; merchant charge only.
 settlement=gross_receipt-tech-logistic
 return dict(list_ticket=ticket,discount=discount,refund=refund,revenue=gross_receipt,sold_food=food,food_waste=food_consumption-food,
   food_cost=food_consumption,packaging=packaging,platform_fee=tech,delivery_fee=logistic,payment_fee=payfee,
   host_fee=host,tax_budget=tax,settlement=settlement,settlement_days=settlement_days,contribution=contrib)

def daily_desired(mode,tier,strategy,scenario,month):
 m=get_market(mode,tier);s=MARKET_SCENARIOS[scenario];i=(month-1)%12
 # Keep conversion written as disjoint new vs returning exposure. Ramp acts once.
 # Mature returning opportunity 35%; conversion rates scaled to weighted mean.
 rr=.08+.27*(1-math.exp(-(month-1)/4.5))
 sc_conv=m['mature_orders_scenario'][scenario]/m['expo']
 new_conv=sc_conv*.75;ret_conv=sc_conv*(1-.65*.75)/.35
 attr=(1-rr)*new_conv+rr*ret_conv
 ramp=min(1,.58+.07*(month-1))
 comp=(1-s['competition_loss']) if month>=s['competition_at'] else 1
 season=m['school_share']*FAMILY[i]+(1-m['school_share'])*OTHER[i]
 base=m['expo']*attr*TIER_DEMAND[tier]*ramp*season*comp
 c=CHANNEL_DEMAND[strategy]
 # Split total latent demand; incremental channel reach not assumed.
 on=base*c['onsite']; d=base*c['delivery']
 return {'onsite':on,'meituan':d*c['mt_share'],'taobao':d*(1-c['mt_share'])},dict(addressable_opportunities=m['expo']*TIER_DEMAND[tier],returning_share=rr,conversion=attr,ramp=ramp,season=season,competition=comp,normal_total_daily=m['mature_orders_scenario'][scenario]*TIER_DEMAND[tier])
def capacity_solve(mode,tier,desired,staff):
 l=get_labor(mode,tier);c=get_cost(mode,tier)
 t_on=l['onsite_person_min_per_order'];t_off=l['delivery_person_min_per_order']
 req_on=desired['onsite'];req_off=desired['meituan']+desired['taobao']
 req_min=req_on*t_on+req_off*t_off
 total= sum(desired.values())
 day_min=l['available_service_person_min']+staff*l['added_staff_service_min_day']
 peak_min=l['peak_partner_person_min']+staff*l['peak_staff_person_min']
 caps=[('demand',1.0),('person_time',day_min/req_min if req_min>0 else 1),('peak',peak_min/(req_min*l['peak_share']) if req_min>0 else 1),('equipment',c['equipment_capacity_day']/total if total>0 else 1)]
 bind, factor=min(caps,key=lambda a:a[1]);factor=max(0,min(1,factor))
 actual={k:v*factor for k,v in desired.items()}
 return actual,dict(bottleneck=bind,allocation_factor=factor,available_person_min=day_min,peak_person_min=peak_min,equipment_capacity_day=c['equipment_capacity_day'],
  work_demand_person_min=req_min,actual_person_min=sum(actual[k]*(t_on if k=='onsite' else t_off) for k in actual),
  peak_actual_person_min=sum(actual[k]*(t_on if k=='onsite' else t_off) for k in actual)*l['peak_share'])
def open_days(mode,tier,month):
 year=START_YEAR+(month-1)//12;i=(month-1)%12
 return max(1,round(calendar.monthrange(year,i+1)[1]*get_labor(mode,tier)['open_days_30']/30))
def fixed(mode,tier,strategy,sc,month,staff):
 year=(month-1)//12;s=MARKET_SCENARIOS[sc];m=get_market(mode,tier);c=get_cost(mode,tier)
 x=(1+s['other_growth'])**year
 platform_ads=0 if strategy=='onsite' else sum(get_platform(p,sc,tier)['marketing_month'] for p in PLATFORMS)*x
 return dict(rent=m['rent']*(1+s['rent_growth'])**year,property_fee=c['property_fee']*x,utilities_fixed=c['utilities_fixed']*x+staff*120*x,
  other_fixed=c['other_fixed']*x,store_marketing=c['marketing_fixed']*x,platform_marketing=platform_ads,staff_payroll=staff*wage(tier,sc,year),owner_salary=0)
def expected_profit(mode,tier,strategy,sc,month,staff):
 days=open_days(mode,tier,month); desired,_=daily_desired(mode,tier,strategy,sc,month); act,_=capacity_solve(mode,tier,desired,staff);year=(month-1)//12
 contribution=sum(act[k]*unit(mode,sc,tier,year,k)['contribution']*days for k in act)
 return contribution-sum(fixed(mode,tier,strategy,sc,month,staff).values())
def choose_staff(mode,tier,strategy,sc,month,prior):
 # Quarterly review: use prior/current model scenario expectations for upcoming 3 months.
 # Hiring/separation allowance discourages churn; it is a scenario, not legal severance.
 l=get_labor(mode,tier); candidates=range(l['min_staff'],l['max_staff']+1)
 options=[]
 for staff in candidates:
  switch=700*max(0,staff-prior)+1200*max(0,prior-staff) if prior is not None else 700*staff
  expected=sum(expected_profit(mode,tier,strategy,sc,m,staff) for m in range(month,min(37,month+3)))-switch
  options.append((expected,-staff,staff))
 return max(options)[2]
def start_cost(mode,tier,strategy,sc):
 m=get_market(mode,tier);c=get_cost(mode,tier)
 # Non-overlapping: transfer is net location/business entry fee, NOT bundled equipment or fitout.
 setup=(c['delivery_setup'] if strategy!='onsite' else 0)
 platform_dep=sum(get_platform(p,sc,tier)['deposit'] for p in PLATFORMS) if strategy!='onsite' else 0
 first_staff=choose_staff(mode,tier,strategy,sc,1,None)
 f=fixed(mode,tier,strategy,sc,1,first_staff)
 out=dict(fitout=c['fitout'],equipment=c['equipment'],transfer=m['transfer'],preopening=c['preopening'],
    delivery_setup=setup,lease_deposit=m['rent']*m['deposit_months'],platform_deposit=platform_dep,opening_inventory=c['opening_inventory'])
 deployed=sum(out.values());reserve=max(0,POST_RESERVE_MONTHS*sum(f.values()))
 return dict(out,transfer_quote=m['transfer_quote'],transfer_bundle_credit=m['transfer_bundle_credit'],area_m2=c['area_m2'],first_staff=first_staff,initial_opening_outlay=deployed,reserve=reserve,initial_funding=deployed+reserve)
def exit_calc(start,row,sc):
 # Remaining retained cash is net of distributions and capital calls, not an additional source.
 # Liabilities and recovery rates explicitly scenario assumptions, not legal promises.
 m=row['month']; rec_deposit={'bad':.45,'base':.75,'good':.95}[sc]
 rec_eq=max(.10,{'bad':.43,'base':.58,'good':.70}[sc]-m*{'bad':.012,'base':.010,'good':.009}[sc])
 rec_inv={'bad':.30,'base':.50,'good':.70}[sc]
 rec_platform={'bad':.60,'base':.85,'good':1}[sc]
 rec_receiv={'bad':.85,'base':.95,'good':.99}[sc]
 rr=dict(lease_deposit_recovery=start['lease_deposit']*rec_deposit,platform_deposit_recovery=start['platform_deposit']*rec_platform,
    equipment_recovery=start['equipment']*rec_eq,stock_recovery=row['inventory_balance']*rec_inv,receivable_recovery=row['receivables']*rec_receiv,
    transfer_recovery=0,fitout_recovery=0)
 # 1-3 months early termination / notice payments as assumption + employee settlement reserve and clearance.
 settlement=dict(lease_exit_charge=row['rent']*{'bad':3,'base':1,'good':.5}[sc],
    staff_exit_cost=row['staff_payroll']*{'bad':1.5,'base':1,'good':.5}[sc],
    clearance={'bad':4500,'base':2500,'good':1500}[sc],
    unsettled_misc={'bad':1800,'base':1000,'good':500}[sc])
 rec=sum(rr.values());liab=sum(settlement.values())
 cash=row['retained_cash']
 net_extra=max(0,liab-cash-rec) # net permanent extra contribution
 provisional=max(0,liab-cash) # bridge if recovery comes later
 cash_back=max(0,cash+rec-liab)
 loss=start['initial_funding']+row['cumulative_additional_capital']+net_extra-row['cumulative_distributions']-cash_back
 # Independent identity: deployed + operational free cash result, no cash reserve or deficit double counted.
 loss_alt=start['initial_opening_outlay']-row['cumulative_business_cashflow']-rec+liab
 assert abs(loss-loss_alt)<1e-5,(loss,loss_alt)
 return dict(case_id=row['case_id'],mode=row['mode'],tier=row['tier'],strategy=row['strategy'],scenario=sc,exit_month=m,
    initial_funding=start['initial_funding'],initial_opening_outlay=start['initial_opening_outlay'],initial_reserve=start['reserve'],
    additional_capital_before_exit=row['cumulative_additional_capital'],cumulative_distributions=row['cumulative_distributions'],
    cumulative_business_cashflow=row['cumulative_business_cashflow'],remaining_cash=cash,**rr,asset_recovery_total=rec,**settlement,
    exit_cost_total=liab,net_exit_payment_needed=net_extra,exit_day_bridge_before_recovery=provisional,
    returned_cash_at_exit=cash_back,total_net_investor_loss=loss,loss_per_partner=loss/2,
    cash_payment_per_partner=net_extra/2,bridge_per_partner=provisional/2)
def simulate(mode,tier,strategy,sc):
 case=f'{mode}_{tier}_{strategy}_{sc}'
 start=start_cost(mode,tier,strategy,sc)
 inv=start['opening_inventory']; receiv=0; cash=start['reserve'];prior=None
 cum_cf=0;cum_add=0;cum_distribute=0; first_shortfall=None; payback=None; fully_paid=None
 rows=[]; exits=[]
 # For illustrative operating policy, quarterly payout of 50% cash excess over 3 months of fixed costs;
 # no payout after any additional capital call, except exit liquidation. No distribution considered profit.
 for month in range(1,37):
  year=(month-1)//12;days=open_days(mode,tier,month)
  if prior is None or (month-1)%3==0:staff=choose_staff(mode,tier,strategy,sc,month,prior)
  else:staff=prior
  staffing_cost=(700*max(0,staff-(prior or 0))+1200*max(0,(prior or 0)-staff))
  desired,dem=daily_desired(mode,tier,strategy,sc,month);act,cap=capacity_solve(mode,tier,desired,staff)
  order={k:act[k]*days for k in act};units={k:unit(mode,sc,tier,year,k) for k in order}
  sums={key:sum(order[k]*units[k][key] for k in order) for key in units['onsite'] if key!='settlement_days'}
  detail={}
  for k in order:
   detail[k+'_orders']=order[k]
   for ukey in units[k]:
    if ukey!='settlement_days':
     detail[k+'_'+ukey+'_per_order']=units[k][ukey]
     detail[k+'_'+ukey+'_total']=order[k]*units[k][ukey]
  frev=sums['revenue'];contrib=sums['contribution'];fixed_costs=fixed(mode,tier,strategy,sc,month,staff);fix=sum(fixed_costs.values())
  op=contrib-fix-staffing_cost
  # non-cash amortization on net distinct opening assets; legal tax treatment varies.
  dep=start['fitout']/36+start['equipment']/60+start['transfer']/36
  acct=op-dep
  target_inv=(sums['food_cost']+sums['packaging'])/days*BASE_INVENTORY_DAYS[mode]
  inv_change=target_inv-inv; inv=target_inv
  target_receiv=sum(order[k]*max(0,units[k]['settlement'])/days*units[k]['settlement_days'] for k in ['meituan','taobao'])
  rec_change=target_receiv-receiv;receiv=target_receiv
  maint=frev*MAINT_RATE
  fcf=op-inv_change-rec_change-maint;cum_cf+=fcf
  before_call=cash+fcf
  call=max(0,-before_call)
  if call>1e-6 and first_shortfall is None:first_shortfall=month
  cash=before_call+call;cum_add+=call
  reserve_target=POST_RESERVE_MONTHS*fix
  possible_distributable=max(0,cash-reserve_target) if cum_add<1e-6 else 0
  payout=.50*possible_distributable if month%3==0 else 0
  cash-=payout;cum_distribute+=payout
  if payback is None and cum_cf>=start['initial_opening_outlay']:payback=month
  if fully_paid is None and cum_cf>=start['initial_funding']+cum_add:fully_paid=month
  total=sum(order.values()); contribution_per_order=contrib/total if total else 0
  cashcontrib_per_order=(contrib-maint)/total if total else 0
  # Normalized operating/cash contribution BEs use actual realized channel mix and current costs.
  break_even=fix/(contribution_per_order*days) if contribution_per_order>0 else None
  break_even_cash=fix/(cashcontrib_per_order*days) if cashcontrib_per_order>0 else None
  dtotal=sum(desired.values());l=get_labor(mode,tier)
  row=dict(case_id=case,mode=mode,mode_name=MODES[mode],tier=tier,strategy=strategy,scenario=sc,month=month,calendar=f'{START_YEAR+year}-{(month-1)%12+1:02}',days=days,
   paid_staff=staff,partner_count=2,partner_daily_work_hours_each=l['partner_daily_hours'],partner_total_hours_month=2*l['partner_daily_hours']*days,
   loaded_wage_per_staff=wage(tier,sc,year),**dem,**cap,desired_onsite_daily=desired['onsite'],desired_delivery_daily=desired['meituan']+desired['taobao'],
   desired_total_daily=dtotal,realized_daily=total/days,lost_daily_orders=dtotal-total/days,
   actual_onsite_daily=act['onsite'],actual_delivery_daily=act['meituan']+act['taobao'],
   total_orders=total,order_value_listed=sums['list_ticket'],discounts=sums['discount'],refund_allowance=sums['refund'],
   recognized_revenue=frev,food_sold=sums['sold_food'],food_waste=sums['food_waste'],food_consumption=sums['food_cost'],packaging_cost=sums['packaging'],platform_tech_fee=sums['platform_fee'],
   merchant_delivery_cost=sums['delivery_fee'],payment_fee=sums['payment_fee'],host_fee=sums['host_fee'],tax_risk_allowance=sums['tax_budget'],
   channel_net_settlement=sums['settlement'],gross_profit=frev-sums['food_cost'],order_contribution=contrib,contribution_per_order=contribution_per_order,
   **fixed_costs,total_fixed_cost=fix,staff_change_cost=staffing_cost,operating_profit=op,amortization=dep,accounting_profit=acct,
   inventory_balance=inv,inventory_change=inv_change,receivables=receiv,receivables_change=rec_change,maintenance_capex=maint,
   business_cashflow=fcf,cumulative_business_cashflow=cum_cf,balance_before_capital_call=before_call,additional_capital=call,cumulative_additional_capital=cum_add,
   required_cash_reserve=reserve_target,potential_distribution_when_excess=possible_distributable,distributed_to_partners=payout,distribution_per_partner=payout/2,cumulative_distributions=cum_distribute,retained_cash=cash,
   break_even_daily_orders=break_even,break_even_cash_daily_orders=break_even_cash,**detail)
  # Independent identities:
  assert abs(sums['list_ticket']-sums['discount']-sums['refund']-frev)<1e-6
  assert abs(frev-sum(sums[k] for k in ['food_cost','packaging','platform_fee','delivery_fee','payment_fee','host_fee','tax_budget'])-contrib)<1e-6
  assert abs(cash-(start['reserve']+cum_cf+cum_add-cum_distribute))<1e-5
  assert cap['actual_person_min']<=cap['available_person_min']+1e-8
  assert cap['peak_actual_person_min']<=cap['peak_person_min']+1e-8
  assert total/days<=cap['equipment_capacity_day']+1e-8
  assert total/days<=dtotal+1e-8 and row['owner_salary']==0
  assert row['paid_staff']>=l['min_staff']
  assert abs(sum(order.values())-total)<1e-6
  assert cash>=-1e-5
  if month in EXIT_MONTHS:exits.append(exit_calc(start,row,sc))
  rows.append(row);prior=staff
 st=start_cost(mode,tier,strategy,sc)
 sumrow=dict(case_id=case,mode=mode,mode_name=MODES[mode],tier=tier,strategy=strategy,scenario=sc,**st,
  ref_partner_hour_each=get_labor(mode,tier)['partner_daily_hours'],
  cash_shortfall_month=first_shortfall,capital_recovery_month=payback,all_funding_recovery_month=fully_paid,
  staff_min=min(r['paid_staff'] for r in rows),staff_max=max(r['paid_staff'] for r in rows),
  mature_staff_m12=rows[11]['paid_staff'],staff_m24=rows[23]['paid_staff'],
  cumulative_business_cashflow=cum_cf,total_capital_calls=cum_add,total_funding_with_calls=st['initial_funding']+cum_add,
  cumulative_distributions=cum_distribute,partner_distribution_each=cum_distribute/2,cash_balance_m36=cash,
  cash_before_calls_and_distributions_m36=start['reserve']+cum_cf)
 for y in range(1,4):
  seg=rows[(y-1)*12:y*12]
  for k in ('recognized_revenue','total_orders','operating_profit','accounting_profit','business_cashflow','additional_capital','distributed_to_partners','staff_payroll'):
   sumrow[f'y{y}_{k}']=sum(r[k] for r in seg)
  sumrow[f'y{y}_avg_monthly_profit']=sumrow[f'y{y}_operating_profit']/12
  sumrow[f'y{y}_avg_daily_orders']=sum(r['total_orders'] for r in seg)/sum(r['days'] for r in seg)
  sumrow[f'y{y}_avg_monthly_each_distribution']=sumrow[f'y{y}_distributed_to_partners']/12/2
 # Standard mature day: month12 inputs and staff, actual status, not expected forever.
 r=rows[11]
 for k in ['realized_daily','actual_onsite_daily','actual_delivery_daily','desired_total_daily','lost_daily_orders','contribution_per_order','break_even_daily_orders',
           'break_even_cash_daily_orders','total_fixed_cost','bottleneck','available_person_min','peak_person_min','equipment_capacity_day','loaded_wage_per_staff']:
  sumrow['m12_'+k]=r[k]
 for x in exits:
  for k in ('total_net_investor_loss','loss_per_partner','net_exit_payment_needed','exit_day_bridge_before_recovery','asset_recovery_total','exit_cost_total','returned_cash_at_exit'):
   sumrow['exit_m'+str(x['exit_month'])+'_'+k]=x[k]
 return rows,sumrow,exits
def write_csv(path,rows):
 if not rows:return
 with path.open('w',encoding='utf-8-sig',newline='') as f:
  fields=list(rows[0]);writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows({k:(round(v,5) if isinstance(v,float) else v) for k,v in row.items()} for row in rows)
def sensitivity_rows(baselines):
 # One-factor experiments on standard investment, mixed channel, base market.
 # Restore every mutation before the next case and leave canonical outputs unchanged.
 rows=[]
 bm={r['mode']:r for r in baselines}
 for m in MODES:
  changes=[
    ('潜在需求少20%', MARKET_RAW['modes'][m]['mature_orders_day'],'base',lambda v:v*.8),
    ('潜在需求多20%', MARKET_RAW['modes'][m]['mature_orders_day'],'base',lambda v:v*1.2),
    ('线下售价低10%',MARKET_RAW['modes'][m]['offline_ticket_cny'],'base',lambda v:v*.9),
    ('食材采购贵10%',MARKET_SCENARIOS['base'],'ingredient',lambda v:v*1.1),
    ('每月租金贵20%',MARKET_RAW['modes'][m]['rent'],'base',lambda v:v*1.2),
    ('已聘员工总成本贵10%',LABOR_RAW['wages'],'base',lambda v:v*1.1),
    ('另发掘20%线上增量且线下无流失',CHANNEL_DEMAND['mixed'],'delivery',lambda v:v+.2),
  ]
  for tag,ob,key,change in changes:
   orig=ob[key];ob[key]=change(orig)
   try:_,r,_=simulate(m,'base','mixed','base')
   finally:ob[key]=orig
   base=bm[m]
   rows.append(sens_result(m,tag,r,base))
  for tag,field,delta in [('两平台商家配送每单贵2元','delivery_cost',2),('两平台交易费率多3个百分点','commission_rate',.03),('两平台商家优惠率多5个百分点','merchant_discount_rate',.05)]:
   orig=[DELIVERY_RAW['platforms'][k][field]['base'] for k in ('meituan','taobao')]
   for j,k in enumerate(('meituan','taobao')):DELIVERY_RAW['platforms'][k][field]['base']=orig[j]+delta
   try:_,r,_=simulate(m,'base','mixed','base')
   finally:
    for j,k in enumerate(('meituan','taobao')): DELIVERY_RAW['platforms'][k][field]['base']=orig[j]
   rows.append(sens_result(m,tag,r,bm[m]))
  # Only as an explicit conditional overlap credit IF verified reuse is secured.
  ob=MARKET_RAW['modes'][m]; amount=min(ob['transfer']['base'],20000)
  if amount>0:
   present='transfer_bundle_credit' in ob;old=ob.get('transfer_bundle_credit')
   ob['transfer_bundle_credit']={'base':amount}
   try:_,r,_=simulate(m,'base','mixed','base')
   finally:
    if present:ob['transfer_bundle_credit']=old
    else:ob.pop('transfer_bundle_credit')
   rows.append(sens_result(m,'核实转让已含2万元可替代项目(仅示例)',r,bm[m]))
 return rows
def sens_result(m,tag,r,base):
 return dict(mode=m,test=tag,initial_funding=r['initial_funding'],base_funding=base['initial_funding'],funding_delta=r['initial_funding']-base['initial_funding'],
  y1_monthly_profit=r['y1_avg_monthly_profit'],base_y1_monthly_profit=base['y1_avg_monthly_profit'],y1_monthly_profit_delta=r['y1_avg_monthly_profit']-base['y1_avg_monthly_profit'],
  y2_monthly_profit=r['y2_avg_monthly_profit'],y2_monthly_profit_delta=r['y2_avg_monthly_profit']-base['y2_avg_monthly_profit'],
  cashflow_36=r['cumulative_business_cashflow'],cashflow_36_delta=r['cumulative_business_cashflow']-base['cumulative_business_cashflow'],capital_calls=r['total_capital_calls'],
  m6_exit_loss=r['exit_m6_total_net_investor_loss'],m6_exit_loss_delta=r['exit_m6_total_net_investor_loss']-base['exit_m6_total_net_investor_loss'],recovery_month=r['capital_recovery_month'],staff_max=r['staff_max'])
def main():
 monthly=[]; summary=[];exits=[]
 for mode,tier,strategy,sc in product(MODES,TIERS,CHANNELS,SCENARIOS):
  m,s,e=simulate(mode,tier,strategy,sc);monthly+=m;summary.append(s);exits+=e
 assert len(summary)==135 and len(monthly)==4860 and len(exits)==540
 write_csv(P/'monthly_v3.csv',monthly);write_csv(P/'summary_v3.csv',summary);write_csv(P/'exit_v3.csv',exits)
 # Use base tier + mixed strategy + base demand as consistent reader comparison; all alternatives retained.
 selected=[s for s in summary if s['tier']=='base' and s['strategy']=='mixed' and s['scenario']=='base']
 sensitivity=sensitivity_rows(selected)
 write_csv(P/'sensitivity_v3.csv',sensitivity)
 units=[]
 for mode,tier,sc,channel in product(MODES,TIERS,SCENARIOS,['onsite','meituan','taobao']):
  units.append(dict(mode=mode,tier=tier,scenario=sc,channel=channel,**unit(mode,sc,tier,0,channel)))
 write_csv(P/'unit_economics_v3.csv',units)
 params=dict(input_status=INPUT_STATUS,market={m:{t:get_market(m,t) for t in TIERS} for m in MODES},startup={m:{t:get_cost(m,t) for t in TIERS} for m in MODES},labor={m:{t:get_labor(m,t) for t in TIERS} for m in MODES},wages={t:{s:wage(t,s,0) for s in SCENARIOS} for t in TIERS},
  platform={p:{s:{t:get_platform(p,s,t) for t in TIERS} for s in SCENARIOS} for p in PLATFORMS},unit_inputs={m:get_unit_inputs(m) for m in MODES},market_scenarios=MARKET_SCENARIOS,channel_demand=CHANNEL_DEMAND,family_season=FAMILY,other_season=OTHER,tier_demand=TIER_DEMAND,
  reserve_months=POST_RESERVE_MONTHS,maintenance_rate=MAINT_RATE,tax_budget=TAX_ALLOWANCE,second_hand_equipment_note='hypothesis not observed liquidation value')
 (P/'model_inputs_v3.json').write_text(json.dumps(params,ensure_ascii=False,indent=2))
 (P/'report_data_v3.json').write_text(json.dumps(dict(summary=summary,selected=selected,monthly_selected=[r for r in monthly if r['case_id'] in {s['case_id'] for s in selected}],exit_selected=[e for e in exits if e['case_id'] in {s['case_id'] for s in selected}],all_exits=exits,monthly_compact=[{k:r[k] for k in ('case_id','mode','tier','strategy','scenario','month','recognized_revenue','operating_profit','business_cashflow','cumulative_business_cashflow','retained_cash','additional_capital','cumulative_additional_capital','distributed_to_partners','paid_staff','realized_daily','actual_onsite_daily','actual_delivery_daily','lost_daily_orders','total_fixed_cost')} for r in monthly],unit_economics=units,sensitivity=sensitivity,inputs=params),ensure_ascii=False))
 (P/'VALIDATION.txt').write_text(f'PASS: {len(summary)} cases, {len(monthly)} months, {len(exits)} exits, {len(units)} per-order unit snapshots; {len(sensitivity)} one-factor tests. All cash/revenue/exit identities, capacity constraints, employer payroll and owner salary asserts passed. Inputs: {INPUT_STATUS}\n')
 print('PASS',len(summary),len(monthly),len(exits),len(units));print('INPUT_STATUS',INPUT_STATUS)
 for s in selected:
  print(s['case_id'], 'start',round(s['initial_funding']), 'm12 orders',round(s['m12_realized_daily']), 'staff',s['staff_min'],s['staff_max'],'y1 avg',round(s['y1_avg_monthly_profit']),'y2 avg',round(s['y2_avg_monthly_profit']),'cum cf',round(s['cumulative_business_cashflow']),'payback',s['capital_recovery_month'],'exit6',round(s['exit_m6_total_net_investor_loss']))
if __name__=='__main__':main()
