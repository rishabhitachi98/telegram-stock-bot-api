# finnhub_news_module.py – Fetches latest, real-time news from Finnhub API

import requests
from datetime import datetime, timedelta

# ❗️❗️ Apni Finnhub API Key yahan daalein ❗️❗️
FINNHUB_API_KEY = "d1n1gnhr01qlvnp520ugd1n1gnhr01qlvnp520v0"

def _get_dates_for_api():
    """Aaj ki aur 7 din purani date ko YYYY-MM-DD format mein return karta hai."""
    today = datetime.now()
    seven_days_ago = today - timedelta(days=7)
    return seven_days_ago.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')

def fetch_stock_news(stock_symbol: str) -> list[str]:
    """
    Finnhub API se kisi stock symbol ke liye latest news laata hai.
    Stock symbol .NS ke bina hona chahiye (e.g., 'RELIANCE', 'TATAMOTORS').
    """
    if not FINNHUB_API_KEY or FINNHUB_API_KEY == "YAHAN_APNI_FINNHUB_API_KEY_PASTE_KAREIN":
        return ["Finnhub API key set nahi hai."]

    from_date, to_date = _get_dates_for_api()
    
    # Finnhub API ke liye URL
    url = (f"https://finnhub.io/api/v1/company-news?"
           f"symbol={stock_symbol}"
           f"&from={from_date}"
           f"&to={to_date}"
           f"&token={FINNHUB_API_KEY}")

    print(f"DEBUG: Calling Finnhub API: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        
        news_items = response.json()
        
        if news_items:
            # Sirf headline return karo, max 5
            headlines = [item['headline'] for item in news_items[:5]]
            return headlines
        else:
            return [f"{stock_symbol} ke liye Finnhub par pichle 7 dino mein koi khabar nahi mili."]

    except requests.exceptions.RequestException as e:
        print(f"Finnhub se news fetch karne mein error: {e}")
        return ["Finnhub news service se connect nahi ho pa raha hai."]
    except Exception as e:
        print(f"Finnhub news module mein anjaan error: {e}")
        return ["Finnhub se news fetch karte samay anjaan error aaya."]

# --- Test karne ke liye ---
if __name__ == '__main__':
    # Finnhub ko .NS ke bina symbol chahiye, jaise RELIANCE, TATAMOTORS
    test_headlines = fetch_stock_news("TATAMOTORS") 
    if test_headlines:
        print("\nTata Motors se judi khabrein (Finnhub):")
        for i, headline in enumerate(test_headlines):
            print(f"{i+1}. {headline}")