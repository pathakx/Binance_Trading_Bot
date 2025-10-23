import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# API Configuration
API_KEY = os.getenv('API_KEY', 'Your Api key')
API_SECRET = os.getenv('API_SECRET', 'Your secret key')
TESTNET = True

# Binance API URLs
TESTNET_BASE_URL = 'https://testnet.binancefuture.com'
PRODUCTION_BASE_URL = 'https://fapi.binance.com'

# Logging Configuration
LOG_LEVEL = 'INFO'
LOG_FILE = 'trading_bot.log'

# Default trading parameters
DEFAULT_SYMBOL = 'BTCUSDT'
DEFAULT_QUANTITY = 0.001  # Minimum quantity for BTC