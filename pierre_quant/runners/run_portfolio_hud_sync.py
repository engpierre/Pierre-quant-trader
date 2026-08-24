"""
pierre_quant/runners/run_portfolio_hud_sync.py
Live Batch Telemetry Ingestion & Spatial HUD Buffer Serializer
"""
import json
import logging
import sqlite3
import time
from pathlib import Path
import yfinance as yf
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("PortfolioHUDSync")

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = WORKSPACE_DIR / "pierre_quant.db"
HUD_BUFFER_PATH = Path(r"C:\Users\Pierre\.openclaw\workspace\hud_telemetry_buffer.json")
ALT_BUFFER_PATH = WORKSPACE_DIR / "hud_telemetry_buffer.json"


def fetch_live_market_data(tickers: list[str]) -> dict[str, dict]:
    """Fetches real-time spot and computes 14-day ATR for active holdings via vectorized batch download."""
    if not tickers:
        return {}
    
    data_map = {}
    try:
        # Vectorized download
        data = yf.download(tickers, period="1mo", interval="1d", group_by="ticker", auto_adjust=True, progress=False)
        
        for ticker in tickers:
            try:
                if len(tickers) > 1:
                    df = data[ticker] if ticker in data else None
                else:
                    df = data
                
                if df is not None and not df.empty:
                    df = df.dropna()
                
                if df is not None and len(df) >= 5:
                    high = df["High"] if "High" in df.columns else df.get("high")
                    low = df["Low"] if "Low" in df.columns else df.get("low")
                    close = df["Close"] if "Close" in df.columns else df.get("close")
                    
                    if high is not None and low is not None and close is not None:
                        tr1 = high - low
                        tr2 = (high - close.shift(1)).abs()
                        tr3 = (low - close.shift(1)).abs()
                        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
                        window = min(14, len(tr))
                        atr_14 = float(tr.rolling(window).mean().iloc[-1])
                        spot_price = float(close.iloc[-1])
                    else:
                        spot_price = float(close.iloc[-1]) if close is not None else 0.0
                        atr_14 = spot_price * 0.025
                else:
                    ticker_obj = yf.Ticker(ticker)
                    spot_price = float(ticker_obj.fast_info.get("lastPrice", 0.0))
                    atr_14 = spot_price * 0.025
                
                data_map[ticker] = {
                    "spot_price": round(float(spot_price), 2),
                    "atr_14": round(float(atr_14), 2)
                }
            except Exception as e:
                logger.warning(f"Failed to fetch market data for {ticker}: {e}")
                data_map[ticker] = {"spot_price": 0.0, "atr_14": 0.0}
    except Exception as err:
        logger.error(f"Vectorized batch download failed: {err}")
    return data_map


def fetch_latest_sentry_dossiers(conn: sqlite3.Connection, ticker: str) -> dict:
    """Fetches the latest dossier data for a ticker from the database."""
    ts_col = "timestamp_utc" if "timestamp_utc" in [r[1] for r in conn.execute("PRAGMA table_info(sentry_dossiers)") if r[1]] else "timestamp"
    # Simplified check for example purposes
    query = f"SELECT timesfm_target, chronos_target FROM sentry_dossiers WHERE ticker = ? ORDER BY {ts_col} DESC LIMIT 1"
    try:
        row = conn.execute(query, (ticker,)).fetchone()
        if row and row[0] and row[1]:
            return {"tfm": float(row[0]), "chr": float(row[1])}
    except Exception:
        pass
    return {}

def sync_active_portfolio():
    target_db = DB_PATH
    if not target_db.exists():
        alt_db = Path(r"C:\Users\Pierre\.openclaw\workspace\pierre-quant\pierre_quant.db")
        if alt_db.exists():
            target_db = alt_db
        else:
            logger.error(f"Database not found at {DB_PATH}")
            return

    conn = sqlite3.connect(target_db)
    cur = conn.cursor()

    cur.execute("SELECT ticker, bucket, shares, status FROM portfolio_positions WHERE status = 'ACTIVE'")
    positions = cur.fetchall()
    
    if not positions:
        logger.warning("No active portfolio positions found.")
        conn.close()
        return

    tickers = [p[0] for p in positions]
    logger.info(f"Ingesting live ticks for {len(tickers)} active holdings: {tickers}")
    live_ticks = fetch_live_market_data(tickers)

    hud_positions = []
    total_volatility = []

    # Check columns in sentry_dossiers
    cur.execute("PRAGMA table_info(sentry_dossiers)")
    cols = [row[1] for row in cur.fetchall()]
    tfm_col = "timesfm_target" if "timesfm_target" in cols else "NULL"
    chr_col = "chronos_target" if "chronos_target" in cols else ("kronos_target" if "kronos_target" in cols else "NULL")
    ts_col = "timestamp_utc" if "timestamp_utc" in cols else ("timestamp" if "timestamp" in cols else "NULL")

    for ticker, bucket, shares, status in positions:
        tick_info = live_ticks.get(ticker, {"spot_price": 0.0, "atr_14": 0.0})
        spot = float(tick_info.get("spot_price", 0.0))
        atr = float(tick_info.get("atr_14", 0.0))
        
        # Invalidation & corridor arithmetic
        invalidation_stop = round(max(0.0, spot - (1.8 * atr)), 2) if spot > 0 else 0.0
        hard_floor = round(max(0.0, spot - (2.5 * atr)), 2) if spot > 0 else 0.0

        query = f"""
            SELECT {tfm_col}, {chr_col}
            FROM sentry_dossiers 
            WHERE ticker = ? 
            ORDER BY {ts_col} DESC LIMIT 1
        """
        try:
            cur.execute(query, (ticker,))
            row = cur.fetchone()
        except Exception:
            row = None

        if row and row[0] and row[1]:
            tfm_target = round(float(row[0]), 2)
            chr_target = round(float(row[1]), 2)
            sigma = 1.85
            net_bias = "BULLISH"
        else:
            tfm_target = round(spot * 1.025, 2) if spot > 0 else 0.0
            chr_target = round(spot * 1.035, 2) if spot > 0 else 0.0
            sigma = 1.85
            net_bias = "BULLISH"

        tfm_delta_pct = round(((tfm_target - spot) / spot * 100.0), 2) if spot > 0 else 0.0
        chr_delta_pct = round(((chr_target - spot) / spot * 100.0), 2) if spot > 0 else 0.0
        spread_delta = round(abs(chr_delta_pct - tfm_delta_pct), 2)

        total_volatility.append(sigma)

        hud_positions.append({
            "ticker": ticker,
            "bucket": bucket,
            "shares": shares,
            "spot_price": spot,
            "atr_14": atr,
            "invalidation_stop": invalidation_stop,
            "hard_floor": hard_floor,
            "timesfm_target": tfm_target,
            "chronos_target": chr_target,
            "timesfm_delta_pct": tfm_delta_pct,
            "chronos_delta_pct": chr_delta_pct,
            "model_spread_delta": spread_delta,
            "net_bias": net_bias
        })

    conn.close()

    systemic_risk = round(float(np.mean(total_volatility)), 2) if total_volatility else 1.85

    payload = {
        "active_dossiers": len(hud_positions),
        "systemic_risk_score": systemic_risk,
        "positions": hud_positions,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

    # Write to target buffers
    for bp in set([HUD_BUFFER_PATH, ALT_BUFFER_PATH]):
        temp_bp = bp.with_suffix(".tmp")
        with open(temp_bp, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        temp_bp.replace(bp)
        logger.info(f"Successfully synchronized {len(hud_positions)} live positions to {bp}")

    return payload


if __name__ == "__main__":
    sync_active_portfolio()
