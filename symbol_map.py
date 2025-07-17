# symbol_map.py (THE ABSOLUTELY FINAL AND CORRECT VERSION - with get_nifty_500_tickers)

import pandas as pd
from rapidfuzz import process, fuzz, utils
import os
import re
import yfinance as yf

# --- Configuration ---
EQUITY_CSV = "EQUITY_L.csv"
ETF_CSV = "ETFs_list.csv"

# --- Data Loading and Caching (Lazy Loading for better startup) ---
_master_name_map = {} # Ab ye ek empty dict hai
_isin_cache = {}

def _normalize_text(text: str) -> str:
    # Replaced with rapidfuzz's default processor for better consistency
    return utils.default_process(text)

def _load_data_if_needed(): # Naya helper function
    """
    Loads and normalizes data from all sources into a master dictionary.
    This function is called only when find_symbol or get_nifty_500_tickers is first used.
    """
    global _master_name_map
    if _master_name_map: return # Agar data pehle se load hai to kuch na karein

    print("DEBUG: Master Name data (Stocks & ETFs) pehli baar load ho raha hai (lazy)..")
    script_dir = os.path.dirname(__file__)
    
    # Load Equity Stocks
    try:
        equity_path = os.path.join(script_dir, EQUITY_CSV)
        df_equity = pd.read_csv(equity_path)
        df_equity.columns = [col.strip().lower() for col in df_equity.columns]

        for _, row in df_equity.iterrows():
            symbol_with_ns = str(row["symbol"]).strip() + ".NS"
            
            name_normalized = _normalize_text(row["name of company"])
            _master_name_map[name_normalized] = symbol_with_ns
            
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
    Finds a stock symbol using a robust, multi-step process for natural language input.
    """
    _load_data_if_needed() # Ensure data is loaded
    
    # Step 1: Local Name Matching with more aggressive normalization
    if name:
        cleaned_name = _normalize_text(name)
        
        # Try exact match first
        if cleaned_name in _master_name_map:
            print(f"✅ '{name}' ke liye local data se direct match mil gaya.")
            return _master_name_map[cleaned_name]
        
        # Use token_set_ratio for better natural language matching with a forgiving cutoff
        result = process.extractOne(
            cleaned_name,
            _master_name_map.keys(),
            scorer=fuzz.token_set_ratio, # Changed scorer for sentences
            score_cutoff=60,              # Lower cutoff for fuzzy matching in sentences
            processor=utils.default_process # Processor for consistency
        )
        
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

def get_nifty_500_tickers() -> list[str]:
    """
    Loads all equity tickers and returns a sample of top 500.
    (Real Nifty 500 filtering requires an external list or more complex logic,
    for simplicity, we take the first 500 from EQUITY_L.csv).
    """
    _load_data_if_needed() # Ensure data is loaded
    
    tickers = []
    try:
        script_dir = os.path.dirname(__file__)
        equity_path = os.path.join(script_dir, EQUITY_CSV)
        df_equity = pd.read_csv(equity_path)
        df_equity.columns = [col.strip().lower() for col in df_equity.columns]

        # Filter for Equity (not ETFs) and take top N entries
        nifty_500_proxy = df_equity.head(500) 
        
        for _, row in nifty_500_proxy.iterrows():
            symbol_with_ns = str(row["symbol"]).strip() + ".NS"
            tickers.append(symbol_with_ns)
        
        print(f"✅ Loaded {len(tickers)} proxy Nifty 500 tickers.")
        return tickers
    except Exception as e:
        print(f"❌ ERROR loading Nifty 500 tickers: {e}")
        return []

# --- Test karne ke liye (Optional, local testing ke liye) ---
if __name__ == '__main__':
    nifty_tickers = get_nifty_500_tickers()
    print(f"Sample Nifty Tickers: {nifty_tickers[:5]}")
    print(f"Total Nifty Tickers: {len(nifty_tickers)}")