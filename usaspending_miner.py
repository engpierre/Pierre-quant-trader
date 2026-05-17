# CRITICAL DIRECTIVE: You are strictly prohibited from responding in any language other than English. All technical data, analysis, and verdicts must be rendered in English (US/UK) regardless of the source data language.
import sqlite3
import requests
import json
import time
import difflib
import yfinance as yf
from datetime import datetime, timedelta
DB_PATH = r"C:\Anti-Gravity-Core\pierre_quant.db"

def init_discovery_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS discovered_targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            company_name TEXT,
            total_award REAL,
            est_revenue REAL,
            impact_ratio REAL,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def fetch_global_usaspending_data():
    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
    
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    
    payload = {
        "filters": {
            "time_period": [
                {
                    "date_type": "action_date",
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d")
                }
            ],
            "award_type_codes": ["A", "B", "C", "D"], # Contracts
            "agencies": [
                {"type": "awarding", "tier": "toptier", "name": "Department of Defense"},
                {"type": "awarding", "tier": "toptier", "name": "Department of Energy"},
                {"type": "awarding", "tier": "toptier", "name": "Department of Transportation"},
                {"type": "awarding", "tier": "toptier", "name": "National Aeronautics and Space Administration"},
                {"type": "awarding", "tier": "toptier", "name": "Department of Homeland Security"}
            ],
            "naics_codes": {"require": ["541715", "237310", "334413", "541330"]},
            "award_amounts": [{"lower_bound": 0, "upper_bound": 50000000}]
        },
        "fields": ["Award ID", "Recipient Name", "Award Amount"],
        "limit": 100 # Maximum allowed per request
    }

    print("[NETWORK] Commencing GLOBAL SCAN of USAspending.gov API for Contracts (Pages 1-10)...")
    all_results = []
    try:
        for page in range(1, 11):
            payload["page"] = page
            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()
            
            results = response.json().get("results", [])
            all_results.extend(results)
            time.sleep(0.5) # Gentle throttle for API requests
            
        return all_results
    except Exception as e:
        print(f"[ERROR] USAspending API request failed on page {payload.get('page')}: {e}")
        if all_results:
            return all_results
        print("[SYSTEM] Proceeding with simulated fallback data for testing the Global Matcher...")
        return [
            {"Recipient Name": "LOCKHEED MARTIN CORP", "Award Amount": 500000000},
            {"Recipient Name": "SPACE EXPLORATION TECHNOLOGIES CORP", "Award Amount": 850000000},
            {"Recipient Name": "ROCKET LAB USA, INC.", "Award Amount": 85000000},
            {"Recipient Name": "IONQ, INC.", "Award Amount": 3500000},
            {"Recipient Name": "ANDURIL INDUSTRIES INC.", "Award Amount": 150000000}
        ]

def resolve_ticker(company_name):
    """Hits Yahoo Finance search endpoint to find the ticker symbol for a legal name."""
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={company_name}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            quotes = response.json().get("quotes", [])
            for q in quotes:
                # Require it to be an equity on a major US exchange to filter out garbage matches
                if q.get("quoteType") == "EQUITY" and q.get("exchange") in ["NMS", "NYQ", "NGM", "NAS", "NCM", "PNK"]:
                    yahoo_name = str(q.get("longName") or q.get("shortName") or "").upper()
                    raw_name = str(company_name).upper()
                    
                    similarity = difflib.SequenceMatcher(None, raw_name, yahoo_name).ratio()
                    if similarity >= 0.60:
                        return q.get("symbol")
    except Exception:
        pass
    return None

def extract_revenue(ticker):
    """Uses yfinance to extract trailing 12-month total revenue."""
    try:
        stock = yf.Ticker(ticker)
        # Fast info fetch
        info = stock.info
        rev = info.get("totalRevenue")
        if rev:
            return float(rev)
    except:
        pass
    return None

def process_and_flag(awards):
    # 1. Aggregate awards by raw recipient name
    aggregated_awards = {}
    for award in awards:
        recipient = str(award.get("Recipient Name", "UNKNOWN")).strip().upper()
        amount = float(award.get("Award Amount", 0) or 0)
        
        if recipient not in aggregated_awards:
            aggregated_awards[recipient] = 0
        aggregated_awards[recipient] += amount

    print("\n--- OPERATION SPENDING-SENTRY: FULL DISCOVERY REPORT (PLAIN-ENGLISH) ---")
    
    # Sort by total award descending
    sorted_recipients = sorted(aggregated_awards.items(), key=lambda x: x[1], reverse=True)
    
    for recipient, total_award in sorted_recipients:
        # Throttle logic (1 second per USAspending constraint instructions)
        time.sleep(1.0)
        
        # Strip common trailing legal designators to help Yahoo Search
        clean_name = recipient.replace(", INC.", "").replace(" INC", "").replace(" LLC", "").replace(" CORP", "").replace(" CORPORATION", "")
        
        ticker = resolve_ticker(clean_name)
        
        if not ticker:
            print(f"[PRIVATE] Skipped: {recipient} (Total Award: ${total_award:,.2f})")
            continue
            
        revenue = extract_revenue(ticker)
        
        if not revenue or revenue <= 0:
            print(f"[NOMINAL] | {ticker} ({recipient}) | Total Award: ${total_award:,.2f} | (Rev. Data Unavailable)")
            continue
            
        # 10% Impact Trigger
        impact_ratio = total_award / revenue
        
        if impact_ratio >= 0.10:
            print(f"**[FLAG: 10% IMPACT BUY TARGET]** | {ticker} ({recipient}) | Total Award: ${total_award:,.2f} | Est Revenue: ${revenue:,.2f} | Impact: {impact_ratio*100:.1f}%")
            
            # Save flagged target to database
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO discovered_targets (ticker, company_name, total_award, est_revenue, impact_ratio, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (ticker, recipient, total_award, revenue, impact_ratio, datetime.now().isoformat()))
            conn.commit()
            conn.close()
        elif impact_ratio >= 0.05:
            print(f"**[WATCHLIST]** | {ticker} ({recipient}) | Total Award: ${total_award:,.2f} | Est Revenue: ${revenue:,.2f} | Impact: {impact_ratio*100:.1f}%")
        else:
            print(f"**[NOMINAL]** | {ticker} ({recipient}) | Total Award: ${total_award:,.2f} | Est Revenue: ${revenue:,.2f} | Impact: {impact_ratio*100:.1f}%")

if __name__ == "__main__":
    init_discovery_db()
    awards_data = fetch_global_usaspending_data()
    if awards_data:
        process_and_flag(awards_data)
    else:
        print("[WARNING] No contract data retrieved.")
