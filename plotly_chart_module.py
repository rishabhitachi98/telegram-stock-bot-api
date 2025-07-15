# plotly_chart_module.py (FINAL VERSION for Chart Readability)
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd

def generate_plotly_candlestick(symbol: str) -> (bytes | None):
    """
    Generates a candlestick chart using Plotly and returns the image as bytes.
    If any error occurs, it will raise an exception for debugging.
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
            xaxis_title='Date',  # X-axis label
            yaxis_title='Price (INR)',  # Y-axis label
            xaxis_rangeslider_visible=True, # Rangeslider visible
            template='plotly_dark',  # Dark theme
            paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
            plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot area
            xaxis_showgrid=True,  # X-axis grid lines
            yaxis_showgrid=True,  # Y-axis grid lines
            xaxis_tickformat='%b %d',  # Dates ko "Jul 15" format mein dikhayega
            font=dict(color='white', size=12),  # Font color aur size dark theme ke liye
            margin=dict(l=80, r=80, t=80, b=80) # Margins badhayi labels ke liye
        )

        # Save the chart image to in-memory bytes
        img_bytes = fig.to_image(format="png", width=1200, height=700, scale=2) # Image dimensions badhayi
        
        return img_bytes

    except Exception as e:
        # Yahan hum error ko print karke raise karenge, taaki Render logs mein dikhe
        error_msg = f"ERROR in generate_plotly_candlestick: {e}"
        print(error_msg)
        raise # <-- Yeh line error ko aage badhayegi