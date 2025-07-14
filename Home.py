# Home.py
import streamlit as st

st.set_page_config(
    page_title="StockBot AI Home",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Welcome to StockBot AI!")
st.sidebar.success("Upar se ek analysis tool chunein.")

st.markdown(
    """
    **StockBot AI aapka personal stock market vishleshak hai.**

    **👈 Sidebar se ek tool chunein:**

    - ### 1. Stock Analyzer
      Kisi bhi ek stock ka gehraai se 360-degree analysis karein.

    - ### 2. Portfolio Analyzer
      Apne Groww portfolio ko upload karke uski sehat, risks, aur performance ka vishleshan karein.
    """
)