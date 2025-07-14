# main1.py (The Final, Cleaned-up Version for Streamlit App)

# Is file ka kaam ab sirf Gemini ke liye prompt banana hai.
# Hum yahan se baaki sabhi bematlab ke imports hata denge taaki koi error na aaye.

def build_gemini_prompt(
    stock_symbol: str,
    current_price: float,
    fundamentals: dict,
    technicals: dict,
    candle_summary: str,
    news_and_sentiment: list[str]
) -> str:
    """
    Gemini AI ke liye final, aadhunik prompt jo HTML/Markdown ka istemal karta hai.
    """
    
    # Data ko aache se format karein
    formatted_fundamentals = "\n".join([f"- {key}: {value}" for key, value in fundamentals.items() if value and value != "N/A"])
    formatted_technicals = "\n".join([f"- {key}: {value}" for key, value in technicals.items() if value])
    formatted_news = "\n".join([f"- {item}" for item in news_and_sentiment])

    # Final prompt
    return f"""
Tum ek anubhavi Indian stock market analyst ho jo modern, visually appealing reports banata hai.
**IMPORTANT RULE: Jawab hamesha HINGLISH mein do, lekin sirf ROMAN SCRIPT (ABCD...) ka istemal karo.**
**OUTPUT FORMAT: Jawab hamesha aache se structured MARKDOWN mein do. Important keywords ko highlight karne ke liye HTML tags ka istemal karo.**

- Positive (Bullish) points ke liye <span style="color: #4CAF50; font-weight: bold;">green color</span> ka istemal karo.
- Negative (Bearish) points ke liye <span style="color: #F44336; font-weight: bold;">red color</span> ka istemal karo.
- Neutral ya important information ke liye <span style="color: #2196F3; font-weight: bold;">blue color</span> ka istemal karo.

--- DATA ---
🔹 **Stock Symbol:** {stock_symbol}
🔹 **Current Price:** ₹{current_price}
🔹 **Fundamental Analysis:**
{formatted_fundamentals}
🔹 **Technical Indicators (from TradingView):**
{formatted_technicals}
🔹 **Candlestick Pattern Analysis:**
{candle_summary}
🔹 **Latest News & Social Sentiment:**
{formatted_news}
--- END OF DATA ---

--- TUMHARA KAAM (HINGLISH MEIN) ---
Upar diye gaye DATA ke aadhar par ek structured, visually appealing report taiyaar karo.

### 📈 Fundamental View
Company ke fundamentals ke baare mein batao.

### 📊 Technical View
Technical indicators aur candlestick patterns kya sanket de rahe hain?

### 📰 News, Deals & Sentiment Analysis
Latest news aur social media sentiment ka stock par kya asar pad sakta hai?

### 🎯 Final Verdict & Actionable Advice
Short-term aur Long-term ke liye kya salah hai? Is stock mein mukhya jokhim (risks) kya hain?

Ant mein ek saaf one-line verdict do:
**<p style="background-color: #E3F2FD; border-left: 5px solid #2196F3; padding: 10px;">Overall Verdict: [Strong Buy / Buy / Hold / Sell / Strong Sell] - [Chhota sa kaaran, HINGLISH MEIN]</p>**
"""