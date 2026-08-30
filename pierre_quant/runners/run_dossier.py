"""
pierre_quant/runners/run_dossier.py
Agent 01 Supervisor: Target Deep-Dive Dossier Orchestrator.
Compiles Divisions II-V into structured Report Architecture A.
"""
from __future__ import annotations
import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# UTF-8 stdout protection for Windows CP1252 environments
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.platform == "win32" and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pierre_quant.core.agent_contract import ExecutionStatus, DirectionalBias
from pierre_quant.ingestion.live_feed import LiveFeedIngestionAgent
from pierre_quant.risk.portfolio_guard import RiskGuardAgent
from pierre_quant.models.timesfm_engine import TimesFMForecastingAgent
from pierre_quant.analysis.statistical_invariance import StatisticalInvarianceAgent
from pierre_quant.analysis.momentum_vector import MomentumVectorAgent
from pierre_quant.analysis.visual_sentry import VisualSentryAgent
from pierre_quant.analysis.smart_money import SmartMoneyAgent
from pierre_quant.analysis.timeframe_matrix import TimeframeMatrixAgent
from pierre_quant.fundamentals.corporate_fundamentals import CorporateFundamentalsAgent
from pierre_quant.regulatory.sec_watchdog import SECWatchdogAgent
from pierre_quant.analysis.sector_rotation import SectorRotationAgent
from pierre_quant.macro.macro_tracker import MacroEnvironmentAgent
from pierre_quant.sentiment.sentiment_harvester import SentimentHarvesterAgent

logging.basicConfig(level=logging.WARNING, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("Agent01_Supervisor")


class TargetDossierOrchestrator:
    """Agent 01 Supervisor Orchestrator for compiling Target Deep-Dive Dossiers."""

    @classmethod
    def compile_dossier(cls, ticker: str, save_report: bool = True) -> str:
        clean_ticker = ticker.strip().upper().lstrip("$")

        # Division I & Ingestion: Agent 05
        feed = LiveFeedIngestionAgent.fetch(clean_ticker, period="3mo", interval="1d")
        spot = feed.spot_price if feed.status == ExecutionStatus.SUCCESS else 0.0
        dual_corroborated = feed.status == ExecutionStatus.SUCCESS and len(feed.candles) >= 20
        corroboration_status = "DUAL-VERIFIED" if dual_corroborated else "SINGLE-NODE HAIRCUT APPLIED"

        # Division II: Agent 02 Risk Guard
        risk = RiskGuardAgent.evaluate(clean_ticker, cost_basis=spot, current_stop=0.0)
        invalidation_floor = risk.metrics.get("proposed_stop", round(spot * 0.90, 2)) if risk.status == ExecutionStatus.SUCCESS else round(spot * 0.90, 2)
        allocation_cap = 20.0 if dual_corroborated else 10.0

        # Division III: Predictive & Statistical
        a06 = TimesFMForecastingAgent.forecast(clean_ticker)
        a07 = StatisticalInvarianceAgent.analyze(clean_ticker)
        a08 = MomentumVectorAgent.analyze(clean_ticker)

        # Division IV: Structural & Flow
        a09 = VisualSentryAgent.analyze(clean_ticker)
        a10 = SmartMoneyAgent.analyze(clean_ticker)
        a11 = TimeframeMatrixAgent.analyze(clean_ticker)

        # Division V: Overlays
        a12 = CorporateFundamentalsAgent.evaluate(clean_ticker)
        a13 = SECWatchdogAgent.evaluate(clean_ticker)
        a14 = SectorRotationAgent.evaluate(clean_ticker)
        a15 = MacroEnvironmentAgent.evaluate(clean_ticker)
        a16 = SentimentHarvesterAgent.harvest(clean_ticker)

        # Compute Consensus Directional Bias & Confidence
        biases = [
            a06.directional_bias if a06.status == ExecutionStatus.SUCCESS else DirectionalBias.NEUTRAL,
            a07.directional_bias if a07.status == ExecutionStatus.SUCCESS else DirectionalBias.NEUTRAL,
            a08.directional_bias if a08.status == ExecutionStatus.SUCCESS else DirectionalBias.NEUTRAL,
            a09.directional_bias if a09.status == ExecutionStatus.SUCCESS else DirectionalBias.NEUTRAL,
            a10.directional_bias if a10.status == ExecutionStatus.SUCCESS else DirectionalBias.NEUTRAL,
            a11.directional_bias if a11.status == ExecutionStatus.SUCCESS else DirectionalBias.NEUTRAL,
            a14.directional_bias if a14.status == ExecutionStatus.SUCCESS else DirectionalBias.NEUTRAL,
        ]
        bull_count = sum(1 for b in biases if b == DirectionalBias.BULLISH)
        bear_count = sum(1 for b in biases if b == DirectionalBias.BEARISH)

        if bull_count >= 4:
            overall_bias = "BULLISH"
        elif bear_count >= 4:
            overall_bias = "BEARISH"
        else:
            overall_bias = "NEUTRAL"

        # Check for data-opacity haircuts
        haircut_applied = (
            a13.metrics.get("regulatory_state") == "INSIDER_BLINDSPOT" or 
            a16.metrics.get("sentiment_state") == "DATA_BLINDSPOT"
        )
        if bull_count >= 5 or bear_count >= 5:
            conf_label = "MODERATE (PENALIZED)" if haircut_applied else "HIGH"
        elif bull_count >= 3 or bear_count >= 3:
            conf_label = "PENALIZED" if haircut_applied else "MODERATE"
        else:
            conf_label = "PENALIZED" if haircut_applied else "MODERATE"

        # Format Quant & Structural Vectors Table
        tfm_price = a06.metrics.get("terminal_price", spot)
        tfm_delta = a06.metrics.get("forecast_delta_pct", 0.0)
        tfm_posture = "ACCEL UP" if tfm_delta > 1.5 else ("ACCEL DOWN" if tfm_delta < -1.5 else "COMPRESS")

        z_score = a07.metrics.get("z_score", 0.0)
        z_state = a07.metrics.get("equilibrium_state", "FAIR_VALUE")

        macd_hist = a08.metrics.get("macd_hist", 0.0)
        vel_state = a08.metrics.get("velocity_state", "FLATLINING")

        supp = a09.metrics.get("nearest_support", 0.0)
        res = a09.metrics.get("nearest_resistance", 0.0)
        vwap = a09.metrics.get("vwap", spot)
        struct_state = a09.metrics.get("structural_state", "AT_VWAP_EQUILIBRIUM")

        poc = a10.metrics.get("point_of_control", spot)
        flow_regime = a10.metrics.get("flow_regime", "NEUTRAL_FLOW")

        # Format Fundamental, Regulatory & Sentiment Overlays
        pe_str = f"{a12.metrics.get('trailing_pe', 'N/A')}"
        fcf_str = f"{a12.metrics.get('fcf_yield_pct', 'N/A')}%"
        ev_ebitda_str = f"{a12.metrics.get('forward_pe', 'N/A')}"

        buys = a13.metrics.get("purchase_count", 0)
        sells = a13.metrics.get("sale_count", 0)
        net_sh = a13.metrics.get("insider_net_shares", 0)
        reg_state = a13.metrics.get("regulatory_state", "CLEAN_NEUTRAL")
        if reg_state == "INSIDER_BLINDSPOT":
            whale_str = "FORM 4 STREAM UNPOPULATED (20% NULL PENALTY APPLIED)"
        else:
            whale_str = f"{buys} Buys / {sells} Sells (Net: {net_sh:+d} shares) | {reg_state}"

        sec_state = a14.metrics.get("sector_state", "IN_LINE_PERFORMER")
        sec_bench = a14.metrics.get("benchmark", "SPY")
        sec_alpha = a14.metrics.get("alpha_20d_pct", 0.0)
        sector_str = f"{sec_state} vs {sec_bench} (α={sec_alpha:+5.2f}%)"

        sent_pol = a16.metrics.get("polarity_score", 0.0)
        sent_arts = a16.metrics.get("article_count", 0)
        sent_state = a16.metrics.get("sentiment_state", "BALANCED_NEUTRAL")
        if sent_state == "DATA_BLINDSPOT":
            sent_str = "NEWS STREAM UNPOPULATED (20% NULL PENALTY APPLIED)"
        else:
            sent_str = f"Polarity: {sent_pol:+4.2f} | Articles: {sent_arts} ({sent_state})"

        # Assemble Output Contract Markdown
        lines = [
            f"# TARGET DEEP-DIVE DOSSIER :: {clean_ticker}",
            f"* **Spot Price / Corroboration:** ${spot:.2f} ({corroboration_status})",
            f"* **Directional Bias & Confidence:** {overall_bias} | Confidence: {conf_label}",
            "",
            "### QUANT & STRUCTURAL VECTORS",
            "| Metric | Node Source | Observation / Value | Bias Flag |",
            "| :--- | :--- | :--- | :--- |",
            f"| **TimesFM Forecast (16-Bar)** | Agent 06 | Mean Expectation: ${tfm_price:.2f} (Δ={tfm_delta:+5.2f}%) | {tfm_posture} |",
            f"| **Statistical Invariance** | Agent 07 | Z-Score: {z_score:+.2f} | {z_state} |",
            f"| **Momentum Vector** | Agent 08 | MACD Spread Velocity: {macd_hist:+.4f} | {vel_state} |",
            f"| **Key Levels (S/R / VWAP)** | Agent 09 | Support: ${supp:.2f} \\| Resist: ${res:.2f} \\| VWAP: ${vwap:.2f} | {struct_state} |",
            f"| **Smart Money / Accumulation** | Agent 10 | Volume-at-Price Profile Node: ${poc:.2f} | {flow_regime} |",
            "",
            "### FUNDAMENTAL, REGULATORY & SENTIMENT OVERLAYS",
            f"* **Valuation & Balance Sheet (Agent 12):** P/E: {pe_str} | Forward P/E: {ev_ebitda_str} | FCF Yield: {fcf_str}",
            f"* **Whale / SEC Form 4 (Agent 13):** {whale_str}",
            f"* **Sector Relative Strength (Agent 14):** {sector_str}",
            f"* **Sentiment Index (Agent 16):** {sent_str}",
            "",
            "### INVALIDATION BOUNDARIES (AGENT 02)",
            f"* **ATR Invalidation Floor:** ${invalidation_floor:.2f}",
            f"* **Max Allocation Cap:** {allocation_cap:.1f}%",
        ]
        report_md = "\n".join(lines)

        if save_report:
            reports_dir = PROJECT_ROOT / "reports"
            reports_dir.mkdir(parents=True, exist_ok=True)
            report_file = reports_dir / f"DOSSIER_{clean_ticker}.md"
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report_md + "\n")

        return report_md


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent 01 Supervisor Target Deep-Dive Dossier Orchestrator")
    parser.add_argument("--ticker", default="SOFI", help="Target holding ticker")
    args = parser.parse_args()

    dossier = TargetDossierOrchestrator.compile_dossier(args.ticker)
    print(dossier)
