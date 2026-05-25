import os
import time
import requests
import json
from bs4 import BeautifulSoup
import praw
import yfinance as yf
import pandas as pd
import numpy as np
import google.generativeai as genai

env_path = r"C:\Users\Pierre\.openclaw\workspace\pierre-quant\.env"
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                os.environ["GEMINI_API_KEY"] = line.split("=", 1)[1].strip()

class SentimentAgent:
    def __init__(self, ticker):
        self.ticker = ticker
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            
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
        
        CRITICAL DIRECTIVE: You are strictly prohibited from responding in any language other than English. All technical data, analysis, and verdicts must be rendered in English (US/UK) regardless of the source data language.
        """
        
        self.model = genai.GenerativeModel(
            model_name="gemini-3.5-flash",
            system_instruction=self.system_prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )

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

    def fetch_finnhub_sentiment(self):
        finnhub_key = os.getenv("FINNHUB_API_KEY")
        if not finnhub_key:
            return "Finnhub API key missing."
        print("[*] Fetching Finnhub News Sentiment...")
        try:
            url = f"https://finnhub.io/api/v1/news-sentiment?symbol={self.ticker}&token={finnhub_key}"
            response = requests.get(url, timeout=5).json()
            time.sleep(1) # 1-second delay for rate limiting
            buzz = response.get("buzz", {}).get("buzz", 0)
            flag = "[HIGH-CONVICTION RALLY]" if buzz > 80 else ""
            return f"--- FINNHUB SENTIMENT ---\nBuzz Score: {buzz} {flag}\nData: {response}"
        except Exception as e:
            return f"[!] Error fetching Finnhub sentiment: {e}"

    def gather_data(self):
        vix_data = self.fetch_vix()
        finviz = self.scrape_finviz()
        reddit = self.fetch_reddit_discussions()
        finnhub_sentiment = self.fetch_finnhub_sentiment()
        
        return f"{vix_data}\n--- FINVIZ ---\n{chr(10).join(finviz)}\n\n--- REDDIT ---\n{chr(10).join(reddit)}\n\n{finnhub_sentiment}\n"

    def write_buffer(self, payload):
        buffer_path = r"C:\Users\Pierre\.openclaw\workspace\pierre-quant\sentiment_intel_buffer.json"
        with open(buffer_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4)

    def review(self, return_raw=False):
        print(f"[*] Generating Sentiment Report for {self.ticker}...")
        
        if not os.environ.get("GEMINI_API_KEY"):
            err = {"status": "offline", "error": "API Key missing. Sentiment Agent offline."}
            self.write_buffer(err)
            return err
            
        try:
            data = self.gather_data()
            if return_raw:
                return data
                
            prompt = f"Please parse this sentiment data and return a JSON status report:\n{data}"
            response = self.model.generate_content(prompt)
            result = json.loads(response.text)
            result["ticker"] = self.ticker
            self.write_buffer(result)
            return result
        except Exception as e:
            err = {"status": "offline", "error": f"Sentiment agent failed: {str(e)}"}
            self.write_buffer(err)
            return err

if __name__ == "__main__":
    agent = SentimentAgent("NVDA")
    print(agent.review(return_raw=True))
