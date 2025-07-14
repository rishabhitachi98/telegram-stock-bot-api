# api_main.py

# Python ki zaroori libraries
from fastapi import FastAPI, HTTPException, Response
import uvicorn
import sys
import os
from concurrent.futures import ThreadPoolExecutor

# Apne custom modules ko import karne ke liye
# (Yeh line sunishchit karti hai ki hamare module mil jayein)
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from symbol_map import find_symbol
from candlestick_analysis_with_chart import analyze_and_plot_candlestick_patterns
from stocktwits_module import fetch_stocktwits_data
from fundamental_analysis_module import get_fundamental_data
from tradingview_module import fetch_tradingview_analysis
from news_aggregator_module import get_all_relevant_news
from gemini_module import chat_with_gemini
from prompt_builder import build_gemini_prompt # Yahan humne main1 ka naya naam use kiya
import yfinance as yf

# --- Ek chhota helper function price ke liye ---
def get_latest_price(symbol: str) -> float:
    """Ek stock ka latest closing price laata hai."""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="2d")
        return hist['Close'].iloc[-1] if not hist.empty else 0.0
    except Exception:
        return 0.0

# --- FastAPI App ko shuru karein ---
app = FastAPI(
    title="AI Stock Analyst API",
    description="Yeh API AI aur alag-alag data sources ka istemaal karke stock ka vishleshan karti hai.",
    version="1.0.0"
)

# --- API ke "Endpoints" (URL) banayein ---

@app.get("/")
def read_root():
    """Root URL, yeh check karne ke liye ki API chal rahi hai."""
    return {"Status": "AI Stock Analyst API is active and running!"}

@app.get("/full_analysis/{stock_name}")
async def get_full_analysis(stock_name: str):
    """Diye gaye stock naam par poora vishleshan karta hai."""
    spoken_company = stock_name.strip()
    symbol = find_symbol(spoken_company)

    if not symbol:
        raise HTTPException(status_code=404, detail=f"Stock '{spoken_company}' nahi mila.")

    try:
        # --- Saara data ek saath fetch karein (performance ke liye) ---
        with ThreadPoolExecutor() as executor:
            future_news = executor.submit(get_all_relevant_news, symbol, spoken_company)
            future_price = executor.submit(get_latest_price, symbol)
            future_technicals = executor.submit(fetch_tradingview_analysis, symbol)
            future_fundamentals = executor.submit(get_fundamental_data, symbol)
            future_candle = executor.submit(analyze_and_plot_candlestick_patterns, symbol)
            future_twits = executor.submit(fetch_stocktwits_data, symbol)

            all_news = future_news.result()
            current_price = round(future_price.result(), 2)
            technicals = future_technicals.result()
            fundamentals = future_fundamentals.result()
            candle_summary, chart_path = future_candle.result()
            twits = future_twits.result()

        # --- Gemini ke liye prompt banayein ---
        news_and_sentiment = all_news + ["Sentiment: " + item for item in twits]
        prompt = build_gemini_prompt(symbol, current_price, fundamentals, technicals, candle_summary, news_and_sentiment)
        
        # --- Gemini se report generate karein ---
        gemini_report = chat_with_gemini(prompt)

        # Poori report JSON format mein return karein
        return {
            "stock_name": spoken_company,
            "symbol": symbol,
            "gemini_analysis_report": gemini_report,
            "chart_image_path": chart_path 
        }
    except Exception as e:
        print(f"Analysis ke dauran error: {e}") # Debugging ke liye
        raise HTTPException(status_code=500, detail=f"Analysis ke dauran ek error aa gaya: {str(e)}")

@app.get("/get_chart/{image_path:path}")
async def get_chart_image(image_path: str):
    """Generate ki hui chart image ko serve karta hai."""
    # Security check
    if not image_path.endswith('.png') or '..' in image_path:
        raise HTTPException(status_code=400, detail="Invalid image path.")
        
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Chart image nahi mili.")
    
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    
    # Browser ko batayein ki yeh ek PNG image hai
    return Response(content=image_bytes, media_type="image/png")