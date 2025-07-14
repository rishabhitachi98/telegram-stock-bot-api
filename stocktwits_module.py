# stocktwits_module.py – Final, Truly Self-Contained Smart Version with Data Cleaning

import requests
import re # Regular Expressions ke liye naya import

def _clean_message_body(text: str) -> str:
    """
    StockTwits message body se faltu cheezein hatata hai.
    """
    if not text:
        return ""

    # 1. URLs ko hatayein
    text = re.sub(r'http\S+|www\S+', '', text)

    # 2. Stock symbols ($SYMBOL.NSE) ko hatayein
    text = re.sub(r'\$\w+\.\w+', '', text)

    # 3. Ajeeb character spacing ko theek karein (e.g., "K A L Y A N...")
    # Yeh pehle ajeeb spacing ko hatata hai, fir saaf karta hai
    text = re.sub(r'\s*([A-Z])\s*', r'\1', text) 
    # Example: "K A L Y A N" banega "KALYAN"

    # 4. Naye lines aur extra spaces ko hatakar ek saaf line banayein
    text = re.sub(r'\s+', ' ', text).strip()

    return text

def _make_api_call(symbol: str) -> dict | None:
    """Helper function to make one API call and handle errors."""
    url = f"https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json"
    print(f"DEBUG: Calling StockTwits API with URL: {url}")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"INFO: Symbol '{symbol}' not found on StockTwits (404).")
        else:
            print(f"StockTwits API par HTTP Error: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"StockTwits se connect hone mein error: {e}")
        return None

def fetch_stocktwits_data(symbol: str) -> list[str]:
    """
    StockTwits se data laata hai aur use saaf karke return karta hai.
    """
    original_symbol = symbol.upper()
    primary_symbol = original_symbol
    fallback_symbol = None

    if original_symbol.endswith(".NS"):
        primary_symbol = original_symbol.replace(".NS", ".NSE") # .NSE ko .XNSE se try karna behtar hai
        fallback_symbol = original_symbol.replace(".NS", "")

    data = _make_api_call(primary_symbol)

    if (data is None or 'messages' not in data or not data['messages']) and fallback_symbol:
        print(f"INFO: Primary symbol '{primary_symbol}' se data nahi mila. Fallback '{fallback_symbol}' se try kar rahe hain...")
        data = _make_api_call(fallback_symbol)

    if data and data.get('messages'):
        formatted_messages = []
        for message in data['messages'][:5]:
            user = message['user']['username']
            # YAHAN NAYA CLEANING FUNCTION CALL HO RAHA HAI
            text = _clean_message_body(message['body'])
            
            # Agar message saaf karne ke baad khali ho jaye, to use skip karein
            if not text:
                continue

            sentiment = "Neutral"
            if message.get('entities', {}).get('sentiment'):
                sentiment = message['entities']['sentiment']['basic']
            
            formatted_messages.append(f"({sentiment}) {user}: {text}")
        
        # Agar saare messages khali nikle, to ek default message dein
        if not formatted_messages:
            return [f"StockTwits par '{original_symbol}' ke liye relevant messages nahi mile."]
        
        return formatted_messages
    
    return [f"StockTwits par '{original_symbol}' ke liye koi khaas message nahi mila."]