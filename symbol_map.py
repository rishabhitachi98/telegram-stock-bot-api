# symbol_map.py (The Ultimate Version with Better Normalization and Fuzzy Logic)

import pandas as pd
from rapidfuzz import process, fuzz
import os
import re
import yfinance as yf

# --- Configuration ---
EQUITY_CSV = "EQUITY_L.csv"
ETF_CSV = "ETFs_list.csv"

# --- Data Loading and Caching ---
_master_name_map = None
_isin_cache = {}

def _normalize_text(text: str) -> str:
    """
    An aggressive normalization that removes all non-alphanumeric characters,
    making fuzzy matching on typos more effective.
    Example: "Tata Power Co. Ltd." -> "tatapower"
    """
    if not isinstance(text, str): text = str(text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Replace '&' with 'and' for consistency
    text = text.replace('&', 'and')
    
    # Remove all non-alphanumeric characters (including spaces, dots, commas, etc.)
    # This joins the words into a single string for better typo matching.
    return re.sub(r'[^a-z0-9]', '', text)

def _initialize_maps():
    """
    Loads and normalizes data from all sources into a master dictionary.
    """
    global _master_name_map
    if _master_name_map is not None: return

    print("DEBUG: Master Name data (Stocks & ETFs) pehli baar load ho raha hai...")
    _master_name_map = {}
    script_dir = os.path.dirname(__file__)
    
    # Load Equity Stocks
    try:
        equity_path = os.path.join(script_dir, EQUITY_CSV)
        df_equity = pd.read_csv(equity_path)
        df_equity.columns = [col.strip().lower() for col in df_equity.columns]

        for _, row in df_equity.iterrows():
            symbol_with_ns = str(row["symbol"]).strip() + ".NS"
            
            # Alias #1: Company's full name
            name_normalized = _normalize_text(row["name of company"])
            _master_name_map[name_normalized] = symbol_with_ns
            
            # Alias #2: Ticker Symbol
            symbol_normalized = _normalize_text(row["symbol"])
            _master_name_map[symbol_normalized] = symbol_with_ns

        print(f"✅ Stocks loaded: {len(df_equity)} entries.")
    except Exception as e:
        print(f"❌ ERROR loading Equity CSV: {e}")

    # Load ETFs
    try:
        etf_path = os.path.join(script_dir, ETF_CSV)
        df_etf = pd.read_csv(etf_path)
        df_etf.columns = [col.strip().lower() for col in df_etf.columns]
        
        for _, row in df_etf.iterrows():
            symbol_with_ns = str(row["symbol"]).strip() + ".NS"
            if 'underlying asset' in row and pd.notna(row['underlying asset']):
                _master_name_map[_normalize_text(row['underlying asset'])] = symbol_with_ns
            if 'symbol' in row and pd.notna(row['symbol']):
                _master_name_map[_normalize_text(row['symbol'])] = symbol_with_ns
        print(f"✅ ETFs loaded and merged.")
    except Exception as e:
        print(f"❌ ERROR loading ETF CSV: {e}")

def _find_symbol_by_isin_live(isin: str) -> str | None:
    # ... (This function remains the same, no changes needed) ...
    isin = str(isin).strip()
    if isin in _isin_cache: return _isin_cache[isin]
    try:
        ticker = yf.Ticker(isin)
        symbol_from_yf = ticker.info.get('symbol')
        if symbol_from_yf:
            base_symbol = str(symbol_from_yf).split('.')[0]
            final_symbol = base_symbol + ".NS"
            _isin_cache[isin] = final_symbol
            return final_symbol
    except Exception:
        return None
    return None

def find_symbol(name: str, isin: str = None) -> str | None:
    """
    Finds a stock symbol using a robust, multi-step process.
    """
    _initialize_maps()

    # Step 1: Local Name Matching with more aggressive normalization
    if name:
        # Use the new aggressive normalization
        cleaned_name = _normalize_text(name)
        
        # Try exact match first
        if cleaned_name in _master_name_map:
            print(f"✅ '{name}' ke liye local data se direct match mil gaya.")
            return _master_name_map[cleaned_name]
        
        # Use a more forgiving scorer for typos on single-string names
        result = process.extractOne(cleaned_name, _master_name_map.keys(), scorer=fuzz.ratio, score_cutoff=90)
        
        if result:
            best_match_str, score, _ = result
            print(f"DEBUG: Smart fuzzy match mila: '{name}' -> '{best_match_str}' (Score: {score})")
            return _master_name_map[best_match_str]

    # Step 2: Live ISIN Lookup (Fallback)
    if isin and str(isin).strip().startswith('INE'):
        symbol_from_isin = _find_symbol_by_isin_live(isin)
        if symbol_from_isin:
            print(f"✅ Naam se nahi mila, lekin Equity ISIN '{isin}' se live match mil gaya.")
            return symbol_from_isin

    print(f"⚠️ WARNING: '{name}' (ISIN: {isin}) ke liye koi bhi accha match nahi mila.")
    return None