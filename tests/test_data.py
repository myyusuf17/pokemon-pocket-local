import sys,unittest,tempfile,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backup import validate_backup
from sync_store import SyncError,Store
from pocket_import import read_collection,export_token
from trade_plan import TradePlan
class DataTests(unittest.TestCase):
 def backup(self):return {'format':'pocket-local-v1','collection':{'overrides':{},'secondOverrides':{},'quantities':{'main':{'A1:1':0}}},'trade':{'balances':{'main':0,'second':None},'selected':[],'plan':None}}
 def test_counts_override_presence(self):
  d=self.backup();d['collection']['overrides']['A1:1']=True;c,t=validate_backup(d,{'A1:1'});self.assertFalse(c['overrides']['A1:1'])
 def test_invalid_backups(self):
  for value in [-1,True,1000000,'1']:
   d=self.backup();d['collection']['quantities']['main']['A1:1']=value
   with self.assertRaises(SyncError):validate_backup(d,{'A1:1'})
 def test_no_credentials_restored(self):
  d=self.backup();d['collection']['devices']=['private'];c,t=validate_backup(d,{'A1:1'});self.assertNotIn('devices',c)
 def test_csv_exact_identifiers(self):
  q,n=read_collection(b'CardId,Normal,Foil\nA1-001,2,1\nA1-002,1,0\n',{'A1:1'});self.assertEqual(q,{'A1:1':3});self.assertEqual(n,1)
 def test_invalid_export_destination(self):
  with self.assertRaises(SyncError):export_token('https://example.org/?token=abc')
 def test_trade_and_counter_card(self):
  with tempfile.TemporaryDirectory() as folder:
   store=Store(folder,{'A1:1','A1:2'});store.data.update(initialized=True,overrides={'A1:2':True},secondOverrides={'A1:1':True},quantities={'main':{'A1:2':2},'second':{'A1:1':2}});store.save()
   class Imports:
    def public(self):return {'accounts':{}}
   flag=Path(folder)/'enabled';flag.touch()
   catalog=[{'code':'A1','name':'Example','cards':[{'id':i,'name':f'İğne ★ {i}','rarity':'★','rarityLabel':'1 yıldız','rarityLevel':5,'missing':True} for i in (1,2)]}]
   trade=TradePlan(folder,catalog,store,Imports(),flag)
   self.assertEqual(trade.public()['balances']['main'],0)
   plan=trade.change({'action':'confirm','revision':0,'balances':{'main':5000,'second':5000},'selected':['A1:1']})['plan']
   self.assertEqual(plan['remainingBalances']['second'],1000);self.assertEqual(plan['cards'][0]['returnCard']['key'],'A1:2');self.assertNotIn('A1:1',store.data['overrides']);self.assertEqual(TradePlan(folder,catalog,store,Imports(),flag).public()['plan']['cards'][0]['name'],'İğne ★ 1')
if __name__=='__main__':unittest.main()
