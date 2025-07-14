# news_aggregator_module.py (The Master Hub for All News)

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from finnhub_corporate_actions import fetch_high_impact_news
from gnews_module import fetch_gnews_for_stock
from et_rss_module import fetch_et_market_news # <-- ET ko wapis import kiya

def get_all_relevant_news(stock_symbol: str, company_name: str) -> list[str]:
    """
    Fetches news from Finnhub, Google News, and ET RSS feed.
    """
    print(f"DEBUG: Fetching news from all sources (Finnhub, GNews, ET)...")
    
    # --- Data Fetching (in parallel for better performance in the future) ---
    finnhub_news = fetch_high_impact_news(stock_symbol)
    gnews = fetch_gnews_for_stock(stock_symbol, company_name)
    et_news = fetch_et_market_news() # <-- ET se data fetch kiya

    # --- Combining and Formatting ---
    combined_news = []
    
    # Section 1: Stock-Specific News
    # Yeh sabse upar dikhegi kyunki yeh sabse relevant hai
    combined_news.append("--- Stock-Specific News ---")

    # Finnhub se Corporate Actions
    finnhub_found = False
    if finnhub_news:
        for item in finnhub_news:
            if "Error:" not in item and "khabar nahi mili" not in item:
                combined_news.append(f"[Corporate Action] {item}")
                finnhub_found = True
    
    # Google News se specific news
    gnews_found = False
    if gnews:
        for article in gnews:
            markdown_link = f"[Google News] [{article['title']}]({article['url']})"
            combined_news.append(markdown_link)
            gnews_found = True

    if not finnhub_found and not gnews_found:
        combined_news.append("Is stock ke liye koi specific news nahi mili.")

    # Section 2: General Market News
    # Yeh neeche dikhegi
    combined_news.append("\n--- General Market Headlines (from ET) ---")
    if et_news:
        for item in et_news:
             if "Error:" not in item and "news nahi mili" not in item:
                combined_news.append(f"[ET] {item}")
    
    if not combined_news:
        return ["Koi bhi news source se khabar nahi mil paayi."]
        
    return combined_news