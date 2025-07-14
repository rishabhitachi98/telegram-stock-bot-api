from data_fetcher import fetch_stock_data
from indicators_module import add_indicators

symbol = "RELIANCE.NS"
df = fetch_stock_data(symbol, period="6mo", interval="1d")

df = add_indicators(df)

print(df.tail(1).T)
