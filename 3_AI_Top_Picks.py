import streamlit as st
import time
from concurrent.futures import ThreadPoolExecutor
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from screener_module import run_screener
from fundamental_analysis_module import get_fundamental_data
from tradingview_module import fetch_tradingview_analysis
from news_aggregator_module import get_all_relevant_news
from gemini_module import chat_with_gemini

def fetch_details_for_shortlist(symbols: list[str]) -> list[dict]:
    all_data = []
    for symbol in symbols:
        print(f"Fetching details for {symbol}...")
        with ThreadPoolExecutor(max_workers=3) as inner_executor:
            funda_future = inner_executor.submit(get_fundamental_data, symbol)
            tech_future = inner_executor.submit(fetch_tradingview_analysis, symbol)
            company_name = symbol.split('.')[0]
            news_future = inner_executor.submit(get_all_relevant_news, symbol, company_name)

            funda = funda_future.result()
            tech = tech_future.result()
            news = news_future.result()

        if 'error' not in funda and 'error' not in tech:
            all_data.append({
                "symbol": symbol,
                "company_name": company_name,
                "fundamentals": funda,
                "technicals": tech,
                "news": news
            })
        time.sleep(0.5)
    return all_data

def build_top_picks_prompt(stocks_data: list[dict]):
    prompt_data = ""
    for stock in stocks_data:
        funda_str = "\n    • " + "\n    • ".join([
            f"{k}: <span style='color:#00f5d4;'><b>{v}</b></span>"
            for k, v in stock['fundamentals'].items() if v != 'N/A'
        ])
        tech_str = "\n    • " + "\n    • ".join([
            f"{k}: <span style='color:#00f5d4;'><b>{v}</b></span>"
            for k, v in stock['technicals'].items() if v != 'N/A'
        ])
        news_str = "\n    • " + "\n    • ".join(stock['news']) if stock.get('news') else "No news."

        prompt_data += f"""
--- Stock: {stock['symbol']} ({stock['company_name']}) ---
🔸 **Fundamentals:**{funda_str}
🔸 **Technicals:**{tech_str}
🔸 **Recent News Headlines:**
{news_str}
"""

    return f"""
Tum ek Senior Research Analyst ho. Jawab HINGLISH mein, ROMAN SCRIPT mein, aur MARKDOWN format mein do.
**IMPORTANT: Apne jawab mein important numbers ko <span style="color: #00f5d4;"><b>teal color</b></span> mein dikhana.**

--- SHORTLISTED STOCKS DATA ---
{prompt_data}
--- END OF DATA ---

--- TUMHARA KAAM (HINGLISH MEIN) ---
In stocks mein se **Top 5 stocks** chuno aur unki ek professional research report likho, yeh format follow karo:

### 🏅 Rank #[n]: [Stock Symbol] - [Company Name]
**🔹 Kyun Chunein (Investment Thesis):**
* **Fundamental Reason:** [Top 1-2 points]
* **Technical Reason:** [Indicators like RSI, MACD, SMA etc.]
* **News/Sentiment Trigger:** [News ya recent trigger]
**🔹 Risk Kya Hai?** [Top 1-2 risks]
**🎯 Target Price (6 Mahine):** [Estimated price in INR]

---
"""

# Streamlit UI
st.set_page_config(page_title="AI Top Picks", page_icon="🏆", layout="wide")
st.title("🏆 AI Top Picks")
st.caption("AI-driven screener jo aapke liye behtareen stocks dhoondhta hai.")

if 'top_picks_response' not in st.session_state:
    st.session_state.top_picks_response = ""

if st.button("Find Best Stocks to Buy Now", type="primary", use_container_width=True):
    st.session_state.top_picks_response = ""
    with st.status("Finding best stocks...", expanded=True) as status:
        status.write("Step 1: Screener ke zariye potential stocks dhoonde ja rahe hain...")
        shortlisted_symbols = run_screener()

        if not shortlisted_symbols:
            status.update(label="Analysis Failed!", state="error", expanded=False)
            st.error("Koi bhi stock screener ke rules pe fit nahi baitha.")
        else:
            status.write(f"Step 2: {len(shortlisted_symbols)} shortlisted stocks ka deep analysis ho raha hai...")
            detailed_data = fetch_details_for_shortlist(shortlisted_symbols)

            if not detailed_data:
                status.update(label="Analysis Failed!", state="error", expanded=False)
                st.error("Detailed data fetch nahi ho paaya.")
            else:
                status.write("Step 3: AI Investment Committee final decision le rahi hai...")
                prompt = build_top_picks_prompt(detailed_data)
                response = chat_with_gemini(prompt)

                if response and "Gemini Error:" not in response:
                    st.session_state.top_picks_response = response
                    status.update(label="AI Top Picks Taiyaar Hain!", state="complete", expanded=False)
                else:
                    st.session_state.top_picks_response = ""
                    status.update(label="AI Analysis Failed!", state="error", expanded=False)
                    st.error("AI se proper report nahi mil paayi.")

if st.session_state.top_picks_response:
    st.subheader("🤖 AI Investment Committee ki Final Research Report")
    st.markdown(st.session_state.top_picks_response, unsafe_allow_html=True)
    if st.button("Clear Results"):
        st.session_state.top_picks_response = ""
        st.rerun()
