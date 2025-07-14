# candlestick_analysis.py – Detect popular candlestick patterns using TA-Lib
# ----------------------------------------------------------------------
# Requirement:
#   pip install TA-Lib yfinance
# ----------------------------------------------------------------------

import yfinance as yf
import talib
import pandas as pd
import numpy as np

def analyze_candlestick_patterns(symbol: str) -> str:
    try:
        # 🔹 Download last 6 months of daily OHLCV data
        df = yf.Ticker(symbol).history(period="6mo")
        if df.empty or len(df) < 50:
            return "Candle analysis ke liye kaafi data nahi mila."

        # 🔹 Prepare required columns
        open_ = df["Open"].values
        high = df["High"].values
        low = df["Low"].values
        close = df["Close"].values

        # 🔹 Define popular candlestick patterns
        patterns = {
            "Hammer": talib.CDLHAMMER,
            "Doji": talib.CDLDOJI,
            "Engulfing": talib.CDLENGULFING,
            "MorningStar": talib.CDLMORNINGSTAR,
            "HangingMan": talib.CDLHANGINGMAN,
            "ShootingStar": talib.CDLSHOOTINGSTAR,
            "InvertedHammer": talib.CDLINVERTEDHAMMER,
            "Piercing": talib.CDLPIERCING,
            "ThreeBlackCrows": talib.CDL3BLACKCROWS,
            "ThreeWhiteSoldiers": talib.CDL3WHITESOLDIERS
        }

        # 🔹 Recent 5-candle pattern detection
        recent_summary = []
        for name, func in patterns.items():
            result = func(open_, high, low, close)
            last_5 = result[-5:]
            non_zero = last_5[last_5 != 0]
            if len(non_zero) > 0:
                direction = "bullish" if non_zero[-1] > 0 else "bearish"
                recent_summary.append(f"{name} ({direction})")

        # 🔹 6-month trend check
        trend = "neutral"
        price_change = close[-1] - close[0]
        if price_change > 0.1 * close[0]:
            trend = "overall bullish trend"
        elif price_change < -0.1 * close[0]:
            trend = "overall bearish trend"

        # 🔹 Final result
        final_report = ""
        if recent_summary:
            final_report += "🕯️ Recent candle patterns (last 5 days): " + ", ".join(recent_summary) + "\n"
        else:
            final_report += "🕯️ Last 5 din mein koi strong candle pattern nahi mila.\n"

        final_report += f"📈 6-month trend: {trend.capitalize()}."

        return final_report

    except Exception as e:
        return f"Candlestick analysis mein error: {e}"
