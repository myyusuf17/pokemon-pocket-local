"""Optional local onboarding. No secrets in shell arguments or output."""
import getpass,json
from pathlib import Path
from pocket_game import PocketGame
from sync_store import SyncError
folder=Path(__file__).resolve().parent/'data'
print('Önce yerel uygulamanın Hesaplar menüsünden kalıcı dışa aktarma bağlantını ekle.')
account=input('Hesap (ana için main, ikinci için second): ').strip()
try:
    links=json.loads((folder/'pocket-import-links.json').read_text())
    token=links.get(account,{}).get('token')
    if not token:raise SyncError(400,'Önce bu hesabın dışa aktarma bağlantısını ekle.')
    auth=getpass.getpass('Kendi DotGG API yetkin (ekranda görünmez; Nintendo şifresi değil): ')
    result=PocketGame(folder).connect(account,auth,token)
    print('Oyun yenileme yetkisi bağlandı. Yerel uygulamadan Şimdi aktar düğmesini kullanabilirsin.')
except (OSError,ValueError):print('Hesap bağlantısı okunamadı. Önce başlatıcıyı kullanarak hesabı bağla.');raise SystemExit(1)
except SyncError as e:print(e.message);raise SystemExit(1)
