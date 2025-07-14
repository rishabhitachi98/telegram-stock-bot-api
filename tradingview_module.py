# tradingview_module.py (The Final Robust Version)

from tradingview_ta import TA_Handler, Interval

def fetch_tradingview_analysis(symbol: str) -> dict:
    """
    Fetches a comprehensive set of indicators from TradingView
    with robust error handling.
    """
    try:
        # Indian stocks ke liye .NS hatana zaroori hai
        clean_symbol = symbol.replace(".NS", "")
        
        handler = TA_Handler(
            symbol=clean_symbol,
            exchange="NSE",
            screener="india",
            interval=Interval.INTERVAL_1_DAY,
            timeout=15
        )

        analysis = handler.get_analysis()

        # Helper function to safely get indicator values and handle None
        def get_indicator(key, default="N/A"):
            value = analysis.indicators.get(key)
            # Agar value None hai, to default return karein
            if value is None:
                return default
            return round(value, 2)

        # Saare zaroori indicators ko ek dictionary mein daalein
        technicals = {
            "Overall Recommendation": analysis.summary.get("RECOMMENDATION", "N/A"),
            "RSI": get_indicator("RSI"),
            "Stoch.K": get_indicator("Stoch.K"),
            "MACD Level": get_indicator("MACD.macd"),
            "MACD Signal": get_indicator("MACD.signal"),
            "Bollinger Upper": get_indicator("BB.upper"),
            "Bollinger Lower": get_indicator("BB.lower"),
            "SMA-20": get_indicator("SMA20"),
            "SMA-50": get_indicator("SMA50"),
            "SMA-200": get_indicator("SMA200"),
        }

        return technicals

    except Exception as e:
        print(f"TradingView se data fetch karte samay error for '{symbol}': {e}")
        # Hamesha ek dictionary return karein, taaki app crash na ho
        return {"error": "TradingView se technical data nahi mil paaya."}

# --- Test karne ke liye ---
if __name__ == '__main__':
    reliance_data = fetch_tradingview_analysis("RELIANCE.NS")
    if "error" not in reliance_data:
        print("--- Reliance Technical Analysis (from TradingView) ---")
        for key, value in reliance_data.items():
            print(f"- {key}: {value}")