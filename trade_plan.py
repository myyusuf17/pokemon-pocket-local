"""Optional, shared trade planning. Never changes collection or game accounts."""
import copy,json,os,threading,time,uuid
from pathlib import Path
from sync_store import SyncError
COSTS={'♦':0,'♦♦':0,'♦♦♦':1200,'♦♦♦♦':5000,'★':4000,'★★':25000,'✦':10000,'✦✦':30000}
class TradePlan:
 def __init__(self,folder,catalog,store,imports,flag):
  self.path=Path(folder)/'pokemon-trade-plan.json';self.catalog=catalog;self.store=store;self.imports=imports;self.flag=Path(flag);self.lock=threading.RLock()
 def enabled(self):return self.flag.exists()
 def _load(self):
  return json.loads(self.path.read_text()) if self.path.exists() else {'revision':0,'balances':{'main':0,'second':None},'selected':[],'plan':None}
 def _save(self,d):
  tmp=self.path.with_suffix('.tmp')
  with open(tmp,'w') as f:
   os.chmod(tmp,0o600);json.dump(d,f,ensure_ascii=False,separators=(',',':'));f.flush();os.fsync(f.fileno())
  os.replace(tmp,self.path)
 def cards(self,state):
  result=[]
  for s in self.catalog:
   for c in s['cards']:
    if not (c.get('special') or c.get('rarityLevel',0)>=5):continue
    key=s['code']+':'+str(c['id']);q=state.get('quantities',{}).get('second',{}).get(key)
    second=q>0 if type(q) is int else state.get('secondOverrides',{}).get(key,c.get('second',False))
    main=state.get('overrides',{}).get(key,not c.get('missing',False))
    if not second or main:continue
    reason='Promo kartlar takas edilemiyor.' if s.get('kind')=='promo' else 'Bu nadirlik takas edilemiyor.' if c['rarity'] not in COSTS else ''
    result.append({'key':key,'series':s['code'],'seriesName':s['name'],'id':c['id'],'name':c['name'],'rarity':c['rarity'],'rarityLabel':c['rarityLabel'],'cost':COSTS.get(c['rarity']) if not reason else None,'reason':reason,'copies':q,'singleCopy':q==1})
  return sorted(result,key=lambda c:(c['cost'] is None,c['series'],c['id']))
 def public(self):
  if not self.enabled():raise SyncError(404,'Trade planlayıcısı kapalı.')
  with self.lock:
   d=self._load();state=self.store.public();cards=self.cards(state);status=self.imports.public()
   return {**copy.deepcopy(d),'enabled':True,'cards':cards,'collectionRevision':state['revision'],'syncTimes':{a:v.get('lastSync') for a,v in status['accounts'].items()},'costs':COSTS,'checkedDate':'2026-10-30'}
 def _returns(self,selected,state):
  pool=[]
  for s in self.catalog:
   if s.get('kind')=='promo':continue
   for c in s['cards']:
    key=s['code']+':'+str(c['id']);q=state.get('quantities',{}).get('main',{}).get(key,0)
    if c['rarity'] in COSTS and type(q) is int and q>=2:pool.append({'key':key,'series':s['code'],'id':c['id'],'name':c['name'],'rarity':c['rarity'],'available':q-1})
  pool.sort(key=lambda c:(-c['available'],c['series'],c['id']))
  for item in selected:
   match=next((c for c in pool if c['rarity']==item['rarity'] and c['available']>0),None)
   item['returnCard']={k:v for k,v in match.items() if k!='available'} if match else None
   if match:match['available']-=1
 def change(self,body):
  if not self.enabled():raise SyncError(404,'Trade planlayıcısı kapalı.')
  with self.lock:
   d=self._load()
   if type(body.get('revision')) is not int or body['revision']!=d['revision']:raise SyncError(409,'Plan başka cihazda değişti. Güncel plan yüklendi; seçimini tekrar kontrol et.')
   action=body.get('action')
   if action not in ('draft','confirm'):raise SyncError(400,'Geçersiz plan işlemi.')
   balances=body.get('balances');keys=body.get('selected')
   if not isinstance(balances,dict) or set(balances)!={'main','second'} or any(v is not None and (type(v) is not int or not 0<=v<=1000000000) for v in balances.values()):raise SyncError(400,'Stardust bakiyesi sıfır veya pozitif tam sayı olmalı.')
   if type(balances.get('main')) is not int:raise SyncError(400,'Ana hesap bakiyesini gir.')
   if not isinstance(keys,list) or len(keys)>2000 or any(not isinstance(k,str) for k in keys) or len(keys)!=len(set(keys)):raise SyncError(400,'Geçersiz kart seçimi.')
   state=self.store.public();cards={c['key']:c for c in self.cards(state)}
   if any(k not in cards or cards[k]['cost'] is None for k in keys):raise SyncError(409,'Seçilen kartlardan biri artık uygun değil. Koleksiyonu yenileyip tekrar seç.')
   total=sum(cards[k]['cost'] for k in keys)
   if action=='confirm':
    if not keys:raise SyncError(400,'Önce en az bir kart seç.')
    if balances['second'] is None:raise SyncError(400,'Yedek hesabının stardust bakiyesini gir.')
    if any(total>v for v in balances.values()):raise SyncError(400,'Seçim iki hesaptan birinin stardust bakiyesini aşıyor.')
    items=[dict(cards[k]) for k in keys];self._returns(items,state)
    remaining={a:v-total for a,v in balances.items()}
    d['plan']={'id':str(uuid.uuid4()),'createdAt':int(time.time()),'collectionRevision':state['revision'],'cards':items,'costPerAccount':total,'startingBalances':balances.copy(),'remainingBalances':remaining,'missingReturnCards':sum(c['returnCard'] is None for c in items),'tradeStaminaPerAccount':len(items)}
   d.update(balances=balances.copy(),selected=keys.copy(),revision=d['revision']+1);self._save(d)
   return self.public()
