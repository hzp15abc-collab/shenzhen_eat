#!/usr/bin/env python3
"""可复算的情景模型；所有店铺参数均为假设，不是当地实测或预测。
Python 3 标准库即可运行: python3 model.py
输出 JSON/CSV，金额单位元，订单量按期望值计算。
"""
import calendar
import csv
import json
import math
from pathlib import Path
from dataclasses import asdict, dataclass, replace

HERE = Path(__file__).resolve().parent
START_YEAR = 2027
MONTHS = 36

@dataclass(frozen=True)
class Product:
    name: str
    orders_share: float
    price: float
    ingredient_rate: float
    spoilage_rate: float
    packaging_per_order: float

@dataclass(frozen=True)
class Mode:
    name: str
    area_m2: str
    lease_cash: int
    property_fee: int
    staff_loaded: int
    owner_labor: int
    owner_hours_month: int
    utilities: int
    fixed_other: int
    marketing: int
    fitout: int
    equipment: int
    transfer: int
    preopening: int
    deposit_months: int
    inventory_days: float
    reference_exposures_per_day: int
    new_conversion: float
    return_conversion: float
    mature_return_exposure: float
    capacity_day: int
    school_dependent_demand_share: float
    days_per_30: int
    other_variable_rate: float  # 支付费、推广等，税费另计
    host_share: float  # 仅 E 类包含共享方抽成假设
    products: tuple

MODES = {
    'A': Mode('传统中式早餐','20–35',4500,500,6500,6500,250,1200,750,400,18000,18000,18000,3800,2,3,1800,.075,.17,.45,260,.55,27,.028,0,(
        Product('现制中式早餐',.80,8.5,.34,.05,.40),
        Product('饮品或便携零食',.20,6.5,.52,.025,.18),
    )),
    'B': Mode('饭团/三明治便携早餐','15–30',5200,500,6500,6200,220,950,800,600,22000,22000,15000,4800,2,3,1500,.06,.15,.43,220,.50,27,.035,0,(
        Product('饭团/三明治/套餐',.80,12.5,.38,.065,.75),
        Product('饮品/零食',.20,8.5,.48,.025,.20),
    )),
    'C': Mode('社区早餐＋较健康零食饮品','30–50',5800,700,7600,6600,250,1450,950,600,28000,24000,18000,5000,2,5,1900,.073,.16,.46,280,.40,28,.030,0,(
        Product('早餐套餐',.57,8.5,.35,.05,.40),
        Product('水果/酸奶/简食',.25,11.0,.43,.10,.55),
        Product('包装饮品及零食',.18,8.0,.64,.015,.10),
    )),
    'D': Mode('全天早餐＋简餐＋茶点/夜餐','45–80',10000,1300,17500,8000,290,2600,1500,1000,48000,42000,30000,8000,3,4,2600,.066,.15,.47,390,.25,28,.045,0,(
        Product('早餐',.43,8.5,.34,.05,.45),
        Product('简餐/夜餐',.35,19.5,.43,.07,.80),
        Product('小食/饮品/茶点',.22,10.5,.40,.045,.45),
    )),
    'E': Mode('分时租赁/店中店早餐试营业','约8–20共享',1800,250,3000,4500,150,650,500,300,3000,8000,0,2000,1,2,1300,.07,.155,.46,170,.45,26,.025,.035,(
        Product('便携早餐',.88,8.0,.34,.045,.38),
        Product('袋装零食/饮品',.12,6.5,.54,.02,.15),
    )),
}

# 这两个系数是示例而非学校日程或实际客流，表示家庭相关/其他消费机会共同影响。
SCHOOL_SEASON = (0.82,0.48,1.0,1.0,1.0,0.91,0.64,0.62,1.0,0.96,1.0,1.0)
OTHER_SEASON = (0.96,0.84,1.0,1.0,1.0,0.98,0.97,0.97,1.0,0.97,1.0,1.0)

@dataclass(frozen=True)
class Scenario:
    traffic: float
    capture: float
    price: float
    ingredient: float
    spoilage: float
    rent: float
    staff: float
    competition_start: int
    competition_loss: float
    return_exposure: float
    annual_rent_growth: float=.03
    annual_wage_growth: float=.04
    annual_ingredient_growth: float=.02
    annual_price_growth: float=.015
    annual_other_cost_growth: float=.025

SCENARIOS = {
    'bad': Scenario(.78,.82,.96,1.08,1.25,1.15,1.08,7,.18,.85,.05,.05,.04,0,.03),
    'base': Scenario(1,1,1,1,1,1,1,19,.07,1),
    'good': Scenario(1.12,1.08,1.04,.96,.80,.90,1,25,.04,1.10,.02,.035,.015,.02,.02),
}
# 仅税费预算，绝不视为实际税率或适用税收政策；真实税负以主体/税务机关确定。
TAX_RISK_ALLOWANCE = .015
MAINT_CAPEX_RATE = .006
RESERVE_FIXED_MONTHS = 3
DISCOUNT_RATE = .06 # 假设资本机会成本年化6%，非真实融资利率

def unit_metrics(mode, sc, year):
    price_factor = sc.price*(1+sc.annual_price_growth)**year
    ingredient_factor = sc.ingredient*(1+sc.annual_ingredient_growth)**year
    avg_ticket = 0
    ingredients = 0
    sale_cogs = 0
    packaging = 0
    for p in mode.products:
        price = p.price*price_factor
        # 原料价格增长独立于售价变化，而非随售价机械增长
        direct = p.price*p.ingredient_rate*ingredient_factor
        spoil = max(0,min(.30,p.spoilage_rate*sc.spoilage))
        avg_ticket += p.orders_share*price
        sale_cogs += p.orders_share*direct
        ingredients += p.orders_share*direct/(1-spoil)
        packaging += p.orders_share*p.packaging_per_order*(1+sc.annual_other_cost_growth)**year
    other_rate = mode.other_variable_rate+mode.host_share+TAX_RISK_ALLOWANCE
    contribution = avg_ticket - ingredients - packaging - avg_ticket*other_rate
    return avg_ticket, ingredients, sale_cogs, packaging, other_rate, contribution

def fixed_components(mode,sc,year):
    rent = mode.lease_cash*sc.rent*(1+sc.annual_rent_growth)**year
    property_fee=mode.property_fee*(1+sc.annual_other_cost_growth)**year
    staff=mode.staff_loaded*sc.staff*(1+sc.annual_wage_growth)**year
    owner=mode.owner_labor*(1+sc.annual_wage_growth)**year
    other=(mode.utilities+mode.fixed_other+mode.marketing)*(1+sc.annual_other_cost_growth)**year
    return rent,property_fee,staff,owner,other

def simulate(mode_key, scenario_key, sc=None, mode_override=None):
    mode = mode_override or MODES[mode_key]
    sc = sc or SCENARIOS[scenario_key]
    rent, prop, staff, owner, other = fixed_components(mode,sc,0)
    avg_ticket, ingredients, sale_cogs, packaging, other_rate, ref_cont = unit_metrics(mode,sc,0)
    # 成熟但尚未引入竞争、无特殊淡季的参考日，目的是计算库存与盈亏平衡。
    mret=min(.75,mode.mature_return_exposure*sc.return_exposure)
    ref_new=mode.reference_exposures_per_day*sc.traffic*(1-mret)*mode.new_conversion*sc.capture
    ref_repeat=mode.reference_exposures_per_day*sc.traffic*mret*mode.return_conversion*sc.capture
    ref_orders=min(mode.capacity_day,ref_new+ref_repeat)
    initial_stock=ref_orders*ingredients*mode.inventory_days
    deposit=rent*mode.deposit_months
    irreversible=mode.fitout+mode.equipment+mode.transfer+mode.preopening
    investment=irreversible+deposit+initial_stock
    reserve=RESERVE_FIXED_MONTHS*(rent+prop+staff+owner+other)
    funding=investment+reserve
    # 简化折旧假设：装修36月/设备60月/转让费按36个月租约摊销，
    # 开业杂项为第0月支出，不重复在第1月计；并不等同于税务账。
    depreciation=mode.fitout/36+mode.equipment/60+mode.transfer/36
    inv=initial_stock
    cumulative=0
    cash_balance=reserve
    min_cash=cash_balance
    initial_recovered_month=None
    funding_recovered_month=None
    first_cash_shortfall=None
    out=[]
    for month in range(1, MONTHS+1):
        i=(month-1)%12
        year=(month-1)//12
        yyyy=START_YEAR+year
        days=max(1,round(calendar.monthrange(yyyy,i+1)[1]*mode.days_per_30/30))
        # 开业早期转化爬坡与老客聚集：假设，不使用未观测实际复购率。
        ramp=min(1,.60+.065*(month-1))
        mret=min(.75,mode.mature_return_exposure*sc.return_exposure)
        returning_exposure = min(mret,.08+(mret-.08)*(1-math.exp(-(month-1)/5))) if mret>.08 else mret
        season = (SCHOOL_SEASON[i]*mode.school_dependent_demand_share+OTHER_SEASON[i]*(1-mode.school_dependent_demand_share))
        comp=1-sc.competition_loss if month>=sc.competition_start else 1
        exposures=mode.reference_exposures_per_day*sc.traffic*days*season
        desired_new=exposures*(1-returning_exposure)*mode.new_conversion*sc.capture*ramp*comp
        desired_repeat=exposures*returning_exposure*mode.return_conversion*sc.capture*ramp*comp
        desired_total=desired_new+desired_repeat
        factor=min(1,mode.capacity_day*days/desired_total) if desired_total>0 else 1
        new_orders=desired_new*factor
        repeat_orders=desired_repeat*factor
        total=new_orders+repeat_orders
        ticket, ingredients, sold_cost, packaging, other_rate, cont=unit_metrics(mode,sc,year)
        revenue=total*ticket
        purchased_consumed=total*ingredients
        sold_cogs=total*sold_cost
        spoilage_cost=purchased_consumed-sold_cogs
        pack=total*packaging
        variable_other=revenue*mode.other_variable_rate
        host_fee=revenue*mode.host_share
        tax_budget=revenue*TAX_RISK_ALLOWANCE
        net_contribution=revenue-purchased_consumed-pack-variable_other-host_fee-tax_budget
        rent,prop,staff,owner,other=fixed_components(mode,sc,year)
        fixed=rent+prop+staff+owner+other
        owner_cash_income_before_alloc = net_contribution-(fixed-owner)
        profit=net_contribution-fixed  # 店主按机会成本计薪后的经营现金利润，未折旧
        accounting_profit=profit-depreciation
        target_inv=purchased_consumed/days*mode.inventory_days
        inv_change=target_inv-inv
        inv=target_inv
        maintenance_capex=revenue*MAINT_CAPEX_RATE
        cashflow=profit-inv_change-maintenance_capex
        cumulative += cashflow
        cash_balance += cashflow
        min_cash=min(min_cash,cash_balance)
        if cumulative>=investment and initial_recovered_month is None: initial_recovered_month=month
        if cumulative>=funding and funding_recovered_month is None: funding_recovered_month=month
        if cash_balance<0 and first_cash_shortfall is None: first_cash_shortfall=month
        target_normal_day_orders=(fixed/(cont-ticket*MAINT_CAPEX_RATE)/days) if cont-ticket*MAINT_CAPEX_RATE>0 else float('inf')
        # 用实际已知存货余额，避免退出和经营现金净流重复释放；
        # 中途退出可能损失押金与未来租约成本，后者固定以一月租金、半月雇员人工加杂费为情景，不是最大法律损失。
        equipment_recovery=max(.15,.40-month*.007)*mode.equipment
        deposit_recovery=.60*deposit
        stock_recovery=.50*inv
        exit_extra=rent+.5*staff+800
        exit_cash=equipment_recovery+deposit_recovery+stock_recovery-exit_extra
        exit_loss=investment-(cumulative+exit_cash)
        row=dict(mode=mode_key,scenario=scenario_key,month=month,calendar=f'{yyyy}-{i+1:02}',
            open_days=days,season_factor=season,ramp=ramp,competition_factor=comp,
            addressable_exposures=exposures,return_exposure_share=returning_exposure,
            new_orders=new_orders,repeat_orders=repeat_orders,orders=total,
            returning_order_share=repeat_orders/total if total else 0,order_conversion=total/exposures if exposures else 0,
            daily_orders=total/days,ticket=ticket,revenue=revenue,
            direct_food_cogs=sold_cogs,waste_cost=spoilage_cost,consumed_food_cost=purchased_consumed,
            packaging=pack,variable_other=variable_other,host_fee=host_fee,tax_budget=tax_budget,
            gross_profit=revenue-purchased_consumed,contribution=net_contribution,rent=rent,property=prop,staff_loaded=staff,owner_labor=owner,other_fixed=other,
            fixed_cost=fixed,pre_owner_cash_income=owner_cash_income_before_alloc,operating_profit=profit,
            depreciation=depreciation,accounting_profit=accounting_profit,inventory=inv,inventory_change=inv_change,
            maintenance_capex=maintenance_capex,cashflow=cashflow,cumulative_free_cash=cumulative,
            cash_balance=cash_balance,break_even_daily_orders=target_normal_day_orders,exit_cash=exit_cash,exit_loss=exit_loss)
        out.append(row)
        assert abs(revenue-(sold_cogs+spoilage_cost+pack+variable_other+host_fee+tax_budget+net_contribution))<1e-6
        assert total<=mode.capacity_day*days+1e-6
        assert net_contribution-fixed==profit
        assert abs((owner_cash_income_before_alloc-owner)-profit)<1e-6
        assert abs(cash_balance-reserve-cumulative)<1e-6
    # 退出净额仅为模型假设；包括实际经营损益，不能保证租约可解约。
    years=[]
    for y in range(3):
        data=out[y*12:y*12+12]
        d={field:sum(x[field] for x in data) for field in ('revenue','orders','new_orders','repeat_orders','gross_profit','contribution','owner_labor','pre_owner_cash_income','operating_profit','accounting_profit','cashflow')}
        d.update(year=START_YEAR+y,daily_orders=sum(x['orders'] for x in data)/sum(x['open_days'] for x in data),end_cash=data[-1]['cash_balance'])
        years.append(d)
    npv=-funding+sum(r['cashflow']/(1+DISCOUNT_RATE)**(r['month']/12) for r in out)+(reserve+out[-1]['exit_cash'])/(1+DISCOUNT_RATE)**3
    summary=dict(mode=mode_key,scenario=scenario_key,name=mode.name,area_m2=mode.area_m2,
        investment=investment,deposit=deposit,initial_stock=initial_stock,irreversible_startup=irreversible,startup_outlay_before_deposit_stock=irreversible,reserve=reserve,total_funding=funding,
        normal_mature_orders_day=ref_orders,normal_avg_ticket=avg_ticket,normal_gross_margin=(avg_ticket-unit_metrics(mode,sc,0)[1])/avg_ticket,normal_margin=ref_cont/avg_ticket,normal_contribution_margin=ref_cont/avg_ticket,
        basic_monthly_fixed=out[0]['fixed_cost'],reference_be_orders_per_day=out[0]['fixed_cost']/(ref_cont-avg_ticket*MAINT_CAPEX_RATE)/mode.days_per_30,
        payback_month=initial_recovered_month,full_funding_payback_month=funding_recovered_month,
        cash_shortfall_month=first_cash_shortfall,min_cash=min_cash,additional_funding_needed=max(0,-min_cash),
        year1=years[0],year2=years[1],year3=years[2],total_free_cash=cumulative,
        month6_exit_loss=out[5]['exit_loss'],month12_exit_loss=out[11]['exit_loss'],
        month36_exit_loss=out[-1]['exit_loss'],month36_cash_balance=out[-1]['cash_balance'],npv_6pct_36month_liquidation=npv,
        last12_operating_margin=sum(x['operating_profit'] for x in out[-12:])/sum(x['revenue'] for x in out[-12:]))
    assert abs(sum(x['cashflow'] for x in out)-summary['total_free_cash'])<1e-6
    return summary,out

def main():
    all_summaries=[]
    all_rows=[]
    sensitivity=[]
    for key,mode in MODES.items():
        assert abs(sum(p.orders_share for p in mode.products)-1)<1e-9
        for scen in SCENARIOS:
            s,r=simulate(key,scen)
            all_summaries.append(s)
            all_rows.extend(r)
        base,_=simulate(key,'base')
        s=SCENARIOS['base']
        # 单因素扰动：比较第2年经营利润，经济资本口径（已经给老板计薪）
        variants=[
            ('商街消费机会量 −10%',replace(s,traffic=.9),None),
            ('新客/回头客成交率 −10%',replace(s,capture=.9),None),
            ('回头客曝光份额 −10%',replace(s,return_exposure=.9),None),
            ('客单价 −10%',replace(s,price=.9),None),
            ('原料采购成本 +10%',replace(s,ingredient=1.1),None),
            ('损耗率 +50%',replace(s,spoilage=1.5),None),
            ('租金 +20%',replace(s,rent=1.2),None),
            ('雇员人工 +10%',replace(s,staff=1.1),None),
            ('业主机会人工 +10%',s,replace(mode,owner_labor=round(mode.owner_labor*1.1))),
            ('日最大产能 −15%',s,replace(mode,capacity_day=round(mode.capacity_day*.85))),
            ('竞争提前且损失扩大',replace(s,competition_start=7,competition_loss=.18),None),
            ('初始转让费 +2万元',s,replace(mode,transfer=mode.transfer+20000)),
        ]
        if key=='E':
            variants.extend([('共享方流水分成至10%（固定租不变）',s,replace(mode,host_share=.10)),('共享方流水分成至15%（固定租不变）',s,replace(mode,host_share=.15))])
        for label,v,mo in variants:
            ss,_=simulate(key,'sensitivity',v,mo)
            sensitivity.append(dict(mode=key,change=label,base_year2_operating_profit=base['year2']['operating_profit'],
              stress_year2_operating_profit=ss['year2']['operating_profit'],
              year2_profit_delta=ss['year2']['operating_profit']-base['year2']['operating_profit'],
              extra_initial_funding=ss['total_funding']-base['total_funding'],
              stress_payback_month=ss['payback_month'],stress_cash_shortfall_month=ss['cash_shortfall_month']))
    for name,rows in [('monthly.csv',all_rows),('sensitivity.csv',sensitivity)]:
        with (HERE/name).open('w',newline='',encoding='utf-8-sig') as f:
            writer=csv.DictWriter(f,fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows({k:round(v,4) if isinstance(v,float) else v for k,v in r.items()} for r in rows)
    summary_flat=[]
    for d in all_summaries:
        flat={k:v for k,v in d.items() if not isinstance(v,dict)}
        for yy in ('year1','year2','year3'):
            flat.update({f'{yy}_{k}':v for k,v in d[yy].items()})
        summary_flat.append(flat)
    with (HERE/'summary.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=summary_flat[0].keys());w.writeheader()
        w.writerows({k:round(v,4) if isinstance(v,float) else v for k,v in r.items()} for r in summary_flat)
    bundle={'disclaimer':'全为示例假设，不是当地实测或承诺。2027年起36个月假设开业。金额单位人民币元。',
      'modes':{k:asdict(v) for k,v in MODES.items()},
      'scenarios':{k:asdict(v) for k,v in SCENARIOS.items()},
      'season_assumptions':{'school_family_related':SCHOOL_SEASON,'other':OTHER_SEASON},
      'model_constants':{'start_year':START_YEAR,'months':MONTHS,'tax_budget':TAX_RISK_ALLOWANCE,'maintenance_capex':MAINT_CAPEX_RATE,'reserve_fixed_months':RESERVE_FIXED_MONTHS,'discount_rate_annual':DISCOUNT_RATE},
      'summary':all_summaries,'sensitivity':sensitivity}
    (HERE/'model_results.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Validation passed: {len(all_summaries)} cases, {len(all_rows)} months, {len(sensitivity)} sensitivity tests')
    for s in all_summaries:
        if s['scenario']=='base':
            print(s['mode'], '启动资金',round(s['total_funding']), '年营收',*(round(s[yy]['revenue']) for yy in ('year1','year2','year3')),'年利润',*(round(s[yy]['operating_profit']) for yy in ('year1','year2','year3')), '现金回本',s['payback_month'],'缺口',round(s['additional_funding_needed']))
if __name__=='__main__':
    main()
