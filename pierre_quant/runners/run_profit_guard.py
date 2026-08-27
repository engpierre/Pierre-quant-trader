"""
pierre_quant/runners/run_profit_guard.py
Autonomous Trailing Profit-Guard and Dynamic Stop-Loss Ratchet Daemon.
"""
from __future__ import annotations
import logging
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
import numpy as np
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
logger = logging.getLogger("ProfitGuard")


def init_audit_table():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sentry_audit_trail (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        ticker TEXT NOT NULL,
        prior_stop REAL NOT NULL,
        new_stop REAL NOT NULL,
        spot_price REAL NOT NULL,
        expansion_sigma REAL NOT NULL,
        trigger_reason TEXT NOT NULL
    );
    """)
    
    # Ensure portfolio_positions has entry_price, current_price, invalidation_stop
    cur.execute("PRAGMA table_info(portfolio_positions)")
    existing_cols = [c[1] for c in cur.fetchall()]
    if "entry_price" not in existing_cols:
        cur.execute("ALTER TABLE portfolio_positions ADD COLUMN entry_price REAL DEFAULT 0.0")
    if "current_price" not in existing_cols:
        cur.execute("ALTER TABLE portfolio_positions ADD COLUMN current_price REAL DEFAULT 0.0")
    if "invalidation_stop" not in existing_cols:
        cur.execute("ALTER TABLE portfolio_positions ADD COLUMN invalidation_stop REAL DEFAULT 0.0")
        
    conn.commit()
    conn.close()


def compute_atr(df: pd.DataFrame, period: int = 14) -> float:
    high = df["High"].squeeze()
    low = df["Low"].squeeze()
    close = df["Close"].squeeze()
    
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(period).mean().iloc[-1]
    return float(atr) if not np.isnan(atr) else float(close.iloc[-1] * 0.02)


def run_profit_guard():
    init_audit_table()
    conn = sqlite3.connect(DB_PATH)
    
    # Ingest active holdings
    positions_df = pd.read_sql_query(
        "SELECT ticker, shares, entry_price, current_price, invalidation_stop FROM portfolio_positions WHERE status = 'ACTIVE' OR status IS NULL", 
        conn
    )
    
    if positions_df.empty:
        logger.info("No active holdings found in portfolio_positions.")
        conn.close()
        return

    tickers = positions_df["ticker"].tolist()
    logger.info(f"Auditing trailing stops for {len(tickers)} active holdings: {tickers}")
    
    try:
        market_data = yf.download(tickers, period="3mo", interval="1d", group_by="ticker", auto_adjust=True, progress=False)
    except Exception as e:
        logger.error(f"Download error: {e}")
        market_data = {}
    
    now_str = datetime.utcnow().isoformat()
    updated_records = []
    ratchet_events = []
    
    cur = conn.cursor()

    for _, row in positions_df.iterrows():
        t = row["ticker"]
        entry = float(row.get("entry_price") or 0.0)
        prior_stop = float(row.get("invalidation_stop") or 0.0)
        
        try:
            df = market_data[t] if (len(tickers) > 1 and t in market_data) else market_data
            if df is not None and not df.empty:
                df = df.dropna()
            
            if df is None or df.empty:
                t_obj = yf.Ticker(t)
                spot = float(t_obj.fast_info.get("lastPrice", 0.0))
                atr_14 = round(spot * 0.025, 2)
                close_vals = np.array([spot])
            else:
                spot = float(df["Close"].squeeze().iloc[-1])
                atr_14 = compute_atr(df, 14)
                close_vals = df["Close"].squeeze().values

            if entry <= 0.0:
                entry = round(float(close_vals[0]) if len(close_vals) > 0 else spot, 2)
            
            # Compute 30-day volatility sigma
            window = min(30, len(close_vals) - 1)
            returns = np.diff(np.log(close_vals[-window:])) if window >= 2 else np.diff(np.log(close_vals))
            sigma_dollar = float(np.std(returns) * spot * np.sqrt(16)) if len(returns) > 1 else (spot * 0.05)
            sigma_expansion = (spot - entry) / sigma_dollar if sigma_dollar > 0 else 0.0

            new_stop = prior_stop
            reason = "Hold Prior Floor"

            # Ratchet Logic
            if sigma_expansion >= 2.5:
                calculated_floor = spot - (0.8 * atr_14)
                if calculated_floor > prior_stop:
                    new_stop = calculated_floor
                    reason = "Phase 3: Hyper-Extension Guard (+2.5σ)"
            elif sigma_expansion >= 1.5:
                calculated_floor = spot - (1.2 * atr_14)
                if calculated_floor > prior_stop:
                    new_stop = calculated_floor
                    reason = "Phase 2: Profit Lock (+1.5σ)"
            elif sigma_expansion >= 1.0:
                calculated_floor = entry + (0.2 * atr_14)
                if calculated_floor > prior_stop:
                    new_stop = calculated_floor
                    reason = "Phase 1: Breakeven Ratchet (+1.0σ)"
            else:
                # Standard volatility baseline
                baseline = spot - (1.8 * atr_14)
                if baseline > prior_stop and prior_stop == 0.0:
                    new_stop = baseline
                    reason = "Phase 0: Initial ATR Baseline"

            new_stop = round(max(prior_stop, new_stop), 2)

            if new_stop > prior_stop:
                cur.execute(
                    "UPDATE portfolio_positions SET invalidation_stop = ?, current_price = ?, entry_price = ? WHERE ticker = ?",
                    (new_stop, round(spot, 2), round(entry, 2), t)
                )
                cur.execute(
                    """INSERT INTO sentry_audit_trail 
                       (timestamp, ticker, prior_stop, new_stop, spot_price, expansion_sigma, trigger_reason)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (now_str, t, prior_stop, new_stop, round(spot, 2), round(sigma_expansion, 2), reason)
                )
                ratchet_events.append({
                    "ticker": t, "prior": prior_stop, "new": new_stop, "spot": spot, "reason": reason
                })
            else:
                cur.execute("UPDATE portfolio_positions SET current_price = ?, entry_price = ? WHERE ticker = ?", (round(spot, 2), round(entry, 2), t))

            gain_pct = ((spot - entry) / entry) * 100.0 if entry > 0 else 0.0
            updated_records.append({
                "ticker": t, "entry": entry, "spot": spot, "stop": new_stop, 
                "gain_pct": gain_pct, "sigma": sigma_expansion, "reason": reason
            })

        except Exception as e:
            logger.error(f"Error auditing {t}: {e}")

    conn.commit()
    conn.close()

    # Generate Obsidian Report
    md_path = REPORTS_DIR / "Profit_Guard_Matrix.md"
    report_content = f"""---
title: "Dynamic Profit-Guard & Stop Ratchet Report"
last_updated: "{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
total_holdings_audited: {len(updated_records)}
ratchet_events_triggered: {len(ratchet_events)}
---

# 🛡️ Dynamic Profit-Guard & Trailing Stop Ledger

| Ticker | Entry Price | Current Spot | Total Gain % | Expansion σ | Dynamic Stop Floor | Stop Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for r in sorted(updated_records, key=lambda x: x["gain_pct"], reverse=True):
        report_content += f"| **${r['ticker']}** | ${r['entry']:.2f} | ${r['spot']:.2f} | {r['gain_pct']:+.2f}% | {r['sigma']:+.2f}σ | **${r['stop']:.2f}** | `{r['reason']}` |\n"

    report_content += "\n## ⚡ Recent Ratchet Modifications\n\n"
    if not ratchet_events:
        report_content += "*No trailing stops required upward ratcheting in this pass. All floors intact.*\n"
    else:
        for ev in ratchet_events:
            report_content += f"* **${ev['ticker']}:** Floor elevated from `${ev['prior']:.2f}` ➔ **`${ev['new']:.2f}`** (Spot: `${ev['spot']:.2f}`) | Reason: *{ev['reason']}*\n"

    md_path.write_text(report_content, encoding="utf-8")
    logger.info("Profit-Guard report successfully exported to Obsidian Vault.")

    # Terminal output
    print("\n" + "=" * 95)
    print(f"{'TICKER':<10} | {'ENTRY':<9} | {'SPOT':<9} | {'GAIN %':<9} | {'SIGMA':<9} | {'DYNAMIC STOP':<14} | {'STATUS'}")
    print("-" * 95)
    for r in sorted(updated_records, key=lambda x: x["gain_pct"], reverse=True):
        print(f"{r['ticker']:<10} | ${r['entry']:<8.2f} | ${r['spot']:<8.2f} | {r['gain_pct']:>+7.2f}% | {r['sigma']:>+7.2f}σ | ${r['stop']:<13.2f} | {r['reason']}")
    print("=" * 95 + "\n")


if __name__ == "__main__":
    run_profit_guard()
