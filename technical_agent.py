import os
import yfinance as yf
import pandas as pd
import numpy as np
from local_inference import LocalInferenceEngine

class TechnicalAgent:
    def __init__(self, ticker, benchmark="SPY"):
        self.ticker = ticker.upper()
        self.benchmark = benchmark.upper()
        
        self.model = LocalInferenceEngine()
            
        self.system_prompt = f"""
        You are the 'Technical Analysis Agent'.
        
        INSTRUCTIONS:
        1. Review mathematical indicators (MAs, RSI, MACD).
        2. Identify OVERBOUGHT/OVERSOLD conditions.
        3. CRITICAL: Check the provided logic for 'Bullish Divergence' (Price made new low, RSI did not).
        4. CRITICAL: Scan for 'Volume Anomalies' (Volume > 200% of SMA).
        5. Assess Mansfield RS and provide ATR stops.
        
        CRITICAL DIRECTIVE: You are a senior financial analyst; integrate a Monte Carlo simulation to project potential price paths for the given ticker. Use historical volatility and returns to model geometric Brownian motion, running thousands of simulations to generate a probability distribution of future prices. Output a summary of key percentiles, the median project price, and include a clear potential price target designed for dashboard display, alongside your existing technical signals. You MUST explicitly list the projected median price target in a clear, standalone format, ensuring it is visually identifiable for the dashboard.
        
        Produce a highly structured Quant Desk Report summarizing these technicals using the strictly current precise price provided.
        
        CRITICAL DIRECTIVE: You are strictly prohibited from responding in any language other than English. All technical data, analysis, and verdicts must be rendered in English (US/UK) regardless of the source data language.
        """

    def calculate_rsi(self, series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def fetch_and_calculate(self):
        print(f"[*] Fetching technical anomaly data and live price for {self.ticker}...")
        stock_data = yf.download(self.ticker, period="1y", interval="1d", progress=False)
        bench_data = yf.download(self.benchmark, period="1y", interval="1d", progress=False)
        
        # Operation Web-Oracle: Obtain the most accurate and strictly current price
        import json
        import os
        
        live_price = None
        
        # 1. Try Twelve Data Buffer
        tech_buffer_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "technical_intel_buffer.json")
        try:
            if os.path.exists(tech_buffer_path):
                with open(tech_buffer_path, 'r') as f:
                    tech_data = json.load(f)
                    for t, data in tech_data.get('technicals', {}).items():
                        if t.upper() == self.ticker and data.get('price') is not None:
                            live_price = float(data.get('price'))
                            break
        except Exception:
            pass
            
        # 2. Fallback to Web Oracle Buffer
        if live_price is None:
            web_buffer_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web_intel_buffer.json")
            try:
                if os.path.exists(web_buffer_path):
                    with open(web_buffer_path, 'r') as f:
                        web_data = json.load(f)
                        for t, data in web_data.get('web_oracle', {}).items():
                            if t.upper() == self.ticker and data.get('price') is not None:
                                live_price = float(data.get('price'))
                                print(f"[!] Technical Agent: API Offline. Using Web Oracle price: {live_price}")
                                break
            except Exception:
                pass
                
        # 3. Final Fallback to yfinance historical
        if live_price is None:
            try:
                live_info = yf.Ticker(self.ticker).info
                live_price = live_info.get('currentPrice', live_info.get('lastPrice', live_info.get('regularMarketPrice')))
            except:
                live_price = None

        if stock_data.empty: return f"Failed to fetch historical data for {self.ticker}."
        if isinstance(stock_data.columns, pd.MultiIndex):
            stock_data.columns = stock_data.columns.droplevel(1)
            bench_data.columns = bench_data.columns.droplevel(1)

        df = stock_data.copy()
        
        # Inject the precise live price into the dataset prior to calculations
        if live_price is not None:
            df.loc[df.index[-1], 'Close'] = live_price

        # Calculate using the precise updated dataframe
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['Vol_SMA_20'] = df['Volume'].rolling(window=20).mean()
        df['RSI'] = self.calculate_rsi(df['Close'])
        
        # --- NEW ATR CALCULATION ---
        df['H-L'] = df['High'] - df['Low']
        df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
        df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
        df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
        df['ATR'] = df['TR'].rolling(window=14).mean()
        
        latest = df.iloc[-1]
        
        # Volume Anomaly check
        vol_anomaly = False
        if latest['Volume'] > (latest['Vol_SMA_20'] * 2.0):
            vol_anomaly = True
            
        # Bullish Divergence check (Looking back 14 periods)
        recent_14 = df.tail(14)
        min_close_idx = recent_14['Close'].idxmin()
        min_rsi_idx = recent_14['RSI'].idxmin()
        
        bullish_divergence = False
        if min_close_idx != min_rsi_idx and df.loc[min_close_idx]['RSI'] > df.loc[min_rsi_idx]['RSI']:
            if latest['Close'] <= df.loc[min_close_idx]['Close'] * 1.02: # Near the low
                bullish_divergence = True

        # --- NEW MONTE CARLO SIMULATION (3-Months / ~63 Days) ---
        # 1. Calculate log returns to find drift and volatility
        log_returns = np.log(1 + df['Close'].pct_change()).dropna()
        u = log_returns.mean()
        var = log_returns.var()
        drift = u - (0.5 * var)
        stdev = log_returns.std()
        
        # 2. Setup 10,000 simulations over 63 trading days
        t_intervals = 63 
        simulations = 10000
        
        Z = np.random.normal(0, 1, size=(t_intervals, simulations))
        daily_returns = np.exp(drift + stdev * Z)
        
        # 3. Project Price Paths
        price_paths = np.zeros_like(daily_returns)
        price_paths[0] = latest['Close']
        for t in range(1, t_intervals):
            price_paths[t] = price_paths[t-1] * daily_returns[t]
            
        # 4. Extract Percentiles
        final_prices = price_paths[-1]
        bear_case_5th = np.percentile(final_prices, 5)
        median_target_50th = np.percentile(final_prices, 50)
        bull_case_95th = np.percentile(final_prices, 95)

        from datetime import datetime
        current_date = datetime.now().strftime("%B %d, %Y")
        
        data = f"""
        LATEST CHART DATA ({self.ticker}) AS OF {current_date}:
        - TARGET SYMBOL: {self.ticker}
        - DATA PROVENANCE: Source: yfinance | Timestamp: {datetime.utcnow().isoformat()} UTC
        - STRICTLY CURRENT PRICE: {latest['Close']:.2f}
        - Current RSI (Calculated on live price): {latest['RSI']:.2f}
        - ATR-BASED STOP LOSS: {latest['Close'] - (latest['ATR'] * 2):.2f} (Using 2x Multiplier on 14-Day ATR)
        - Volume: {latest['Volume']:.0f} (20-SMA: {latest['Vol_SMA_20']:.0f})
        - Volume Anomaly (>200%): {"YES (FLAGGED)" if vol_anomaly else "NO"}
        - Bullish Divergence Detected: {"YES (FLAGGED)" if bullish_divergence else "NO"}
        
        --- MONTE CARLO PROBABILITY DISTRIBUTION (3-MONTH / 63-DAY PROJECTION) ---
        (Simulated using Geometric Brownian Motion with 10,000 iterations based on 1-Year Historical Volatility: {stdev*100:.2f}% Daily)
        - 5th Percentile (Bear Case): ${bear_case_5th:.2f}
        - 50th Percentile (Median Base Target): ${median_target_50th:.2f}
        - 95th Percentile (Bull Case): ${bull_case_95th:.2f}
        """
        return data

    def review(self, return_raw=False):
        print(f"[*] Generating Technical Report for {self.ticker}...")
        data = self.fetch_and_calculate()
        if return_raw: return data
        
        if not self.model: return f"[!] Missing GEMINI_API_KEY. Data:\n{data}"
        try:
            prompt = f"{self.system_prompt}\n\nPlease generate the technical summary report for {self.ticker} based on this data:\n{data}"
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return str(e)

if __name__ == "__main__":
    TechnicalAgent("AAPL").review()
