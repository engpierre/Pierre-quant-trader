"""
pierre_quant/orchestration/supervisor.py
Agent 01 (Supervisor Orchestrator) - Master Confluence Engine with Resilient Environment Fallback.
"""
from __future__ import annotations
import argparse
import json
import logging
import os
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict

# Force UTF-8 output on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# --- ENVIRONMENT & SITE-PACKAGES INJECTION HOOK ---
VENV_PYTHON = Path(r"C:\Users\Pierre\.openclaw\workspace\Julie-Core\.venv\Scripts\python.exe")
VENV_SITE_PACKAGES = Path(r"C:\Users\Pierre\.openclaw\workspace\Julie-Core\.venv\Lib\site-packages")

if VENV_SITE_PACKAGES.exists() and str(VENV_SITE_PACKAGES) not in sys.path:
    sys.path.insert(0, str(VENV_SITE_PACKAGES))

PROJECT_ROOT = Path(r"C:\Users\Pierre\.openclaw\workspace\pierre-quant")
if PROJECT_ROOT.exists() and str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Safe fallback imports for core analytical nodes
from pierre_quant.core.agent_contract import AgentExecutionPayload, DirectionalBias, ExecutionStatus
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
from pierre_quant.risk.portfolio_guard import PortfolioGuardAgent

logging.basicConfig(level=logging.WARNING, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("Agent01_Supervisor")


class ConsensusBias(str, Enum):
    BULLISH_CONVERGENCE = "BULLISH_CONVERGENCE"
    BEARISH_CONVERGENCE = "BEARISH_CONVERGENCE"
    NEUTRAL_CONSOLIDATION = "NEUTRAL_CONSOLIDATION"


@dataclass(slots=True, frozen=True)
class SupervisorSynthesisResult:
    ticker: str
    spot_price: float
    consensus_bias: ConsensusBias
    net_confluence_score: float
    predictive_spread_pct: float
    predictive_regime: str
    risk_invalidation_floor: float
    vote_breakdown: Dict[str, Dict[str, Any]]
    action_directive: str


class SupervisorOrchestrator:
    AGENT_ID = "01_supervisor_orchestrator"

    @classmethod
    def _execute_cli_worker(cls, script_rel_path: str, ticker: str) -> Dict[str, Any]:
        """Runs heavy PyTorch predictive engines via isolated CLI subprocess to prevent sandbox import crashes."""
        py_bin = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable
        script_path = PROJECT_ROOT / script_rel_path
        
        try:
            cmd = [py_bin, str(script_path), "--ticker", ticker, "--json"]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if proc.returncode == 0 and proc.stdout.strip():
                # Extract JSON substring if other stdout precedes it
                stdout_clean = proc.stdout.strip()
                json_start = stdout_clean.find("{")
                json_end = stdout_clean.rfind("}")
                if json_start != -1 and json_end != -1:
                    return json.loads(stdout_clean[json_start : json_end + 1])
        except Exception as e:
            logger.error(f"Failed CLI subprocess for {script_rel_path}: {e}")
        
        # Fallback default payload
        return {
            "status": "FAILED", "directional_bias": "NEUTRAL", "confidence_score": 50.0,
            "spot_price": 0.0, "metrics": {"forecast_delta_pct": 0.0}, "error_message": "Subprocess execution failure"
        }

    @classmethod
    def synthesize(cls, ticker: str) -> SupervisorSynthesisResult:
        clean_ticker = ticker.strip().upper().lstrip("$")

        # 1. Execute Isolated Predictive Workers (GPU 0 & GPU 1)
        res_timesfm = cls._execute_cli_worker("pierre_quant/models/timesfm_engine.py", clean_ticker)
        res_chronos = cls._execute_cli_worker("pierre_quant/models/chronos_engine.py", clean_ticker)

        # 2. Execute Deterministic Analytical Pipeline (Divisions III–V)
        p_stat = StatisticalInvarianceAgent.analyze(clean_ticker)
        p_mom = MomentumVectorAgent.analyze(clean_ticker)
        p_sentry = VisualSentryAgent.analyze(clean_ticker)
        p_money = SmartMoneyAgent.analyze(clean_ticker)
        p_timeframe = TimeframeMatrixAgent.analyze(clean_ticker)
        p_fund = CorporateFundamentalsAgent.evaluate(clean_ticker)
        p_sec = SECWatchdogAgent.evaluate(clean_ticker)
        p_sector = SectorRotationAgent.evaluate(clean_ticker)
        p_macro = MacroEnvironmentAgent.evaluate(clean_ticker)
        p_sent = SentimentHarvesterAgent.harvest(clean_ticker)
        p_risk = PortfolioGuardAgent.calculate_stops(clean_ticker)

        spot = res_timesfm.get("spot_price") or p_sentry.spot_price

        # 3. Predictive Divergence Engine
        t_delta = res_timesfm.get("metrics", {}).get("forecast_delta_pct", 0.0)
        c_delta = res_chronos.get("metrics", {}).get("forecast_delta_pct", 0.0)
        pred_spread = round(t_delta - c_delta, 2)
        
        t_bias = res_timesfm.get("directional_bias", "NEUTRAL")
        c_bias = res_chronos.get("directional_bias", "NEUTRAL")
        is_pred_conflict = (t_bias != c_bias) or (abs(pred_spread) > 1.5)
        pred_regime = "CONFLICTING_REGIME" if is_pred_conflict else "CONVERGENT_REGIME"

        # 4. Weighted Confluence Vote Engine
        bull_weight, bear_weight, total_weight = 0.0, 0.0, 0.0
        vote_table: Dict[str, Dict[str, Any]] = {}

        # Ingest Predictive Payloads
        for key, res in [("06a_timesfm", res_timesfm), ("06b_chronos", res_chronos)]:
            raw_conf = res.get("confidence_score", 50.0)
            discount = 0.80 if is_pred_conflict else 1.0
            eff_wt = raw_conf * discount
            total_weight += eff_wt
            bias_val = res.get("directional_bias", "NEUTRAL")
            if bias_val == "BULLISH":
                bull_weight += eff_wt
            elif bias_val == "BEARISH":
                bear_weight += eff_wt
            vote_table[key] = {
                "bias": bias_val, "confidence": raw_conf, "effective_weight": round(eff_wt, 2), "metrics": res.get("metrics", {})
            }

        # Ingest Standard Analytical Nodes
        payload_map = {
            "07_stat_invariance": p_stat, "08_momentum": p_mom, "09_visual_sentry": p_sentry,
            "10_smart_money": p_money, "11_timeframe": p_timeframe, "12_fundamentals": p_fund,
            "13_sec_watchdog": p_sec, "14_sector_rotation": p_sector, "15_macro": p_macro, "16_sentiment": p_sent
        }

        for key, p in payload_map.items():
            if p.status != ExecutionStatus.SUCCESS:
                continue
            raw_conf = p.confidence_score
            discount = 1.0
            if key == "16_sentiment" and p_money.directional_bias == DirectionalBias.BEARISH and p.directional_bias == DirectionalBias.BULLISH:
                discount *= 0.50
            eff_wt = raw_conf * discount
            total_weight += eff_wt
            if p.directional_bias == DirectionalBias.BULLISH:
                bull_weight += eff_wt
            elif p.directional_bias == DirectionalBias.BEARISH:
                bear_weight += eff_wt
            vote_table[key] = {
                "bias": p.directional_bias.value, "confidence": raw_conf, "effective_weight": round(eff_wt, 2), "metrics": p.metrics
            }

        net_confluence = round(((bull_weight - bear_weight) / total_weight * 100.0), 2) if total_weight > 0 else 0.0

        if net_confluence >= 25.0:
            consensus = ConsensusBias.BULLISH_CONVERGENCE
            directive = "ACCUMULATE / HOLD LONG (Trail stop via Agent 02)"
        elif net_confluence <= -25.0:
            consensus = ConsensusBias.BEARISH_CONVERGENCE
            directive = "DEFENSIVE DE-RISK / TRIM / SHORT CONGRUENT"
        else:
            consensus = ConsensusBias.NEUTRAL_CONSOLIDATION
            directive = "HOLD INERTIA / AVOID SIZE EXPANSION"

        invalidation_floor = p_risk.metrics.get("proposed_stop") or p_risk.metrics.get("invalidation_floor") or p_sentry.metrics.get("nearest_support", 0.0)

        return SupervisorSynthesisResult(
            ticker=clean_ticker, spot_price=spot, consensus_bias=consensus,
            net_confluence_score=net_confluence, predictive_spread_pct=pred_spread,
            predictive_regime=pred_regime, risk_invalidation_floor=invalidation_floor,
            vote_breakdown=vote_table, action_directive=directive
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent 01: Supervisor Master Harness CLI")
    parser.add_argument("--ticker", required=True, help="Ticker to analyze")
    parser.add_argument("--json", action="store_true", help="Output pure JSON")
    args = parser.parse_args()

    res = SupervisorOrchestrator.synthesize(args.ticker)
    if args.json:
        print(json.dumps({
            "ticker": res.ticker, "spot_price": res.spot_price, "consensus_bias": res.consensus_bias.value,
            "net_confluence_score": res.net_confluence_score, "predictive_spread_pct": res.predictive_spread_pct,
            "predictive_regime": res.predictive_regime, "risk_invalidation_floor": res.risk_invalidation_floor,
            "action_directive": res.action_directive, "vote_breakdown": res.vote_breakdown
        }))
    else:
        print(f"\n# TARGET DEEP-DIVE DOSSIER :: ${res.ticker}")
        print(f"* **Spot Price:** ${res.spot_price:.2f}")
        print(f"* **Consensus Bias:** `{res.consensus_bias.value}` | **Net Confluence:** {res.net_confluence_score:+5.2f}%")
        print(f"* **Predictive Spread:** {res.predictive_spread_pct:+5.2f}% ({res.predictive_regime})")
        print(f"* **Risk Stop Floor (Agent 02):** ${res.risk_invalidation_floor:.2f}")
        print(f"* **Action Directive:** {res.action_directive}\n")
        print("| Agent Node | Bias | Raw Conf | Eff Wt | Key Metric Summary |")
        print("| :--- | :--- | :--- | :--- | :--- |")
        for node, data in res.vote_breakdown.items():
            print(f"| **{node}** | `{data['bias']}` | {data['confidence']:.1f}% | {data['effective_weight']:.1f} | `{str(data['metrics'])[:50]}` |")
