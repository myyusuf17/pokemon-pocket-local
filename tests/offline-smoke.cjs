const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const storage=new Map(),ctx={window:null,localStorage:{getItem:k=>storage.get(k)??null,setItem:(k,v)=>storage.set(k,v)},location:{protocol:'file:'},Response,URLSearchParams,console};ctx.window=ctx;ctx.fetch=()=>{throw Error('Unexpected network request');};vm.createContext(ctx);
for(const f of ['catalog.js','local-api.js'])vm.runInContext(fs.readFileSync(require('node:path').join(__dirname,'..',f),'utf8'),ctx);
async function api(path,body){const r=await ctx.fetch('/api/pokemon/'+path,{body:body?JSON.stringify(body):undefined});return {status:r.status,data:await r.json()};}
(async()=>{
assert.equal(Object.keys((await api('state')).data.overrides).length,0);
const s=ctx.POCKET_CATALOG.find(s=>s.cards.some(c=>c.rarity==='★'&&s.kind!=='promo')),c=s.cards.find(c=>c.rarity==='★'),key=s.code+':'+c.id;
await api('quantity',{account:'second',key,count:2});let trade=(await api('trade')).data;assert(trade.cards.some(c=>c.key===key));
let plan=(await api('trade',{action:'confirm',revision:trade.revision,balances:{main:5000,second:5000},selected:[key]})).data.plan;assert.equal(plan.remainingBalances.second,1000);
let bad=await api('quantity',{account:'second',key,count:-1});assert.equal(bad.status,400);
let backup=(await api('backup')).data;assert(!JSON.stringify(backup).includes('token'));assert.equal((await api('restore',backup)).status,200);assert.equal((await api('trade')).data.plan,null);
await api('quantity',{account:'second',key,count:0});assert.equal((await api('trade')).data.cards.length,0);
console.log('Offline state, quantity, comparison, budget, plan, backup/restore and invalid-input checks passed.');
})().catch(e=>{console.error(e);process.exit(1);});
