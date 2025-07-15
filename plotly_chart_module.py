# plotly_chart_module.py (THE CORRECTED AND FINAL SYNTAX VERSION)
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
            # Agar data nahi milta, to None return karein (aur raise na karein, ye expected hai)
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
            xaxis_title='Date',
            yaxis_title='Price (INR)',
            xaxis_rangeslider_visible=True,
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_showgrid=True,
            yaxis_showgrid=True,
            xaxis_tickformat='%b %d',
            font=dict(color='white', size=12)
        )

        # Save the chart image to in-memory bytes
        img_bytes = fig.to_image(format="png", width=1000, height=600, scale=2)
        
        return img_bytes

    except Exception as e:
        # Yahan hum error ko print karke raise karenge, taaki Render logs mein dikhe
        error_msg = f"ERROR in generate_plotly_candlestick: {e}"
        print(error_msg)
        raise # <--- Yeh line error ko aage badhayegi