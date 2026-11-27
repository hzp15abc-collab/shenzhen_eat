#!/usr/bin/env node
// Functional JS test fallback when the local browser binary is absent.
const fs = require('fs'); const path = require('path'); const vm=require('vm'); const assert=require('assert'); const crypto=require('crypto');
const project=path.resolve(__dirname,'../..'); const filename=path.join(project,'deliverables','Shenzhen_Eat_情景模拟_V4.html'); const html=fs.readFileSync(filename,'utf8');
const script=html.match(/<script>\s*([\s\S]*?)<\/script>/)[1]; const data=html.match(/<script id="scenario-data" type="application\/json">([\s\S]*?)<\/script>/)[1]; const parsed=JSON.parse(data);
assert.equal(parsed.report_sha256,crypto.createHash('sha256').update(fs.readFileSync(path.join(project,'v4/models/report_data_v4.json'))).digest('hex'));
assert.equal(parsed.reader_sha256,crypto.createHash('sha256').update(fs.readFileSync(path.join(project,'v4/models/reader_finance_v4.json'))).digest('hex'));
assert.equal(parsed.monthly_sha256,crypto.createHash('sha256').update(fs.readFileSync(path.join(project,'v3/models/monthly_v3.csv'))).digest('hex'));
class Element { constructor(dataset={},value=''){ this.dataset=dataset;this.value=value;this.innerHTML='';this.textContent='';this.handlers={};this.attrs={}; } addEventListener(evt,f){this.handlers[evt]=f;} setAttribute(k,v){this.attrs[k]=v;} click(){this.handlers.click();} change(v){ this.value=v; this.handlers.change(); }}
const nodes={}; ['overview','result','startupBody','orderBody','unitBody','monthBody','cashBody','exitBody','evidenceBody','sha','monthlySha','readerSha'].forEach(x=>nodes[x]=new Element());
for(const [k,v] of Object.entries({mode:'A',tier:'base',strategy:'mixed',scenario:'base'}))nodes[k]=new Element({},v);
const allChannels=['onsite','meituan','taobao'].map(c=>new Element({channel:c}));const allExits=['3','6','12','24'].map(e=>new Element({exit:e}));
const document={documentElement:new Element(),querySelector:sel=>sel==='#scenario-data'?{textContent:data}:null,getElementById:id=>nodes[id],querySelectorAll:sel=>sel==='[data-channel]'?allChannels:allExits};
const sandbox={document, console}; vm.createContext(sandbox); vm.runInContext(script,sandbox);
const check=code=>vm.runInContext(code,sandbox);
assert.equal(document.documentElement.dataset.case,'A_base_mixed_base');
let scenarios=0, channels=0, exits=0, conditions=new Set(), asymmetrics=new Set(), corrections=new Set(), sourced=new Set();
for(const mode of 'ABCDE')for(const tier of ['low','base','high'])for(const strategy of ['onsite','mixed','delivery_heavy'])for(const scenario of ['bad','base','good']){
 const key=[mode,tier,strategy,scenario].join('_'); Object.entries({mode,tier,strategy,scenario}).forEach(([k,v])=>nodes[k].change(v));assert.equal(document.documentElement.dataset.case,key);
 const row=parsed.cases[key]; const {s,m12:m}=row;
 assert.equal(m.owner_salary,0);assert.equal(m.partner_count,2);
 assert(nodes.overview.innerHTML.includes(check('money(current.s.initial_funding)')));assert(nodes.startupBody.innerHTML.includes(check('money(current.s.initial_funding)')));assert(nodes.orderBody.innerHTML.includes(check('count(current.m12.realized_daily)')));assert(nodes.monthBody.innerHTML.includes(check('money(current.m12.operating_profit)')));assert(nodes.cashBody.innerHTML.includes(check('money(current.s.cumulative_business_cashflow)')));
 const cond=parsed.conditional_tests.filter(x=>x.mode===mode); for (const c of cond){assert(nodes.evidenceBody.innerHTML.includes(c.label));assert(nodes.evidenceBody.innerHTML.includes(check(`money(DATA.conditional_tests.find(x=>x.key===${JSON.stringify(c.key)}).initial_funding)`)));assert(nodes.evidenceBody.innerHTML.includes(check(`money(DATA.conditional_tests.find(x=>x.key===${JSON.stringify(c.key)}).y1_avg_profit)`)));conditions.add(c.key);if(c.source.startsWith('http')){sourced.add(c.source); assert(nodes.evidenceBody.innerHTML.includes(c.source.replace(/&/g,'&amp;')));}if(c.lease_end){assert(nodes.evidenceBody.innerHTML.includes('正常到期净损失'));assert(nodes.evidenceBody.innerHTML.includes(check(`money(DATA.conditional_tests.find(x=>x.key===${JSON.stringify(c.key)}).lease_end.exit_loss_if_no_early_charge)`)));}}
 const a=parsed.platform_tests.filter(x=>x.mode===mode); for(const t of a){assert(nodes.evidenceBody.innerHTML.includes(t.condition));assert(nodes.evidenceBody.innerHTML.includes(check(`money(DATA.platform_tests.find(x=>x.mode===${JSON.stringify(mode)}&&x.channel===${JSON.stringify(t.channel)}&&x.condition===${JSON.stringify(t.condition)}).y1_avg_monthly_profit)`)));asymmetrics.add([mode,t.channel,t.condition].join('|'));}
 const fix=parsed.corrections.find(x=>x.mode===mode);assert(nodes.evidenceBody.innerHTML.includes('V4修正'));assert(nodes.evidenceBody.innerHTML.includes(check(`money(DATA.corrections.find(x=>x.mode===${JSON.stringify(mode)}).new_y1_monthly_profit)`)));corrections.add(mode);
 assert(nodes.overview.innerHTML.includes('data:image/jpeg;base64,')&&nodes.overview.innerHTML.includes('一条现金链'));assert(!nodes.overview.innerHTML.includes('单单'));
 for(const ch of allChannels){ch.click();assert.equal(ch.attrs['aria-pressed'],'true');assert(nodes.unitBody.innerHTML.includes(check("yuan(current.m12[channel+'_contribution_per_order'])")));channels++;}
 for(const e of allExits){e.click();assert.equal(e.attrs['aria-pressed'],'true');assert(nodes.exitBody.innerHTML.includes(check('money(Math.abs(current.e.find(e=>e.exit_month===endMonth).total_net_investor_loss))')));exits++;}
 for(const [id,el] of Object.entries(nodes)){const m=el.innerHTML.replace(/data:image\/jpeg;base64,[A-Za-z0-9+/=]+/g,'<embedded-photo>').match(/.{0,70}(?:NaN|\bundefined\b|Infinity).{0,70}/);assert(!m, `${key} render artifact ${id} ${m}`)}
 scenarios++;
}
assert.equal(scenarios,135);assert.equal(channels,405);assert.equal(exits,540);assert.equal(conditions.size,11);assert.equal(asymmetrics.size,30);assert.equal(corrections.size,5);
assert(!/<(?:script|img|iframe|link)\b[^>]+(?:src|href)\s*=\s*["'](?:https?:)?\/\//i.test(html));assert(!/\bfetch\s*\(|\bXMLHttpRequest\s*\(|\bWebSocket\s*\(/.test(script));
console.log(`PASS: ${scenarios} scenario combinations, ${channels} channel detail selections, ${exits} exit selections; 11 evidence conditions, 30 platform-asymmetric cases, 5 corrected price sensitivities; all summary fields refer to source rows; no NaN/undefined/Infinity; source hashes verified; no external-resource or network calls. Node VM uses lightweight DOM/test doubles, not browser pixels.`)
