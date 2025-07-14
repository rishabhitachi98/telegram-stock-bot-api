from tradingview_module import get_tv_indicators

symbol = "RELIANCE"
data = get_tv_indicators(symbol)

print(f"\n📈 TradingView Indicators for {symbol}:\n")

# Summary
summary = data["summary"]
print(f"👉 Overall Summary: {summary['RECOMMENDATION']} (Buy: {summary['BUY']}, Sell: {summary['SELL']}, Neutral: {summary['NEUTRAL']})")

# Indicators
ind = data["indicators"]

print("\n📊 Important Indicators:")
print(f"🔸 RSI: {ind.get('RSI', 'N/A')} (Signal: {ind.get('RSI_SIGNAL', 'N/A')})")
print(f"🔸 MACD: {ind.get('MACD.macd', 'N/A')} (Signal: {ind.get('MACD.signal', 'N/A')})")
print(f"🔸 STOCH.K: {ind.get('Stoch.K', 'N/A')} | STOCH.D: {ind.get('Stoch.D', 'N/A')}")
print(f"🔸 BB Upper: {ind.get('BB.upper', 'N/A')} | BB Lower: {ind.get('BB.lower', 'N/A')}")
