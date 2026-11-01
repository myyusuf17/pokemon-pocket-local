# Pocket Local

**Pokémon TCG Pocket koleksiyonunu tek veya iki hesapla takip et; eksik kartlarını bul ve takaslarını planla.**

Türkçe arayüz, manuel kart adedi girişi, isteğe bağlı hesap aktarımı, kart açıklamaları ve taşınabilir JSON yedekleri. Bir Pocket Local hesabı oluşturman gerekmez. Koleksiyonun boş başlar; kendi kartlarını eklersin veya kendi hesaplarını bağlarsın.

[İndirmeler ve sürüm notları](https://github.com/myyusuf17/pokemon-pocket-local/releases/tag/v1.0.0) · [Hesap bağlama rehberi](#hesap-bağlama-rehberi) · [Sık sorulan sorular](#sık-sorulan-sorular)

## Hangi sürümü seçmeliyim?

| Seçenek | İndir | Veriler nerede saklanır? | Terminal / Python kurulumu |
| --- | --- | --- | --- |
| **Tarayıcı** | [Web ZIP](https://github.com/myyusuf17/pokemon-pocket-local/releases/download/v1.0.0/Pocket-Local-1.0.0-web.zip) | Kullandığın tarayıcıda | Gerekmez |
| **macOS — Apple Silicon / M serisi** | [Mac ZIP](https://github.com/myyusuf17/pokemon-pocket-local/releases/download/v1.0.0/Pocket-Local-1.0.0-mac-arm64.zip) | Bilgisayarındaki uygulama veri klasöründe | Gerekmez |
| **Windows — 64 bit / x64** | [Windows ZIP](https://github.com/myyusuf17/pokemon-pocket-local/releases/download/v1.0.0/Pocket-Local-1.0.0-win-x64.zip) | Bilgisayarındaki uygulama veri klasöründe | Gerekmez |

**Yalnızca manuel takip için** tarayıcı sürümü yeterlidir. **Hesap bağlama ve otomatik aktarım için** masaüstü uygulamasını seç. Üç sürüm arasında JSON yedeğiyle koleksiyonunu taşıyabilirsin.

ZIP'i tamamen çıkar; dosyaları ZIP'in içinden çalıştırma. Web sürümünde `index.html`, Mac'te `Pocket Local.app`, Windows'ta `Pocket Local.exe` açılır. Mac ZIP'i Intel işlemciler için değildir.

> **İlk sürüm / ön sürüm:** Mac uygulamasının açılışı ve dosyaya kaydı macOS'ta doğrulandı. Windows paketi üretildi; Windows uygulama penceresinde elle kullanım testi henüz yapılmadı. Paketlerde ticari kod imzası ve Apple noterlemesi yoktur; işletim sistemi yayıncıyı doğrulayamayabilir. Otomatik güncelleme bulunmaz. Her sürümün doğrulama durumunu sürüm notlarından kontrol et.

## Neler yapabilirim?

- Bir hesapla koleksiyon tutabilir veya ikinci hesapla karşılaştırabilirsin.
- Her kartın adedini elle artırıp azaltabilirsin; değişiklik kutudan çıkınca kaydedilir.
- Seri, kart adı / numarası, nadirlik ve sahiplik durumuna göre filtreleyebilirsin.
- 27 serilik, 4.577 kartlık mevcut katalogdaki görselleri ve İngilizce kart açıklamalarını internet olmadan inceleyebilirsin.
- İkinci hesapta bulunan, ana hesapta eksik olan özel kartlar için takas planı oluşturabilirsin.
- JSON yedeği alabilir, başka sürüme / cihaza aktarabilir; takas planını metin olarak indirebilir veya yazdırabilirsin.

Katalog ve takas maliyetleri paketle birlikte gelen bir anlık listedir; yeni kart serileri otomatik eklenmez.

## İlk kullanım: hesap bağlamadan başla

1. Yukarıdaki üç paketten uygun olanı indir ve ZIP'i çıkar.
2. Uygulamayı veya `index.html` dosyasını aç.
3. **Tek hesap** veya **İki hesap** seçip **Koleksiyonumu aç** düğmesine bas.
4. Soldan bir seri seç. Kartın altındaki **Ana** kutusuna adedini yaz. İki hesap modunda **İkinci** kutusunu da doldur.
5. **Eksikler**, **Sende olanlar**, nadirlik ve arama filtrelerini kullan.
6. Düzenli olarak **Hesaplar → Verilerimi yedekle (JSON)** ile yedek al.

İkinci hesabı daha sonra gizlemek o hesabın kayıtlarını silmez. Manuel kullanımda internet bağlantısı veya herhangi bir oyun hesabını bağlama zorunluluğu yoktur.

## Hesap bağlama rehberi

### Bağlantı nasıl çalışıyor?

Pocket Local, normal aktarımda **ptcgpocket.gg / DotGG üzerindeki koleksiyon dışa aktarımını okur**. Nintendo hesabına doğrudan kullanıcı adı / şifreyle giriş yapmaz. Oyun koleksiyonunun önce bu üçüncü taraf serviste güncellenmiş olması gerekir.

Normal akış:

```text
Oyun koleksiyonun
      ↓ ptcgpocket.gg üzerindeki kendi senkronizasyonun
ptcgpocket.gg / DotGG koleksiyon listesi
      ↓ kalıcı dışa aktarma bağlantısı
Pocket Local → kendi bilgisayarındaki koleksiyon
```

**“Şimdi aktar” normal bağlantıda DotGG'deki son listeyi alır.** Bu düğme tek başına oyunun güncel verilerini çekme yetkisi vermez. Oyunda yeni kart aldıysan önce ptcgpocket.gg'deki senkronizasyonun tamamlanmasını bekle.

### 1. Kendi koleksiyonunu ptcgpocket.gg'de hazırla

1. [ptcgpocket.gg hesap ayarlarını](https://ptcgpocket.gg/u/me/settings/#pocket-sync) aç ve kendi hesabına giriş yap.
2. Servisin **Pocket Sync / Pokémon TCG Pocket** bölümündeki adımlarla kendi Nintendo / oyun hesabının bağlantısını kur. Bu bağlantı ve gereken onaylar üçüncü taraf servisin kendi ekranında yapılır.
3. Koleksiyonunu o servis üzerinden bir kez senkronize et; kartlarının orada göründüğünü kontrol et.
4. Serviste gerekiyorsa **Automatic sync** seçeneğini aç.
5. Koleksiyon / hesap ayarlarında **Permanent export link** veya **kalıcı dışa aktarma bağlantısı** olarak sunulan bağlantıyı kopyala.

Üçüncü taraf sitenin menü adları ve hesap bağlantısı koşulları değişebilir. Bu proje, o servisin bağlantı kurmayı veya senkronizasyonu her zaman sunacağını garanti etmez.

Uygulamanın desteklediği bağlantı biçimi şudur; aşağıdaki yalnızca biçim örneğidir:

```text
https://api.dotgg.gg/cgfw/exportcollection?game=pokepocket&token=KENDI_TOKENIN
```

Profil, paylaşım veya Binder sayfasının bağlantısını kullanma. Uygulama desteklenen dışa aktarma adresini ve token biçimini doğrular.

### 2. Bağlantıyı Pocket Local'e ekle

1. **Mac veya Windows uygulamasını aç.** Web ZIP'i otomatik aktarımı tek başına çalıştırmaz.
2. **Koleksiyon → Hesaplar → Oyundan aktarım** bölümünü aç.
3. **Ana hesap → Kalıcı dışa aktarma bağlantısı** alanına kendi bağlantını yapıştır.
4. **Bağla ve aktar** düğmesine bas.
5. İşlem tamamlandığında bağlantı durumu, aktarım sonucu ve kart adetlerini kontrol et.

İlk bağlantı sırasında liste okunur ve bilinen seri / kart numaralarıyla eşleştirilir. Başarısız bir okuma mevcut koleksiyonunu sıfırlamaz. Kart kataloğunda henüz olmayan kartlar eşleşmeyen kayıt olarak bildirilebilir.

**Nintendo şifreni, e-posta şifreni veya DotGG giriş şifreni bu kutuya yazma.** Kutunun beklediği şey kalıcı dışa aktarma bağlantısıdır.

### 3. İstersen ikinci hesabı bağla

1. **Hesaplar → Hesap sayısı → İki hesap** seç.
2. İkinci oyun hesabın için ayrı ptcgpocket.gg hesabında aynı hazırlığı yap.
3. O hesabın **kendi kalıcı dışa aktarma bağlantısını**, **İkinci hesap** alanına ekle.
4. **Bağla ve aktar** düğmesine bas.

Aynı dışa aktarma bağlantısını iki hesap alanında kullanamazsın. Tarayıcıda birden fazla ptcgpocket.gg hesabını yönetirken hangi hesaptan bağlantı kopyaladığını kontrol et. Tek hesapla kullanıyorsan bu adımı atlayabilirsin.

### 4. Sonraki güncellemeler

- **Şimdi aktar:** Bağlı hesabın son dışa aktarımını yeniden okur. Normal manuel aktarım istekleri arasında en az bir dakika beklenir.
- **24 saatte bir otomatik aktar:** Etkinse, masaüstü uygulaması açıkken çalışır.
- **Uygulama kapalıysa:** Arka planda kalıcı bir servis kurulmaz; aktarım durur. Tekrar açıldığında zamanı gelmiş aktarım uygulamanın kontrol döngüsünde ele alınır.
- **Bağlantıyı kaldır:** Pocket Local'de kaydedilmiş aktarım bağlantısını kaldırır. Mevcut koleksiyon kartlarını silmez; üçüncü taraf sitedeki Nintendo bağlantısını kaldırmaz.

### Manuel adetlerle aktarım birlikte nasıl çalışıyor?

Elle kart adedi girebilirsin. Bir sonraki başarılı aktarım, o hesapta dönen **adetleri son dışa aktarımdaki sayılarla değiştirir**; manuel adedin korunacağını varsayma.

Sahiplik işaretleri ve son aktarım adetleri ayrı tutulur. Aktarım, bulunan kartları ekler; sıfır veya eksik veriye bakarak eski sahiplik işaretlerini otomatik silmez. Bu nedenle takas sonrasında bir kart “sende var” görünüp son aktarım adedi 0 olabilir. Kontrol ederek kartın adedini elle 0'a ayarlayabilirsin. Her başarılı aktarım öncesinde yerel koleksiyon geçmişi yedeklenir.

### İleri seviye: doğrudan oyun yenileme yetkisi

Normal kullanım için gerekli değildir. Kaynak koddan çalışan yerel başlatıcıda, kalıcı dışa aktarma bağlantısını kurduktan sonra `python3 connect_game.py` ile **zaten sahip olduğun DotGG API yetkisini** yerel, gizli giriş alanına verebilirsin. Bu aracın hedefi kaynak projenin `data/` klasörüdür; paketlenmiş masaüstü uygulamasının veri klasörünü otomatik yönetmez. Bu sürümde masaüstü kullanıcıları normal dışa aktarma akışını kullanmalıdır.

Ek yetki sağlanırsa kod, dışa aktarma hesabıyla API yetkisinin aynı hesaba ait olduğunu doğrular; ardından yenilemelerde önce oyun yenilemesini dener. Servis bekleme süresi, bağlantı hatası veya sürmekte olan işlem bildirirse tekrar isteği sınırlanır. API yetkisi bir Nintendo şifresi değildir. Yetkiyi veya bağlantı token'ını herkese açık paylaşma. [DotGG API dokümantasyonu](https://dotgg.gg/api/).

## Bağlantı sorunları

| Durum | Kontrol et |
| --- | --- |
| “Geçerli kalıcı dışa aktarma bağlantısı” isteniyor | Profil / Binder linki yerine Pokémon TCG Pocket kalıcı export linkini kullan. |
| Listede eşleşen sahip olunan kart bulunamıyor | Önce ptcgpocket.gg'de doğru oyun hesabının koleksiyonunu senkronize et. Boş veya beklenmeyen liste mevcut verilerin yerine yazılmaz. |
| Yeni kartlar görünmüyor | Önce üçüncü taraf listedeki kartlarını kontrol et; Pocket Local normal bağlantıda o son listeyi okur. Yeni seri katalogda olmayabilir. |
| Bağlantı geçersiz / iptal edilmiş | Üçüncü taraf servisten yeni kalıcı bağlantı alıp doğru hesap alanına ekle. |
| İkinci hesap aynı hesap olarak algılanıyor | İki farklı ptcgpocket.gg hesabından iki farklı bağlantı kullan. |
| Tekrar güncelleme için bekle uyarısı | Normal aktarımda en az bir dakika bekle. Ek oyun yenileme yetkisinin kendi bekleme ve hata koşulları da vardır. |
| Servise ulaşılamıyor | İnternet bağlantını ve üçüncü taraf servisin erişilebilirliğini kontrol et. Mevcut kayıtlar korunur. |
| Web ZIP'inde hesap bağlanmıyor | Hesap aktarımı için Mac / Windows uygulamasını kullan veya kaynak koddan yerel başlatıcıyı çalıştır. |

## Takas planı

İki hesap modunda **Trade planı** düğmesini aç. Ana hesapta eksik, ikinci hesapta bulunan özel kartlar listelenir. İki hesabın Stardust bakiyesini gir, kartlarını seç ve kalan bakiyeleri kontrol et. **Onayla ve planı oluştur** yalnızca yerel bir plan kaydeder; oyunda takas yapmaz, gerçek bakiyeni veya koleksiyonunu değiştirmez.

Karşı kart önerileri ana hesapta en az bir kopya bırakacak fazla kartlardan seçilir. Uygun karşı kart bulunamayan adımlar ayrıca işaretlenir. Planı yazdırabilir veya metin olarak indirebilirsin. Maliyet tablosu mevcut sistemin 30 Ekim 2026 tarihli sürümüdür; son nadirlik, takas uygunluğu, flair / çerçeve ve bakiye koşullarını oyunda kontrol et.

## Yedekleme ve veri yeri

**Hesaplar → Verilerimi yedekle (JSON)** ile yedek al. Diğer sürümde **Yedeği yükle** ile içeri alabilirsin.

| Kullanım | Asıl kayıt yeri |
| --- | --- |
| Web ZIP'i | O tarayıcının yerel kayıt alanı |
| Mac uygulaması | `~/Library/Application Support/Pocket Local/` |
| Windows uygulaması | `%APPDATA%/Pocket Local/` |
| Kaynak koddan yerel başlatıcı | Proje içindeki `data/` klasörü |

Masaüstünde **Pocket Local → Veri klasörünü aç** menüsü gerçek klasörü gösterir. Koleksiyon ve takas planı bu klasörde dosyadır; bazı görünüm tercihleri uygulamanın Chromium profilinde tutulabilir.

Tarayıcı verilerini silmek web sürümünün kayıtlarını silebilir. Farklı tarayıcı, dosya yolu, bilgisayar ve uygulama sürümü aynı veri alanını paylaşmaz; taşımak için JSON yedeğini kullan.

JSON yedeği koleksiyonu, takas taslağını ve bakiyeleri taşır; kalıcı hesap bağlantılarını veya API yetkisini içermez. Geri yükleme mevcut koleksiyonun yerini alır, kayıtlı planı temizler ve taslağı yeniden onaylamanı gerektirir. Masaüstü / başlatıcı modunda eski aktarım bağlantıları kaldırılır; kendi bağlantılarını tekrar ekle.

## Gizlilik

Kullanım için bu GitHub deposuna veya ortak bir Pocket Local sunucusuna hesap verisi gönderilmez. Bağlantı ekleyip aktarımı etkinleştirirsen DotGG servisine HTTPS istekleri yapılır. Projede analitik / telemetri yoktur. Manuel kullanım internetsiz çalışabilir.

**Kalıcı dışa aktarma bağlantısı, koleksiyonunu okuyabilen bir token içerir.** Bu bağlantıyı ekran görüntülerinde, GitHub issue'larında veya yedek paylaşımında görünür bırakma. Yerel veri klasöründeki `pocket-import-links.json` ve varsa `pocket-game-links.json` paylaşılmamalıdır. Bağlantılar diskte saklanır; bu proje onları uygulama düzeyinde şifrelemez. JSON yedekleri de koleksiyon ve bakiye bilgilerini içerdiği için kişisel tutulmalıdır.

Dağıtım paketleri boş koleksiyonla gelir. Geliştirme sırasında kullanılan özel kaynak kopyası, gerçek hesap bağlantıları ve deneme profilleri bu depoya veya uygulama paketlerine dahil edilmez.

## Sık sorulan sorular

**Hesap bağlamak zorunda mıyım?** Hayır. Kart adetlerini tamamen elle girebilirsin.

**Tek hesapla çalışır mı?** Evet. İkinci hesap isteğe bağlıdır.

**Masaüstü uygulaması için terminal açık mı kalacak?** Hayır. Gerekli çalışma ortamı uygulamanın içinde gelir. Uygulamayı açman yeterlidir.

**Uygulamayı kapatınca kayıtlar gider mi?** Masaüstünde dosyalarda kalırlar. Uygulama kapalıyken otomatik aktarım çalışmaz.

**Oyun içinde takas veya satın alma yapar mı?** Hayır. Koleksiyon takibi ve takas planlaması yapar.

**GitHub'a bir token veya şifre koymam gerekiyor mu?** Hayır. Kendi dışa aktarma bağlantını yalnızca kendi çalışan uygulamanda ilgili kutuya gir.

## Kaynak koddan çalıştırma

Bu bölüm geliştiriciler içindir; masaüstü ZIP'lerini kullanmak için Python kurmana gerek yoktur.

Python 3.10+ ile, ek Python paketi kurmadan:

```sh
python3 server.py
```

Windows'ta `py -3 server.py` kullanılabilir. Alternatif başlatıcılar: `Baslat.command` / `Baslat.bat`. Yerel sayfa `http://127.0.0.1:8795` adresinde açılır. Port doluysa `python3 server.py --port 8796` çalıştır. Bu kaynak başlatıcısı kullanıldığında terminal açık kalmalıdır; kapatmak için Ctrl+C.

```sh
python3 -m unittest discover -s tests -v
node tests/offline-smoke.cjs
```

Masaüstü derleme, bağımsız Python ortamı ve GitHub Actions ayrıntıları: [desktop/README.md](desktop/README.md). Web paketi: `python3 scripts/release-browser.py`. İzin verilen kaynaklardan temiz paylaşım ZIP'i: `python3 package_release.py`.

## Katkı ve kaynaklar

Bir hata bildirirken işletim sistemini, kullandığın sürümü, beklenen davranışı ve gizli verilerden temizlenmiş hata mesajını ekle. Hesap bağlantısı / token gönderme. Menü ve aktarım sorunları için önce yukarıdaki rehberi kontrol et.

Kart kataloğu ve görsellerin kaynakları: [Centro Pokémon](https://tcgpocket.centropkmn.com/) ve taşınan mevcut katalog. Üçüncü taraf aktarım servisi: [ptcgpocket.gg](https://ptcgpocket.gg/) / [DotGG](https://dotgg.gg/api/).

Bağımsız ve resmî olmayan bir hayran projesidir. Pokémon, Nintendo, Creatures ve GAME FREAK ile bağlantılı değildir. Kart adları, görseller ve markalar ilgili hak sahiplerine aittir. Bu depo üçüncü taraf varlıklar için yeniden lisans hakkı vermez.
