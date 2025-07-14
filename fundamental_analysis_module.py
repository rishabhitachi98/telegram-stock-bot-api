# fundamental_analysis_module.py (The Final Robust Version)

import yfinance as yf

def get_fundamental_data(symbol: str) -> dict:
    """
    Fetches key fundamental ratios from yfinance with robust error handling.
    """
    try:
        ticker = yf.Ticker(symbol)
        # .info dictionary mein saara data hota hai
        info = ticker.info
        
        # Helper function to safely get data and handle None values
        def get_info(key, default="N/A"):
            value = info.get(key)
            return value if value is not None and value != 0 else default

        # Zaroori data nikalein
        fundamentals = {
            "Market Cap": get_info('marketCap'),
            "P/E Ratio": get_info('trailingPE'),
            "P/B Ratio": get_info('priceToBook'),
            "Debt to Equity": get_info('debtToEquity'),
            "Dividend Yield": get_info('dividendYield'),
            "Sector": get_info('sector', "Not Available"),
            "Industry": get_info('industry', "Not Available")
        }
        
        # --- Smart Formatting ---
        # Data ko format karne se pehle check karein ki woh ek number hai
        if isinstance(fundamentals.get("Market Cap"), (int, float)):
            mc = fundamentals["Market Cap"]
            if mc > 1_00_00_00_000: # 1 Lakh Crore
                 fundamentals["Market Cap"] = f"₹{mc / 1_00_00_00_000:,.2f} L Cr"
            else:
                 fundamentals["Market Cap"] = f"₹{mc / 1_00_00_000:,.2f} Cr"
        
        if isinstance(fundamentals.get("Dividend Yield"), (int, float)):
            fundamentals["Dividend Yield"] = f"{fundamentals['Dividend Yield'] * 100:.2f}%"

        # Ratios ko 2 decimal places tak round karein
        for key in ["P/E Ratio", "P/B Ratio", "Debt to Equity"]:
            if isinstance(fundamentals.get(key), (int, float)):
                fundamentals[key] = round(fundamentals[key], 2)

        return fundamentals

    except Exception as e:
        print(f"Fundamental data fetch karne mein error '{symbol}' ke liye: {e}")
        # Hamesha ek dictionary return karein, taaki app crash na ho
        return {"error": "Company ka fundamental data nahi mil paaya."}

# --- Test karne ke liye ---
if __name__ == '__main__':
    reliance_fundamentals = get_fundamental_data("RELIANCE.NS")
    if "error" not in reliance_fundamentals:
        print("--- Reliance Fundamental Analysis ---")
        for key, value in reliance_fundamentals.items():
            print(f"- {key}: {value}")