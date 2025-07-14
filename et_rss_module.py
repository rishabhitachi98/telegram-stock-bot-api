# et_rss_module.py – Fetches top market news from The Economic Times RSS feed.

import feedparser
import time

# --- Module Level Configuration ---
rss_cache = {}
CACHE_DURATION_SECONDS = 1800 # 30 minute cache
ET_MARKETS_RSS_URL = "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"

def fetch_et_market_news() -> list[str]:
    """
    The Economic Times Markets RSS feed se top headlines laata hai.
    """
    if 'et_market_news' in rss_cache:
        timestamp, cached_data = rss_cache['et_market_news']
        if time.time() - timestamp < CACHE_DURATION_SECONDS:
            print("DEBUG: Economic Times news found in cache!")
            return cached_data

    try:
        print(f"DEBUG: Fetching news from Economic Times RSS Feed...")
        feed = feedparser.parse(ET_MARKETS_RSS_URL)

        if feed.entries:
            # Sirf top 5 headlines laayein
            headlines = [entry.title for entry in feed.entries[:5]]
            rss_cache['et_market_news'] = (time.time(), headlines)
            return headlines
        else:
            return ["Economic Times RSS feed se koi news nahi mili."]

    except Exception as e:
        print(f"Economic Times RSS feed fetch karne mein error: {e}")
        return ["Economic Times news service se connect nahi ho pa raha hai."]