# gnews_module.py (Upgraded to return headlines with URLs)

from gnews import GNews
import time

# --- Module Level Configuration ---
gnews_cache = {}
CACHE_DURATION_SECONDS = 1800 # 30 minute cache

def fetch_gnews_for_stock(stock_symbol: str, company_name: str) -> list[dict]:
    """
    Google News se specific stock ya company ke liye relevant news laata hai.
    Returns a list of dictionaries, each containing 'title' and 'url'.
    """
    cache_key = f"gnews_{stock_symbol}"
    
    if cache_key in gnews_cache:
        timestamp, cached_data = gnews_cache[cache_key]
        if time.time() - timestamp < CACHE_DURATION_SECONDS:
            print(f"DEBUG: Google News for '{stock_symbol}' found in cache!")
            return cached_data

    try:
        print(f"DEBUG: Fetching news from Google News for '{company_name}'...")
        google_news = GNews(language='en', country='IN', period='7d')
        
        search_query = f'"{company_name}" share price OR stock news'
        
        news_articles = google_news.get_news(search_query)

        if news_articles:
            # ⬇️⬇️⬇️ YAHAN BADLAV KIYA GAYA HAI ⬇️⬇️⬇️
            # Ab hum title aur url, dono ko ek dictionary mein save karenge
            headlines_with_links = []
            for article in news_articles[:5]: # Sirf top 5 articles lein
                headlines_with_links.append({
                    "title": article['title'],
                    "url": article['url']
                })
            
            # Cache mein save karein
            gnews_cache[cache_key] = (time.time(), headlines_with_links)
            return headlines_with_links
        else:
            # Agar koi news nahi mili, to khali list return karein
            return []

    except Exception as e:
        print(f"Google News fetch karne mein error: {e}")
        # Error ke case mein bhi khali list return karein
        return []