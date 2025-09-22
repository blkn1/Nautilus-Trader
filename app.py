import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

from nautilus_trader.common.actor import Actor
from nautilus_trader.config import ActorConfig
from nautilus_trader.live.node import TradingNode
from nautilus_trader.config import TradingNodeConfig
from nautilus_trader.model import InstrumentId, BarType, BarSpecification

# Binance Testnet için gerekli modülleri içe aktaralım
from nautilus_trader.adapters.binance import (
    BinanceDataClientConfig,
    BinanceLiveDataClientFactory,
    BinanceAccountType,
)

# .env dosyasındaki ortam değişkenlerini yükle
load_dotenv()

# Temel loglama yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
# Nautilus'un gürültülü loglarını biraz kısalım
logging.getLogger("nautilus_trader").setLevel(logging.WARNING)
log = logging.getLogger(__name__)


# --- 1. Ortam Değişkenleri ve Yapılandırma ---
API_KEY = os.getenv("BINANCE_TESTNET_API_KEY")
API_SECRET = os.getenv("BINANCE_TESTNET_API_SECRET")

if not API_KEY or not API_SECRET:
    log.error("HATA: Lütfen .env dosyasında BINANCE_TESTNET_API_KEY ve BINANCE_TESTNET_API_SECRET değişkenlerini ayarlayın.")
    sys.exit(1)

# Yapılandırmada tutarlılık için sabitler
CLIENT_ID = "BINANCE-FUTURES-TESTNET"
INSTRUMENT_ID_STR = "BTCUSDT-PERP.BINANCE"
BAR_TYPE_STR = f"{INSTRUMENT_ID_STR}-1-MINUTE-LAST-EXTERNAL"


# --- 2. Test için Geliştirilmiş Actor ---
class DataClientTesterConfig(ActorConfig):
    instrument_id: InstrumentId = InstrumentId.from_str(INSTRUMENT_ID_STR)
    bar_type: BarType = BarType.from_str(BAR_TYPE_STR)
    test_successful: asyncio.Event  # Testin başarılı olup olmadığını işaretlemek için

class DataClientTester(Actor):
    def __init__(self, config: DataClientTesterConfig) -> None:
        super().__init__(config)
        # Actor'a özel loglama
        self.actor_log = logging.getLogger(self.id)
        self.actor_log.setLevel(logging.INFO)
        self.actor_log.info("Test Aktörü başlatıldı.")

    def on_start(self) -> None:
        """
        Node başladığında tetiklenir. Doğrudan abone olmak yerine,
        önce enstrümanın varlığını kontrol etmek için talepte bulunuruz.
        """
        self.actor_log.info(f"Enstrüman talep ediliyor: {self.config.instrument_id}")
        self.request_instrument(self.config.instrument_id)

    def on_stop(self) -> None:
        self.actor_log.info("Aktör durduruluyor ve abonelikler iptal ediliyor.")
        try:
            self.unsubscribe_bars(self.config.bar_type)
        except Exception as e:
            self.actor_log.error(f"Abonelik iptal edilirken hata oluştu: {e}")

    def on_instrument_cached(self, instrument):
        """
        Talep edilen enstrüman başarıyla alınıp önbelleğe eklendiğinde tetiklenir.
        Artık bu enstrümana güvenle abone olabiliriz.
        """
        self.actor_log.info(f"Enstrüman başarıyla alındı ve önbelleğe eklendi: {instrument.id}")
        self.actor_log.info(f"Şu bar verisine abone olunuyor: {self.config.bar_type}")
        self.subscribe_bars(self.config.bar_type)

    def on_bar(self, bar):
        """
        Eğer bu metoda ulaşabildiysek, test başarılıdır.
        """
        self.actor_log.info(f"TEST BAŞARILI: Yeni bar alındı -> {bar}")
        # Testin başarılı olduğunu ana döngüye bildirelim
        if not self.config.test_successful.is_set():
            self.config.test_successful.set()

    def on_bar_subscription_success(self, bar_type: BarType, spec: BarSpecification):
        self.actor_log.info(f"Başarıyla abone olundu: {bar_type} (Spec: {spec})")

    def on_bar_subscription_failure(self, bar_type: BarType, error: str):
        self.actor_log.error(f"Abonelik BAŞARISIZ: {bar_type}, Hata: {error}")

    def on_error(self, error):
        """Genel hataları yakalamak için."""
        self.actor_log.error(f"Aktörde bir hata oluştu: {error}")

    def on_event(self, event):
        # Diğer sistem olaylarını loglamak için (debug amaçlı)
        self.actor_log.debug(f"Alınan olay: {event}")


# --- 3. Trading Node'u Yapılandırın ---
# Testin durumunu takip etmek için bir asyncio Event nesnesi oluşturalım
test_successful_event = asyncio.Event()

config = TradingNodeConfig(
    trader_id="TESTNET-TRADER-002",
    data_clients={
        CLIENT_ID: BinanceDataClientConfig(
            api_key=API_KEY,
            api_secret=API_SECRET,
            account_type=BinanceAccountType.USDT_FUTURES,
            testnet=True,
        ),
    },
    exec_clients={},
    actors=[
        DataClientTesterConfig(
            test_successful=test_successful_event,
        ),
    ],
)

# --- 4. Trading Node'u Oluşturun ve Çalıştırın ---
node = TradingNode(config=config)

# Binance DataClient'i oluşturmak için ilgili factory'yi node'a ekle
node.add_data_client_factory(CLIENT_ID, BinanceLiveDataClientFactory)

# Gerekli tüm bileşenleri oluştur
node.build()

# Asenkron olarak node'u çalıştır
async def run_test():
    # Node'u başlat. Bu, aktörlerin on_start metodunu tetikleyecektir.
    node.start()

    log.info("DataClient testi çalışıyor. Bar verileri için 60 saniye beklenecek...")
    log.info("Durdurmak için CTRL+C'ye basın.")

    try:
        # İlk 15 saniye içinde bar gelip gelmediğini kontrol et
        await asyncio.wait_for(test_successful_event.wait(), timeout=15.0)
    except asyncio.TimeoutError:
        log.warning("UYARI: İlk 15 saniyede bar verisi alınamadı. Beklemeye devam ediliyor...")
        log.warning(
            "Olası Nedenler:\n"
            "  - API anahtarları yanlış veya yetkileri eksik.\n"
            "  - Binance Testnet hizmetinde anlık bir sorun olabilir.\n"
            "  - Makinenizin saati Binance sunucularıyla senkronize değil.\n"
            "  - Ağ bağlantınızda veya güvenlik duvarınızda bir sorun olabilir."
        )
        try:
            # Kalan süre boyunca beklemeye devam et (toplam 60 saniye)
            await asyncio.wait_for(test_successful_event.wait(), timeout=45.0)
        except asyncio.TimeoutError:
            log.error("ZAMAN AŞIMI: Toplam 60 saniye içinde bar verisi alınamadı.")
    except asyncio.CancelledError:
        log.info("Test iptal edildi.")
    finally:
        log.info("Test tamamlandı, node durduruluyor...")
        node.stop()
        node.dispose()
        log.info("Node başarıyla durduruldu.")

if __name__ == "__main__":
    try:
        asyncio.run(run_test())
    except KeyboardInterrupt:
        log.info("Kullanıcı tarafından durduruldu.")
    except Exception as e:
        log.error(f"Beklenmedik bir hata oluştu: {e}", exc_info=True)