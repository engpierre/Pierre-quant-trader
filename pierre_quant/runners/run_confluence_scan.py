"""
pierre_quant/runners/run_confluence_scan.py
Executes Multi-Factor Confluence Scan, Logs Recommendations to SQLite, and Resolves Historical Accuracy.
"""
from __future__ import annotations
import json
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

# Setup Paths
WORKSPACE_ROOT = Path(r"C:\Users\Pierre\.openclaw\workspace")
sys.path.insert(0, str(WORKSPACE_ROOT / "pierre-quant"))

from pierre_quant.tools.confluence_engine import evaluate_confluence, ConfluenceMetrics

DB_PATH = WORKSPACE_ROOT / "pierre-quant" / "pierre_quant.db"
REPORTS_DIR = WORKSPACE_ROOT / "vault" / "Reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("ConfluenceScanner")

WATCHLIST = ["NVDA", "SMR", "ORCL", "BABA", "BIDU", "BTC-USD", "OKLO", "IONQ"]


def init_sentry_recommendations_table():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sentry_recommendations (
        rec_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        agent_origin TEXT NOT NULL,
        ticker TEXT NOT NULL,
        spot_at_rec REAL NOT NULL,
        invalidation_stop REAL NOT NULL,
        confluence_score INTEGER NOT NULL,
        timesfm_target REAL NOT NULL,
        chronos_target REAL NOT NULL,
        horizon_days INTEGER DEFAULT 5,
        resolved_price REAL DEFAULT NULL,
        direction_correct INTEGER DEFAULT NULL,
        pnl_pct REAL DEFAULT NULL,
        resolution_date TEXT DEFAULT NULL
    );
    """)
    conn.commit()
    conn.close()


def resolve_past_recommendations():
    """Resolves historical recommendations that reached horizon or hit stop floors."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT rec_id, ticker, spot_at_rec, invalidation_stop, timesfm_target, timestamp FROM sentry_recommendations WHERE direction_correct IS NULL")
    pending = cur.fetchall()

    if not pending:
        conn.close()
        return

    tickers = list(set([row[1] for row in pending]))
    quotes = {}
    try:
        data = yf.download(tickers, period="1d", interval="1m", progress=False)
        for t in tickers:
            df = data[t] if len(tickers) > 1 else data
            quotes[t] = float(df["Close"].dropna().iloc[-1])
    except Exception as e:
        logger.warning(f"Failed to fetch live quotes for resolution: {e}")
        conn.close()
        return

    now_str = datetime.utcnow().isoformat()
    for rec_id, ticker, spot_orig, stop_floor, target, ts_str in pending:
        cur_price = quotes.get(ticker, spot_orig)
        # Check if stop hit or target reached
        if cur_price <= stop_floor:
            pnl = ((cur_price - spot_orig) / spot_orig) * 100.0
            cur.execute("UPDATE sentry_recommendations SET resolved_price = ?, direction_correct = 0, pnl_pct = ?, resolution_date = ? WHERE rec_id = ?",
                        (cur_price, round(pnl, 2), now_str, rec_id))
        elif (target > spot_orig and cur_price >= target) or (datetime.utcnow() - datetime.fromisoformat(ts_str)).days >= 5:
            pnl = ((cur_price - spot_orig) / spot_orig) * 100.0
            win = 1 if pnl > 0 else 0
            cur.execute("UPDATE sentry_recommendations SET resolved_price = ?, direction_correct = ?, pnl_pct = ?, resolution_date = ? WHERE rec_id = ?",
                        (cur_price, win, round(pnl, 2), now_str, rec_id))

    conn.commit()
    conn.close()


def log_today_recommendations(metrics_list: list[ConfluenceMetrics]):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now_str = datetime.utcnow().isoformat()

    for m in metrics_list:
        if m.composite_score >= 70:  # Log qualifying setups
            cur.execute("""
            INSERT INTO sentry_recommendations 
            (timestamp, agent_origin, ticker, spot_at_rec, invalidation_stop, confluence_score, timesfm_target, chronos_target)
            VALUES (?, 'CONFLUENCE_SCANNER', ?, ?, ?, ?, ?, ?)
            """, (now_str, m.ticker, m.spot_price, m.invalidation_stop, m.composite_score, m.timesfm_target, m.chronos_target))
    conn.commit()
    conn.close()


def export_reports_to_vault(metrics_list: list[ConfluenceMetrics]):
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # 1. Daily Alpha Matrix
    matrix_md = REPORTS_DIR / "Daily_Alpha_Matrix.md"
    matrix_content = f"""---
title: "Daily Multi-Factor Confluence Matrix"
last_updated: "{now_str}"
---

# 🎯 Daily Multi-Factor Alpha Matrix

| Ticker | Spot | Stop Floor | ADX (14) | Volume POC | TFM Δ% | CHR Δ% | Spread | Score | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for m in sorted(metrics_list, key=lambda x: x.composite_score, reverse=True):
        status = "⚡ HIGH ALPHA" if m.is_high_alpha else ("CONFLUENT" if m.composite_score >= 70 else "STANDBY")
        poc_tag = f"${m.poc_price:.2f} (Above)" if m.is_above_poc else f"${m.poc_price:.2f} (Below)"
        matrix_content += f"| **${m.ticker}** | ${m.spot_price:.2f} | ${m.invalidation_stop:.2f} | {m.adx_14:.1f} | {poc_tag} | {m.timesfm_delta_pct:+.2f}% | {m.chronos_delta_pct:+.2f}% | {m.model_spread:.2f}% | **{m.composite_score}/100** | `{status}` |\n"

    matrix_content += "\n## 📝 Signal Confluence Logic\n\n"
    for m in sorted(metrics_list, key=lambda x: x.composite_score, reverse=True):
        matrix_content += f"* **${m.ticker} ({m.composite_score}/100):** {m.breakdown_notes}\n"

    matrix_md.write_text(matrix_content, encoding="utf-8")

    # 2. Rolling Track Record
    conn = sqlite3.connect(DB_PATH)
    resolved_df = pd.read_sql_query("SELECT * FROM sentry_recommendations WHERE direction_correct IS NOT NULL", conn)
    conn.close()

    track_md = REPORTS_DIR / "Rolling_Hit_Rate.md"
    total_recs = len(resolved_df)
    wins = len(resolved_df[resolved_df["direction_correct"] == 1])
    win_rate = (wins / total_recs * 100.0) if total_recs > 0 else 0.0
    avg_pnl = resolved_df["pnl_pct"].mean() if total_recs > 0 else 0.0

    track_content = f"""---
title: "Sentry Recommendation Rolling Track Record"
last_updated: "{now_str}"
total_resolved: {total_recs}
win_rate: {win_rate:.2f}
---

# 📈 Quantitative Recommendation Track Record

| Metric | System Value | Benchmark Standard |
| :--- | :--- | :--- |
| **Total Resolved Signals** | {total_recs} | > 30 for Statistical Significance |
| **Directional Hit Rate** | **{win_rate:.1f}%** | Target $\ge 65.0\%$ |
| **Mean Realized Delta %** | **{avg_pnl:+.2f}%** | Dynamic Risk Floor Protected |

## 📜 Historical Resolved Recommendations
"""
    if resolved_df.empty:
        track_content += "\n*Tracking initialized. Awaiting historical resolution window (1-5 days).*\n"
    else:
        track_content += "\n| Date | Ticker | Origin Spot | Resolved Spot | Stop Floor | Target | Direction | Realized PnL |\n"
        track_content += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
        for _, row in resolved_df.tail(15).iterrows():
            win_str = "✅ WIN" if row['direction_correct'] == 1 else "❌ STOPPED"
            track_content += f"| {row['timestamp'][:10]} | **${row['ticker']}** | ${row['spot_at_rec']:.2f} | ${row['resolved_price']:.2f} | ${row['invalidation_stop']:.2f} | ${row['timesfm_target']:.2f} | {win_str} | {row['pnl_pct']:+.2f}% |\n"

    track_md.write_text(track_content, encoding="utf-8")
    logger.info("Successfully exported Daily Alpha Matrix and Rolling Track Record to Obsidian.")


def main():
    init_sentry_recommendations_table()
    resolve_past_recommendations()

    logger.info(f"Downloading market data for {len(WATCHLIST)} watchlist targets...")
    try:
        data = yf.download(WATCHLIST, period="3mo", interval="1d", group_by="ticker", auto_adjust=True, progress=False)
    except Exception as e:
        logger.error(f"Download error: {e}")
        data = {}

    metrics_list = []
    for ticker in WATCHLIST:
        try:
            df = data[ticker] if (len(WATCHLIST) > 1 and ticker in data) else data
            if df is not None and not df.empty:
                df = df.dropna()
                metrics = evaluate_confluence(ticker, df)
                metrics_list.append(metrics)
        except Exception as e:
            logger.error(f"Error evaluating {ticker}: {e}")

    log_today_recommendations(metrics_list)
    export_reports_to_vault(metrics_list)

    print("\n" + "=" * 105)
    print(f"{'TICKER':<10} | {'SPOT':<9} | {'STOP':<9} | {'ADX':<6} | {'POC':<9} | {'TFM Delta':<10} | {'CHR Delta':<10} | {'SCORE':<7} | {'STATUS'}")
    print("-" * 105)
    for m in sorted(metrics_list, key=lambda x: x.composite_score, reverse=True):
        status = "[HIGH ALPHA]" if m.is_high_alpha else ("CONFLUENT" if m.composite_score >= 70 else "STANDBY")
        print(f"{m.ticker:<10} | ${m.spot_price:<8.2f} | ${m.invalidation_stop:<8.2f} | {m.adx_14:<6.1f} | ${m.poc_price:<8.2f} | {m.timesfm_delta_pct:>+8.2f}% | {m.chronos_delta_pct:>+8.2f}% | {m.composite_score:>3}/100 | {status}")
    print("=" * 105 + "\n")


if __name__ == "__main__":
    main()
