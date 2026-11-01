"""Create a clean shareable archive from an explicit source allowlist."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import hashlib,json
ROOT=Path(__file__).resolve().parent
FILES=['index.html','pokemon.html','pokemon-trade.html','catalog.js','card-text.js','bridge.js','local-api.js','local-ui.js','local.css','server.py','backup.py','sync_store.py','pocket_import.py','pocket_game.py','trade_plan.py','connect_game.py','pokemon-trade-enabled','Baslat.command','Baslat.bat','README.md','.gitignore','package_release.py']

def paths():
    for name in FILES:
        p=ROOT/name
        if not p.is_file():raise SystemExit('Eksik proje dosyası: '+name)
        yield p
    for name in ['package.json','package-lock.json','RELEASE_NOTES.md','desktop/main.cjs','desktop/README.md','desktop/requirements-build.txt','scripts/prepare-desktop.py','scripts/release-browser.py','.github/workflows/desktop-release.yml']:
        p=ROOT/name
        if p.is_file():yield p
    for p in sorted((ROOT/'pokemon-assets'/'v1').rglob('*')):
        if p.is_file() and not p.is_symlink() and p.suffix in ('.webp','.json'):yield p
    for p in sorted((ROOT/'tests').glob('*')):
        if p.is_file() and p.suffix in ('.py','.cjs'):yield p

def main():
    output=ROOT.parent/'pokemon-pocket-local-paylasim.zip'
    entries=list(paths())
    if not any('pokemon-assets' in p.parts for p in entries):raise SystemExit('Kart görselleri henüz tamamlanmamış.')
    sensitive=['/srv/','/var/lib/','ssh root@']
    for p in entries:
        if p.suffix in ('.py','.js','.html','.md','.json','.cjs'):
            text=p.read_text()
            # Scanner's own list must not become a publication of private identifiers.
            if p.name!='package_release.py' and any(s in text for s in sensitive):raise SystemExit('Kişisel kaynak kalıntısı: '+str(p.relative_to(ROOT)))
    with ZipFile(output,'w',ZIP_DEFLATED,compresslevel=6) as archive:
        for p in entries:archive.write(p,Path('pokemon-pocket-local')/p.relative_to(ROOT))
    with ZipFile(output) as archive:
        if archive.testzip():raise SystemExit('ZIP bütünlük kontrolü başarısız.')
    print(f'Paylaşılabilir paket: {output}\n{len(entries)} dosya · {output.stat().st_size/1024/1024:.1f} MB')
if __name__=='__main__':main()
