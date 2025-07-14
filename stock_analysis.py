# stock_analysis.py
import yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend import MACD

def analyze_stock(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="30d", interval="1d")

    if hist.empty:
        return f"No data for {ticker}"

    rsi = RSIIndicator(close=hist["Close"]).rsi().iloc[-1]
    macd = MACD(close=hist["Close"])
    macd_diff = macd.macd_diff().iloc[-1]

    cmp = hist["Close"].iloc[-1]

    return {
        "ticker": ticker,
        "CMP": round(cmp, 2),
        "RSI": round(rsi, 2),
        "MACD Diff": round(macd_diff, 2)
    }
