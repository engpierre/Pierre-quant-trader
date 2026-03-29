import os
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import google.generativeai as genai

class FundamentalAgent:
    def __init__(self, ticker):
        self.ticker = ticker.upper()
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None
            
        self.system_prompt = """
        You are the 'Fundamental Agent'.
        
        INSTRUCTIONS:
        1. Evaluate Profitability Margins, Debt, and Revenue Growth.
        2. Evaluate P/E against Sector expectation.
        3. CRITICAL NEW DIRECTIVE: Analyze explicitly the SEC Form 4 insider buying/selling activity provided.
           - FLAG clusters of net positive buying within the 60-day window.
           - Calculate overall net accumulation/distribution context.
        """

    def scrape_openinsider(self):
        """Scrapes Form 4 clusters in 60-day window."""
        print(f"[*] Fetching Form 4 Insider Clusters for {self.ticker}...")
        try:
            url = f"http://openinsider.com/search?q={self.ticker}"
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'class': 'tinytable'})
            if not table or not table.find('tbody'): return "No insider data found."
            
            buys, sells = 0, 0
            limit_date = datetime.now() - timedelta(days=60)
            
            for row in table.find('tbody').find_all('tr'):
                cols = row.find_all('td')
                if len(cols) < 12: continue
                
                dt_str = cols[1].text.split(' ')[0]
                if datetime.strptime(dt_str, "%Y-%m-%d") < limit_date: continue
                
                ttype = cols[7].text.upper()
                c_suite = "CEO" in cols[5].text.upper() or "CFO" in cols[5].text.upper()
                
                if "P - PURCHASE" in ttype and c_suite: buys += 1
                elif "S - SALE" in ttype and c_suite: sells += 1
                
            return f"\n--- 60-DAY FORM 4 CLUSTER DATA ---\nC-Suite Purchases (Count): {buys}\nC-Suite Sales (Count): {sells}\nNet Activity: {'ACCUMULATION' if buys > sells else 'DISTRIBUTION'}"
        except Exception as e:
            return f"Error scraping openinsider: {e}"

    def fetch_financial_data(self):
        print(f"[*] Fetching fundamentals for {self.ticker}...")
        try:
            stock = yf.Ticker(self.ticker)
            info = stock.info
            pe = info.get('trailingPE', 'N/A')
            marg = info.get('profitMargins', 'N/A')
            dte = info.get('debtToEquity', 'N/A')
            sect = info.get('sector', 'N/A')
        except:
            pe, marg, dte, sect = 'N/A', 'N/A', 'N/A', 'N/A'
            
        form4_data = self.scrape_openinsider()
        
        return f"""
        FUNDAMENTALS FOR {self.ticker} (Sector: {sect}):
        Trailing P/E: {pe}
        Profit Margin: {marg}
        Debt-to-Equity: {dte}
        {form4_data}
        """

    def review(self, return_raw=False):
        print(f"[*] Generating Fundamental Report for {self.ticker}...")
        data = self.fetch_financial_data()
        if return_raw: return data
        if not self.model: return data
        
        try:
            prompt = f"{self.system_prompt}\n\nParse this SEC fundamental data:\n{data}"
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return str(e)

if __name__ == "__main__":
    FundamentalAgent("AAPL").review()
