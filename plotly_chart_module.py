# plotly_chart_module.py (The new TA-Lib Free module)
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd

def generate_plotly_candlestick(symbol: str) -> (bytes | None):
    """
    Generates a candlestick chart using Plotly and returns the image as bytes.
    It does NOT do any analysis. Analysis will be done by Gemini AI.
    """
    try:
        # Fetch 6 months of data for the chart
        df = yf.Ticker(symbol).history(period="6mo")
        if df.empty:
            print(f"Warning: No data found for {symbol} to generate chart.")
            return None
        
        # Create a Plotly Candlestick Figure
        fig = go.Figure(data=[go.Candlestick(x=df.index,
                                           open=df['Open'],
                                           high=df['High'],
                                           low=df['Low'],
                                           close=df['Close'],
                                           name=symbol)])
        
        fig.update_layout(
            title=f'{symbol} - 6 Month Candlestick Chart',
            yaxis_title='Price (INR)',
            xaxis_rangeslider_visible=False, # Slider ko hata dete hain, aacha dikhta hai
            template='plotly_dark', # Dark theme
            paper_bgcolor='rgba(0,0,0,0)', # Transparent background
            plot_bgcolor='rgba(0,0,0,0)'
        )

        # Save the chart image to in-memory bytes
        # Kaleido library is needed for this: pip install kaleido
        img_bytes = fig.to_image(format="png", width=1000, height=600, scale=2)
        
        return img_bytes

    except Exception as e:
        print(f"ERROR in generate_plotly_candlestick: {e}")
        return None