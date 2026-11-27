#!/usr/bin/env node
// Functional JS test fallback when the local browser binary is absent.
const fs = require('fs'); const path = require('path'); const vm=require('vm'); const assert=require('assert'); const crypto=require('crypto');
const project=path.resolve(__dirname,'../..'); const filename=path.join(project,'deliverables','Shenzhen_Eat_情景模拟_V3.html'); const html=fs.readFileSync(filename,'utf8');
const script=html.match(/<script>\s*([\s\S]*?)<\/script>/)[1]; const data=html.match(/<script id="scenario-data" type="application\/json">([\s\S]*?)<\/script>/)[1]; const parsed=JSON.parse(data);
assert.equal(parsed.report_sha256,crypto.createHash('sha256').update(fs.readFileSync(path.join(project,'v3/models/report_data_v3.json'))).digest('hex'));
assert.equal(parsed.monthly_sha256,crypto.createHash('sha256').update(fs.readFileSync(path.join(project,'v3/models/monthly_v3.csv'))).digest('hex'));
class Element { constructor(dataset={},value=''){ this.dataset=dataset;this.value=value;this.innerHTML='';this.textContent='';this.handlers={};this.attrs={}; } addEventListener(evt,f){this.handlers[evt]=f;} setAttribute(k,v){this.attrs[k]=v;} click(){this.handlers.click();} change(v){ this.value=v; this.handlers.change(); }}
const nodes={}; ['overview','result','startupBody','orderBody','unitBody','monthBody','cashBody','exitBody','sha','monthlySha'].forEach(x=>nodes[x]=new Element());
for(const [k,v] of Object.entries({mode:'A',tier:'base',strategy:'mixed',scenario:'base'}))nodes[k]=new Element({},v);
const allChannels=['onsite','meituan','taobao'].map(c=>new Element({channel:c}));const allExits=['3','6','12','24'].map(e=>new Element({exit:e}));
const document={documentElement:new Element(),querySelector:sel=>sel==='#scenario-data'?{textContent:data}:null,getElementById:id=>nodes[id],querySelectorAll:sel=>sel==='[data-channel]'?allChannels:allExits};
const sandbox={document, console}; vm.createContext(sandbox); vm.runInContext(script,sandbox);
const check=code=>vm.runInContext(code,sandbox);
assert.equal(document.documentElement.dataset.case,'A_base_mixed_base');
let scenarios=0, channels=0, exits=0;
for(const mode of 'ABCDE')for(const tier of ['low','base','high'])for(const strategy of ['onsite','mixed','delivery_heavy'])for(const scenario of ['bad','base','good']){
 const key=[mode,tier,strategy,scenario].join('_'); Object.entries({mode,tier,strategy,scenario}).forEach(([k,v])=>nodes[k].change(v));assert.equal(document.documentElement.dataset.case,key);
 const row=parsed.cases[key]; const {s,m12:m}=row;
 assert.equal(m.owner_salary,0);assert.equal(m.partner_count,2);
 assert(nodes.overview.innerHTML.includes(check('money(current.s.initial_funding)')));assert(nodes.startupBody.innerHTML.includes(check('money(current.s.initial_funding)')));assert(nodes.orderBody.innerHTML.includes(check('count(current.m12.realized_daily)')));assert(nodes.monthBody.innerHTML.includes(check('money(current.m12.operating_profit)')));assert(nodes.cashBody.innerHTML.includes(check('money(current.s.cumulative_business_cashflow)')));
 for(const ch of allChannels){ch.click();assert.equal(ch.attrs['aria-pressed'],'true');assert(nodes.unitBody.innerHTML.includes(check("yuan(current.m12[channel+'_contribution_per_order'])")));channels++;}
 for(const e of allExits){e.click();assert.equal(e.attrs['aria-pressed'],'true');assert(nodes.exitBody.innerHTML.includes(check('money(Math.abs(current.e.find(e=>e.exit_month===endMonth).total_net_investor_loss))')));exits++;}
 for(const el of Object.values(nodes)) assert(!/NaN|\bundefined\b|Infinity/.test(el.innerHTML),`${key} render artifact`);
 scenarios++;
}
assert.equal(scenarios,135);assert.equal(channels,405);assert.equal(exits,540);
assert(!/<(?:script|img|iframe|link)\b[^>]+(?:src|href)\s*=\s*["'](?:https?:)?\/\//i.test(html));assert(!/\bfetch\s*\(|\bXMLHttpRequest\s*\(|\bWebSocket\s*\(/.test(script));
console.log(`PASS: ${scenarios} scenario combinations, ${channels} channel detail selections, ${exits} exit selections; all summary fields refer to source rows; no NaN/undefined/Infinity; source hashes verified; no external-resource or network calls. Node VM uses lightweight DOM/test doubles, not browser pixels.`)
