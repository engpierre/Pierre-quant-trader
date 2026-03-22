import json
import logging
import requests
import pandas as pd
from datetime import datetime, timedelta
from io import StringIO
import time

logging.basicConfig(level=logging.INFO, format='%(message)s')

def get_insider_transactions(ticker, days=60):
    """Scrape OpenInsider for the ticker's recent transactions."""
    url = f"http://openinsider.com/search?q={ticker}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return pd.DataFrame()
        
        tables = pd.read_html(StringIO(response.text))
        
        main_table = pd.DataFrame()
        for t in tables:
            if 'Trade Date' in t.columns and 'Value' in t.columns:
                main_table = t
                break
                
        if main_table.empty:
            return pd.DataFrame()
            
        main_table['Trade Date'] = pd.to_datetime(main_table['Trade Date'], errors='coerce')
        main_table = main_table.dropna(subset=['Trade Date'])
        
        cutoff = datetime.now() - timedelta(days=days)
        recent = main_table[main_table['Trade Date'] >= cutoff]
        
        return recent
    except Exception as e:
        return pd.DataFrame()

def analyze_insiders():
    input_file = 'enhanced_candidates.json'
    try:
        with open(input_file, 'r') as f:
            candidates = json.load(f)
    except:
        logging.error(f"Could not load {input_file}. Run sentiment agent first.")
        return

    logging.info(f"Loaded {len(candidates)} candidates. Performing Integrity Audit (OpenInsider 60-day)...")
    
    enhanced = []
    red_flags = []
    
    for idx, c in enumerate(candidates):
        ticker = c['symbol']
        logging.info(f"[{idx+1}/{len(candidates)}] Auditing insiders for {ticker}...")
        
        df = get_insider_transactions(ticker, days=60)
        
        net_buy = 0
        net_sell = 0
        ceo_cfo_buy = False
        massive_selling = False
        weighted_net_sell = 0
        unscheduled_sell_val = 0
        scheduled_sell_val = 0
        tax_sell_val = 0
        
        if not df.empty:
            # Aggregate transaction values cleanly
            df['Value_Num'] = df['Value'].astype(str).str.replace('$', '').str.replace(',', '').str.replace('+', '').str.replace('-', '')
            df['Value_Num'] = pd.to_numeric(df['Value_Num'], errors='coerce').fillna(0)
            
            # Context-Aware Transaction Parsing
            tax_mask = df['Trade Type'].astype(str).str.contains('Tax|F -', case=False, na=False)
            scheduled_mask = df['Trade Type'].astype(str).str.contains('OE|Option', case=False, na=False)
            sell_mask = df['Trade Type'].astype(str).str.contains('Sale|Sell', case=False, na=False)
            
            buys = df[df['Trade Type'].astype(str).str.contains('Buy|Purchase|P -', case=False, na=False)]
            net_buy = buys['Value_Num'].sum()
            
            # Extract sell tranches
            tax_sell_val = df[tax_mask & df['Trade Type'].astype(str).str.contains('Sale|Sell|F -', case=False, na=False)]['Value_Num'].sum()
            scheduled_sell_val = df[scheduled_mask & sell_mask]['Value_Num'].sum()
            unscheduled_sell_val = df[sell_mask & ~scheduled_mask & ~tax_mask]['Value_Num'].sum()
            
            # Total raw sell volume (for telemetry)
            net_sell = unscheduled_sell_val + scheduled_sell_val + tax_sell_val
            
            # Weighted Context Equation (Unscheduled=100%, Scheduled/Options=20%, Tax=0%)
            weighted_net_sell = (unscheduled_sell_val * 1.0) + (scheduled_sell_val * 0.2)
            
            ceo_cfo_buys = buys[buys['Title'].astype(str).str.contains('CEO|CFO', case=False, na=False)]
            if not ceo_cfo_buys.empty:
                ceo_cfo_buy = True
                
            # Core parameter: massive insider distributions (using contextual weighting)
            if weighted_net_sell > 5_000_000 or (weighted_net_sell > 1_000_000 and weighted_net_sell > (net_buy * 10)):
                massive_selling = True

        audit_score = 0
        if ceo_cfo_buy:
             audit_score += 15  # Per user constitution rule
             
        red_flag = massive_selling
        divergence = False
        
        # Constitution Rule: Divergence Check (Sentiment High but Insiders Selling)
        if 'sentiment' in c:
            if c['sentiment'].get('hype_score', 0) > 75 and weighted_net_sell > 500_000:
                divergence = True
                red_flag = True
            
        c['insider_audit'] = {
            '60d_net_buy_usd': float(net_buy),
            '60d_net_sell_usd': float(net_sell),
            '60d_unscheduled_sell_usd': float(unscheduled_sell_val),
            '60d_scheduled_sell_usd': float(scheduled_sell_val),
            '60d_tax_sell_usd': float(tax_sell_val),
            'weighted_net_sell_usd': float(weighted_net_sell),
            'ceo_cfo_buy': ceo_cfo_buy,
            'massive_selling_detected': massive_selling,
            'divergence_flag': divergence,
            'red_flag': red_flag,
            'audit_bonus': audit_score
        }
        
        enhanced.append(c)
        if red_flag:
            reason = "Massive Selling Detected" if massive_selling else "Structural Divergence Risk"
            red_flags.append(f"{ticker} ({reason})")
            
        time.sleep(1.2) # Polite scraping compliance
        
    with open('audited_candidates.json', 'w') as f:
        json.dump(enhanced, f, indent=4)
        
    logging.info("\n--- INSIDER AUDIT COMPLETE ---")
    logging.info("Saved telemetry to audited_candidates.json.")
    logging.info(f"Identified {len(red_flags)} Red Flags:")
    if not red_flags:
        logging.info("  Clean slate! No structural insider red flags triggered.")
    for flag in red_flags:
        logging.info(f"  [!] RED FLAG APPLIED: {flag}")

if __name__ == "__main__":
    analyze_insiders()
