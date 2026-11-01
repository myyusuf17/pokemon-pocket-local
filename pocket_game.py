"""Optional authenticated DotGG game refresh. Credentials never enter public JSON."""
import hashlib
import hmac
import json
import os
import re
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from sync_store import SyncError

BASE = 'https://api.dotgg.gg/cgfw/'
MAX_RESPONSE = 256 * 1024

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

class PocketGame:
    def __init__(self, folder, transport=None, clock=None):
        self.folder = Path(folder)
        self.path = self.folder / 'pocket-game-links.json'
        self.lock = threading.RLock()
        self.request_lock = threading.Lock()
        self.last_request = 0
        self.clock = clock or time.time
        self.transport = transport or self._request

    def _load(self):
        return json.loads(self.path.read_text()) if self.path.exists() else {}

    def _save(self, data):
        self.folder.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix('.tmp')
        with open(temp, 'w', encoding='utf-8') as f:
            os.chmod(temp, 0o600)
            # When run as root, match the existing state file
            # owner so the local process can read the new credential.
            reference = self.folder / 'pocket-import-links.json'
            if getattr(os, 'geteuid', lambda: 1)() == 0 and reference.exists():
                owner = reference.stat()
                os.fchown(f.fileno(), owner.st_uid, owner.st_gid)
            json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, self.path)

    @staticmethod
    def _account(account):
        if account not in ('main', 'second'):
            raise SyncError(400, 'Ana hesap veya ikinci hesap seçilmeli.')
        return account

    @staticmethod
    def _auth(value):
        if not isinstance(value, str) or not re.fullmatch(r'[1-9][0-9]{0,17}:[A-Za-z0-9._~+/=-]{8,1024}', value):
            raise SyncError(400, 'Geçerli bir DotGG API yetkisi gerekiyor.')
        return value

    @staticmethod
    def _fingerprint(token):
        return hashlib.sha256(token.encode()).hexdigest()

    def _request(self, action, auth):
        if action not in ('pocketstatus', 'pocketsync', 'exporttoken'):
            raise SyncError(400, 'Geçersiz oyun işlemi.')
        request = urllib.request.Request(BASE + action + '?game=pokepocket',
            method='POST' if action == 'pocketsync' else 'GET',
            headers={'Dotgguserauth': auth, 'Accept': 'application/json', 'User-Agent': 'PocketLocal/2.0'})
        try:
            with self.request_lock:
                delay = 1 - (time.monotonic() - self.last_request)
                if delay > 0:
                    time.sleep(delay)
                self.last_request = time.monotonic()
                with urllib.request.build_opener(NoRedirect()).open(request, timeout=30 if action == 'pocketsync' else 10) as response:
                    raw = response.read(MAX_RESPONSE + 1)
            if len(raw) > MAX_RESPONSE:
                raise ValueError()
            result = json.loads(raw)
            if not isinstance(result, dict):
                raise ValueError()
            return result
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                raise SyncError(401, 'DotGG yetkisi geçersiz. Oyun bağlantısını bu bilgisayardan yeniden yetkilendir.')
            raise SyncError(502, 'Oyun servisi yanıt vermedi. İşlem tekrar gönderilmedi; durumu biraz sonra kontrol et.')
        except (OSError, ValueError):
            raise SyncError(502, 'Oyun servisine ulaşılamadı. İşlem tekrar gönderilmedi; durumu biraz sonra kontrol et.')

    @staticmethod
    def _status(response):
        status = response if type(response.get('connected')) is bool else response.get('status')
        if not isinstance(status, dict):
            raise SyncError(401, 'DotGG oyun durumu okunamadı. Yetkilendirmeyi kontrol et.')
        return status

    def _record(self, link, status):
        now = int(self.clock())
        link['checkedAt'] = now
        for source, target in [('connected', 'connected'), ('syncing', 'syncing'),
                ('auto_sync', 'autoSync'), ('needs_reconnect', 'needsReconnect')]:
            if type(status.get(source)) is bool:
                link[target] = status[source]
        for source, target in [('last_synced', 'lastGameSync'), ('fail_count', 'failCount')]:
            if type(status.get(source)) is int and status[source] >= 0:
                link[target] = status[source]
        cooldown = status.get('cooldown')
        if type(cooldown) is int and cooldown >= 0:
            link['cooldownUntil'] = now + min(cooldown, 86400)

    def public(self, account, export_token):
        with self.lock:
            link = self._load().get(account, {})
            bound = bool(export_token) and link.get('exportHash') == self._fingerprint(export_token)
            result = {k: link.get(k) for k in ('connected', 'syncing', 'autoSync', 'needsReconnect',
                'lastGameSync', 'checkedAt', 'cooldownUntil', 'failCount', 'paused', 'error', 'message')}
            result.update(configured=bool(link.get('auth')) and bound, authorizationNeeded=not bool(link.get('auth')) or not bound)
            return result

    def connect(self, account, auth, export_token):
        account = self._account(account)
        auth = self._auth(auth)
        if not export_token:
            raise SyncError(400, 'Önce hesabın kalıcı dışa aktarma bağlantısı kurulmalı.')
        # Match the authenticated account with the existing CSV account, without changing either.
        exported = self.transport('exporttoken', auth)
        remote_token = exported.get('token')
        if not isinstance(remote_token, str) or not hmac.compare_digest(remote_token, export_token):
            raise SyncError(400, 'Bu DotGG hesabı seçtiğin koleksiyon hesabıyla eşleşmiyor. Doğru hesapla giriş yap.')
        response = self.transport('pocketstatus', auth)
        status = self._status(response)
        if response.get('error') or not status.get('connected'):
            raise SyncError(400, 'Bu DotGG hesabında Nintendo bağlantısı görünmüyor. Önce ptcgpocket.gg ayarlarından bağla.')
        link = {'auth': auth, 'exportHash': self._fingerprint(export_token), 'paused': False, 'error': '',
                'message': 'Yetkilendirildi. Bir sonraki aktarımda oyun koleksiyonu da yenilenir.'}
        self._record(link, status)
        with self.lock:
            data = self._load()
            if any(k != account and v.get('auth', '').split(':', 1)[0] == auth.split(':', 1)[0] for k, v in data.items()):
                raise SyncError(400, 'Bu DotGG hesabı diğer koleksiyon hesabına bağlı.')
            data[account] = link
            self._save(data)
        return self.public(account, export_token)

    def disconnect(self, account):
        self._account(account)
        with self.lock:
            data = self._load()
            data.pop(account, None)
            self._save(data)

    def _update(self, account, link):
        with self.lock:
            data = self._load()
            if account in data and data[account].get('auth') == link.get('auth'):
                data[account] = link
                self._save(data)

    def refresh(self, account, export_token):
        self._account(account)
        with self.lock:
            link = self._load().get(account)
        if not link:
            return False  # Existing export-only connections continue unchanged.
        if not export_token or link.get('exportHash') != self._fingerprint(export_token):
            raise SyncError(409, 'Dışa aktarma hesabı değişmiş. Oyun bağlantısını bu bilgisayardan yeniden yetkilendir.')
        auth = link['auth']
        now = int(self.clock())
        try:
            response = self.transport('pocketstatus', auth)
            status = self._status(response)
            self._record(link, status)
            if response.get('error'):
                raise SyncError(401, 'DotGG yetkisi doğrulanamadı. Oyun bağlantısını yeniden yetkilendir.')
            if not status.get('connected') or status.get('needs_reconnect'):
                link['paused'] = True
                raise SyncError(409, 'Nintendo bağlantısının yenilenmesi gerekiyor. ptcgpocket.gg üzerinden yeniden bağla; tekrar denemeler durduruldu.')
            if int(status.get('fail_count') or 0) > 0:
                link['paused'] = True
                raise SyncError(409, 'Nintendo bağlantısı hata bildirdi. Bağlantının silinmesini önlemek için oyun yenileme durduruldu; ptcgpocket.gg üzerinden kontrol et.')
            if status.get('syncing') or now < link.get('uncertainUntil', 0):
                raise SyncError(409, 'Oyun yenileme işlemi sürüyor olabilir. Tekrar gönderilmedi; birkaç dakika sonra durumu kontrol et.')
            if status.get('status') == 'error':
                raise SyncError(409, 'Son oyun yenilemesi başarısız. İşlem tekrar gönderilmedi; ptcgpocket.gg üzerinden durumu kontrol et.')
            if int(status.get('cooldown') or 0) > 0:
                link.update(error='', paused=False, message='Oyun yakın zamanda kontrol edilmiş. Son kayıtlı koleksiyon aktarıldı.')
                self._update(account, link)
                return False
            # Never retry a POST, including timeouts and HTTP 5xx responses.
            link['uncertainUntil'] = now + 180
            self._update(account, link)
            result = self.transport('pocketsync', auth)
            result_status = result.get('status')
            if isinstance(result_status, dict):
                self._record(link, result_status)
            if result.get('error') is not False:
                if link.get('failCount', 0) > 0 or link.get('needsReconnect'):
                    link['paused'] = True
                raise SyncError(409, 'Oyun yenilenemedi. İşlem tekrar gönderilmedi; ptcgpocket.gg üzerinden durumu kontrol et.')
            link.update(uncertainUntil=0, error='', paused=False, message='Oyun koleksiyonu yenilendi ve son liste aktarıldı.')
            self._update(account, link)
            return True
        except SyncError as e:
            link['error'] = e.message
            self._update(account, link)
            raise

