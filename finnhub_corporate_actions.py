# finnhub_corporate_actions.py – Using API Key from config.ini (No Caching)

import requests
from datetime import datetime, timedelta
from config_loader import FINNHUB_API_KEY # <-- Naya import

# --- Module Level Configuration ---
is_finnhub_configured = False

# Sirf ek baar check karein ki key config se aayi hai ya nahi
if FINNHUB_API_KEY and "YAHAN_APNI" not in FINNHUB_API_KEY:
    is_finnhub_configured = True
    print("✅ Finnhub module configured successfully.")
else:
    print("❌ WARNING: Finnhub API Key not found or is a placeholder in config.ini.")


def _make_api_call(endpoint: str, params: dict):
    """Helper function to make API calls to Finnhub."""
    base_url = "https://finnhub.io/api/v1"
    url = f"{base_url}/{endpoint}"
    params['token'] = FINNHUB_API_KEY # Key ab config se aa rahi hai
    
    print(f"DEBUG: Calling Finnhub API for '{endpoint}'...")
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Finnhub API call to '{endpoint}' failed: {e}")
        return None

def fetch_high_impact_news(stock_symbol: str) -> list[str]:
    """
    Finnhub se high-impact news jaise dividends, earnings, aur khaas deals laata hai.
    """
    # Guard Clause: Sabse pehle check karo ki module aache se configure hua hai ya nahi
    if not is_finnhub_configured:
        return ["Finnhub Error: Module is not configured. Please check your API Key in config.ini."]

    symbol_for_api = stock_symbol.upper().replace(".NS", "")
    today = datetime.now()
    ten_days_ago = (today - timedelta(days=10)).strftime('%Y-%m-%d')
    all_events = []

    # 1. Fetch Earnings
    earnings_data = _make_api_call("calendar/earnings", {'symbol': symbol_for_api})
    if earnings_data and earnings_data.get('earningsCalendar'):
        for event in earnings_data['earningsCalendar']:
            event_date = event.get('date', '')
            if event_date >= ten_days_ago:
                eps = event.get('epsEstimate', 'N/A')
                all_events.append(f"Earnings Announcement: Expected on {event_date} (Est. EPS: {eps})")

    # 2. Fetch News
    keywords = {'deal', 'acquisition', 'merger', 'order', 'launch', 'partnership', 'profit', 'results', 'dividend', 'raise fund', 'joint venture', 'approve', 'contract', 'new plant'}
    news_data = _make_api_call("company-news", {
        'symbol': symbol_for_api, 'from': ten_days_ago, 'to': today.strftime('%Y-%m-%d')
    })
    
    if news_data:
        filtered_headlines = {item['headline'] for item in news_data if item and any(keyword in item.get('headline', '').lower() for keyword in keywords)}
        if filtered_headlines:
            all_events.extend(list(filtered_headlines)[:5])

    if not all_events:
        return [f"Finnhub par pichle 10 dino mein koi khaas deals/dividend/projects ki khabar nahi mili."]

    return all_events