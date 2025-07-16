import plotly.graph_objects as go
import yfinance as yf
import pandas as pd

def generate_plotly_candlestick(symbol: str) -> (bytes | None):
    """
    Generates a high-res candlestick chart with axis labels, ticks, and white font for Telegram.
    """
    try:
        df = yf.Ticker(symbol).history(period="6mo")
        if df.empty:
            print(f"Warning: No data found for {symbol} to generate chart.")
            return None

        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name=symbol
        )])

        # Combined layout block with both your request + enhancements
        fig.update_layout(
            title=f'{symbol} - 6 Month Candlestick Chart',
            xaxis_title='Date',
            yaxis_title='Price (INR)',
            xaxis_rangeslider_visible=False,
            template='plotly_dark',
            font=dict(size=20, color='white'),
            xaxis_tickangle=-45,
            xaxis=dict(
                showgrid=True,
                tickformat='%b %d',
                tickfont=dict(size=20)
            ),
            yaxis=dict(
                showgrid=True,
                tickfont=dict(size=20)
            ),
            margin=dict(l=100, r=100, t=100, b=100),
            width=2400,
            height=1400
        )

        img_bytes = fig.to_image(format="png", width=2400, height=1400, scale=3)
        return img_bytes

    except Exception as e:
        print(f"ERROR in generate_plotly_candlestick: {e}")
        raise
