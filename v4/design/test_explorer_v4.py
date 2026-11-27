#!/usr/bin/env python3
"""Exercise offline file on real Chromium, including all 135 selectors, 3 channels, 4 exits."""
from pathlib import Path
from itertools import product
from playwright.sync_api import sync_playwright
import json,re,hashlib,os,sys
from playwright.sync_api import Error
P=Path(__file__).resolve().parents[2]
FILE=P/'deliverables'/'Shenzhen_Eat_情景模拟_V4.html'; DATA=json.loads(re.search(r'<script id="scenario-data" type="application/json">(.*?)</script>',FILE.read_text(),re.S)[1]); assert DATA['report_sha256']==hashlib.sha256((P/'v4/models/report_data_v4.json').read_bytes()).hexdigest()
errors=[]; requests=[]
with sync_playwright() as w:
 path=os.environ.get('EXPLORER_CHROME')
 try:
  b=w.chromium.launch(executable_path=path, args=['--no-sandbox']) if path else w.chromium.launch(args=['--no-sandbox'])
 except Error as e:
  print('SKIP browser verification: a usable Chromium binary is unavailable. Set EXPLORER_CHROME to an actual binary or install Playwright Chromium. JS functional fallback: node v4/design/test_explorer_v4_node.js. '+str(e).splitlines()[0]);sys.exit(77)
 page=b.new_page(viewport={'width':390,'height':844},device_scale_factor=1,is_mobile=True,has_touch=True)
 page.on('pageerror',lambda e:errors.append(str(e))); page.on('request',lambda r:requests.append(r.url))
 page.goto(FILE.as_uri()); page.wait_for_function('document.documentElement.dataset.case');
 assert len(page.locator('h2').all())>=8; assert page.locator('.story img').count()==1; assert page.locator('.chain li').count()==7
 out=P/'v4/design/explorer_screenshots'; out.mkdir(exist_ok=True)
 page.screenshot(path=out/'390_initial.png')
 for case in product('ABCDE',('low','base','high'),('onsite','mixed','delivery_heavy'),('bad','base','good')):
  key='_'.join(case)
  for ident,v in zip(['mode','tier','strategy','scenario'],case): page.select_option('#'+ident,v)
  assert page.locator('html').get_attribute('data-case')==key
  # All data areas updated and contain expected values and no render artifacts.
  vals=page.evaluate('''()=>{const {s,m12:m}=current;return {key:document.documentElement.dataset.case,overview:document.querySelector('#overview').innerText,startup:document.querySelector('#startupBody').innerText,orders:document.querySelector('#orderBody').innerText,monthly:document.querySelector('#monthBody').innerText,cash:document.querySelector('#cashBody').innerText,money:money(s.initial_funding),day:count(m.realized_daily),profit:money(m.operating_profit),cumulative:money(s.cumulative_business_cashflow),salary:m.owner_salary,partners:m.partner_count};}''')
  assert vals['money'] in vals['overview'] and vals['money'] in vals['startup'] and vals['day'] in vals['orders'] and vals['profit'] in vals['monthly'] and vals['cumulative'] in vals['cash'] and vals['salary']==0 and vals['partners']==2
  for c in ['onsite','meituan','taobao']:
   page.locator(f'[data-channel="{c}"]').click();assert page.locator(f'[data-channel="{c}"]').get_attribute('aria-pressed')=='true'
   assert page.evaluate('''()=>document.querySelector('#unitBody').innerText.includes(yuan(current.m12[channel+'_contribution_per_order']))''')
  for x in [3,6,12,24]:
   page.locator(f'[data-exit="{x}"]').click();assert page.locator(f'[data-exit="{x}"]').get_attribute('aria-pressed')=='true'
   assert page.evaluate('''()=>document.querySelector('#exitBody').innerText.includes(money(Math.abs(current.e.find(e=>e.exit_month===endMonth).total_net_investor_loss)))''')
  assert 'V4修正' in page.locator('#evidenceBody').inner_text(); txt=page.locator('main').inner_text(); assert not re.search(r'NaN|undefined|Infinity',txt),key
  overflow=page.evaluate('document.documentElement.scrollWidth > innerWidth'); assert not overflow,key
 # Screenshots at representative widths and viewport panels in a separate default mode.
 for ident,v in zip(['mode','tier','strategy','scenario'],('D','base','mixed','base')):page.select_option('#'+ident,v)
 for width in [360,390,430,1024]:
  page.set_viewport_size({'width':width,'height':844});page.locator('#startup').scroll_into_view_if_needed();page.locator('#startup').screenshot(path=out/f'{width}_startup.png');page.locator('#cash').screenshot(path=out/f'{width}_cash.png');page.locator('#overview').screenshot(path=out/f'{width}_causal_chain.png');page.locator('#evidence').screenshot(path=out/f'{width}_evidence.png');assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
 page.locator('[data-exit="6"]').click();page.set_viewport_size({'width':390,'height':844});page.locator('#exit').screenshot(path=out/'390_exit.png');page.locator('#unit').screenshot(path=out/'390_unit.png')
 b.close()
assert not errors,errors
assert all(x.startswith('file:') or x.startswith('data:') for x in requests),requests
print('PASS: 135/135 scenario combinations; 405/405 channel clicks; 540/540 exit clicks; 360,390,430,1024 viewport widths; zero JS errors, zero external requests; current SHA256 verified')
