# api_main.py (THE CORRECTED AND FINAL SYNTAX VERSION)
from fastapi import FastAPI, HTTPException, Response
import uvicorn
import sys
import os
from concurrent.futures import ThreadPoolExecutor


# --- Path aur Imports Setup ---
# Yeh line ensure karti hai ki aapke custom modules mil jayein
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from symbol_map import find_symbol
from plotly_chart_module import generate_plotly_candlestick # <-- Plotly chart module
from stocktwits_module import fetch_stocktwits_data
from fundamental_analysis_module import get_fundamental_data
from tradingview_module import fetch_tradingview_analysis
from news_aggregator_module import get_all_relevant_news
from gemini_module import chat_with_gemini
from prompt_builder import build_gemini_prompt
import yfinance as yf

import re # <-- Naya import

# --- FastAPI App ---
app = FastAPI(title="AI Stock Analyst API", version="2.0.0")

# --- Helper Functions ---
def get_price_and_ohlc(symbol: str) -> (float, str):
    """Ek hi call mein price aur pichle 10 din ka OHLC data laata hai."""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="11d") 
        if hist.empty:
            return 0.0, "OHLC data nahi mila."
        
        latest_price = hist['Close'].iloc[-1]
        ohlc_string = hist.tail(10)[['Open', 'High', 'Low', 'Close']].round(2).to_string()
        
        return latest_price, ohlc_string
    except Exception as e:
        print(f"Error fetching price/OHLC for {symbol}: {e}")
        return 0.0, "OHLC data nahi mila."

# In-memory cache for the chart image (server restart hone par clear ho jayega)
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
            # generate_plotly_candlestick ab exception raise karega agar fail hua
            future_candle_chart = executor.submit(generate_plotly_candlestick, symbol) 
            future_twits = executor.submit(fetch_stocktwits_data, symbol)

            all_news = future_news.result()
            current_price, ohlc_data_string = future_price_ohlc.result()
            current_price = round(current_price, 2)
            technicals = future_technicals.result()
            fundamentals = future_fundamentals.result()
            
            # Chart generation mein error aane par future_candle_chart.result() yahan exception raise karega
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
            "chart_data_status": "Chart generated successfully!" if chart_bytes else "Chart generation failed!",
            "chart_available": True if chart_bytes else False
        }
    except Exception as e:
        # Global exception handler, will catch errors from any of the future.result() calls
        print(f"Analysis ke dauran anjaan error aaya: {e}") # Render logs mein dikhega
        raise HTTPException(status_code=500, detail=f"Analysis ke dauran ek error aa gaya: {str(e)}")

# Naya endpoint chart image ke liye
@app.get("/get_chart/{symbol}")




# api_main.py (New endpoint for /list command)

from symbol_map import get_nifty_500_tickers # <-- Naya import

@app.get("/list_top_stocks")
async def list_top_stocks_endpoint():
    """
    Lists top N stocks based on combined analysis.
    This is a resource-intensive operation.
    """
    try:
        # 1. Stocks ki list lo
        # Abhi ke liye, hum Nifty 500 proxy se sirf 50 stocks lenge
        # Sabhi 500 stocks ka data fetch karna timeout de sakta hai free tier par
        all_nifty_tickers = get_nifty_500_tickers()
        
        # Limited number of stocks for actual processing on free tier
        # Aap is number ko baad mein badha sakte hain agar performance theek rahi
        tickers_to_process = all_nifty_tickers[:50] 

        if not tickers_to_process:
            raise HTTPException(status_code=500, detail="Stock tickers list empty.")

        # 2. Bulk data fetch karein
        # get_bulk_stock_data is function ko hum bana chuke hain
        bulk_data = get_bulk_stock_data(tickers_to_process)

        if not bulk_data:
            raise HTTPException(status_code=500, detail="Bulk stock data fetch nahi ho paaya.")

        # 3. Scoring aur Ranking (Abhi ke liye dummy logic)
        # Yahan hum ranking logic daalenge. Abhi ke liye, sirf sample data
        ranked_stocks = []
        for stock in bulk_data:
            # Dummy Score: P/E (inverted) + Dividend Yield + Market Cap (random)
            score = (1 / (stock.get('pe_ratio', 100) + 1)) * 100 \
                    + (stock.get('dividend_yield', 0) * 100) \
                    + (stock.get('market_cap', 0) / 1_00_00_000_000_000) * 10 # Random factor
            
            # Agar koi fundamental data missing hai, score ko kam karein
            if stock.get('pe_ratio') is None or stock.get('debt_to_equity') is None:
                score = score * 0.5 # Kam score kar do
            
            ranked_stocks.append({
                "symbol": stock['symbol'],
                "current_price": stock['current_price'],
                "pe_ratio": stock.get('pe_ratio'),
                "dividend_yield": stock.get('dividend_yield'),
                "score": score,
                # Yahan aap dummy target bhi de sakte hain abhi
                "nearest_target": "N/A (AI Target will come here)", 
                "brief_reason": "Loading..." # AI reason will come here
            })
        
        # Scores ke aadhar par sort karein (Highest score top par)
        ranked_stocks.sort(key=lambda x: x['score'], reverse=True)

        # Top 10 stocks ko select karein
        top_10_stocks = ranked_stocks[:10]

        # 4. Gemini se Final Analysis aur Target Price (Loop ke andar)
        # Har stock ke liye AI se brief summary aur nearest target nikalwayenge.
        # Yeh process time-consuming hoga.
        final_top_stocks_with_ai = []
        print(f"DEBUG: Getting AI insights for top {len(top_10_stocks)} stocks...")
        
        for stock_item in top_10_stocks:
            # Ek brief prompt banayein is stock item ke liye
            brief_prompt = f"""
            Tum ek Indian Stock Market Analyst ho. Neeche ek stock ka data hai:
            Symbol: {stock_item['symbol']}
            Current Price: ₹{stock_item['current_price']}
            P/E Ratio: {stock_item['pe_ratio']}
            Dividend Yield: {stock_item['dividend_yield']}

            Is data ke aadhar par, is stock mein invest karne ka ek **chhota sa reason (20-30 words)** HINGLISH mein do.
            Aur is stock ka **nearest possible target price (अगले 1-3 mahine)** HINGLISH mein batao.
            Format:
            Reason: [Reason here]
            Target: [Target Price]
            """
            
            ai_response = chat_with_gemini(brief_prompt)
            
            # Gemini ke response ko parse karein
            reason_match = re.search(r"Reason: (.*)", ai_response, re.IGNORECASE)
            target_match = re.search(r"Target: (.*)", ai_response, re.IGNORECASE)

            stock_item['brief_reason'] = reason_match.group(1).strip() if reason_match else "Reason not available."
            stock_item['nearest_target'] = target_match.group(1).strip() if target_match else "Target not available."
            
            final_top_stocks_with_ai.append(stock_item)

        return {"top_stocks": final_top_stocks_with_ai}

    except HTTPException: # Re-raise HTTPException if find_symbol failed etc.
        raise
    except Exception as e:
        print(f"ERROR in list_top_stocks_endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Top stocks list generate nahi ho paayi: {str(e)}")
        
async def get_chart_image(symbol: str):
    # Cache se chart bytes lo
    image_bytes = chart_cache.get(symbol)
    
    if not image_bytes:
        raise HTTPException(status_code=404, detail="Chart not found in cache. Pehle /full_analysis call karein.")
    
    return Response(content=image_bytes, media_type="image/png")

@app.get("/ping")
def ping_pong():
    """
    Health check endpoint for keeping the service alive.
    """
    return {"status": "pong", "message": "API is awake!"}

if __name__ == "__main__":
    uvicorn.run("api_main:app", host="0.0.0.0", port=8000, reload=True)