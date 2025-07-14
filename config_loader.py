# config_loader.py - Reads the config.ini file once and provides settings to all other modules.


import os
from dotenv import load_dotenv

# .env file se environment variables load karega
load_dotenv()

# Environment variables se keys lega
GEMINI_API_KEY = os.getenv("AIzaSyCacfMKc6q5r71Qi2sF04nztZNCJ37nxRA")
FINNHUB_API_KEY = os.getenv("d1n1gnhr01qlvnp520ugd1n1gnhr01qlvnp520v0")

# Sirf check karne ke liye ki keys load hui ya nahi
if not GEMINI_API_KEY:
    print("❌ WARNING: GEMINI_API_KEY .env file mein nahi mili.")
    
if not FINNHUB_API_KEY:
    print("❌ WARNING: FINNHUB_API_KEY .env file mein nahi mili.")