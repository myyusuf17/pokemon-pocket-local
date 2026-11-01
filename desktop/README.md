# Masaüstü paketleri

Electron penceresi mevcut yerel veri servisini pakete dahil edilen Python ile başlatır. Python kurulumu ve terminal gerekmez. Uygulamayı kapatınca veri servisi de kapanır. Harici servis kurulmaz ve bilgisayar açılışında kendiliğinden başlamaz.

Koleksiyon tarayıcı belleğine yazılmaz. Kullanıcının uygulama veri klasöründeki `collection.json` ve `pokemon-trade-plan.json` dosyalarına kaydedilir. **Pocket Local → Veri klasörünü aç** menüsü klasörü gösterir. Görünüm tercihleri uygulamanın Chromium profilinde tutulabilir; koleksiyonun asıl kaydı dosyalardadır. Başka cihaza geçmek için uygulama içinden JSON yedeği alın.

- macOS: `~/Library/Application Support/Pocket Local/`
- Windows: `%APPDATA%/Pocket Local/`

Gerçek klasör adı Electron'un uygulama adından türetilir; menüden açılan klasör esas alınmalıdır. Otomatik aktarım yalnızca uygulama açıkken çalışır. Mevcut kalıcı dışa aktarma bağlantıları Hesaplar menüsünden eklenebilir.

## Yeniden derleme

```
npm ci
python3 -m pip install -r desktop/requirements-build.txt
python3 scripts/prepare-desktop.py --platform mac
npm run build:mac
```

Windows kaynak hazırlığı `python scripts/prepare-desktop.py --platform windows`, paketleme `npm run build:windows` komutuyla yapılır. Windows gömülü Python'u resmî python.org paketinden alınır. Windows ZIP'i başka işletim sisteminde üretilebilir; son çalışma testi Windows'ta yapılmalıdır. macOS derlemesi yerel mimariye uygun Python ve Electron gerektirir. GitHub Actions iş akışı her platformda paket ve veri servisi testi üretir; kendi başına yayınlamaz.

Paketler mağaza sertifikasıyla imzalanmış veya Apple tarafından noterlenmiş değildir. Kamuya açık nihai dağıtımda imzalama / noterleme ayrıca yapılandırılabilir. Güvenlik uyarılarını otomatik devre dışı bırakan işlem yapılmaz.
