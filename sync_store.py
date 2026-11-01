import hashlib,json,os,secrets,threading,time
from pathlib import Path

class SyncError(Exception):
    def __init__(self,status,message):self.status=status;self.message=message

class Store:
    def __init__(self,folder,valid):
        self.folder=Path(folder);self.path=self.folder/'collection.json';self.lock=threading.RLock();self.valid=set(valid);self.attempts={}
        self.data=json.loads(self.path.read_text(encoding='utf-8')) if self.path.exists() else {'revision':0,'initialized':False,'overrides':{},'devices':[]}
    def save(self):
        self.folder.mkdir(parents=True,exist_ok=True)
        temp=self.path.with_suffix('.tmp')
        with open(temp,'w',encoding='utf-8') as f:
            os.chmod(temp,0o600);json.dump(self.data,f,ensure_ascii=False,separators=(',',':'));f.flush();os.fsync(f.fileno())
        os.replace(temp,self.path)
    @staticmethod
    def digest(value):return hashlib.sha256(value.encode()).hexdigest()
    def authorized(self,token):return bool(token) and self.digest(token) in self.data['devices']
    def public(self,token=''):
        with self.lock:return {'revision':self.data['revision'],'initialized':self.data['initialized'],'overrides':self.data['overrides'].copy(),'canEdit':self.data['initialized'],'secondOverrides':self.data.get('secondOverrides',{}).copy(),'quantities':self.data.get('quantities',{})}
    def bootstrap(self,ip,allowed):
        with self.lock:
            if ip!=allowed or self.data['devices']:raise SyncError(403,'Bu bağlantı kullanılamıyor.')
            token=secrets.token_urlsafe(32);self.data['devices'].append(self.digest(token));self.save();return token
    def validate(self,changes):
        if not isinstance(changes,dict) or any(k not in self.valid or type(v) is not bool for k,v in changes.items()):raise SyncError(400,'Geçersiz kart kaydı.')
    def import_computer(self,token,changes):
        with self.lock:
            if not self.authorized(token):raise SyncError(401,'Cihazı bağlaman gerekiyor.')
            if self.data['initialized']:raise SyncError(409,'Bilgisayar kaydı zaten aktarıldı.')
            self.validate(changes)
            if set(changes)!=self.valid:raise SyncError(400,'Bilgisayar kaydı eksik.')
            backup=self.folder/'initial-computer-backup.json'
            with open(backup,'x',encoding='utf-8') as f:os.chmod(backup,0o600);json.dump({'capturedAt':time.time(),'overrides':changes},f,ensure_ascii=False)
            self.data.update(initialized=True,revision=1,overrides=changes.copy());self.save();return self.public(token)
    def patch(self,token,revision,changes):
        with self.lock:
            if not self.data['initialized']:raise SyncError(409,'Önce bilgisayar kaydı aktarılmalı.')
            self.validate(changes)
            if type(revision) is not int or revision!=self.data['revision']:raise SyncError(409,'Kayıt başka bir cihazda güncellendi.')
            self.data['overrides'].update(changes);self.data['revision']+=1;self.save();return self.public(token)

    def import_cards(self,account,quantities,unmapped):
        if account not in ('main','second') or not quantities or any(k not in self.valid or type(v) is not int or v<0 for k,v in quantities.items()):
            raise SyncError(400,'Geçersiz aktarım.')
        with self.lock:
            if not self.data['initialized']:raise SyncError(409,'Önce mevcut koleksiyon hazırlanmalı.')
            # Backup precedes every successful import; failed reads never reach here.
            history=self.folder/'pokemon-import-history';history.mkdir(mode=0o700,exist_ok=True)
            name=f'{time.time_ns()}-{account}.json'
            with open(history/name,'x',encoding='utf-8') as f:
                os.chmod(history/name,0o600);json.dump(self.data,f,ensure_ascii=False,separators=(',',':'));f.flush();os.fsync(f.fileno())
            target=self.data['overrides'] if account=='main' else self.data.setdefault('secondOverrides',{})
            added=0
            for key,count in quantities.items():
                if count>0:
                    if not target.get(key):added+=1
                    target[key]=True
            # Counts describe the last export. Manual presence remains independent.
            self.data.setdefault('quantities',{})[account]=quantities.copy()
            self.data['revision']+=1
            self.save()
            return {'matched':len(quantities),'owned':sum(n>0 for n in quantities.values()),'copies':sum(quantities.values()),'marked':added,'unmapped':unmapped}
