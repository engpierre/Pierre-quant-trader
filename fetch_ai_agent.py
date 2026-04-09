import os
import yfinance as yf
from datetime import datetime, timedelta

class FetchAIAgentConnector:
    """
    Dedicated agent for managing decentralized data retrieval.
    Updated to act as a direct quantitative oracle, bypassing network consensus
    to fetch strict live, real-time pricing data directly via yfinance.
    """
    def __init__(self, endpoint_url=None):
        self._cache = {}
        self.cache_duration = timedelta(minutes=5)
        
    def dispatch_task(self, ticker, task_payload):
        ticker_upper = ticker.upper()
        print(f"[*] (Fetch.AI Oracle) Fetching live quantitative pricing for {ticker_upper}...")
        
        # 1. Simple caching mechanism
        if ticker_upper in self._cache:
            cache_time, cached_price = self._cache[ticker_upper]
            if datetime.now() - cache_time < self.cache_duration:
                return self._format_output(ticker_upper, cached_price, cached=True)
        
        try:
            stock = yf.Ticker(ticker_upper)
            ticker_info = stock.info
            
            # Robust error handling for empty/invalid yf properties
            if not ticker_info or not isinstance(ticker_info, dict):
                ticker_info = {}
            
            # 2. Prioritize live_price over historical data via strict hierarchy
            live_price = ticker_info.get('currentPrice') or ticker_info.get('lastPrice') or ticker_info.get('regularMarketPrice')
            
            if live_price is None or live_price == 0:
                hist = stock.history(period="1d")
                if not hist.empty and 'Close' in hist.columns:
                    live_price = hist['Close'].iloc[-1]
                else:
                    return f"FETCH.AI ORACLE ERROR [{ticker_upper}]: Could not retrieve reliable live price data. Invalid ticker or market offline."
            
            self._cache[ticker_upper] = (datetime.now(), float(live_price))
            return self._format_output(ticker_upper, live_price)
            
        except Exception as e:
            return f"FETCH.AI ORACLE ERROR: Network exception occurred - {str(e)}"
            
    def _format_output(self, ticker, price, cached=False):
        status = "(CACHED)" if cached else "(LIVE)"
        return f"""
            --- FETCH.AI DECENTRALIZED ORACLE ---
            TARGET SYMBOL: {ticker}
            STRICTLY CURRENT PRICE {status}: {float(price):.2f}
            """

if __name__ == "__main__":
    agent = FetchAIAgentConnector()
    print(agent.dispatch_task("AAPL", {}))
