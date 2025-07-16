# prompt_builder.py (FINALIZED Version for Text Formatting)

def build_gemini_prompt(
    stock_symbol: str,
    current_price: float,
    fundamentals: dict,
    technicals: dict,
    ohlc_data_string: str,
    news_and_sentiment: list[str]
) -> str:
    """
    Gemini AI ke liye updated prompt jo raw candlestick data ka istemal karta hai.
    Ab Markdown formatting aur emojis use honge, HTML tags nahi.
    """
    
    # Data ko aache se format karein
    formatted_fundamentals = "\n".join([f"- {key}: {value}" for key, value in fundamentals.items() if value and value != "N/A"])
    formatted_technicals = "\n".join([f"- {key}: {value}" for key, value in technicals.items() if value])
    formatted_news = "\n".join([f"- {item}" for item in news_and_sentiment])

    # Final prompt
    return f"""
Tum ek anubhavi Indian stock market analyst ho jo modern, visually appealing reports banata hai.
**IMPORTANT RULE: Jawab hamesha HINGLISH mein do, lekin sirf ROMAN SCRIPT (ABCD...) ka istemal karo.**
**OUTPUT FORMAT: Jawab hamesha aache se structured MARKDOWN mein do. HTML tags ka istemal mat karo.**

- Positive (Bullish) points ke liye 🟢 emoji aur **bold text** ka istemal karo.
- Negative (Bearish) points ke liye 🔴 emoji aur **bold text** ka istemal karo.
- Neutral ya important information ke liye 🔵 emoji aur **bold text** ka istemal karo.

--- DATA ---
🔹 **Stock Symbol:** {stock_symbol}
🔹 *   **Current Price:** ₹{current_price}  (Yeh value ko aap apni report mein pehle hi Fundamental View ke upar ya Key Metrics mein highlight kar sakte hain).
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

**Current Live Price:** ₹{current_price}

### 📈 Fundamental View
Company ke fundamentals ke baare mein batao. **Sirf bullet points mein** detail mein batao. Har point ko 🟢, 🔴, 🔵 emoji ke saath shuru karo.

### 📊 Technical View
Technical indicators **aur upar diye gaye candlestick data se mile patterns** kya sanket de rahe hain? Is section ko bhi **sirf bullet points mein** likho. Har point ko 🟢, 🔴, 🔵 emoji ke saath shuru karo.

### 📰 News, Deals & Sentiment Analysis
Latest news aur social media sentiment ka stock par kya asar pad sakta hai? Yeh section bhi **sirf bullet points mein** hona chahiye. Har point ko 🟢, 🔴, 🔵 emoji ke saath shuru karo.

### 🎯 Final Verdict & Actionable Advice
Short-term aur Long-term ke liye kya salah hai? Is stock mein mukhya jokhim (risks) kya hain? Yeh section bhi **sirf bullet points mein** hona chahiye. Har point ko 🟢, 🔴, 🔵 emoji ke saath shuru karo.

Ant mein ek saaf one-line verdict do, use <p> tags mein mat daalna:
**Overall Verdict:** [Strong Buy / Buy / Hold / Sell / Strong Sell] - [Chhota sa kaaran, HINGLISH MEIN]
"""
