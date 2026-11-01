"""Prepare a clean UI and bundled Python runtime. Never copy data or account links."""
import argparse,os,shutil,subprocess,sys,urllib.request,zipfile,ssl
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from package_release import paths
parser=argparse.ArgumentParser();parser.add_argument('--platform',choices=['mac','windows'],required=True);parser.add_argument('--pyinstaller',default=sys.executable);args=parser.parse_args()
staging=ROOT/'.desktop-build';site=staging/'site';runtime=staging/'runtime'
site.mkdir(parents=True,exist_ok=True)
if runtime.exists():shutil.rmtree(runtime)
runtime.mkdir(parents=True,exist_ok=True)
for p in paths():
 relative=p.relative_to(ROOT)
 if relative.parts[0] in ('tests','desktop','scripts','.github') or p.name in ('Baslat.command','Baslat.bat','package_release.py','package.json','package-lock.json'):continue
 target=site/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
if args.platform=='mac':
 output=staging/'frozen';work=staging/'pyinstaller'
 subprocess.run([args.pyinstaller,'-m','PyInstaller','--noconfirm','--clean','--onedir','--collect-data','certifi','--name','pocket-backend','--distpath',str(output),'--workpath',str(work),'--specpath',str(work),str(ROOT/'server.py')],cwd=ROOT,check=True)
 target=runtime/'pocket-backend'
 if target.exists():shutil.rmtree(target)
 shutil.copytree(output/'pocket-backend',target)
else:
 archive=staging/'python-3.14.10-embed-amd64.zip'
 url='https://www.python.org/ftp/python/3.14.10/python-3.14.10-embed-amd64.zip'
 if not archive.exists():
  try:
   import certifi
   context=ssl.create_default_context(cafile=certifi.where())
  except ImportError:context=ssl.create_default_context()
  with urllib.request.urlopen(url,context=context,timeout=60) as response:archive.write_bytes(response.read())
 target=runtime/'python';target.mkdir(exist_ok=True)
 with zipfile.ZipFile(archive) as z:z.extractall(target)
 pth=next(target.glob('python*._pth'));text=pth.read_text()
 text=text.replace('../site','../../site')
 if '../../site' not in text:text+='\n../../site\n'
 pth.write_text(text)
print('Prepared',args.platform,'desktop resources:',staging)
