# CRITICAL DIRECTIVE: You are strictly prohibited from responding in any language other than English. All technical data, analysis, and verdicts must be rendered in English (US/UK) regardless of the source data language.
import json
import os
import sys
import time
import requests

API_KEY = "f76a1dce8347443a8aa2ca4dd09a90cd"
BASE_URL = "https://api.twelvedata.com"

def fetch_indicator(endpoint, params):
    params['apikey'] = API_KEY
    url = f"{BASE_URL}{endpoint}"
    for attempt in range(3):
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            if 'code' in data and data.get('status') == 'error':
                print(f"API Error for {endpoint}: {data.get('message')}")
                return None
            return data
        except Exception as e:
            if attempt < 2:
                print(f"Request failed for {endpoint} (Attempt {attempt+1}/3). Retrying in 2s...")
                time.sleep(2)
            else:
                print(f"Request failed for {endpoint} after 3 attempts: {e}")
                return None

def fetch_technical_data(ticker):
    print(f"Executing Technical Ingestion for {ticker} (Throttled Mode)...")
    
    # To stay under 8 calls/min, we execute sequentially with a delay
    # instead of a simultaneous burst.
    endpoints = [
        ("/quote", {"symbol": ticker}),
        ("/rsi", {"symbol": ticker, "interval": "1day", "time_period": 14}),
        ("/sma", {"symbol": ticker, "interval": "1day", "time_period": 50}),
        ("/sma", {"symbol": ticker, "interval": "1day", "time_period": 200})
    ]
    
    results = []
    for endpoint, params in endpoints:
        res = fetch_indicator(endpoint, params)
        results.append(res)
        # 8 calls per min = 1 call every 7.5 seconds.
        # To be safe, we wait 8 seconds between calls.
        time.sleep(8)
        
    quote_data, rsi_data, sma50_data, sma200_data = results
    
    price = quote_data.get('close') if quote_data else None
    
    rsi_14 = None
    if rsi_data and 'values' in rsi_data and len(rsi_data['values']) > 0:
        rsi_14 = rsi_data['values'][0].get('rsi')
        
    sma_50 = None
    if sma50_data and 'values' in sma50_data and len(sma50_data['values']) > 0:
        sma_50 = sma50_data['values'][0].get('sma')
        
    sma_200 = None
    if sma200_data and 'values' in sma200_data and len(sma200_data['values']) > 0:
        sma_200 = sma200_data['values'][0].get('sma')
        
    return {
        "ticker": ticker.upper(),
        "price": price,
        "rsi_14": rsi_14,
        "sma_50": sma_50,
        "sma_200": sma_200
    }

def main():
    # Dynamic Ticker Fix: Check for CLI arguments, otherwise default to a safe list or prompt
    if len(sys.argv) > 1:
        tickers = [sys.argv[1]]
    else:
        print("No ticker provided. Usage: python twelve_data_ingestor.py <TICKER>")
        sys.exit(1)
        
    all_tech_data = {}
    
    print("Initiating Technical Engine Ingestion (Throttled Mode)...")
    
    for ticker in tickers:
        tech_info = fetch_technical_data(ticker)
        if tech_info:
            all_tech_data[ticker] = tech_info
            
            # Verification output
            print("\n--- Tactical Intel Buffer ---")
            print(f"[{ticker}] Current Price: {tech_info['price']}")
            print(f"[{ticker}] 14-period RSI: {tech_info['rsi_14']}")
            print(f"[{ticker}] 50-day SMA: {tech_info['sma_50']}")
            print(f"[{ticker}] 200-day SMA: {tech_info['sma_200']}")
            print("-----------------------------\n")
            
    # Output path in the same workspace directory
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "technical_intel_buffer.json")
    try:
        with open(output_path, "w") as f:
            json.dump({"technicals": all_tech_data}, f, indent=4)
        print(f"Successfully generated technical payload: {output_path}")
    except IOError as e:
        print(f"Failed to write to {output_path}: {e}")

if __name__ == "__main__":
    main()
