# finnhub_news_module.py – Fetches latest, real-time news from Finnhub API

import requests
from datetime import datetime, timedelta

# ❗️❗️ Apni Finnhub API Key yahan daalein ❗️❗️
FINNHUB_API_KEY = "d1n1gnhr01qlvnp520ugd1n1gnhr01qlvnp520v0" # Apni key daalein

def _get_dates_for_api():
    today = datetime.now()
    seven_days_ago = today - timedelta(days=7)
    return seven_days_ago.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')

def fetch_stock_news(stock_symbol: str) -> list[str]:
    if not FINNHUB_API_KEY or "YAHAN_APNI_KEY" in FINNHUB_API_KEY:
        return ["Finnhub API key set nahi hai."]

    from_date, to_date = _get_dates_for_api()
    
    url = (f"https://finnhub.io/api/v1/company-news?"
           f"symbol={stock_symbol}"
           f"&from={from_date}"
           f"&to={to_date}"
           f"&token={FINNHUB_API_KEY}")

    print(f"DEBUG: Calling Finnhub API with URL: {url}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        news_items = response.json()
        
        if news_items:
            # Sirf headline return karo, max 5
            headlines = [item['headline'] for item in news_items[:5]]
            return headlines
        else:
            # Zyaada informative message
            return [f"Finnhub par '{stock_symbol}' ke liye pichle 7 dino mein koi khabar nahi mili. Unka Indian stock coverage seemit ho sakta hai."]

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return ["Finnhub API Key galat ya invalid hai. Kripya check karein."]
        else:
            print(f"Finnhub se news fetch karne mein HTTP error: {e}")
            return [f"Finnhub news service se connect nahi ho pa raha hai (Error: {e.response.status_code})."]
    except requests.exceptions.RequestException as e:
        print(f"Finnhub se news fetch karne mein error: {e}")
        return ["Finnhub news service se connect nahi ho pa raha hai. Network check karein."]