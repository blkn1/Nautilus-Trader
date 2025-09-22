# Nautilus-Trader

Elbette, sağladığınız kod dosyası için bir `README.md` dosyası aşağıda oluşturulmuştur. Bu dosya, kodun amacını, nasıl kurulacağını, yapılandırılacağını ve çalıştırılacağını adım adım açıklamaktadır.

---

# NautilusTrader Binance Testnet Canlı Veri Akışı Testi

Bu betik, [NautilusTrader](https://github.com/nautechsystems/nautilus_trader) platformunu kullanarak **Binance Futures Testnet**'ten canlı piyasa verilerinin alınıp alınmadığını test etmek için tasarlanmıştır. Betik, platformun temel bileşenlerini kullanarak bir veri istemcisine abone olur ve gelen bar verilerini konsola yazdırarak bağlantının başarılı olduğunu doğrular.

## Genel Bakış

Bu örnek, NautilusTrader'ın aşağıdaki temel konseptlerini göstermektedir:
*   **Actor**: Ticaret sisteminin temel bir bileşenidir; piyasa verilerini alır, olayları işler ve durumu yönetir.
*   **TradingNode**: Canlı ticaret veya simülasyon ortamını yöneten merkezi birimdir.
*   **DataClient**: Harici veri sağlayıcıları (bu örnekte Binance) ile entegrasyonu sağlayan adaptördür.
*   **Yapılandırma Nesneleri**: `TradingNodeConfig`, `ActorConfig` ve `BinanceDataClientConfig` gibi nesneler kullanılarak sistemin modüler bir şekilde yapılandırılması.

## Gereksinimler

- Python 3.11+
- NautilusTrader kütüphanesi ve Binance entegrasyonu:
  ```bash
  pip install -U "nautilus_trader[binance]"
  ```
- Binance Futures Testnet API anahtarları.

## Kurulum ve Yapılandırma

### 1. API Anahtarlarını Ayarlayın

Betik, API anahtarlarını güvenli bir şekilde yönetmek için ortam değişkenlerini kullanır. Kodun çalışabilmesi için Binance Futures Testnet API anahtarınızı ve gizli anahtarınızı aşağıdaki gibi ortam değişkenleri olarak ayarlamanız gerekmektedir.

**Linux/macOS:**
```bash
export BINANCE_FUTURES_TESTNET_API_KEY="SIZIN_API_ANAHTARINIZ"
export BINANCE_FUTURES_TESTNET_API_SECRET="SIZIN_GIZLI_ANAHTARINIZ"
```

**Windows (PowerShell):**
```powershell
$env:BINANCE_FUTURES_TESTNET_API_KEY="SIZIN_API_ANAHTARINIZ"
$env:BINANCE_FUTURES_TESTNET_API_SECRET="SIZIN_GIZLI_ANAHTARINIZ"
```
Kod, bu değişkenlerin ayarlanıp ayarlanmadığını kontrol ederek başlar.

## Kodun Çalışma Mantığı

1.  **`DataClientTester` Aktörü**:
    *   Bu basit `Actor` sınıfı, Nautilus ticaret sisteminin temel etkileşim birimidir.
    *   `on_start` metodu çalıştığında, `BTCUSDT-PERP.BINANCE` enstrümanının 1 dakikalık bar verilerine abone olur (`subscribe_bars`). Bu metot, gerçek zamanlı veri akışını başlatır.
    *   `on_bar` metodu, her yeni bar verisi geldiğinde tetiklenir ve başarılı bir şekilde veri alındığını belirten bir mesajı konsola yazdırır. Bu, veri akışının doğru çalıştığını teyit eder.

2.  **`TradingNode` Yapılandırması**:
    *   `TradingNodeConfig` kullanılarak sistemin ana yapılandırması oluşturulur.
    *   `data_clients` bölümünde, `BinanceDataClientConfig` ile Binance Futures Testnet'e bağlanacak bir veri istemcisi tanımlanır. Burada `account_type` olarak `USDT_FUTURES` ve `testnet` parametresi `True` olarak ayarlanmıştır.
    *   `DataClientTester` aktörü, `actors` listesine eklenerek sisteme dahil edilir.

3.  **Sistemin Başlatılması ve Test Edilmesi**:
    *   Bir `TradingNode` nesnesi oluşturulur.
    *   Binance entegrasyonu için gerekli olan `BinanceLiveDataClientFactory`, `node.add_data_client_factory` metodu ile düğüme kaydedilir. Bu "fabrika" sınıfları, Nautilus'un farklı entegrasyonlar için uygun istemcileri oluşturmasını sağlar.
    *   `node.build()` ile tüm bileşenler kurulur ve `node.start()` ile sistem başlatılır.
    *   Betik, `asyncio.sleep(60)` komutu ile 60 saniye boyunca çalışır ve bu süre içinde Binance'den canlı bar verilerinin gelmesini bekler.
    *   Bu süre zarfında `on_bar` metodu tetiklenirse, konsolda **"TEST BAŞARILI"** mesajı görünür.

## Nasıl Çalıştırılır?

1.  Yukarıdaki adımları takip ederek ortamınızı kurun ve API anahtarlarınızı ayarlayın.
2.  Betik dosyasını bir terminalde çalıştırın:
    ```bash
    python <dosya_adi>.py
    ```
3.  Terminalde aşağıdaki gibi bir çıktı görmelisiniz:
    ```
    DataClient testi çalışıyor. Bar verileri için 60 saniye beklenecek...
    Durdurmak için CTRL+C'ye basın.
    ```
4.  Birkaç dakika içinde, Binance Testnet'ten veri akışı başladığında aşağıdaki gibi başarılı log mesajları görmeye başlamalısınız:
    ```
    ... [INFO] TEST BAŞARILI: Yeni bar alindi -> Bar(BTCUSDT-PERP.BINANCE-1-MINUTE-LAST-EXTERNAL, O=..., H=..., L=..., C=..., V=...)
    ```
5.  60 saniye sonra test otomatik olarak sonlanacak ve node güvenli bir şekilde kapatılacaktır.
