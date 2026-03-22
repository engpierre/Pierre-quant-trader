import yfinance as yf
import pandas as pd
import json
import logging
from datetime import datetime
import sys
import warnings
import re
import requests
from io import StringIO

warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO, format='%(message)s')

def get_sp500_tickers_by_sector():
    logging.info("Fetching S&P 500 constituents from Wikipedia...")
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    tables = pd.read_html(StringIO(response.text))
    df = tables[0]
    return df

sector_etf_mapping = {
    'Information Technology': 'XLK',
    'Health Care': 'XLV',
    'Financials': 'XLF',
    'Consumer Discretionary': 'XLY',
    'Communication Services': 'XLC',
    'Industrials': 'XLI',
    'Consumer Staples': 'XLP',
    'Energy': 'XLE',
    'Utilities': 'XLU',
    'Real Estate': 'XLRE',
    'Materials': 'XLB'
}

def analyze_sectors():
    etfs = list(sector_etf_mapping.values())
    symbols = etfs + ['SPY']
    logging.info(f"Downloading data for ETFs: {symbols}")
    
    data = yf.download(symbols, period='1y', interval='1d')['Close']
    data = data.dropna()
    
    rs_df = pd.DataFrame()
    for etf in etfs:
        rs_df[etf] = data[etf] / data['SPY']
        
    m_rs = pd.DataFrame()
    for etf in etfs:
        rs_sma = rs_df[etf].rolling(window=20).mean()
        m_rs[etf] = ((rs_df[etf] / rs_sma) - 1) * 100
        
    latest_m_rs = m_rs.iloc[-1].sort_values(ascending=False)
    top_2_etfs = latest_m_rs.head(2).index.tolist()
    
    inv_map = {v: k for k, v in sector_etf_mapping.items()}
    top_2_gics = [inv_map[etf] for etf in top_2_etfs]
    
    return top_2_gics

def aggregate_cross_platform_movers():
    logging.info("Scouting Cross-Platform Market Movers (Finviz, Yahoo, MSN, MarketWatch)...")
    movers = set()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    # 1. Yahoo Finance Trending
    try:
         res = requests.get("https://finance.yahoo.com/trending-tickers", headers=headers, timeout=5)
         tickers = re.findall(r'data-symbol="([A-Z]{1,5})"', res.text)
         movers.update(tickers[:15])
    except Exception as e:
         pass
         
    # 2. Finviz 
    try:
         res = requests.get("https://finviz.com/", headers=headers, timeout=5)
         tickers = re.findall(r'quote\.ashx\?t=([A-Z]{1,5})', res.text)
         movers.update(tickers[:15])
    except Exception as e:
         pass
         
    # 3. MarketWatch 
    try:
         res = requests.get("https://www.marketwatch.com/tools/screener/market-movers", headers=headers, timeout=5)
         tickers = re.findall(r'/investing/stock/([a-z]{1,5})', res.text.lower())
         movers.update([t.upper() for t in tickers][:15])
    except Exception as e:
         pass
         
    # 4. MSN Money
    try:
         res = requests.get("https://www.msn.com/en-us/money/markets", headers=headers, timeout=5)
         tickers = re.findall(r'(?:NYSE|NASDAQ):\s*([A-Z]{1,5})', res.text)
         movers.update(tickers[:10])
    except Exception as e:
         pass
         
    movers = list(movers)
    if movers:
         logging.info(f"Cross-platform scan identified {len(movers)} unique trending tickers: {', '.join(movers[:10])}...")
    else:
         logging.info("Cross-platform trending scan returned 0 reliable targets. Relying solely on S&P sector momentum.")
         
    return movers

def screen_tickers(top_2_gics, sp500_df, external_tickers=None):
    if external_tickers is None: external_tickers = []
    
    candidates = sp500_df[sp500_df['GICS Sector'].isin(top_2_gics)]
    tickers = candidates['Symbol'].tolist()
    tickers = [t.replace('.', '-') for t in tickers]
    
    tickers = list(set(tickers + external_tickers))
    
    logging.info(f"Screening {len(tickers)} combined tickers (Leading Sectors + Market Movers)...")
    
    passed_tickers = []
    
    try:
        data = yf.download(tickers, period='1y', group_by='ticker', threads=True)
    except Exception as e:
        logging.error(f"Failed to batch download: {e}")
        return passed_tickers

    for t in tickers:
        try:
            if len(tickers) == 1:
                df = data
            else:
                df = data[t]
                
            df = df.dropna()
            
            if len(df) < 200:
                continue
                
            latest_close = float(df['Close'].iloc[-1])
            sma_200 = float(df['Close'].rolling(window=200).mean().iloc[-1])
            avg_vol = float(df['Volume'].rolling(window=20).mean().iloc[-1])
            
            if latest_close > sma_200 and avg_vol > 1000000:
                info = yf.Ticker(t).info
                market_cap = info.get('marketCap', 0)
                
                if market_cap >= 2_000_000_000:
                    orig_ticker = t.replace('-', '.')
                    sector_match = sp500_df[sp500_df['Symbol'] == orig_ticker]
                    if not sector_match.empty:
                        sector_val = sector_match['GICS Sector'].values[0]
                    else:
                        sector_val = info.get('sector', 'Unknown')
                        
                    passed_tickers.append({
                        'symbol': t,
                        'price': round(latest_close, 2),
                        'sma_200': round(sma_200, 2),
                        'avg_vol_20d': round(avg_vol, 0),
                        'market_cap': market_cap,
                        'sector': sector_val
                    })
        except Exception as e:
            pass

    return passed_tickers

def run_single_ticker(ticker):
    logging.info(f"Initiating single-ticker Scout scan for: {ticker}")
    df = yf.download(ticker, period='1y', progress=False)
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
        
    if df.empty or len(df) < 200:
        logging.error(f"  [!] Insufficient data mapping for {ticker}. Aborting pipeline.")
        return
        
    latest_close = float(df['Close'].iloc[-1])
    sma_200 = float(df['Close'].rolling(window=200).mean().iloc[-1])
    avg_vol = float(df['Volume'].rolling(window=20).mean().iloc[-1])
    
    info = yf.Ticker(ticker).info
    market_cap = info.get('marketCap', 0)
    sector_val = info.get('sector', 'Unknown')
    
    candidates = [{
        'symbol': ticker,
        'price': round(latest_close, 2),
        'sma_200': round(sma_200, 2),
        'avg_vol_20d': round(avg_vol, 0),
        'market_cap': market_cap,
        'sector': sector_val
    }]
    
    with open('candidates.json', 'w') as f:
        json.dump(candidates, f, indent=4)
        
    logging.info(f"\nPhase 1 Scout complete: Single candidate {ticker} seeded into pipeline. Moving to Phase 1.1...")

if __name__ == "__main__":
    ticker = None
    sector_filter = None
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv):
            if arg == '--ticker' and i+1 < len(sys.argv):
                ticker = sys.argv[i+1].upper()
            if arg == '--sector' and i+1 < len(sys.argv):
                sector_filter = sys.argv[i+1]
                
        if not ticker and not sector_filter and not sys.argv[1].startswith('--'):
            ticker = sys.argv[1].upper()

    if ticker:
        run_single_ticker(ticker)
    else:
        if sector_filter:
            logging.info(f"Targeting overriding sector filter scan: {sector_filter}")
            top_2_gics = [sector_filter]
        else:
            top_2_gics = analyze_sectors()
            
        sp500_df = get_sp500_tickers_by_sector()
        
        # Enhance pipeline by injecting real-time market movers
        external_movers = aggregate_cross_platform_movers()
        
        candidates = screen_tickers(top_2_gics, sp500_df, external_movers)
        
        candidates = sorted(candidates, key=lambda x: x['avg_vol_20d'], reverse=True)
        candidates = candidates[:50]
        
        with open('candidates.json', 'w') as f:
            json.dump(candidates, f, indent=4)
            
        logging.info(f"\nPhase 1 Scout complete: {len(candidates)} high momentum candidate tickers aggregated and saved to candidates.json")
