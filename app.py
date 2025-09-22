import asyncio
import os
from nautilus_trader.common.actor import Actor
from nautilus_trader.config import ActorConfig
from nautilus_trader.live.node import TradingNode
from nautilus_trader.config import TradingNodeConfig
from nautilus_trader.model import InstrumentId, BarType

# Binance Testnet için DataClient ve ExecClient yapilandirmalarini içe aktaralim
# Kaynaklarda özellikle testnet için bu konfigürasyonlarin olduğu belirtiliyor [2-5]
from nautilus_trader.adapters.binance import (
    BinanceDataClientConfig,
    BinanceExecClientConfig,
    BinanceLiveDataClientFactory,
    BinanceLiveExecClientFactory,
    BinanceAccountType,
    BINANCE, # "BINANCE" string değişmezini temsil eder
)

# 1. API Anahtarlarinizi Ortam Değişkenleri Olarak Ayarlayin
# Nautilus, API anahtarlarini ortam değişkenlerinden okumayi destekler [6].
# Bu, kodunuzda hassas bilgileri tutmamaniz için en iyi yöntemdir.
# Lütfen Binance Futures Testnet'ten aldiğiniz anahtarlari aşağidaki gibi ayarlayin:
# os.environ["BINANCE_FUTURES_TESTNET_API_KEY"] = "YOUR_API_KEY"
# os.environ["BINANCE_FUTURES_TESTNET_API_SECRET"] = "YOUR_API_SECRET"

# API anahtarlarinin ayarlandiğindan emin olalim
assert "BINANCE_FUTURES_TESTNET_API_KEY" in os.environ, "ec7c1cbd3a1c7aac364a3168f60da145c2f40ccd800317be0692e4420e3aeda8"
assert "BINANCE_FUTURES_TESTNET_API_SECRET" in os.environ, "b4d08bd4e33c504e34eceded5e837e151cd44d95913767a149ccbce1182953e1"


# 2. Test için Basit Bir Actor Tanimlayin
# Bu Actor, sadece gelen bar verilerini log'layacak [7, 8].
class DataClientTesterConfig(ActorConfig):
    instrument_id: InstrumentId = InstrumentId.from_str("BTCUSDT-PERP.BINANCE")
    bar_type: BarType = BarType.from_str("BTCUSDT-PERP.BINANCE-1-MINUTE-LAST-EXTERNAL")

class DataClientTester(Actor):
    def __init__(self, config: DataClientTesterConfig) -> None:
        super().__init__(config)
        self.log.info(f"Test Aktörü '{self.id}' başlatildi.")

    def on_start(self) -> None:
        # Testnet'ten canli bar verilerine abone olalim [9].
        self.log.info(f"Şu bar verisine abone olunuyor: {self.config.bar_type}")
        self.subscribe_bars(self.config.bar_type)

    def on_stop(self) -> None:
        self.log.info("Aktör durduruluyor ve abonelikler iptal ediliyor.")
        self.unsubscribe_bars(self.config.bar_type)

    def on_bar(self, bar):
        # Eğer bu mesaji görüyorsak, DataClient çalişiyor demektir! [9]
        self.log.info(f"TEST BAŞARILI: Yeni bar alindi -> {bar}", color="green")

    def on_event(self, event):
        # Sistemdeki diğer olaylari görmek için
        self.log.debug(f"Alinan olay: {event}")


# 3. Trading Node'u Yapilandirin
# TradingNode, canli ticaret için tüm bileşenleri bir araya getirir [10-12].
# Binance Futures testnet'ine bağlanacak şekilde yapilandiralim.
config = TradingNodeConfig(
    trader_id="TESTNET-TRADER-001",
    data_clients={
        # Binance Data Client'i testnet modunda yapilandir [2, 5].
        "BINANCE": BinanceDataClientConfig(
            account_type=BinanceAccountType.USDT_FUTURES,
            testnet=True,
        ),
    },
    # Canli işlem yapmayacağimiz için exec_clients boş olabilir, ancak genellikle olmasi gerekir.
    exec_clients={},
    # Test aktörümüzü sisteme ekleyelim
    actors=[
        DataClientTesterConfig(),
    ],
)

# 4. Trading Node'u Oluşturun ve Çaliştirin
node = TradingNode(config=config)

# Nautilus, farkli entegrasyonlar için 'factory' siniflari kullanir [13].
# Binance DataClient'i oluşturmak için ilgili factory'yi node'a eklemeliyiz.
node.add_data_client_factory("BINANCE", BinanceLiveDataClientFactory)

# Gerekli tüm bileşenleri oluştur
node.build()

# Asenkron olarak node'u çaliştir
async def run_test():
    # Node'u başlat. Bu, on_start metodunu tetikleyecektir.
    node.start()
    
    # Testin bir süre çalişmasina izin verelim (örneğin 60 saniye)
    # Bu süre boyunca on_bar metodu tetiklenmelidir.
    print("DataClient testi çalişiyor. Bar verileri için 60 saniye beklenecek...")
    print("Durdurmak için CTRL+C'ye basin.")
    
    try:
        await asyncio.sleep(60)
    except asyncio.CancelledError:
        pass
    finally:
        # Node'u güvenli bir şekilde durdur
        print("Test tamamlandi, node durduruluyor...")
        node.stop()
        node.dispose()

if __name__ == "__main__":
    try:
        asyncio.run(run_test())
    except KeyboardInterrupt:
        print("Kullanici tarafindan durduruldu.")