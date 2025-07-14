# candlestick_analysis_with_chart.py – Detect and visualize popular candlestick patterns
# ----------------------------------------------------------------------
# Requirement:
#   pip install TA-Lib yfinance mplfinance matplotlib
# ----------------------------------------------------------------------

import yfinance as yf
import talib
import pandas as pd
import numpy as np
import mplfinance as mpf
import os

def analyze_and_plot_candlestick_patterns(symbol: str) -> (str, str):
    """
    Ek stock symbol ke liye candlestick patterns analyze karta hai, 
    ek text report banata hai, aur ek chart generate karta hai 
    jismein patterns highlight kiye gaye hon.

    Returns:
        tuple: (text_report, image_path)
               text_report (str): Analysis ki summary.
               image_path (str or None): Generate hui image ka path, ya error par None.
    """
    try:
        # 🔹 Step 1: Data download karna (pichle 6 mahine ka)
        df = yf.Ticker(symbol).history(period="6mo")
        if df.empty or len(df) < 50:
            return "Candle analysis ke liye kaafi data nahi mila.", None

        # 🔹 Step 2: Zaroori columns taiyaar karna
        open_ = df["Open"]
        high = df["High"]
        low = df["Low"]
        close = df["Close"]

        # 🔹 Step 3: Mashhoor candlestick patterns define karna
        # Har pattern ke saath yeh bhi define karenge ki woh bullish hai ya bearish
        patterns = {
            "Hammer": {"func": talib.CDLHAMMER, "type": "bullish"},
            "Morning Star": {"func": talib.CDLMORNINGSTAR, "type": "bullish"},
            "Three White Soldiers": {"func": talib.CDL3WHITESOLDIERS, "type": "bullish"},
            "Inverted Hammer": {"func": talib.CDLINVERTEDHAMMER, "type": "bullish"},
            "Piercing Line": {"func": talib.CDLPIERCING, "type": "bullish"},
            
            "Hanging Man": {"func": talib.CDLHANGINGMAN, "type": "bearish"},
            "Shooting Star": {"func": talib.CDLSHOOTINGSTAR, "type": "bearish"},
            "Three Black Crows": {"func": talib.CDL3BLACKCROWS, "type": "bearish"},

            # Yeh patterns bullish ya bearish dono ho sakte hain
            "Engulfing Pattern": {"func": talib.CDLENGULFING, "type": "both"},
            "Doji": {"func": talib.CDLDOJI, "type": "neutral"},
        }
        
        # 🔹 Step 4: Chart par highlight karne ke liye markers taiyaar karna
        # Markers ke liye do alag series banayenge: ek bullish ke liye, ek bearish ke liye
        bullish_markers = pd.Series(np.nan, index=df.index)
        bearish_markers = pd.Series(np.nan, index=df.index)
        
        found_patterns_summary = []

        for name, info in patterns.items():
            # Pattern detection
            result = info["func"](open_, high, low, close)
            
            # Jin dates par pattern mila hai, unhe dhoondhna
            pattern_dates = df.index[result != 0]

            if not pattern_dates.empty:
                for date in pattern_dates:
                    signal = result.loc[date]
                    
                    # Pattern ka direction (bullish/bearish) decide karna
                    direction = ""
                    if info["type"] == "bullish":
                        direction = "bullish"
                    elif info["type"] == "bearish":
                        direction = "bearish"
                    elif info["type"] == "both": # Engulfing jaiso ke liye
                        direction = "bullish" if signal > 0 else "bearish"

                    # Summary ke liye text add karna
                    if direction:
                       found_patterns_summary.append(f"{name} ({direction}) on {date.strftime('%Y-%m-%d')}")

                    # Chart par marker lagane ki position taiyaar karna
                    if direction == "bullish":
                        # Bullish marker ko candle ke 'Low' ke neeche lagayenge
                        bullish_markers.loc[date] = df['Low'].loc[date] * 0.98
                    elif direction == "bearish":
                        # Bearish marker ko candle ke 'High' ke upar lagayenge
                        bearish_markers.loc[date] = df['High'].loc[date] * 1.02

        # 🔹 Step 5: Chart ko plot karna aur save karna
        
        # mplfinance ke liye 'addplot' list taiyaar karna
        addplots = []
        if not bullish_markers.isnull().all():
            addplots.append(mpf.make_addplot(bullish_markers, type='scatter', marker='^', color='green', markersize=100))
        if not bearish_markers.isnull().all():
            addplots.append(mpf.make_addplot(bearish_markers, type='scatter', marker='v', color='red', markersize=100))

        # Chart ko generate aur save karna
        image_path = f"{symbol.upper()}_candlestick_patterns.png"
        chart_title = f"{symbol.upper()} - Candlestick Pattern Analysis (6 Months)\nGreen Arrow (▲) = Bullish, Red Arrow (▼) = Bearish"
        
        mpf.plot(df, 
                 type='candle', 
                 style='yahoo', 
                 title=chart_title,
                 ylabel='Price',
                 addplot=addplots,
                 figratio=(16, 8), # Chart ka size
                 figscale=1.2,
                 savefig=dict(fname=image_path, dpi=100, pad_inches=0.25)
                )

        # 🔹 Step 6: Final text report taiyaar karna
        
        # 6-month ka trend check karna
        trend = "Neutral"
        price_change_pct = (close.iloc[-1] - close.iloc[0]) / close.iloc[0]
        if price_change_pct > 0.10:
            trend = "Overall Bullish"
        elif price_change_pct < -0.10:
            trend = "Overall Bearish"

        final_report = f"--- Candlestick Analysis for {symbol.upper()} ---\n\n"
        if found_patterns_summary:
            final_report += "🕯️ Haal hi mein mile patterns:\n"
            # Sirf recent 10 patterns dikhayenge report mein
            for summary in found_patterns_summary[-10:]:
                final_report += f"- {summary}\n"
        else:
            final_report += "🕯️ Pichle 6 mahino mein koi khaas pattern nahi mila.\n"
        
        final_report += f"\n📈 6-Month Trend: {trend}.\n"
        final_report += f"\n📊 Chart saved to: {image_path}"

        return final_report, image_path

    except Exception as e:
        return f"Candlestick analysis mein error aaya: {e}", None

# --- Example: Is code ko kaise istemal karein ---
if __name__ == "__main__":
    # Yahan koi bhi stock symbol daalein (e.g., 'RELIANCE.NS', 'AAPL', 'MSFT')
    stock_symbol = "RELIANCE.NS"
    
    print(f"Analyzing {stock_symbol}...")
    report, image_file = analyze_and_plot_candlestick_patterns(stock_symbol)
    
    print("\n" + "="*50)
    print(report)
    print("="*50 + "\n")

    if image_file and os.path.exists(image_file):
        print(f"Chart image '{image_file}' सफलतापूर्वक generate ho gayi hai.")
        print("Aap is file ko apne file explorer mein dekh sakte hain.")