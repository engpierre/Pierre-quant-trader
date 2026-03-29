import os
import requests
from bs4 import BeautifulSoup
import praw
import yfinance as yf
import pandas as pd
import numpy as np
import google.generativeai as genai

class SentimentAgent:
    def __init__(self, ticker):
        self.ticker = ticker
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None
            
        self.reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
        self.reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.reddit_user_agent = "QuantDeskSentimentBot/2.0"
        
        self.system_prompt = f"""
        You are the 'Sentiment Agent'. Target: '{self.ticker}'.
        
        INSTRUCTIONS:
        1. Classify the overall sentiment strictly as Positive, Negative, or Neutral from Finviz and Reddit.
        2. Evaluate the VIX data provided.
           - FLAG as FEAR/PANIC if VIX surges by >= 10%.
        3. Assign a quantitative Sentiment Score (0 to 100).
           - FLAG if consecutive sentiment shifts surpass +/- 0.5 standard deviations from baseline expectations.
        4. Cross-Reference: Is retail sentiment diverging from institutional market action?
        
        Output a structured Quant Desk Report.
        """

    def fetch_vix(self):
        """Fetches the ^VIX standard deviation and surge metrics."""
        print("[*] Fetching VIX fear metrics from yfinance...")
        try:
            vix = yf.download("^VIX", period="1mo", progress=False)
            if vix.empty:
                return "VIX data unavailable."
            if isinstance(vix.columns, pd.MultiIndex):
                vix.columns = vix.columns.droplevel(1)
            closes = vix['Close'].dropna()
            latest = float(closes.iloc[-1])
            prev = float(closes.iloc[-2])
            pct_change = ((latest - prev) / prev) * 100
            
            surge_flag = "SURGE DETECTED (FEAR/PANIC)" if pct_change >= 10 else "NORMAL"
            std_dev = np.std(closes)
            
            return f"""
            --- MARKET VIX DATA ---
            Latest VIX: {latest:.2f}
            Previous VIX: {prev:.2f}
            VIX Change %: {pct_change:.2f}%
            VIX Status: {surge_flag}
            20-Day Std Dev: {std_dev:.2f}
            """
        except Exception as e:
            return f"[!] Error fetching VIX: {e}"

    def scrape_finviz(self):
        try:
            url = f"https://finviz.com/quote.ashx?t={self.ticker}"
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.text, 'html.parser')
            news_table = soup.find(id='news-table')
            headlines = [row.a.text for row in news_table.findAll('tr')[:10] if row.a] if news_table else []
            return headlines
        except:
            return []

    def fetch_reddit_discussions(self, limit=5):
        if not self.reddit_client_id:
            return ["(Reddit API credentials missing - simulated retail hype...)"]
        try:
            reddit = praw.Reddit(client_id=self.reddit_client_id, client_secret=self.reddit_client_secret, user_agent=self.reddit_user_agent)
            return [f"[{sub}] {s.title}" for sub in ["wallstreetbets", "investing"] for s in reddit.subreddit(sub).search(self.ticker, sort='new', limit=limit)]
        except:
            return []

    def gather_data(self):
        vix_data = self.fetch_vix()
        finviz = self.scrape_finviz()
        reddit = self.fetch_reddit_discussions()
        
        return f"{vix_data}\n--- FINVIZ ---\n{chr(10).join(finviz)}\n\n--- REDDIT ---\n{chr(10).join(reddit)}\n"

    def review(self, return_raw=False):
        print(f"[*] Generating Sentiment Report for {self.ticker}...")
        data = self.gather_data()
        if return_raw:
            return data
            
        if not self.model: return f"[!] Missing GEMINI_API_KEY. Context:\n{data}"
        try:
            prompt = f"{self.system_prompt}\n\nPlease parse this data:\n{data}"
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return str(e)

if __name__ == "__main__":
    SentimentAgent("AAPL").review()
