# excel_to_json_converter.py (Final Stable Version)

import pandas as pd
import json
import sys

try:
    from symbol_map import find_symbol
except ImportError:
    print("❌ ERROR: 'symbol_map.py' file nahi mili.")
    sys.exit(1)

EXCEL_COLUMN_NAMES = {
    "name": "Stock Name",
    "isin": "ISIN",
    "quantity": "Quantity",
    "avg_price": "Average buy price"
}

def convert_excel_to_json(excel_path, json_path):
    try:
        print(f"Reading Excel file: {excel_path}")
        df = pd.read_excel(excel_path)
        required_cols = list(EXCEL_COLUMN_NAMES.values())
        if not all(col in df.columns for col in required_cols):
            print(f"\n❌ ERROR: Excel file mein zaroori columns nahi mile! Humein chahiye: {required_cols}")
            return

        portfolio_data = []
        print("Processing portfolio...")
        for index, row in df.iterrows():
            try:
                company_name = str(row[EXCEL_COLUMN_NAMES["name"]])
                isin = str(row[EXCEL_COLUMN_NAMES["isin"]])
                if pd.isna(row[EXCEL_COLUMN_NAMES["quantity"]]) or pd.isna(row[EXCEL_COLUMN_NAMES["avg_price"]]): continue
                quantity = int(row[EXCEL_COLUMN_NAMES["quantity"]])
                avg_price = float(row[EXCEL_COLUMN_NAMES["avg_price"]])
                if quantity <= 0: continue

                symbol = find_symbol(company_name, isin=isin)
                
                if not symbol: continue
                
                portfolio_data.append({"symbol": symbol, "quantity": quantity, "avg_price": avg_price})
            except (ValueError, TypeError):
                print(f"⚠️ WARNING: Row #{index+2} ({company_name}) ko skip kar rahe hain.")
                continue

        with open(json_path, 'w') as f: json.dump(portfolio_data, f, indent=2)
        print(f"\n✅ SUCCESS! File '{json_path}' सफलतापूर्वक ban gayi hai.")
    except Exception as e:
        print(f"❌ ERROR: Ek anjaan error aa gaya: {e}")

if __name__ == "__main__":
    print("--- Groww Excel to JSON Converter (Ultimate Version) ---")
    default_excel_path = "Holdings.xlsx"
    excel_file = input(f"Aapki Groww Excel file ka naam kya hai? (default: {default_excel_path}): ")
    if not excel_file: excel_file = default_excel_path
    convert_excel_to_json(excel_file, "portfolio.json")
    print("\nAb aap is 'portfolio.json' file ko StockBot app mein upload kar sakte hain.")
    input("Press Enter to exit.")