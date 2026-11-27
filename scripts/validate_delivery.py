"""Run executable delivery checks after regenerating models and PDF."""
import csv,json
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[1]
for p in ['AGENTS.md','GOALS.md','WORKFLOW.md','ACCEPTANCE.md','TASKS.md','research/01_market.md','research/02_competition.md','research/03_product.md','research/04_operations.md','models/model.py','models/FINANCIAL_MODEL.md','tooling/TOOL_REGISTRY.md','tooling/BEST_PRACTICES.md','tooling/SELECTION_LOG.md','reviews/INDEPENDENT_REVIEW.md']:
 assert (ROOT/p).stat().st_size>0,p
monthly=list(csv.DictReader(open(ROOT/'models/monthly.csv',encoding='utf-8-sig')))
summary=list(csv.DictReader(open(ROOT/'models/summary.csv',encoding='utf-8-sig')))
sensitivity=list(csv.DictReader(open(ROOT/'models/sensitivity.csv',encoding='utf-8-sig')))
assert len(monthly)==540 and len(summary)==15 and len(sensitivity)==62
for r in monthly:
 f=lambda k:float(r[k])
 assert abs(f('orders')*f('ticket')-f('revenue'))<1
 assert abs(f('contribution')-f('fixed_cost')-f('operating_profit'))<.01
 assert abs(f('operating_profit')-f('inventory_change')-f('maintenance_capex')-f('cashflow'))<.01
doc=fitz.open(ROOT/'deliverables'/'Shenzhen_Eat_商业可行性研究.pdf')
assert len(doc)==36
assert sum(len(p.get_links()) for p in doc)==64
for i,p in enumerate(doc):
 assert len(p.get_text().strip())>35,i
 for b in p.get_text('blocks'):
  assert b[0]>=-1 and b[1]>=-1 and b[2]<=p.rect.width+1 and b[3]<=p.rect.height+1,(i,b[:4])
print(f'H01-H08 delivery checks PASS: {len(summary)} scenarios, {len(monthly)} monthly rows, {len(sensitivity)} sensitivity tests, {len(doc)} PDF pages, 64 source links')
