# api_main.py (THE ABSOLUTELY FINAL AND CORRECT VERSION)
from fastapi import FastAPI, HTTPException, Response
import uvicorn
import sys
import os
from concurrent.futures import ThreadPoolExecutor
import re # Needed for list_top_stocks_endpoint
import yfinance as yf # Needed for get_price_and_ohlc, get_bulk_stock_data, get_quarterly_financials

# --- Path aur Imports Setup ---
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from symbol_map import find_symbol, get_nifty_500_tickers # get_nifty_500_tickers for /list
from plotly_chart_module import generate_plotly_candlestick 
from stocktwits_module import fetch_stocktwits_data
from fundamental_analysis_module import get_fundamental_data
from tradingview_module import fetch_tradingview_analysis
from news_aggregator_module import get_all_relevant_news
from gemini_module import chat_with_gemini
from prompt_builder import build_gemini_prompt


# --- FastAPI App ---
app = FastAPI(title="AI Stock Analyst API", version="2.0.0")

# --- In-memory cache for the chart image (server restart hone par clear ho jayega)
chart_cache = {}

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

def get_bulk_stock_data(symbols_list: list[str]) -> list[dict]:
    """
    Fetches essential data for a list of symbols in bulk for screening.
    Returns a list of dictionaries, one for each stock.
    """
    all_stocks_data = []
    print(f"DEBUG: Starting bulk data fetch for {len(symbols_list)} stocks...")

    for symbol in symbols_list: 
        try:
            ticker_obj = yf.Ticker(symbol)
            info = ticker_obj.info 
            
            current_price = info.get('currentPrice')
            if current_price is None:
                hist = ticker_obj.history(period="1d")
                current_price = hist['Close'].iloc[-1] if not hist.empty else 0.0

            stock_data = {
                "symbol": symbol,
                "current_price": round(current_price, 2),
                "pe_ratio": info.get('trailingPE'),
                "pb_ratio": info.get('priceToBook'),
                "debt_to_equity": info.get('debtToEquity'),
                "dividend_yield": info.get('dividendYield'),
                "market_cap": info.get('marketCap'),
                "sector": info.get('sector'),
                "industry": info.get('industry'),
            }
            all_stocks_data.append(stock_data)
            
        except Exception as e:
            print(f"Warning: Could not fetch data for {symbol} in bulk: {e}")
            continue 

    print(f"DEBUG: Finished bulk data fetch for {len(all_stocks_data)} stocks.")
    return all_stocks_data

def get_quarterly_financials(symbol: str) -> str:
    """
    Fetches and formats quarterly financial data (Revenue, Net Income, EPS) 
    and calculates YoY/QoQ growth.
    """
    try:
        ticker = yf.Ticker(symbol)
        financials = ticker.quarterly_financials
        earnings = ticker.quarterly_earnings

        if financials.empty and earnings.empty:
            return "Quarterly financial data uplabdh nahi hai."

        report_lines = ["--- Quarterly Financials ---"]
        report_lines.append("| Quarter | Revenue | YoY % | QoQ % | Net Income | YoY % | QoQ % | EPS | YoY % |")
        report_lines.append("|---|---|---|---|---|---|---|---|---|")

        prev_revenue_yoy = None
        prev_net_income_yoy = None
        prev_eps_yoy = None
        
        # Get latest 4 unique quarter dates
        dates_financials = financials.T.index.to_list()
        dates_earnings = earnings.T.index.to_list()
        all_relevant_dates = sorted(list(set(dates_financials + dates_earnings)), reverse=True)[:4]

        # Collect data for the last 4 quarters for display and calculation
        quarter_data_for_display = []
        for date in all_relevant_dates:
            revenue = financials.T.loc[date].get('Total Revenue', 0) if date in financials.T.index else 0
            net_income = financials.T.loc[date].get('Net Income', 0) if date in financials.T.index else 0
            eps = earnings.T.loc[date].get('Diluted EPS', 0) if date in earnings.T.index else 0
            quarter_data_for_display.append({'date': date, 'revenue': revenue, 'net_income': net_income, 'eps': eps})
        
        # Sort data by date ascending for correct QoQ calculation
        quarter_data_for_display.sort(key=lambda x: x['date'])

        for i, q_data in enumerate(quarter_data_for_display):
            date = q_data['date']
            revenue = q_data['revenue']
            net_income = q_data['net_income']
            eps = q_data['eps']

            revenue_str = f"₹{revenue / 1_00_00_000:,.2f} Cr" if revenue else "N/A"
            net_income_str = f"₹{net_income / 1_00_00_000:,.2f} Cr" if net_income else "N/A"
            eps_str = f"{eps:,.2f}" if eps else "N/A"
            
            yoy_revenue_growth = "N/A"
            qoq_revenue_growth = "N/A"
            yoy_net_income_growth = "N/A"
            qoq_net_income_growth = "N/A"
            yoy_eps_growth = "N/A"

            # YoY Calculation (Requires data from a year ago)
            prev_year_date = date - pd.DateOffset(years=1)
            if prev_year_date in financials.T.index and prev_year_date in earnings.T.index:
                prev_y_rev = financials.T.loc[prev_year_date].get('Total Revenue')
                prev_y_net = financials.T.loc[prev_year_date].get('Net Income')
                prev_y_eps = earnings.T.loc[prev_year_date].get('Diluted EPS')

                if prev_y_rev and revenue:
                    growth = ((revenue - prev_y_rev) / prev_y_rev) * 100 if prev_y_rev != 0 else float('inf')
                    yoy_revenue_growth = f"{growth:+.2f}%" if abs(growth) < 1000 else "N/A"
                if prev_y_net and net_income:
                    growth = ((net_income - prev_y_net) / prev_y_net) * 100 if prev_y_net != 0 else float('inf')
                    yoy_net_income_growth = f"{growth:+.2f}%" if abs(growth) < 1000 else "N/A"
                if prev_y_eps and eps:
                    growth = ((eps - prev_y_eps) / prev_y_eps) * 100 if prev_y_eps != 0 else float('inf')
                    yoy_eps_growth = f"{growth:+.2f}%" if abs(growth) < 1000 else "N/A"
            
            # QoQ Calculation (Requires data from previous quarter in current loop)
            if i > 0:
                prev_q_data = quarter_data_for_display[i-1]
                if prev_q_data['revenue'] and revenue and prev_q_data['revenue'] != 0:
                    qoq_revenue_growth = f"{((revenue - prev_q_data['revenue']) / prev_q_data['revenue']) * 100:+.2f}%"
                if prev_q_data['net_income'] and net_income and prev_q_data['net_income'] != 0:
                    qoq_net_income_growth = f"{((net_income - prev_q_data['net_income']) / prev_q_data['net_income']) * 100:+.2f}%"

            report_lines.append(f"| {date.strftime('%Y-%m')} | {revenue_str} | {yoy_revenue_growth} | {qoq_revenue_growth} | {net_income_str} | {yoy_net_income_growth} | {qoq_net_income_growth} | {eps_str} | {yoy_eps_growth} |")
        
        return "\n".join(report_lines)

    except Exception as e:
        print(f"Error fetching quarterly financials for {symbol}: {e}")
        return "Quarterly financial data fetch nahi ho paaya."

# --- API Endpoints ---

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
        with ThreadPoolExecutor() as executor:
            future_news = executor.submit(get_all_relevant_news, symbol, spoken_company)
            future_price_ohlc = executor.submit(get_price_and_ohlc, symbol)
            future_technicals = executor.submit(fetch_tradingview_analysis, symbol)
            future_fundamentals = executor.submit(get_fundamental_data, symbol)
            future_quarterly_data = executor.submit(get_quarterly_financials, symbol) # New for Quarterly
            future_candle_chart = executor.submit(generate_plotly_candlestick, symbol) 
            future_twits = executor.submit(fetch_stocktwits_data, symbol)

            all_news = future_news.result()
            current_price, ohlc_data_string = future_price_ohlc.result()
            current_price = round(current_price, 2)
            technicals = future_technicals.result()
            fundamentals = future_fundamentals.result()
            quarterly_financials_report = future_quarterly_data.result() # New for Quarterly
            chart_bytes = future_candle_chart.result()
            twits = future_twits.result()
            
        if chart_bytes:
            chart_cache[symbol] = chart_bytes

        prompt = build_gemini_prompt(
            symbol, current_price, fundamentals, technicals, ohlc_data_string, 
            news_and_sentiment, quarterly_financials_report # Pass new quarterly data
        )
        
        gemini_report = chat_with_gemini(prompt)

        return {
            "stock_name": spoken_company,
            "symbol": symbol,
            "gemini_analysis_report": gemini_report,
            "chart_data_status": "Chart generated successfully!" if chart_bytes else "Chart generation failed!",
            "chart_available": True if chart_bytes else False
        }
    except Exception as e:
        print(f"Analysis ke dauran anjaan error aaya: {e}") 
        raise HTTPException(status_code=500, detail=f"Analysis ke dauran ek error aa gaya: {str(e)}")

@app.get("/list_top_stocks")
async def list_top_stocks_endpoint():
    """
    Lists top N stocks based on combined analysis.
    This is a resource-intensive operation.
    """
    try:
        all_nifty_tickers = get_nifty_500_tickers()
        tickers_to_process = all_nifty_tickers[:50] 

        if not tickers_to_process:
            raise HTTPException(status_code=500, detail="Stock tickers list empty.")

        bulk_data = get_bulk_stock_data(tickers_to_process)

        if not bulk_data:
            raise HTTPException(status_code=500, detail="Bulk stock data fetch nahi ho paaya.")

        ranked_stocks = []
        for stock in bulk_data:
            score = (1 / (stock.get('pe_ratio', 100) + 1)) * 100 \
                    + (stock.get('dividend_yield', 0) * 100) \
                    + (stock.get('market_cap', 0) / 1_00_00_000_000_000) * 10 
            
            if stock.get('pe_ratio') is None or stock.get('debt_to_equity') is None:
                score = score * 0.5 
            
            ranked_stocks.append({
                "symbol": stock['symbol'],
                "current_price": stock['current_price'],
                "pe_ratio": stock.get('pe_ratio'),
                "dividend_yield": stock.get('dividend_yield'),
                "score": score,
                "nearest_target": "N/A (AI Target will come here)", 
                "brief_reason": "Loading..." 
            })
        
        ranked_stocks.sort(key=lambda x: x['score'], reverse=True)

        top_10_stocks = ranked_stocks[:10]

        final_top_stocks_with_ai = []
        print(f"DEBUG: Getting AI insights for top {len(top_10_stocks)} stocks...")
        
        for stock_item in top_10_stocks:
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
            
            reason_match = re.search(r"Reason: (.*)", ai_response, re.IGNORECASE)
            target_match = re.search(r"Target: (.*)", ai_response, re.IGNORECASE)

            stock_item['brief_reason'] = reason_match.group(1).strip() if reason_match else "Reason not available."
            stock_item['nearest_target'] = target_match.group(1).strip() if target_match else "Target not available."
            
            final_top_stocks_with_ai.append(stock_item)

        return {"top_stocks": final_top_stocks_with_ai}

    except HTTPException: 
        raise
    except Exception as e:
        print(f"ERROR in list_top_stocks_endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Top stocks list generate nahi ho paayi: {str(e)}")

@app.get("/get_chart/{symbol}")
async def get_chart_image(symbol: str):
# Cache se chart bytes lo
    image_bytes = chart_cache.get(symbol)
    if not image_bytes:
        raise HTTPException(status_code=404, detail="Chart not found in cache. Pehle /full_analysis call karein.")

    return Response(content=image_bytes, media_type="image/png")
    
@app.get("/ping")
def ping_pong():
    """Health check endpoint for keeping the service alive."""
    return {"status": "pong", "message": "API is awake!"}

if __name__ == "__main__":
    uvicorn.run("api_main:app", host="0.0.0.0", port=8000, reload=True)