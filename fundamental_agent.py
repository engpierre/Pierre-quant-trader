import os
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from local_inference import LocalInferenceEngine

class FundamentalAgent:
    def __init__(self, ticker):
        self.ticker = ticker.upper()
        self.model = LocalInferenceEngine()
            
        self.system_prompt = """
        You are the 'Fundamental Agent'.
        
        INSTRUCTIONS:
        1. Evaluate the strictly current active price provided alongside Profitability Margins, Debt, and Revenue Growth.
        2. Evaluate P/E against Sector expectation.
        3. CRITICAL NEW DIRECTIVE: Analyze explicitly the SEC Form 4 insider buying/selling activity provided.
           - FLAG clusters of net positive buying within the 60-day window.
           - Calculate overall net accumulation/distribution context.
        
        CRITICAL DIRECTIVE: You are strictly prohibited from responding in any language other than English. All technical data, analysis, and verdicts must be rendered in English (US/UK) regardless of the source data language.
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
            
            # Prioritize retrieving the most accurate and strictly current price available
            current_price = info.get('currentPrice', info.get('lastPrice', info.get('regularMarketPrice', 'N/A')))
            pe = info.get('trailingPE', 'N/A')
            marg = info.get('profitMargins', 'N/A')
            dte = info.get('debtToEquity', 'N/A')
            if isinstance(dte, (int, float)):
                # Before passing to the Supervisor, normalize the D/E ratio
                # Most APIs return D/E as a raw number where 0.20 = 20%
                # If the value is > 5 and it's a Mega-cap, it's almost certainly a percentage misread
                if dte > 5.0:
                    # Check if the value looks like a percentage (e.g., 19.5)
                    # Standard Mega-cap D/E is rarely over 2.0 (200%)
                    dte = dte / 100
            sect = info.get('sector', 'N/A')
        except:
            current_price, pe, marg, dte, sect = 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'
            
        form4_data = self.scrape_openinsider()
        
        return f"""
        FUNDAMENTALS FOR {self.ticker} (Sector: {sect}):
        STRICTLY CURRENT PRICE: {current_price}
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
