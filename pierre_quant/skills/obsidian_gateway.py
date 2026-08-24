"""
pierre_quant/skills/obsidian_gateway.py
Deterministic Obsidian Skills Gateway for OpenClaw, Hermes, and Julie Core.
Conforms to kepano/obsidian-skills specification (YAML Markdown + .canvas JSON).
"""
from __future__ import annotations
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("ObsidianGateway")

VAULT_PATH = Path(r"C:\Users\Pierre\.openclaw\workspace\vault")
RECON_DIR = VAULT_PATH / "Recons"
BRIEFS_DIR = VAULT_PATH / "Briefs"
CANVAS_DIR = VAULT_PATH / "Canvas"

for d in [RECON_DIR, BRIEFS_DIR, CANVAS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


@dataclass(slots=True, frozen=True)
class SentryDossierPayload:
    ticker: str
    bucket: str
    spot_price: float
    atr_14: float
    invalidation_stop: float
    timesfm_target: float
    chronos_target: float
    net_bias: str
    notes: str = ""


def write_recon_note(dossier: SentryDossierPayload) -> Path:
    """Generates a standardized YAML-frontmatter Markdown note for an asset."""
    file_path = RECON_DIR / f"{dossier.ticker}.md"
    content = f"""---
ticker: "{dossier.ticker}"
bucket: "{dossier.bucket}"
spot_price: {dossier.spot_price:.2f}
atr_14: {dossier.atr_14:.2f}
invalidation_stop: {dossier.invalidation_stop:.2f}
timesfm_target: {dossier.timesfm_target:.2f}
chronos_target: {dossier.chronos_target:.2f}
net_bias: "{dossier.net_bias}"
last_synced: "{datetime.now().isoformat()}"
---

# 🎯 Quantitative Recon Dossier: ${dossier.ticker}

| Metric | Target Level | Risk Boundary |
| :--- | :--- | :--- |
| **Spot Price** | ${dossier.spot_price:.2f} | — |
| **14-Day ATR** | ${dossier.atr_14:.2f} | Dynamic Volatility Baseline |
| **Invalidation Stop** | ${dossier.invalidation_stop:.2f} | 1.8x ATR Protective Floor |
| **TimesFM Horizon** | ${dossier.timesfm_target:.2f} | 16-Bar Neural Projection (cuda:0) |
| **Chronos-Bolt** | ${dossier.chronos_target:.2f} | Dual-Node Corroboration (cuda:1) |

## Operational Notes
{dossier.notes or "Automated Sentry sync generated via Pierre Quant Swarm."}

## Related Links
- [[Portfolio Overview]]
- [[Morning Briefs]]
- [[{dossier.ticker}_setup.canvas|Interactive Setup Canvas]]
"""
    file_path.write_text(content, encoding="utf-8")
    logger.info(f"Recon note generated: {file_path}")
    return file_path


def generate_trade_canvas(dossier: SentryDossierPayload) -> Path:
    """Generates an Obsidian JSON Canvas visual trade setup."""
    canvas_path = CANVAS_DIR / f"{dossier.ticker}_setup.canvas"
    
    canvas_data = {
        "nodes": [
            {"id": "node_spot", "type": "text", "text": f"### ${dossier.ticker} Spot\n**${dossier.spot_price:.2f}**", "x": 0, "y": 0, "width": 250, "height": 120, "color": "1"},
            {"id": "node_stop", "type": "text", "text": f"### ⚠️ Invalidation Stop\n**${dossier.invalidation_stop:.2f}**\n*(1.8x ATR: ${dossier.atr_14:.2f})*", "x": -300, "y": 150, "width": 250, "height": 140, "color": "4"},
            {"id": "node_tfm", "type": "text", "text": f"### 📈 TimesFM Target\n**${dossier.timesfm_target:.2f}**\n*(16-Bar cuda:0)*", "x": 300, "y": -100, "width": 250, "height": 140, "color": "2"},
            {"id": "node_chr", "type": "text", "text": f"### ⚡ Chronos-Bolt Target\n**${dossier.chronos_target:.2f}**\n*(cuda:1 Horizon)*", "x": 300, "y": 100, "width": 250, "height": 140, "color": "3"}
        ],
        "edges": [
            {"id": "edge_1", "fromNode": "node_spot", "fromSide": "left", "toNode": "node_stop", "toSide": "top", "label": "Protective Floor"},
            {"id": "edge_2", "fromNode": "node_spot", "fromSide": "right", "toNode": "node_tfm", "toSide": "left", "label": "Forecast Vector"},
            {"id": "edge_3", "fromNode": "node_spot", "fromSide": "right", "toNode": "node_chr", "toSide": "left", "label": "Convergence Vector"}
        ]
    }
    
    canvas_path.write_text(json.dumps(canvas_data, indent=2), encoding="utf-8")
    logger.info(f"JSON Canvas generated: {canvas_path}")
    return canvas_path


def write_morning_brief_note(brief_text: str, systemic_sigma: float = 1.85, total_positions: int = 20) -> Path:
    """Generates an executive morning brief note in vault/Briefs/."""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    timestamp_str = now.strftime("%Y-%m-%d_%H%M%S")
    file_path = BRIEFS_DIR / f"Brief_{timestamp_str}.md"

    content = f"""---
title: "Executive Flight Check - {date_str}"
date: "{date_str}"
timestamp: "{now.isoformat()}"
systemic_risk_sigma: {systemic_sigma:.2f}
active_holdings: {total_positions}
type: "morning_flight_check"
---

# 🌅 Executive Morning Flight Check ({date_str})

{brief_text}

## References
- [[Portfolio Overview]]
- [[Morning Briefs]]
"""
    file_path.write_text(content, encoding="utf-8")
    logger.info(f"Morning brief note generated: {file_path}")
    return file_path


def write_master_portfolio_overview(dossiers: list[SentryDossierPayload]) -> Path:
    """Generates the master Portfolio Overview linking all recon notes and canvases."""
    overview_path = VAULT_PATH / "Portfolio Overview.md"
    
    lines = [
        "---",
        "title: 'Portfolio Overview'",
        f"last_updated: '{datetime.now().isoformat()}'",
        f"total_holdings: {len(dossiers)}",
        "---",
        "",
        "# 🏛️ Active Quantitative Portfolio Overview",
        "",
        "| Bucket | Ticker | Spot Price | 14-Day ATR | Invalidation Stop | TimesFM Target | Chronos Target | Canvas Map |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
    ]
    
    for d in dossiers:
        lines.append(
            f"| **{d.bucket}** | [[Recons/{d.ticker}|${d.ticker}]] | ${d.spot_price:.2f} | ${d.atr_14:.2f} | "
            f"${d.invalidation_stop:.2f} | ${d.timesfm_target:.2f} | ${d.chronos_target:.2f} | "
            f"[[Canvas/{d.ticker}_setup.canvas|🗺️ Setup]] |"
        )
    
    lines.extend([
        "",
        "## Vault Structure",
        "- `Recons/`: Standardized Markdown dossiers with YAML frontmatter",
        "- `Canvas/`: Obsidian JSON spatial trajectory graphs",
        "- `Briefs/`: Executive morning briefs and flight checks"
    ])
    
    overview_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info(f"Master overview generated: {overview_path}")
    return overview_path
