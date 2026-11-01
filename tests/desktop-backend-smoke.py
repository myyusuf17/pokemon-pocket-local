"""Exercise the exact bundled runtime on its native OS without UI or user accounts."""
import json,os,subprocess,sys,tempfile,time,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];stage=ROOT/'.desktop-build'
if sys.platform=='win32':cmd=[str(stage/'runtime/python/python.exe'),str(stage/'site/server.py')]
else:cmd=[str(stage/'runtime/pocket-backend/pocket-backend')]
with tempfile.TemporaryDirectory() as folder:
 token='test-session-token';env={**os.environ,'POCKET_SITE_ROOT':str(stage/'site'),'POCKET_DESKTOP_TOKEN':token,'PYTHONUNBUFFERED':'1','PYTHONUTF8':'1','PYTHONIOENCODING':'utf-8'}
 process=subprocess.Popen(cmd+['--port','0','--no-browser','--data-dir',folder],cwd=stage/'site',env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 try:
  line=process.stdout.readline().strip()
  if not line.startswith('Pocket Local: http://127.0.0.1:'):raise AssertionError(line+' '+process.stderr.read())
  base=line.removeprefix('Pocket Local: ')
  def req(path,body=None,authorized=True):
   headers={'Origin':base,'Content-Type':'application/json'}
   if authorized:headers['X-Pocket-Desktop-Token']=token
   request=urllib.request.Request(base+path,data=json.dumps(body).encode() if body is not None else None,headers=headers)
   with urllib.request.urlopen(request,timeout=10) as response:return json.load(response)
  try:req('/api/pokemon/state',authorized=False);raise AssertionError('Missing token accepted')
  except urllib.error.HTTPError as error:assert error.code==403
  assert req('/api/pokemon/state')['overrides']=={}
  req('/api/pokemon/quantity',{'account':'main','key':'A1:1','count':2})
  assert req('/api/pokemon/state')['quantities']['main']['A1:1']==2
  assert json.loads((Path(folder)/'collection.json').read_text(encoding='utf-8'))['quantities']['main']['A1:1']==2
  print('Bundled runtime: clean start, random port, session authorization and disk persistence passed.')
 finally:
  process.terminate();process.wait(timeout=10)
