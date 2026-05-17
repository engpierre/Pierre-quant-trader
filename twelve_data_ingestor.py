# CRITICAL DIRECTIVE: You are strictly prohibited from responding in any language other than English. All technical data, analysis, and verdicts must be rendered in English (US/UK) regardless of the source data language.
import asyncio
import json
import os
import sys

try:
    import aiohttp
except ImportError:
    print("Error: The 'aiohttp' library is missing.")
    print("Please run the following command to install it: pip install aiohttp")
    sys.exit(1)

API_KEY = "f76a1dce8347443a8aa2ca4dd09a90cd"
BASE_URL = "https://api.twelvedata.com"

async def fetch_indicator(session, endpoint, params):
    params['apikey'] = API_KEY
    url = f"{BASE_URL}{endpoint}"
    try:
        async with session.get(url, params=params, timeout=15) as response:
            response.raise_for_status()
            data = await response.json()
            if 'code' in data and data.get('status') == 'error':
                print(f"API Error for {endpoint}: {data.get('message')}")
                return None
            return data
    except Exception as e:
        print(f"Request failed for {endpoint}: {e}")
        return None

async def fetch_technical_data(ticker):
    print(f"Executing Asynchronous Burst to Twelve Data for {ticker}...")
    
    async with aiohttp.ClientSession() as session:
        # Fire 4 requests simultaneously
        tasks = [
            fetch_indicator(session, "/quote", {"symbol": ticker}),
            fetch_indicator(session, "/rsi", {"symbol": ticker, "interval": "1day", "time_period": 14}),
            fetch_indicator(session, "/sma", {"symbol": ticker, "interval": "1day", "time_period": 50}),
            fetch_indicator(session, "/sma", {"symbol": ticker, "interval": "1day", "time_period": 200})
        ]
        
        results = await asyncio.gather(*tasks)
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
    tickers = ["PLTR"]
    all_tech_data = {}
    
    print("Initiating Technical Engine Ingestion (Asynchronous Burst Mode)...")
    
    for ticker in tickers:
        # Since Python 3.7+ we can just use asyncio.run
        tech_info = asyncio.run(fetch_technical_data(ticker))
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
    # Windows platform specific fix for asyncio
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    main()
