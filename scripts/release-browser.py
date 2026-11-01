"""Create the browser-only member of the three download options."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import json,sys,re
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from package_release import paths
version=json.loads((ROOT/'package.json').read_text(encoding='utf-8'))['version']
out=ROOT/'releases'/f'Pocket-Local-{version}-web.zip';out.parent.mkdir(exist_ok=True)
allowed={'.html','.js','.css','.webp','.json'}
with ZipFile(out,'w',ZIP_DEFLATED,compresslevel=6) as z:
 for p in paths():
  rel=p.relative_to(ROOT)
  if rel.parts[0] in ('tests','desktop','scripts','.github') or p.name=='package.json' or p.name=='package-lock.json':continue
  if p.suffix in allowed:
   if p.name=='index.html':
    html=p.read_text(encoding='utf-8')
    html=re.sub(r'<details><summary>Oyun koleksiyonumu otomatik aktarabilir miyim\?</summary>.*?</details>', '<details><summary>Oyun koleksiyonumu otomatik aktarabilir miyim?</summary><p>Bu ZIP yalnızca tarayıcı sürümüdür. Otomatik aktarım için Mac veya Windows masaüstü paketini indir. Masaüstü uygulamasında Python kurulumu ve terminal gerekmez. Kayıtlarını taşımak için Hesaplar menüsünden JSON yedeği alıp uygulamada yükle.</p></details>',html,flags=re.S)
    z.writestr(str(Path('Pocket-Local-Web')/rel),html)
   else:z.write(p,Path('Pocket-Local-Web')/rel)
 z.writestr('Pocket-Local-Web/BENI-OKU.txt','Pocket Local — Tarayıcı sürümü\n\nZIP dosyasını çıkarıp index.html dosyasına çift tıklayın.\nKartlar tarayıcıda tutulur; indirilen yedekler dosyadır. Hesaplar menüsünden düzenli JSON yedeği alın.\nOtomatik oyun aktarımı için Mac veya Windows uygulamasını kullanın.\nBu paket önceki kullanıcının kişisel verilerini içermez.\n')
print(out)
