/* Browser-only storage adapter. With the optional bridge the same UI uses disk storage. */
(()=>{
'use strict';
const nativeFetch=window.fetch.bind(window), bridge=window.POCKET_BRIDGE===true;
const embedded=location.protocol==='file:'&&window.parent&&window.parent!==window;
let relaySequence=0;const relayPending=new Map();
if(embedded){window.addEventListener('message',e=>{if(e.source!==window.parent||e.data?.type!=='pocket-response')return;const pending=relayPending.get(e.data.id);if(pending){clearTimeout(pending.timer);relayPending.delete(e.data.id);pending.resolve(new Response(JSON.stringify(e.data.data),{status:e.data.status}));}});document.addEventListener('DOMContentLoaded',()=>{document.querySelector('a[href="pokemon.html"]')?.addEventListener('click',e=>{e.preventDefault();window.parent.postMessage({type:'pocket-close-trade'},'*');});});}
const KEY='pocket-local-independent-v1',valid=new Set(POCKET_CATALOG.flatMap(s=>s.cards.map(c=>s.code+':'+c.id)));
const blank=()=>({format:'pocket-local-v1',collection:{revision:1,initialized:true,canEdit:true,overrides:{},secondOverrides:{},quantities:{}},trade:{revision:0,balances:{main:0,second:null},selected:[],plan:null}});
function load(){const raw=localStorage.getItem(KEY);return raw?JSON.parse(raw):blank();}
function save(d){localStorage.setItem(KEY,JSON.stringify(d));}
function fail(message){throw new Error(message);}
function validate(d){
 if(!d||d.format!=='pocket-local-v1'||!d.collection||!d.trade)fail('Geçerli bir Pocket Local JSON yedeği seç.');
 const result=blank(),c=d.collection;
 for(const field of ['overrides','secondOverrides']){
  const map=c[field]??{};if(!map||typeof map!=='object'||Array.isArray(map)||Object.entries(map).some(([k,v])=>!valid.has(k)||typeof v!=='boolean'))fail('Yedekte geçersiz kart kaydı var.');result.collection[field]={...map};
 }
 const quantities=c.quantities??{};if(typeof quantities!=='object'||!quantities||Array.isArray(quantities)||Object.keys(quantities).some(a=>!['main','second'].includes(a)))fail('Geçersiz adet kaydı.');
 for(const [a,map]of Object.entries(quantities)){
  if(!map||typeof map!=='object'||Array.isArray(map)||Object.entries(map).some(([k,v])=>!valid.has(k)||!Number.isInteger(v)||v<0||v>999999))fail('Geçersiz kart adedi.');
  result.collection.quantities[a]={...map};for(const [k,v]of Object.entries(map))result.collection[a==='main'?'overrides':'secondOverrides'][k]=v>0;
 }
 const b=d.trade.balances,selected=d.trade.selected;
 if(!b||Object.keys(b).sort().join(',')!=='main,second'||!Number.isInteger(b.main)||Object.values(b).some(v=>v!==null&&(!Number.isInteger(v)||v<0||v>1e9)))fail('Geçersiz bakiye.');
 if(!Array.isArray(selected)||selected.some(k=>!valid.has(k)))fail('Geçersiz plan seçimi.');
 result.trade.balances={...b};result.trade.selected=[...new Set(selected)];return result;
}
const COSTS={'♦':0,'♦♦':0,'♦♦♦':1200,'♦♦♦♦':5000,'★':4000,'★★':25000,'✦':10000,'✦✦':30000};
function tradeView(d){
 const state=d.collection,cards=[];
 for(const s of POCKET_CATALOG)for(const c of s.cards){
  const key=s.code+':'+c.id,q=state.quantities.second?.[key],second=Number.isInteger(q)?q>0:state.secondOverrides[key]===true,main=state.overrides[key]===true;
  if(!(c.special||c.rarityLevel>=5)||!second||main)continue;
  const reason=s.kind==='promo'?'Promo kartlar takas edilemiyor.':!Object.hasOwn(COSTS,c.rarity)?'Bu nadirlik takas edilemiyor.':'';
  cards.push({key,series:s.code,seriesName:s.name,id:c.id,name:c.name,rarity:c.rarity,rarityLabel:c.rarityLabel,cost:reason?null:COSTS[c.rarity],reason,copies:q??null,singleCopy:q===1});
 }
 return {...d.trade,enabled:true,cards,collectionRevision:state.revision,syncTimes:{main:null,second:null},costs:COSTS,checkedDate:'2026-10-30'};
}
function route(path,body){
 const d=load();
 if(path==='state')return d.collection;
 if(path==='backup')return d;
 if(path==='restore'){const clean=validate(body);clean.collection.revision=d.collection.revision+1;save(clean);return clean.collection;}
 if(path==='quantity'){
  const {account,key,count}=body;if(!['main','second'].includes(account)||!valid.has(key)||!Number.isInteger(count)||count<0||count>999999)fail('0–999999 arası tam sayı gir.');
  (d.collection.quantities[account]??={})[key]=count;d.collection[account==='main'?'overrides':'secondOverrides'][key]=count>0;d.collection.revision++;save(d);return d.collection;
 }
 if(path==='trade/availability')return {enabled:true};
 if(path==='import/status')return {intervalHours:24,accounts:Object.fromEntries(['main','second'].map(a=>[a,{configured:false,automatic:false,busy:false,game:{configured:false},error:''}]))};
 if(path.startsWith('import/'))fail('Otomatik aktarım için klasördeki Baslat.command (Mac) veya Baslat.bat (Windows) dosyasını çalıştır ve açılan yerel sayfayı kullan.');
 if(path==='trade'){
  let view=tradeView(d);if(!body)return view;
  if(body.revision!==d.trade.revision)fail('Plan başka sekmede değişti. Sayfayı yenile.');
  if(!['draft','confirm'].includes(body.action))fail('Geçersiz işlem.');
  validate({...d,trade:{...d.trade,balances:body.balances,selected:body.selected}});
  const items=body.selected.map(k=>view.cards.find(c=>c.key===k));if(items.some(c=>!c||c.cost===null))fail('Seçilen kart artık takasa uygun değil.');
  const total=items.reduce((n,c)=>n+c.cost,0),b=body.balances;
  if(body.action==='confirm'){
   if(!items.length||b.second===null||Object.values(b).some(v=>v<total))fail('Kart seç ve iki hesabın yeterli bakiyesini gir.');
   const pool=[];for(const s of POCKET_CATALOG)if(s.kind!=='promo')for(const c of s.cards){const key=s.code+':'+c.id,q=d.collection.quantities.main?.[key]??0;if(q>=2&&Object.hasOwn(COSTS,c.rarity))pool.push({...c,key,series:s.code,available:q-1});}
   for(const c of items){const p=pool.find(p=>p.rarity===c.rarity&&p.available>0);c.returnCard=p?{key:p.key,series:p.series,id:p.id,name:p.name,rarity:p.rarity}:null;if(p)p.available--;}
   d.trade.plan={id:String(Date.now()),createdAt:Math.floor(Date.now()/1000),collectionRevision:d.collection.revision,cards:items,costPerAccount:total,startingBalances:{...b},remainingBalances:{main:b.main-total,second:b.second-total},missingReturnCards:items.filter(c=>!c.returnCard).length,tradeStaminaPerAccount:items.length};
  }
  d.trade.balances={...b};d.trade.selected=[...body.selected];d.trade.revision++;save(d);return tradeView(d);
 }
 fail('İşlem bulunamadı.');
}
window.fetch=async(input,options={})=>{
 const url=String(input);
 // Keep file:// browsing independent of fetch/CORS for bundled card details.
 if(location.protocol==='file:'&&url.includes('pokemon-assets/v1/text/')){
  const key=url.split('/').pop().replace('.json','');const value=window.POCKET_TEXT?.[key];return new Response(JSON.stringify(value??{}),{status:value?200:404,headers:{'Content-Type':'application/json'}});
 }
 if(bridge||!url.includes('/api/pokemon/'))return nativeFetch(input,options);
 if(embedded)return new Promise((resolve,reject)=>{const id=++relaySequence,timer=setTimeout(()=>{relayPending.delete(id);reject(Error('Koleksiyon ekranıyla bağlantı kurulamadı.'));},10000);relayPending.set(id,{resolve,timer});window.parent.postMessage({type:'pocket-request',id,path:url.split('/api/pokemon/')[1].split('?')[0],body:options.body?JSON.parse(options.body):null},'*');});
 try{const part=url.split('/api/pokemon/')[1],path=part.split('?')[0],body=options.body?JSON.parse(options.body):null;let result=route(path,body);if(path==='state'&&new URLSearchParams(part.split('?')[1]).get('since')===String(result.revision))result={revision:result.revision,initialized:true};return new Response(JSON.stringify(result),{headers:{'Content-Type':'application/json'}});}
 catch(e){return new Response(JSON.stringify({error:e.message||'Tarayıcı kayıt alanı kullanılamıyor. Başlatıcıyı kullan.'}),{status:400,headers:{'Content-Type':'application/json'}});}
};
window.PocketLocal={bridge,validate,handleRequest:route};
})();
