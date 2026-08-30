"""
pierre_quant/execution/paper/paper_ledger.py
Sandboxed paper portfolio execution, state persistence, and dynamic ATR stop-ratcheting engine.
"""
from __future__ import annotations
import logging
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

# Database resolution
DB_PATH = Path(r"C:\Users\Pierre\.openclaw\workspace\pierre-quant\pierre_quant.db")
if not DB_PATH.parent.exists():
    DB_PATH = Path(__file__).resolve().parent.parent.parent.parent / "pierre_quant.db"

logging.basicConfig(level=logging.WARNING, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("PaperLedger")

from pierre_quant.ingestion.live_feed import LiveFeedIngestionAgent
from pierre_quant.risk.portfolio_guard import PortfolioGuardAgent


def init_paper_tables(conn: sqlite3.Connection) -> None:
    """Creates the paper execution ledger schema if not existing."""
    with conn:
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS paper_portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                ticker TEXT NOT NULL,
                shares INTEGER NOT NULL,
                entry_price REAL NOT NULL,
                current_stop REAL NOT NULL,
                target_price REAL NOT NULL,
                status TEXT DEFAULT 'OPEN',
                unrealized_pnl REAL DEFAULT 0.0,
                realized_pnl REAL DEFAULT 0.0,
                highest_price REAL NOT NULL
            );
        """)


class PaperLedger:
    @classmethod
    def add_position(
        cls,
        ticker: str,
        shares: int,
        spot_price: float,
        atr_stop: float,
        target_price: float = 0.0
    ) -> int:
        """Logs a new sandboxed paper execution."""
        clean_ticker = ticker.strip().upper().lstrip("$")
        conn = sqlite3.connect(str(DB_PATH), timeout=1.0)
        init_paper_tables(conn)
        now = time.time()
        with conn:
            cursor = conn.execute("""
                INSERT INTO paper_portfolio (
                    timestamp, ticker, shares, entry_price, current_stop,
                    target_price, status, unrealized_pnl, realized_pnl, highest_price
                ) VALUES (?, ?, ?, ?, ?, ?, 'OPEN', 0.0, 0.0, ?)
            """, (now, clean_ticker, shares, spot_price, atr_stop, target_price, spot_price))
            pos_id = cursor.lastrowid
        conn.close()
        return pos_id

    @classmethod
    def get_open_positions(cls) -> List[Dict[str, Any]]:
        """Retrieves all active open positions."""
        conn = sqlite3.connect(str(DB_PATH), timeout=1.0)
        init_paper_tables(conn)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, ticker, shares, entry_price, current_stop, target_price, status, unrealized_pnl, realized_pnl, highest_price
            FROM paper_portfolio
            WHERE status = 'OPEN'
        """)
        rows = cursor.fetchall()
        conn.close()
        positions = []
        for r in rows:
            positions.append({
                "id": r[0],
                "timestamp": r[1],
                "ticker": r[2],
                "shares": r[3],
                "entry_price": r[4],
                "current_stop": r[5],
                "target_price": r[6],
                "status": r[7],
                "unrealized_pnl": r[8],
                "realized_pnl": r[9],
                "highest_price": r[10]
            })
        return positions

    @classmethod
    def sync_positions(cls) -> Dict[str, Any]:
        """
        Polls live prices, ratchets ATR stops upward monotonically,
        triggers exits if stop breached, and updates unrealized/realized PnL.
        """
        conn = sqlite3.connect(str(DB_PATH), timeout=1.0)
        init_paper_tables(conn)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, ticker, shares, entry_price, current_stop, target_price, highest_price
            FROM paper_portfolio
            WHERE status = 'OPEN'
        """)
        open_rows = cursor.fetchall()

        synced_positions: List[Dict[str, Any]] = []
        total_equity = 0.0
        total_unrealized_pnl = 0.0
        total_realized_pnl = 0.0

        for pos_id, ticker, shares, entry_price, current_stop, target_price, highest_price in open_rows:
            # 1. Fetch live market spot price
            feed = LiveFeedIngestionAgent.fetch(ticker, period="1mo", interval="1d")
            spot = feed.spot_price if (feed and feed.spot_price > 0) else entry_price

            # 2. Inquire Agent 02 for ATR stop calculation
            risk_payload = PortfolioGuardAgent.calculate_stops(ticker)
            proposed_stop = risk_payload.metrics.get("proposed_stop", current_stop)

            new_highest = max(highest_price, spot)
            # Monotonic stop ratchet: stops ONLY move upwards, never down
            new_stop = max(current_stop, proposed_stop)

            # 3. Check for Stop-Out or Target Exits
            if spot <= new_stop:
                status = "STOPPED_OUT"
                realized = round((spot - entry_price) * shares, 2)
                unrealized = 0.0
                total_realized_pnl += realized
            else:
                status = "OPEN"
                realized = 0.0
                unrealized = round((spot - entry_price) * shares, 2)
                total_unrealized_pnl += unrealized
                total_equity += (spot * shares)

            # 4. Atomic database update
            cursor.execute("""
                UPDATE paper_portfolio
                SET current_stop = ?, highest_price = ?, unrealized_pnl = ?, realized_pnl = realized_pnl + ?, status = ?
                WHERE id = ?
            """, (new_stop, new_highest, unrealized, realized, status, pos_id))

            pnl_pct = round(((spot - entry_price) / entry_price) * 100.0, 2) if entry_price > 0 else 0.0
            stop_dist_pct = round(((spot - new_stop) / spot) * 100.0, 2) if spot > 0 else 0.0

            synced_positions.append({
                "ticker": ticker,
                "shares": shares,
                "entry": entry_price,
                "spot": spot,
                "stop": new_stop,
                "pnl_usd": unrealized if status == "OPEN" else realized,
                "pnl_pct": pnl_pct,
                "stop_dist_pct": stop_dist_pct,
                "status": status
            })

        conn.commit()
        conn.close()

        return {
            "last_sync": time.time(),
            "total_equity": round(total_equity, 2),
            "unrealized_pnl": round(total_unrealized_pnl, 2),
            "realized_pnl": round(total_realized_pnl, 2),
            "positions": synced_positions
        }
