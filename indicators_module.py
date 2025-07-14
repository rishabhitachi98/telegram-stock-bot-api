# indicators_module.py

import pandas as pd
import ta  # ta library

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Yahoo Finance se aayi candle data par technical indicators lagata hai
    ta library ka use karke — stable aur clean
    """

  

    # ✅ RSI
    rsi = ta.momentum.RSIIndicator(close=df['Close'], window=14)
    df['RSI'] = rsi.rsi()

    # ✅ MACD
    macd = ta.trend.MACD(close=df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_Signal'] = macd.macd_signal()
    df['MACD_Diff'] = macd.macd_diff()

    # ✅ Bollinger Bands
    bb = ta.volatility.BollingerBands(close=df['Close'], window=20, window_dev=2)
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_middle'] = bb.bollinger_mavg()
    df['BB_lower'] = bb.bollinger_lband()

    # ✅ Moving Averages
    df['DMA50'] = ta.trend.SMAIndicator(close=df['Close'], window=50).sma_indicator()
    df['DMA200'] = ta.trend.SMAIndicator(close=df['Close'], window=200).sma_indicator()

    # ✅ Clean-up
    df.dropna(inplace=True)
    df = df.round(2)

    return df
