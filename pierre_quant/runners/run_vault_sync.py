"""
pierre_quant/runners/run_vault_sync.py
Synchronizes active portfolio sentry dossiers and generates Obsidian Canvas graphs.
Enforces read-only persistence lock (?mode=ro) and writes clean JSON Canvas + Markdown files.
"""
from __future__ import annotations
import json
import logging
import sqlite3
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pierre_quant.skills.obsidian_gateway import (
    SentryDossierPayload,
    write_recon_note,
    generate_trade_canvas,
    write_master_portfolio_overview,
    VAULT_PATH,
)

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("VaultSyncRunner")

BUFFER_PATH = Path(r"C:\Users\Pierre\.openclaw\workspace\hud_telemetry_buffer.json")
DB_PATH = Path(r"C:\Users\Pierre\.openclaw\workspace\pierre-quant\pierre_quant.db")


def sync_vault_from_telemetry() -> list[SentryDossierPayload]:
    """Ingests live HUD telemetry buffer and syncs Obsidian Markdown recons and Canvas files."""
    dossiers: list[SentryDossierPayload] = []

    # Strategy A: Read from active HUD telemetry buffer if available
    if BUFFER_PATH.exists():
        try:
            with open(BUFFER_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            positions = data.get("positions", [])
            for p in positions:
                dossiers.append(
                    SentryDossierPayload(
                        ticker=p.get("ticker", "UNK"),
                        bucket=p.get("bucket", "SWING"),
                        spot_price=float(p.get("spot_price", 0.0)),
                        atr_14=float(p.get("atr_14", 0.0)),
                        invalidation_stop=float(p.get("invalidation_stop", 0.0)),
                        timesfm_target=float(p.get("timesfm_target", 0.0)),
                        chronos_target=float(p.get("chronos_target", 0.0)),
                        net_bias=p.get("net_bias", "BULLISH"),
                        notes=f"Corridor Spread Δ: {p.get('model_spread_delta', 0.0):.2f}%"
                    )
                )
        except Exception as e:
            logger.warning(f"Could not parse telemetry buffer: {e}")

    # Strategy B: Fallback to SQLite database under read-only lock
    if not dossiers and DB_PATH.exists():
        try:
            conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
            cur = conn.cursor()
            cur.execute("SELECT ticker, bucket, shares FROM portfolio_positions WHERE status = 'ACTIVE'")
            rows = cur.fetchall()
            for ticker, bucket, shares in rows:
                dossiers.append(
                    SentryDossierPayload(
                        ticker=ticker,
                        bucket=bucket,
                        spot_price=0.0,
                        atr_14=0.0,
                        invalidation_stop=0.0,
                        timesfm_target=0.0,
                        chronos_target=0.0,
                        net_bias="BULLISH",
                        notes=f"Active position: {shares} shares."
                    )
                )
            conn.close()
        except Exception as err:
            logger.error(f"Failed to query database: {err}")

    if not dossiers:
        logger.error("No active dossiers found to sync into Vault.")
        return []

    logger.info(f"Syncing {len(dossiers)} assets into Obsidian Vault at {VAULT_PATH}")

    # Write Markdown recons and JSON Canvas graphs
    for d in dossiers:
        write_recon_note(d)
        generate_trade_canvas(d)

    # Write master portfolio overview
    write_master_portfolio_overview(dossiers)

    logger.info(f"Successfully synchronized Obsidian Vault: {len(dossiers)} recons, {len(dossiers)} canvases.")
    return dossiers


if __name__ == "__main__":
    sync_vault_from_telemetry()
