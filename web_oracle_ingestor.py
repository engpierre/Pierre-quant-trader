import yfinance as yf
import requests
from bs4 import BeautifulSoup
import json
import os

def fetch_web_price(ticker):
    print(f"Executing Web Oracle ingestion for {ticker}...")
    
    # 1. Primary Source: yfinance
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        price = info.get('currentPrice', info.get('lastPrice', info.get('regularMarketPrice')))
        
        # Calculate day change %
        prev_close = info.get('regularMarketPreviousClose')
        change_pct = None
        if price and prev_close:
            change_pct = ((price - prev_close) / prev_close) * 100
            
        if price:
            print(f" -> Successfully fetched {ticker} price from yfinance: {price}")
            return {"ticker": ticker.upper(), "price": price, "change_pct": round(change_pct, 2) if change_pct else None, "source": "yfinance"}
    except Exception as e:
        print(f" -> yfinance failed for {ticker}: {e}")
        
    # 2. Fallback Source: Google Finance scraping
    print(f" -> Falling back to Google Finance for {ticker}...")
    try:
        url = f"https://www.google.com/finance/quote/{ticker}:NASDAQ"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            # Try NYSE
            url = f"https://www.google.com/finance/quote/{ticker}:NYSE"
            response = requests.get(url, headers=headers, timeout=10)
            
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Search for <meta itemprop='price'>
        price_meta = soup.find('meta', itemprop='price')
        if price_meta and price_meta.get('content'):
            price = float(price_meta['content'].replace(',', ''))
            print(f" -> Successfully fetched {ticker} price from Google Finance: {price}")
            return {"ticker": ticker.upper(), "price": price, "change_pct": None, "source": "google_finance"}
        else:
            print(f" -> Could not find <meta itemprop='price'> for {ticker}")
    except Exception as e:
        print(f" -> Google Finance fallback failed for {ticker}: {e}")
        
    return {"ticker": ticker.upper(), "price": None, "change_pct": None, "source": "failed"}

def main():
    tickers = ["NVDA"] # Cross-Verification test for NVDA
    all_web_data = {}
    
    print("Initiating Web Oracle...")
    for ticker in tickers:
        data = fetch_web_price(ticker)
        all_web_data[ticker] = data
        
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web_intel_buffer.json")
    try:
        with open(output_path, "w") as f:
            json.dump({"web_oracle": all_web_data}, f, indent=4)
        print(f"\nSuccessfully generated web intel payload: {output_path}")
    except IOError as e:
        print(f"Failed to write to {output_path}: {e}")

if __name__ == "__main__":
    main()
