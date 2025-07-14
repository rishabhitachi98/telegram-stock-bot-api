# prompt_builder.py (Updated for Plan B)

def build_gemini_prompt(
    stock_symbol: str,
    current_price: float,
    fundamentals: dict,
    technicals: dict,
    ohlc_data_string: str, # <-- Badlaav: 'candle_summary' ki jagah yeh naya argument
    news_and_sentiment: list[str]
) -> str:
    """
    Gemini AI ke liye updated prompt jo raw candlestick data ka istemaal karta hai.
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
🔹 **Latest News & Social Sentiment:**
{formatted_news}

--- CANDLESTICK ANALYSIS TASK ---
Neeche pichle 10 dinon ka Open, High, Low, Close (OHLC) data hai.
{ohlc_data_string}
Is OHLC data ko gehraai se analyze karo aur batao ki kya koi important bullish (jaise Hammer, Morning Star, Bullish Engulfing) ya bearish (jaise Shooting Star, Hanging Man, Bearish Engulfing) candlestick patterns ban rahe hain. Apne analysis ko "Technical View" section mein shaamil karna.
--- END OF DATA ---

--- TUMHARA KAAM (HINGLISH MEIN) ---
Upar diye gaye DATA aur CANDLESTICK ANALYSIS TASK ke aadhar par ek structured, visually appealing report taiyaar karo.

### 📈 Fundamental View
Company ke fundamentals ke baare mein batao.

### 📊 Technical View
Technical indicators **aur upar diye gaye candlestick data se mile patterns** kya sanket de rahe hain?

### 📰 News, Deals & Sentiment Analysis
Latest news aur social media sentiment ka stock par kya asar pad sakta hai?

### 🎯 Final Verdict & Actionable Advice
Short-term aur Long-term ke liye kya salah hai? Is stock mein mukhya jokhim (risks) kya hain?

Ant mein ek saaf one-line verdict do:
**<p style="background-color: #E3F2FD; border-left: 5px solid #2196F3; padding: 10px;">Overall Verdict: [Strong Buy / Buy / Hold / Sell / Strong Sell] - [Chhota sa kaaran, HINGLISH MEIN]</p>**
"""