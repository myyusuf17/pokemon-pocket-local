"""Optional loopback-only bridge for automatic collection import. Python standard library."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
import json, re, argparse, webbrowser, os, secrets, sys
from sync_store import Store, SyncError
from pocket_import import PocketImport
from trade_plan import TradePlan
if getattr(sys, 'frozen', False):
    import certifi
    os.environ.setdefault('SSL_CERT_FILE', certifi.where())
ROOT = Path(os.environ.get('POCKET_SITE_ROOT', Path(__file__).resolve().parent))
CATALOG = json.loads((ROOT/'catalog.js').read_text(encoding='utf-8').removeprefix('window.POCKET_CATALOG=').strip().removesuffix(';'))
VALID = {s['code']+':'+str(c['id']) for s in CATALOG for c in s['cards']}

def serve(port, open_browser=True, data_dir=None):
    folder=Path(data_dir) if data_dir else ROOT/'data';folder.mkdir(mode=0o700,parents=True,exist_ok=True)
    desktop_token=os.environ.get('POCKET_DESKTOP_TOKEN','')
    store=Store(folder, VALID)
    if not store.data['initialized']:
        store.data.update(initialized=True,revision=1,overrides={},secondOverrides={},quantities={})
        store.save()
    imports=PocketImport(folder,store)
    trade=TradePlan(folder,CATALOG,store,imports,ROOT/'pokemon-trade-enabled')
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
        def log_message(self,*args):pass
        def allowed(self):return self.headers.get('Host') in (f'127.0.0.1:{port}',f'localhost:{port}') and (not desktop_token or secrets.compare_digest(self.headers.get('X-Pocket-Desktop-Token',''),desktop_token))
        def reply(self,status,data):
            body=json.dumps(data,ensure_ascii=False).encode();self.send_response(status)
            self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff');self.send_header('Content-Length',str(len(body)));self.end_headers()
            if self.command!='HEAD':self.wfile.write(body)
        def do_HEAD(self):self.do_GET()
        def do_GET(self):
            if not self.allowed():self.reply(403,{'error':'Yerel adresi kullan.'});return
            path=urlsplit(self.path).path
            if path=='/bridge.js':
                body=('window.POCKET_BRIDGE=true;window.POCKET_DESKTOP='+('true' if desktop_token else 'false')+';').encode();self.send_response(200);self.send_header('Content-Type','text/javascript');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(body)));self.end_headers();
                if self.command!='HEAD':self.wfile.write(body)
                return
            if path=='/api/pokemon/state':
                state=store.public()
                if parse_qs(urlsplit(self.path).query).get('since',[''])[0]==str(state['revision']):state={'revision':state['revision'],'initialized':True}
                self.reply(200,state);return
            if path=='/api/pokemon/import/status':self.reply(200,imports.public());return
            if path=='/api/pokemon/trade/availability':self.reply(200,{'enabled':True});return
            if path=='/api/pokemon/trade':self.reply(200,trade.public());return
            if path=='/api/pokemon/backup':
                self.reply(200,{'format':'pocket-local-v1','collection':store.public(),'trade':trade._load()});return
            # Explicit public allowlist. Runtime files, Python source and links never leave the bridge.
            if path=='/':self.path='/index.html';path='/index.html'
            if path in {'/index.html','/pokemon.html','/pokemon-trade.html','/catalog.js','/local-api.js','/local-ui.js','/local.css','/card-text.js','/README.md'} or re.fullmatch(r'/pokemon-assets/v1/(thumb|detail|logo|text)/[A-Za-z0-9-]+\.(webp|json)',path):
                super().do_GET() if self.command=='GET' else super().do_HEAD()
            else:self.reply(404,{'error':'Bulunamadı.'})
        def do_POST(self):
            if not self.allowed() or self.headers.get('Origin') not in (f'http://127.0.0.1:{port}',f'http://localhost:{port}') or self.headers.get('Content-Type','').split(';')[0]!='application/json':
                self.reply(403,{'error':'İstek doğrulanamadı.'});return
            try:
                n=int(self.headers.get('Content-Length','0'))
                if not 0<n<=3*1024*1024:raise SyncError(413,'İstek çok büyük veya boş.')
                self.connection.settimeout(15);d=json.loads(self.rfile.read(n))
                if not isinstance(d,dict):raise SyncError(400,'Geçersiz kayıt.')
                path=urlsplit(self.path).path
                if path=='/api/pokemon/quantity':
                    account=d.get('account');key=d.get('key');count=d.get('count')
                    if account not in ('main','second') or key not in VALID or type(count) is not int or not 0<=count<=999999:raise SyncError(400,'Geçersiz kart adedi.')
                    with store.lock:
                        store.data.setdefault('quantities',{}).setdefault(account,{})[key]=count
                        store.data.setdefault('overrides' if account=='main' else 'secondOverrides',{})[key]=count>0
                        store.data['revision']+=1;store.save()
                    result=store.public()
                elif path=='/api/pokemon/changes':result=store.patch('',d.get('revision'),d.get('changes'))
                elif path=='/api/pokemon/restore':
                    from backup import validate_backup
                    c,t=validate_backup(d,VALID)
                    with store.lock,trade.lock:
                        backup=folder/'before-restore.json';backup.write_text(json.dumps({'collection':store.public(),'trade':trade._load()}),encoding='utf-8');backup.chmod(0o600)
                        # Any previous connected accounts are disconnected before replacing user data.
                        for a in ('main','second'):imports.disconnect(a)
                        store.data.update(c,revision=store.data['revision']+1,initialized=True);store.save();trade._save(t)
                    result=store.public()
                elif path=='/api/pokemon/trade':result=trade.change(d)
                elif path.startswith('/api/pokemon/import/'):
                    action=path.rsplit('/',1)[-1];a=d.get('account')
                    if action=='connect':result=imports.connect(a,d.get('exportUrl'),d.get('automatic',True))
                    elif action=='sync':result=imports.sync(a)
                    elif action=='settings':result=imports.settings(a,d.get('automatic'))
                    elif action=='disconnect':result=imports.disconnect(a)
                    elif action=='game-disconnect':result=imports.game_disconnect(a)
                    else:raise SyncError(404,'İşlem bulunamadı.')
                else:raise SyncError(404,'İşlem bulunamadı.')
                self.reply(200,result)
            except SyncError as e:self.reply(e.status,{'error':e.message})
            except (ValueError,TypeError,KeyError):self.reply(400,{'error':'Dosya veya istek geçersiz.'})
            except OSError:self.reply(503,{'error':'Yerel kayıt okunamadı veya kaydedilemedi.'})
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler);port=server.server_port;imports.start()
    url=f'http://127.0.0.1:{port}'
    print(f'Pocket Local: {url}\nDurdurmak için Ctrl+C. Bu pencere açıkken otomatik aktarım çalışır.',flush=True)
    if open_browser:webbrowser.open(url)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8795);parser.add_argument('--no-browser',action='store_true');parser.add_argument('--data-dir');args=parser.parse_args()
    serve(args.port,not args.no_browser,args.data_dir)
