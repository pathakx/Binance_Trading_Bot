from binance.client import Client

API_KEY = "YOUR_KEY"
API_SECRET = "YOUR_SECRET"
client = Client(API_KEY, API_SECRET)

# Point to futures testnet
client.FUTURES_URL = "https://testnet.binancefuture.com"

try:
    client.futures_ping()
    print("✅ Futures ping successful")
    info = client.futures_account()
    print("✅ Account info fetched successfully")
except Exception as e:
    print("❌ Error:", e)
