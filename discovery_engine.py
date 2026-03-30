import yfinance as yf
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')

class ScoutAgent:
    def __init__(self):
        # A representative basket of high-liquidity mega/large caps for rapid scanning (Proxy for S&P 100)
        self.universe = [
            "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "BRK-B", "LLY", "AVGO",
            "JPM", "V", "WMT", "UNH", "MA", "PG", "HD", "JNJ", "ORCL", "MRK", 
            "COST", "ABBV", "CVX", "CRM", "BAC", "NFLX", "AMD", "PEP", "LIN", "KO",
            "TMO", "WFC", "DIS", "CSCO", "MCD", "ABT", "INTU", "INTC", "QCOM", "AMAT"
        ]
        self.benchmark = "SPY"
        self.period = "1y" # Pulling 1 year of data for the moving average calculation constraints

    def get_mrs(self, ticker_history, spy_history):
        """
        Mansfield Relative Strength (MRS)
        Formula: ((Price_Ticker / Price_SPY) / SMA(Price_Ticker / Price_SPY, 52) - 1) * 10
        Using a 52 rolling window to perfectly execute the "Base Breakout" hunt.
        """
        try:
            # Align indices safely
            df = pd.DataFrame({
                'ticker_close': ticker_history['Close'],
                'spy_close': spy_history['Close'],
                'volume': ticker_history['Volume']
            }).dropna()

            if len(df) < 52:
                return -999, 0

            # Step 1: Ratio of Target vs SPY
            df['ratio'] = df['ticker_close'] / df['spy_close']
            
            # Step 2: 52-period SMA of that Ratio
            df['sma_ratio'] = df['ratio'].rolling(window=52).mean()
            
            # Step 3: Core Mansfield Eq.
            df['mrs'] = ((df['ratio'] / df['sma_ratio']) - 1) * 10
            
            # Volume Delta (Current Volume vs 20 day avg to align with Swarm Technical triggers)
            df['vol_sma'] = df['volume'].rolling(window=20).mean()
            df['vol_delta'] = df['volume'] / df['vol_sma']

            current_mrs = df['mrs'].iloc[-1]
            current_vol_delta = df['vol_delta'].iloc[-1]
            
            return current_mrs, current_vol_delta
        except Exception as e:
            return -999, 0

    def run_reconnaissance(self):
        print(f"[*] Dispatching Scout Engine: Scanning Universe ({len(self.universe)} target nodes) vs {self.benchmark}...")
        
        # Download benchmark
        spy_hist = yf.download(self.benchmark, period=self.period, progress=False)
        
        results = []
        
        # Batch download for operational speed
        tickers_str = " ".join(self.universe)
        data = yf.download(tickers_str, period=self.period, group_by='ticker', progress=False)

        for ticker in self.universe:
            try:
                # Handle single vs multi ticker dataframe formatting
                if len(self.universe) == 1:
                    hist = data
                else:
                    hist = data[ticker]
                    
                mrs, vol_delta = self.get_mrs(hist, spy_hist)
                
                # Rule of Engagement: Only flag Positive MRS & Solid Volume Divergences
                if mrs > 0 and vol_delta > 1.2:
                    results.append({
                        "ticker": ticker,
                        "mrs": round(mrs, 3),
                        "vol_delta": round(vol_delta, 2)
                    })
            except Exception as e:
                continue
                
        df_results = pd.DataFrame(results)
        if df_results.empty:
            print("[!] Scout returned no explosive nodes. Defaulting to Megacap baselines.")
            return ["AAPL", "MSFT", "NVDA"] 

        # Sort by highest mathematically isolated breakout strength
        df_results = df_results.sort_values(by="mrs", ascending=False)
        
        # Lock top 10 Targets for Covariance Routing
        top_targets = df_results.head(10)['ticker'].tolist()
        print(f"[!] Autonomously Extracted {len(top_targets)} Breakouts. Routing to Correlation Agent: {top_targets}")
        return top_targets

if __name__ == "__main__":
    scout = ScoutAgent()
    targets = scout.run_reconnaissance()
    print("Execution Hand-Out:", targets)
