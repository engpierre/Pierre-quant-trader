import yfinance as yf
from fredapi import Fred
import pandas as pd

class MarketOracle:
    def __init__(self, fred_api_key=None):
        self.fred = Fred(api_key=fred_api_key) if fred_api_key else None

    def get_ticker_telemetry(self, ticker):
        """Fetches raw, sanitized market data for the Reality Anchor."""
        print(f"[Oracle] Fetching live telemetry for {ticker}...")
        data = yf.Ticker(ticker)
        hist = data.history(period="5d")
        
        if hist.empty:
            return None

        current_price = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2]
        volume = hist['Volume'].iloc[-1]
        avg_volume = hist['Volume'].mean()

        # Sanitize for the Critic
        telemetry = {
            "price": round(current_price, 2),
            "change_pct": round(((current_price - prev_close) / prev_close) * 100, 2),
            "volume_delta": round(((volume - avg_volume) / avg_volume) * 100, 2),
            "source": "Live yFinance Ticks"
        }
        return telemetry

    def get_macro_regime(self):
        """Queries FRED for Yield Curve data to define the Regime Anchor."""
        if not self.fred: return "Unknown"
        # 10Y-2Y Spread calculation for Recession/Volatility mapping
        ten_year = self.fred.get_series('DGS10').iloc[-1]
        two_year = self.fred.get_series('DGS2').iloc[-1]
        spread = ten_year - two_year
        return "Trending-Bull" if spread > 0 else "Volatile-Bear"
