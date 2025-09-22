# NautilusTrader ile Binance Testnet Canlı Veri Testi

Bu proje, [NautilusTrader](https://github.com/nautechsystems/nautilus_trader) kütüphanesini kullanarak **Binance Futures Testnet**'e bağlanıp canlı bar verisi almayı gösteren basit bir test uygulamasıdır. Kod, ortam değişkenlerinden okunan API anahtarlarıyla güvenli bir şekilde bağlantı kurar, bir enstrümana abone olur ve gelen verileri loglar.

Bu örnek, özellikle `nautilus_trader` ile başlarken karşılaşılabilecek yaygın sorunları (API anahtarı yönetimi, enstrüman abonelik sırası, loglama) ele alacak şekilde tasarlanmıştır.

## Temel Özellikler

- **Güvenli API Anahtarı Yönetimi**: API anahtarları, `.env` dosyası üzerinden güvenli bir şekilde yönetilir.
- **Sağlamlaştırılmış Bağlantı Akışı**: Kod, önce enstrümanın varlığını kontrol eder, ardından veri akışına abone olur. Bu, "enstrüman bulunamadı" gibi hataların önüne geçer.
- **Anlaşılır Loglama**: Bağlantı durumu, abonelik süreci ve olası hatalar hakkında net loglar üretir.
- **Erken Uyarı Sistemi**: Veri akışı 15 saniye içinde başlamazsa, olası sorunları belirten bir uyarı verir.
- **Kolay Çalıştırma**: `Makefile` sayesinde tek komutla (`make testnet-run`) test başlatılabilir.

## Gereksinimler

- Python 3.11+
- `make` komutunun sisteminizde yüklü olması (genellikle Linux ve macOS'ta varsayılan olarak bulunur).

## Kurulum ve Çalıştırma

### Adım 1: Projeyi Klonlayın

```bash
git clone <repo_adresi>
cd <proje_dizini>
```

### Adım 2: Gerekli Kütüphaneleri Kurun

Proje için gerekli olan `nautilus_trader` ve `python-dotenv` kütüphanelerini kurun.

```bash
pip install -U "nautilus_trader[binance]" python-dotenv
```

### Adım 3: API Anahtarlarınızı Yapılandırın

Proje, API anahtarlarını `.env` dosyasından okur. Örnek dosyayı kopyalayarak kendi yapılandırmanızı oluşturun:

```bash
cp .env.example .env
```

Şimdi, bir metin editörü ile `.env` dosyasını açın ve Binance Futures Testnet'ten aldığınız API anahtarlarınızı girin:

```dotenv
# .env dosyasının içeriği
BINANCE_TESTNET_API_KEY="SIZIN_API_ANAHTARINIZ"
BINANCE_TESTNET_API_SECRET="SIZIN_GIZLI_ANAHTARINIZ"
```
**ÖNEMLİ:** `.env` dosyası hassas bilgiler içerdiğinden, asla Git gibi versiyon kontrol sistemlerine göndermeyin. `.gitignore` dosyasında varsayılan olarak engellenmiştir.

### Adım 4: Testi Çalıştırın

Tüm ayarları yaptıktan sonra, aşağıdaki komutla testi başlatabilirsiniz:

```bash
make testnet-run
```

## Beklenen Çıktı

Komutu çalıştırdığınızda, terminalde aşağıdaki gibi loglar görmelisiniz. Önce bağlantı ve abonelik süreci loglanır, ardından bar verileri gelmeye başlar.

```log
Binance Testnet bağlantı testi başlatılıyor...
2024-10-27 10:30:00,123 - __main__ - INFO - DataClient testi çalışıyor. Bar verileri için 60 saniye beklenecek...
2024-10-27 10:30:00,124 - __main__ - INFO - Durdurmak için CTRL+C'ye basın.
2024-10-27 10:30:01,456 - DataClientTester-001 - INFO - Test Aktörü başlatıldı.
2024-10-27 10:30:01,457 - DataClientTester-001 - INFO - Enstrüman talep ediliyor: BTCUSDT-PERP.BINANCE
2024-10-27 10:30:02,890 - DataClientTester-001 - INFO - Enstrüman başarıyla alındı ve önbelleğe eklendi: BTCUSDT-PERP.BINANCE
2024-10-27 10:30:02,891 - DataClientTester-001 - INFO - Şu bar verisine abone olunuyor: BTCUSDT-PERP.BINANCE-1-MINUTE-LAST-EXTERNAL
2024-10-27 10:30:03,120 - DataClientTester-001 - INFO - Başarıyla abone olundu: BTCUSDT-PERP.BINANCE-1-MINUTE-LAST-EXTERNAL (Spec: BarSpecification(1, MINUTE, LAST))
2024-10-27 10:31:00,500 - DataClientTester-001 - INFO - TEST BAŞARILI: Yeni bar alındı -> Bar(BTCUSDT-PERP.BINANCE-1-MINUTE-LAST-EXTERNAL, O=70123.45, H=70150.00, L=70120.10, C=70145.50, V=1234, T=1698388260000)
...
```

Eğer 15 saniye içinde veri gelmezse, aşağıdaki gibi bir uyarı mesajı alırsınız:
```log
2024-10-27 10:30:15,125 - __main__ - WARNING - UYARI: İlk 15 saniyede bar verisi alınamadı. Beklemeye devam ediliyor...
2024-10-27 10:30:15,126 - __main__ - WARNING - Olası Nedenler:
  - API anahtarları yanlış veya yetkileri eksik.
  - Binance Testnet hizmetinde anlık bir sorun olabilir.
  - Makinenizin saati Binance sunucularıyla senkronize değil.
  - Ağ bağlantınızda veya güvenlik duvarınızda bir sorun olabilir.
```

## Sık Karşılaşılan Hatalar ve Çözümleri

- **Hata: `Lütfen .env dosyasında BINANCE_TESTNET_API_KEY... ayarlayın.`**
  - **Çözüm:** `.env.example` dosyasını `.env` olarak kopyaladığınızdan ve içindeki API anahtarlarını doğru bir şekilde doldurduğunuzdan emin olun.

- **Veri Akışı Başlamıyor / Sürekli Zaman Aşımı Uyarısı Alıyorum**
  - **Çözüm:**
    1.  `.env` dosyanızdaki API anahtarlarının geçerli ve Binance Futures Testnet için olduğundan emin olun.
    2.  Binance Testnet sitesine giderek hesabınızın aktif olduğunu ve API anahtarlarınızın "ticaret" veya en azından "okuma" yetkisine sahip olduğunu doğrulayın.
    3.  Bilgisayarınızın saatinin internet saat sunucularıyla (NTP) senkronize olduğundan emin olun. API istekleri genellikle zaman damgası hassasiyeti gerektirir.
    4.  Kurumsal bir ağdaysanız veya bir VPN kullanıyorsanız, WebSocket bağlantılarını (genellikle port 443) engelleyen bir güvenlik duvarı olup olmadığını kontrol edin.
