# 🔧 Updated build_top_picks_prompt()
def build_top_picks_prompt(stocks_data: list[dict]):
    prompt_data = ""
    for stock in stocks_data:
        funda_str = "\n    • " + "\n    • ".join([
            f"{k}: <span style='color:#00f5d4;'><b>{v}</b></span>"
            for k, v in stock['fundamentals'].items() if v != 'N/A'
        ])
        tech_str = "\n    • " + "\n    • ".join([
            f"{k}: <span style='color:#00f5d4;'><b>{v}</b></span>"
            for k, v in stock['technicals'].items() if v != 'N/A'
        ])
        news_str = "\n    • " + "\n    • ".join(stock['news']) if stock.get('news') else "No news."

        prompt_data += f"""
--- Stock: {stock['symbol']} ({stock['company_name']}) ---
🔸 **Fundamentals:**{funda_str}
🔸 **Technicals:**{tech_str}
🔸 **Recent News Headlines:**
{news_str}
"""

    return f"""
Tum ek Senior Research Analyst ho. Jawab HINGLISH mein, ROMAN SCRIPT mein, aur MARKDOWN format mein do.
**IMPORTANT: Apne jawab mein important numbers ko <span style="color: #00f5d4;"><b>teal color</b></span> mein highlight karo.**

--- SHORTLISTED STOCKS DATA ---
{prompt_data}
--- END OF DATA ---

--- TUMHARA KAAM (HINGLISH MEIN) ---
In stocks mein se **Top 5 stocks** chuno aur unhe ek professional report ke roop mein likho. Har stock ke liye neeche ka format follow karo:

### 🏅 Rank #[n]: [Stock Symbol] - [Company Name]

**🔹 Kyun Chunein (Investment Thesis):**
* **Fundamental Reason:** [Top 1-2 fundamental points]
* **Technical Reason:** [Top 1-2 technical indicators]
* **News/Sentiment Trigger:** [Relevant positive ya negative news headline]

**🔹 Risk Kya Hai?**
* [Top 1–2 risks mention karo based on data]

**🎯 Target Price (6 Mahine):** [Realistic estimated price range]

---
❗IMPORTANT: Koi table ya short summary mat do. Har stock ke liye upar wale format ka use karo aur markdown mein likho.
"""


# ✅ Target Price Estimator
def estimate_target_price(pe_ratio, eps, expected_growth_pct):
    try:
        if pe_ratio and eps and expected_growth_pct:
            return round(pe_ratio * eps * (1 + expected_growth_pct / 100), 2)
    except:
        pass
    return "Unavailable"

# ✅ Updated get_fundamental_data()
import yfinance as yf

def get_fundamental_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        pe = info.get("trailingPE")
        eps = info.get("trailingEps")
        roe = info.get("returnOnEquity")
        debt_to_equity = info.get("debtToEquity")
        promoter_hold = info.get("heldPercentInsiders")
        market_cap = info.get("marketCap")
        revenue_growth = info.get("revenueGrowth")

        target = estimate_target_price(pe, eps, 12)  # Assume 12% annual growth

        return {
            "P/E Ratio": pe,
            "EPS (TTM)": eps,
            "ROE": roe,
            "Debt/Equity": debt_to_equity,
            "Promoter Holding %": promoter_hold,
            "Market Cap": market_cap,
            "Revenue Growth %": revenue_growth,
            "Estimated Target Price": f"₹{target}" if target != "Unavailable" else "N/A"
        }
    except Exception as e:
        return {"error": str(e)}

# ✅ Updated fetch_tradingview_analysis()
from tradingview_ta import TA_Handler, Interval, Exchange

def fetch_tradingview_analysis(symbol):
    try:
        handler = TA_Handler(
            symbol=symbol.replace(".NS", ""),
            screener="india",
            exchange="NSE",
            interval=Interval.INTERVAL_1_DAY
        )
        analysis = handler.get_analysis()
        indicators = analysis.indicators

        return {
            "RSI": indicators.get("RSI"),
            "MACD": indicators.get("MACD.macd"),
            "SMA50": indicators.get("SMA50"),
            "SMA200": indicators.get("SMA200"),
            "Recommendation": analysis.summary.get("RECOMMENDATION"),
            "Support": indicators.get("S1"),
            "Resistance": indicators.get("R1"),
            "Volume": indicators.get("volume")
        }
    except Exception as e:
        return {"error": str(e)}

# ✅ Screener Module: get_quantitative_data and run_screener()
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor

EQUITY_CSV = "EQUITY_L.csv"
_screener_cache = None

def _calculate_rsi(data: pd.Series, window: int = 14) -> float:
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    if loss.iloc[-1] == 0: return 100.0
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def get_quantitative_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        hist = ticker.history(period="1y")
        if len(hist) < 200: return None

        close_prices = hist['Close']
        score = 0

        market_cap = info.get('marketCap', 0)
        if market_cap > 50000000000: score += 1

        pe_ratio = info.get('trailingPE')
        if pe_ratio is not None and 0 < pe_ratio < 40: score += 1

        debt_to_equity = info.get('debtToEquity')
        if debt_to_equity is not None and debt_to_equity < 1.0: score += 2

        sma_50 = close_prices.rolling(window=50).mean().iloc[-1]
        sma_200 = close_prices.rolling(window=200).mean().iloc[-1]
        if sma_50 > sma_200: score += 1

        rsi = _calculate_rsi(close_prices, 14)
        if rsi is not None and 40 < rsi < 65: score += 1

        return {"symbol": symbol, "score": score}
    except Exception:
        return None

def run_screener() -> list[str]:
    global _screener_cache
    if _screener_cache is not None:
        print("DEBUG: Cached screener results ka istemal ho raha hai.")
        return _screener_cache

    print("DEBUG: Niyam-aadharit screener (scoring system) chal raha hai...")
    try:
        df = pd.read_csv(EQUITY_CSV)
        symbols_to_scan = [s + ".NS" for s in df['SYMBOL'].head(200)]
    except Exception as e:
        print(f"❌ ERROR: '{EQUITY_CSV}' ko load karte samay error aaya: {e}")
        return []

    all_stock_scores = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(get_quantitative_data, symbols_to_scan))

    print("DEBUG: Fetched data ko score kiya ja raha hai...")
    for data in results:
        if data and data['score'] >= 3:
            all_stock_scores.append(data)

    if not all_stock_scores:
        print("DEBUG: Scoring ke baad bhi koi stock nahi mila.")
        return []

    sorted_stocks = sorted(all_stock_scores, key=lambda x: x['score'], reverse=True)
    shortlisted_symbols = [s['symbol'] for s in sorted_stocks[:20]]

    print(f"DEBUG: Screener poora hua. Shortlisted {len(shortlisted_symbols)} stocks.")
    _screener_cache = shortlisted_symbols
    return shortlisted_symbols
