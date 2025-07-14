# data_fetcher.py

import yfinance as yf
import pandas as pd


def fetch_live_price(symbol):
    stock = yf.Ticker(symbol)
    todays_data = stock.history(period='1d', interval='1m')
    return round(todays_data['Close'].iloc[-1], 2)

# data_fetcher.py
import yfinance as yf

def fetch_stock_data(symbol, period="6mo", interval="1d"):
    return yf.download(symbol, period=period, interval=interval, auto_adjust=True)
