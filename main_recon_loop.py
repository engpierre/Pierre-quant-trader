import time
import datetime
import os
import sys

# Append path to allow absolute imports
sys.path.append(r"c:\Users\Pierre\.openclaw\workspace\pierre-quant")

from tv_pull_agent import TVPullAgent
from web_oracle_ingestor import fetch_web_price

# Sentry Memory
state_memory = {}

def get_active_tickers():
    """Determine tickers based on day of week. Weekends: BTCUSD, Weekdays: NVDA, GLW."""
    # 5 = Saturday, 6 = Sunday
    if datetime.datetime.today().weekday() >= 5:
        return ["BTCUSD"]
    else:
        return ["NVDA", "GLW"]

def check_sentry_filter(ticker, current_price, current_rsi):
    global state_memory
    
    if ticker not in state_memory:
        state_memory[ticker] = {"price": current_price, "rsi": current_rsi}
        return False, "Initial state recorded."
        
    prev_price = state_memory[ticker]["price"]
    prev_rsi = state_memory[ticker]["rsi"]
    
    # Calculate deltas safely
    price_delta_pct = 0.0
    if prev_price and current_price:
        price_delta_pct = abs(current_price - prev_price) / prev_price
        
    rsi_delta = 0.0
    if prev_rsi and current_rsi:
        rsi_delta = abs(current_rsi - prev_rsi)
        
    trigger = False
    reasons = []
    
    if price_delta_pct > 0.0025:
        trigger = True
        reasons.append(f"Price Delta {price_delta_pct*100:.2f}% > 0.25%")
        
    if rsi_delta > 5.0:
        trigger = True
        reasons.append(f"RSI Delta {rsi_delta:.2f} > 5.0")
        
    # Update memory
    state_memory[ticker] = {"price": current_price, "rsi": current_rsi}
    
    if trigger:
        return True, " | ".join(reasons)
    return False, "Thresholds nominal."

def run_recon_loop(test_mode=False):
    agent = TVPullAgent()
    print("**SYSTEM ONLINE**: Sentry-Pull Architecture Active")
    print("**DIRECTIVE**: Primary Data Failure triggers Web Oracle | Status in Condensed Markdown")
    
    iteration = 0
    while True:
        iteration += 1
        tickers = get_active_tickers()
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        print(f"\n**[HEARTBEAT {iteration} @ {timestamp}]** | TARGETS: {','.join(tickers)}")
        
        for ticker in tickers:
            try:
                # 1. Pull Data
                payload = agent.fetch_technicals(ticker)
                
                # 2. Check for Failure
                if payload.get("status") == "ERROR":
                    print(f"**[ERROR]** | Primary Data Failure: TradingView API offline for {ticker}. Falling back to Web Oracle.")
                    web_data = fetch_web_price(ticker)
                    price = web_data.get("price", 0.0)
                    print(f"**[WEB ORACLE]** | {ticker} | Price: ${price:.2f}")
                    continue
                
                price = float(payload.get("price", 0.0))
                rsi = float(payload.get("rsi", 0.0))
                rec = payload.get("recommendation", "UNKNOWN")
                
                # 3. Apply Sentry Filter
                triggered, reason = check_sentry_filter(ticker, price, rsi)
                
                # 4. Condensed Markdown Output
                status_str = f"**[{ticker}]** | P: ${price:.2f} | RSI: {rsi:.1f} | REC: {rec} | SENTRY: {reason}"
                print(status_str)
                
                if triggered:
                    print(f"**[CRITIC_TRIGGERED: VOLATILITY_THRESHOLD_EXCEEDED]** | Actioning Swarm on {ticker}...")
                    # Placeholder for BlackwellCritic().audit_swarm() to avoid headless Torch crash
                    
            except Exception as e:
                print(f"**[CRITICAL EXCEPTION]** | Loop failure on {ticker}: {str(e)}")
                
        if test_mode:
            break
            
        print("**[SLEEP]** | Awaiting 60s cycle...")
        time.sleep(60)

if __name__ == "__main__":
    # If run with 'test' arg, run once and exit
    test_mode = len(sys.argv) > 1 and sys.argv[1] == "test"
    run_recon_loop(test_mode)
