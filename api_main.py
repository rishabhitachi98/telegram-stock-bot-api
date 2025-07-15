# api_main.py (The Final Plan B Version)
from fastapi import FastAPI, HTTPException, Response
import uvicorn
import sys
import os
from concurrent.futures import ThreadPoolExecutor

# --- Path aur Imports Setup ---
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from symbol_map import find_symbol
from plotly_chart_module import generate_plotly_candlestick # <-- Naya import
from stocktwits_module import fetch_stocktwits_data
from fundamental_analysis_module import get_fundamental_data
from tradingview_module import fetch_tradingview_analysis
from news_aggregator_module import get_all_relevant_news
from gemini_module import chat_with_gemini
from prompt_builder import build_gemini_prompt
import yfinance as yf

# --- FastAPI App ---
app = FastAPI(title="AI Stock Analyst API", version="2.0.0")

# --- Helper Functions ---
def get_price_and_ohlc(symbol: str) -> (float, str):
    """Ek hi call mein price aur pichle 10 din ka OHLC data laata hai."""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="11d") # 11 din ka data taaki 10 din ka result mile
        if hist.empty:
            return 0.0, "OHLC data nahi mila."
        
        latest_price = hist['Close'].iloc[-1]
        # Pichle 10 din ka data string format mein
        ohlc_string = hist.tail(10)[['Open', 'High', 'Low', 'Close']].round(2).to_string()
        
        return latest_price, ohlc_string
    except Exception as e:
        print(f"Error fetching price/OHLC for {symbol}: {e}")
        return 0.0, "OHLC data nahi mila."

# In-memory cache for the chart image
chart_cache = {}

@app.get("/")
def read_root():
    return {"Status": "AI Stock Analyst API v2.0 (Plotly) is running!"}

@app.get("/full_analysis/{stock_name}")
async def get_full_analysis(stock_name: str):
    spoken_company = stock_name.strip()
    symbol = find_symbol(spoken_company)

    if not symbol:
        raise HTTPException(status_code=404, detail=f"Stock '{spoken_company}' not found.")

    try:
        # --- Data Concurrently Fetch Karein ---
        with ThreadPoolExecutor() as executor:
            future_news = executor.submit(get_all_relevant_news, symbol, spoken_company)
            future_price_ohlc = executor.submit(get_price_and_ohlc, symbol)
            future_technicals = executor.submit(fetch_tradingview_analysis, symbol)
            future_fundamentals = executor.submit(get_fundamental_data, symbol)
            future_candle_chart = executor.submit(generate_plotly_candlestick, symbol)
            future_twits = executor.submit(fetch_stocktwits_data, symbol)

            all_news = future_news.result()
            current_price, ohlc_data_string = future_price_ohlc.result()
            current_price = round(current_price, 2)
            technicals = future_technicals.result()
            fundamentals = future_fundamentals.result()
            chart_bytes = future_candle_chart.result()
            twits = future_twits.result()
            
        # Chart ko cache mein store karein
        if chart_bytes:
            chart_cache[symbol] = chart_bytes

        # --- Gemini ke liye Prompt Banayein ---
        news_and_sentiment = all_news + ["Sentiment: " + item for item in twits]
        prompt = build_gemini_prompt(
            symbol, current_price, fundamentals, technicals, ohlc_data_string, news_and_sentiment
        )
        
        # --- Gemini se Report Generate Karein ---
        gemini_report = chat_with_gemini(prompt)

        return {
            "stock_name": spoken_company,
            "symbol": symbol,
            "gemini_analysis_report": gemini_report,
            "chart_available": True if chart_bytes else False
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis ke dauran error: {str(e)}")

# Naya endpoint chart image ke liye
@app.get("/get_chart/{symbol}")
async def get_chart_image(symbol: str):
    # Cache se chart bytes lo
    image_bytes = chart_cache.get(symbol)
    
    if not image_bytes:
        raise HTTPException(status_code=404, detail="Chart not found in cache. Pehle /full_analysis call karein.")
    
    return Response(content=image_bytes, media_type="image/png")

# api_main.py (New Ping Endpoint)

@app.get("/ping")
def ping_pong():
    """
    Health check endpoint for keeping the service alive.
    """
    return {"status": "pong", "message": "API is awake!"}
if __name__ == "__main__":
    uvicorn.run("api_main:app", host="0.0.0.0", port=8000, reload=True)