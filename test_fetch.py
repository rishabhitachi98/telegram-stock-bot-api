# test_fetch.py

from data_fetcher import fetch_stock_data

# 🔍 Symbol example: INFY.NS, TCS.NS, HDFCBANK.NS
symbol = "RELIANCE.NS"

df = fetch_stock_data(symbol)

# ✅ Print last 5 candles
print("\n📊 Last 5 rows of stock data:")
print(df.tail(5))

# ✅ Optional: Save to CSV for checking
df.to_csv(f"{symbol}_data.csv")
print(f"\n✅ Data saved as {symbol}_data.csv")
