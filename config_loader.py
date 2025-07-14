import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use the variable names (not actual values!)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

if GEMINI_API_KEY:
    print("✅ GEMINI_API_KEY loaded successfully.")
else:
    print("❌ WARNING: GEMINI_API_KEY not found in .env file.")

if FINNHUB_API_KEY:
    print("✅ FINNHUB_API_KEY loaded successfully.")
else:
    print("❌ WARNING: Finnhub API Key not found or is a placeholder in config.ini.")
