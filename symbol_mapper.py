# symbol_map.py – Enhanced Substring + Fuzzy Matching for NSE symbols

import pandas as pd
from rapidfuzz import process, fuzz

# 🔹 Load NSE data
try:
    df = pd.read_csv("EQUITY_L.csv")
except Exception as e:
    print(f"CSV load error: {e}")
    df = pd.DataFrame(columns=["NAME OF COMPANY", "SYMBOL"])

# 🔹 Normalize helper
def normalize(text):
    return text.strip().lower().replace(" ", "").replace("-", "")

# 🔹 Build master lookup map
company_symbol_map = {
    normalize(row["NAME OF COMPANY"]): row["SYMBOL"].strip() + ".NS"
    for _, row in df.iterrows()
}
symbol_name_map = {
    normalize(row["SYMBOL"]): row["SYMBOL"].strip() + ".NS"
    for _, row in df.iterrows()
}

# 🔹 Combine all possible aliases
all_aliases = {
    **company_symbol_map,
    **symbol_name_map,
    **{normalize(row["NAME OF COMPANY"] + row["SYMBOL"]): row["SYMBOL"].strip() + ".NS"
       for _, row in df.iterrows()}
}

# 🔹 Matching logic
def map_spoken_to_symbol(spoken: str) -> str | None:
    if not spoken:
        return None

    cleaned = normalize(spoken)

    # 1️⃣ Exact match
    if cleaned in all_aliases:
        return all_aliases[cleaned]

    # 2️⃣ Substring match
    for alias in all_aliases:
        if cleaned in alias:
            return all_aliases[alias]

    # 3️⃣ Fuzzy match
    result = process.extractOne(cleaned, all_aliases.keys(), scorer=fuzz.partial_ratio)
    if result:
        match, score, _ = result
        if score > 75:
            return all_aliases[match]

    return None
