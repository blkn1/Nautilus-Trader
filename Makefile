.PHONY: testnet-run

# Bu komut, Binance Testnet veri akışı testini başlatır.
# Çalıştırmadan önce .env dosyasını oluşturduğunuzdan ve
# API anahtarlarınızı girdiğinizden emin olun.
testnet-run:
	@echo "Binance Testnet bağlantı testi başlatılıyor..."
	@python app.py
