"""Read-only DotGG collection import. No Nintendo credentials are accepted."""
import csv
import io
import json
import os
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from sync_store import SyncError
from pocket_game import PocketGame

INTERVAL = 24 * 60 * 60
MAX_BYTES = 2 * 1024 * 1024


def export_token(value):
    if not isinstance(value, str) or len(value) > 1000:
        raise SyncError(400, 'Kalıcı dışa aktarma bağlantısını yapıştır.')
    try:
        u = urllib.parse.urlsplit(value.strip())
        query = urllib.parse.parse_qs(u.query, strict_parsing=True)
        token = query.get('token', [''])[0]
        valid = (u.scheme == 'https' and u.netloc == 'api.dotgg.gg'
                 and u.path == '/cgfw/exportcollection' and not u.fragment
                 and query.get('game') == ['pokepocket']
                 and len(query.get('token', [])) == 1
                 and set(query) == {'game', 'token'}
                 and re.fullmatch(r'[0-9a-fA-F]{48}', token))
    except ValueError:
        valid = False
    if not valid:
        raise SyncError(400, 'ptcgpocket.gg hesabındaki Pokémon TCG Pocket kalıcı dışa aktarma bağlantısını kullan. Binder bağlantıları desteklenmiyor.')
    return token


def read_collection(raw, valid_keys):
    """Match only exact expansion/number IDs, never card names or shared game IDs."""
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeError:
        raise SyncError(502, 'Kart listesi okunamadı. Mevcut kayıtların korundu.')
    rows = csv.DictReader(io.StringIO(text))
    fields=set(rows.fieldnames or [])
    if not {'Normal','Foil'}.issubset(fields) or not ('CardId' in fields or {'Set','Number'}.issubset(fields)):
        raise SyncError(502, 'Servis beklenen kart listesini göndermedi. Mevcut kayıtların korundu.')
    quantities, unknown = {}, set()
    codes={key.rsplit(':',1)[0].casefold():key.rsplit(':',1)[0] for key in valid_keys}
    aliases={'p-a':'promo-a','p-b':'promo-b','p-c':'promo-c'}
    for index, row in enumerate(rows):
        if index >= 20000 or None in row:
            raise SyncError(502, 'Kart listesi geçersiz. Mevcut kayıtların korundu.')
        if not any(row.values()):
            continue
        counts = []
        for field in ['Normal', 'Foil']:
            value = row.get(field)
            if not isinstance(value, str) or not re.fullmatch(r'\d{1,6}', value.strip()):
                raise SyncError(502, 'Kart adetleri geçersiz. Mevcut kayıtların korundu.')
            counts.append(int(value))
        count = sum(counts)
        card = row.get('CardId', '').strip()
        if not card and {'Set','Number'}.issubset(fields):
            card = row.get('Set','').strip()+'-'+row.get('Number','').strip()
        match = re.fullmatch(r'([A-Za-z][A-Za-z0-9-]*)[-:](\d{1,3})', card)
        code=aliases.get(match[1].casefold(),match[1].casefold()) if match else ''
        canonical=codes.get(code)
        key = canonical+':'+str(int(match[2])) if canonical and match else None
        if key not in valid_keys:
            if count:
                unknown.add(card)
            continue
        quantities[key] = max(quantities.get(key, 0), count)
    if not any(quantities.values()):
        raise SyncError(422, 'Bu bağlantıda eşleşen sahip olunan kart yok. Önce ptcgpocket.gg üzerinde oyun koleksiyonunu senkronize et. Mevcut kayıtların korundu.')
    return quantities, len(unknown)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class PocketImport:
    def __init__(self, folder, store):
        self.folder = Path(folder)
        self.path = self.folder / 'pocket-import-links.json'
        self.store = store
        self.game = PocketGame(folder)
        self.lock = threading.RLock()
        self.busy = set()
        self.links = json.loads(self.path.read_text()) if self.path.exists() else {}
        self.opener = urllib.request.build_opener(NoRedirect())

    def save(self):
        self.folder.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix('.tmp')
        with open(temp, 'w', encoding='utf-8') as f:
            os.chmod(temp, 0o600)
            json.dump(self.links, f, ensure_ascii=False, separators=(',', ':'))
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, self.path)

    @staticmethod
    def account(value):
        if value not in ('main', 'second'):
            raise SyncError(400, 'Ana hesap veya ikinci hesap seçilmeli.')
        return value

    def public(self):
        with self.lock:
            return {'intervalHours': INTERVAL // 3600, 'accounts': {
                account: {**{k: link.get(k) for k in ('lastSync', 'nextSync', 'result', 'error')},
                          'configured': bool(link.get('token')),
                          'automatic': bool(link.get('automatic')),
                          'busy': account in self.busy,
                          'game': self.game.public(account, link.get('token'))}
                for account in ('main', 'second')
                for link in [self.links.get(account, {})]
            }}

    def fetch(self, token):
        url = 'https://api.dotgg.gg/cgfw/exportcollection?' + urllib.parse.urlencode({'game': 'pokepocket', 'token': token})
        request = urllib.request.Request(url, headers={'User-Agent': 'PocketLocal/1.0', 'Accept': 'text/csv'})
        try:
            with self.opener.open(request, timeout=30) as r:
                raw = r.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise SyncError(502, 'Kart listesi beklenenden büyük. Mevcut kayıtların korundu.')
            return read_collection(raw, self.store.valid)
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                raise SyncError(401, 'Dışa aktarma bağlantısı geçersiz veya iptal edilmiş. ptcgpocket.gg üzerinden yeni bağlantı al.')
            raise SyncError(502, 'ptcgpocket.gg şu anda yanıt vermiyor. Mevcut kayıtların korundu.')
        except (OSError, ValueError):
            raise SyncError(502, 'Kart servisine ulaşılamadı. Mevcut kayıtların korundu; biraz sonra tekrar dene.')

    def connect(self, account, url, automatic):
        account = self.account(account)
        token = export_token(url)
        if type(automatic) is not bool:
            raise SyncError(400, 'Otomatik aktarım seçimi geçersiz.')
        with self.lock:
            if account in self.busy:
                raise SyncError(409, 'Bu hesap zaten güncelleniyor.')
            if any(a != account and link.get('token') == token for a, link in self.links.items()):
                raise SyncError(400, 'Bu bağlantı diğer hesaba ait. İkinci hesap için farklı ptcgpocket.gg hesabının bağlantısını kullan.')
            self.busy.add(account)
        try:
            quantities, unmapped = self.fetch(token)
            result = self.store.import_cards(account, quantities, unmapped)
            now = int(time.time())
            with self.lock:
                self.links[account] = {'token': token, 'automatic': automatic, 'lastSync': now, 'lastAttempt': now,
                                       'nextSync': now + INTERVAL, 'result': result, 'error': ''}
                self.save()
        finally:
            with self.lock:
                self.busy.discard(account)
        return self.public()

    def sync(self, account):
        account = self.account(account)
        with self.lock:
            link = self.links.get(account)
            if not link:
                raise SyncError(400, 'Önce bu hesabın dışa aktarma bağlantısını ekle.')
            if account in self.busy:
                raise SyncError(409, 'Bu hesap zaten güncelleniyor.')
            if time.time() < link.get('lastAttempt', 0) + 60:
                raise SyncError(429, 'Tekrar güncellemeden önce bir dakika bekle.')
            self.busy.add(account)
            token = link['token']
            link['lastAttempt'] = int(time.time())
        try:
            self.game.refresh(account, token)
            quantities, unmapped = self.fetch(token)
            result = self.store.import_cards(account, quantities, unmapped)
            with self.lock:
                link.update(lastSync=int(time.time()), result=result, error='')
        except SyncError as e:
            with self.lock:
                link['error'] = e.message
            raise
        finally:
            with self.lock:
                link['nextSync'] = int(time.time()) + INTERVAL
                self.busy.discard(account)
                self.save()
        return self.public()

    def settings(self, account, automatic):
        account = self.account(account)
        if type(automatic) is not bool:
            raise SyncError(400, 'Otomatik aktarım seçimi geçersiz.')
        with self.lock:
            if account not in self.links:
                raise SyncError(400, 'Önce hesabı bağla.')
            self.links[account]['automatic'] = automatic
            self.save()
        return self.public()

    def disconnect(self, account):
        account = self.account(account)
        with self.lock:
            if account in self.busy:
                raise SyncError(409, 'Aktarım bitince bağlantıyı kaldırabilirsin.')
            self.game.disconnect(account)
            self.links.pop(account, None)
            self.save()
        return self.public()

    def game_disconnect(self, account):
        account = self.account(account)
        with self.lock:
            if account in self.busy:
                raise SyncError(409, 'Aktarım bitince oyun yetkisini kaldırabilirsin.')
            self.game.disconnect(account)
        return self.public()

    def start(self):
        def worker():
            while True:
                time.sleep(60)
                with self.lock:
                    due = [a for a, link in self.links.items() if link.get('automatic')
                           and time.time() >= link.get('nextSync', 0) and a not in self.busy]
                for account in due:
                    try:
                        self.sync(account)
                    except SyncError:
                        pass
                    except Exception:
                        with self.lock:
                            if account in self.links:
                                self.links[account]['nextSync'] = int(time.time()) + INTERVAL
                                self.links[account]['error'] = 'Aktarım tamamlanamadı. Mevcut kayıtların korundu.'
                                self.save()
        threading.Thread(target=worker, name='pocket-import', daemon=True).start()
