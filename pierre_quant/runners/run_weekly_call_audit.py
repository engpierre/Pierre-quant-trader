"""
pierre_quant/runners/run_weekly_call_audit.py
Audits all forward recommendations generated since Monday against live market spot prices.
"""
from __future__ import annotations
import logging
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
import pandas as pd
import yfinance as yf

# Reconfigure stdout for utf-8 if supported
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

WORKSPACE_ROOT = Path(r"C:\Users\Pierre\.openclaw\workspace")
DB_PATH = WORKSPACE_ROOT / "pierre-quant" / "pierre_quant.db"
REPORTS_DIR = WORKSPACE_ROOT / "vault" / "Reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("WeeklyCallAudit")

# Monday of the current trading week
MONDAY_ISO = "2026-08-24T00:00:00"


def audit_weekly_calls():
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    query = f"""
    SELECT rec_id, timestamp, agent_origin, ticker, spot_at_rec, 
           invalidation_stop, confluence_score, timesfm_target, chronos_target
    FROM sentry_recommendations
    WHERE timestamp >= '{MONDAY_ISO}'
    ORDER BY timestamp DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    md_path = REPORTS_DIR / "Weekly_Call_Performance.md"

    if df.empty:
        logger.warning("No recommendations recorded in sentry_recommendations since Monday (2026-08-24).")
        empty_content = f"""---
title: "Weekly Recommendation Performance Audit (Since Monday)"
last_updated: "{now_str}"
total_calls: 0
win_rate_pct: 0.0
avg_return_pct: 0.0
---

# 🎯 Weekly Forward Recommendation Audit (Since Aug 24, 2026)

*No forward recommendations logged in `sentry_recommendations` since Monday (2026-08-24). Run `run_confluence_scan.py` to populate active forward setups.*
"""
        md_path.write_text(empty_content, encoding="utf-8")
        return

    tickers = df["ticker"].unique().tolist()
    try:
        data = yf.download(tickers, period="5d", interval="1d", group_by="ticker", auto_adjust=True, progress=False)
    except Exception as e:
        logger.error(f"Download error: {e}")
        data = {}

    live_quotes = {}
    for t in tickers:
        try:
            t_df = data[t] if (len(tickers) > 1 and t in data) else data
            if t_df is not None and not t_df.empty:
                close = t_df["Close"].squeeze().dropna()
                if not close.empty:
                    live_quotes[t] = float(close.iloc[-1])
                else:
                    t_obj = yf.Ticker(t)
                    live_quotes[t] = float(t_obj.fast_info.get("lastPrice", 0.0))
            else:
                t_obj = yf.Ticker(t)
                live_quotes[t] = float(t_obj.fast_info.get("lastPrice", 0.0))
        except Exception:
            live_quotes[t] = None

    results = []
    for _, row in df.iterrows():
        t = row["ticker"]
        rec_price = float(row["spot_at_rec"])
        stop_floor = float(row["invalidation_stop"])
        current_spot = live_quotes.get(t, rec_price)
        
        if current_spot and rec_price > 0:
            call_return_pct = ((current_spot - rec_price) / rec_price) * 100.0
            stopped_out = current_spot <= stop_floor
            target_hit = current_spot >= float(row["timesfm_target"])
            
            if stopped_out:
                status = "❌ STOPPED OUT"
            elif target_hit:
                status = "🎯 TARGET HIT"
            elif call_return_pct > 0:
                status = "🟢 IN PROFIT"
            else:
                status = "🔴 DRAWDOWN"
        else:
            call_return_pct = 0.0
            current_spot = rec_price
            status = "UNKNOWN"

        results.append({
            "Rec Date": row["timestamp"][:10],
            "Agent": row["agent_origin"],
            "Ticker": t,
            "Call Price": rec_price,
            "Current Spot": current_spot,
            "Gain/Loss %": round(call_return_pct, 2),
            "Stop Floor": stop_floor,
            "Score": row["confluence_score"],
            "Status": status
        })

    audit_df = pd.DataFrame(results)
    
    total_calls = len(audit_df)
    positive_calls = len(audit_df[audit_df["Gain/Loss %"] > 0])
    win_rate = (positive_calls / total_calls * 100.0) if total_calls > 0 else 0.0
    avg_return = audit_df["Gain/Loss %"].mean() if total_calls > 0 else 0.0

    content = f"""---
title: "Weekly Recommendation Performance Audit (Since Monday)"
last_updated: "{now_str}"
total_calls: {total_calls}
win_rate_pct: {win_rate:.2f}
avg_return_pct: {avg_return:.2f}
---

# 🎯 Weekly Forward Recommendation Audit (Since Aug 24, 2026)

| Rec Date | Agent | Ticker | Call Spot | Current Spot | Call Δ % | Stop Floor | Score | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for _, r in audit_df.iterrows():
        content += f"| {r['Rec Date']} | `{r['Agent']}` | **${r['Ticker']}** | ${r['Call Price']:.2f} | ${r['Current Spot']:.2f} | **{r['Gain/Loss %']:+.2f}%** | ${r['Stop Floor']:.2f} | {r['Score']}/100 | `{r['Status']}` |\n"

    content += f"""
---
### 📊 Summary Statistics
* **Total Forward Signals:** `{total_calls}`
* **Active Win Rate:** **`{win_rate:.1f}%`** ({positive_calls}/{total_calls} in profit)
* **Average Return Per Call:** **`{avg_return:+.2f}%`**
"""
    md_path.write_text(content, encoding="utf-8")
    logger.info("Successfully exported Weekly_Call_Performance.md to Obsidian.")

    print("\n" + "=" * 100)
    print(f"WEEKLY CALL PERFORMANCE AUDIT | MONDAY (2026-08-24) TO PRESENT")
    print("=" * 100)
    print(audit_df.to_string(index=False))
    print("=" * 100)
    print(f"Win Rate: {win_rate:.1f}% | Mean Return: {avg_return:+.2f}%\n")


if __name__ == "__main__":
    audit_weekly_calls()
