import os
import yfinance as yf
import pandas as pd
import numpy as np
import google.generativeai as genai

class TechnicalAgent:
    def __init__(self, ticker, benchmark="SPY"):
        self.ticker = ticker.upper()
        self.benchmark = benchmark.upper()
        
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None
            
        self.system_prompt = f"""
        You are the 'Technical Analysis Agent'.
        
        INSTRUCTIONS:
        1. Review mathematical indicators (MAs, RSI, MACD).
        2. Identify OVERBOUGHT/OVERSOLD conditions.
        3. CRITICAL: Check the provided logic for 'Bullish Divergence' (Price made new low, RSI did not).
        4. CRITICAL: Scan for 'Volume Anomalies' (Volume > 200% of SMA).
        5. Assess Mansfield RS and provide ATR stops.
        
        Produce a highly structured Quant Desk Report summarizing these technicals using the strictly current precise price provided.
        """

    def calculate_rsi(self, series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def fetch_and_calculate(self):
        print(f"[*] Fetching technical anomaly data and live price for {self.ticker}...")
        stock_data = yf.download(self.ticker, period="3mo", interval="1d", progress=False)
        bench_data = yf.download(self.benchmark, period="3mo", interval="1d", progress=False)
        
        # Obtain the most accurate and strictly current price
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
