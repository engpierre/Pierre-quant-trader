"""
pierre_quant/orchestration/supervisor.py
Agent 01 (Supervisor Orchestrator) - Master Multi-Agent Confluence Engine with Opportunistic Learning Hook.
"""
from __future__ import annotations
import argparse
import json
import logging
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Tuple

# Force UTF-8 output on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.platform == "win32" and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# --- ENVIRONMENT & SITE-PACKAGES INJECTION HOOK ---
VENV_PYTHON = Path(r"C:\Users\Pierre\.openclaw\workspace\Julie-Core\.venv\Scripts\python.exe")
VENV_SITE_PACKAGES = Path(r"C:\Users\Pierre\.openclaw\workspace\Julie-Core\.venv\Lib\site-packages")

if VENV_SITE_PACKAGES.exists() and str(VENV_SITE_PACKAGES) not in sys.path:
    sys.path.insert(0, str(VENV_SITE_PACKAGES))

PROJECT_ROOT = Path(r"C:\Users\Pierre\.openclaw\workspace\pierre-quant")
if PROJECT_ROOT.exists() and str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Core Analytical Node Imports
from pierre_quant.core.agent_contract import (
    AgentExecutionPayload, DirectionalBias, ExecutionStatus
)
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
from pierre_quant.learning.settlement_engine import (
    run_opportunistic_settlement, record_forecast_batch
)

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
    NODE_TIMEOUT_SECONDS = 10.0

    @classmethod
    def _execute_cli_worker(cls, script_rel_path: str, ticker: str) -> Dict[str, Any]:
        """Runs heavy PyTorch predictive engines via isolated CLI subprocess to prevent sandbox import crashes."""
        py_bin = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable
        script_path = PROJECT_ROOT / script_rel_path
        
        try:
            cmd = [py_bin, str(script_path), "--ticker", ticker, "--json"]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=cls.NODE_TIMEOUT_SECONDS)
            if proc.returncode == 0 and proc.stdout.strip():
                stdout_clean = proc.stdout.strip()
                json_start = stdout_clean.find("{")
                json_end = stdout_clean.rfind("}")
                if json_start != -1 and json_end != -1:
                    parsed = json.loads(stdout_clean[json_start : json_end + 1])
                    if isinstance(parsed, dict) and parsed.get("status") == "SUCCESS":
                        return parsed
        except Exception as e:
            logger.error(f"Failed CLI subprocess for {script_rel_path}: {e}")
        
        # Explicit data-opacity failure payload
        return {
            "status": "FAILED",
            "directional_bias": "NEUTRAL",
            "confidence_score": 50.0,
            "spot_price": 0.0,
            "metrics": {
                "forecast_delta_pct": 0.0,
                "opacity_penalty": True,
                "execution_error": "Subprocess CLI exit failure"
            },
            "error_message": "Subprocess execution failure"
        }

    @classmethod
    def _safe_execute_node(cls, node_key: str, ticker: str, fn: Callable[..., Any], *args, **kwargs) -> Tuple[str, Any]:
        """Executes a single specialist worker inside a timeout-protected thread wrapper."""
        try:
            result = fn(*args, **kwargs)
            return node_key, result
        except Exception as err:
            logger.warning(f"Specialist worker {node_key} failed on {ticker}: {err}")
            fallback_payload = AgentExecutionPayload(
                agent_id=node_key,
                ticker=ticker,
                status=ExecutionStatus.FAILED,
                directional_bias=DirectionalBias.NEUTRAL,
                confidence_score=50.0,
                spot_price=0.0,
                metrics={
                    "opacity_penalty": True,
                    "execution_error": str(err)
                },
                error_message=str(err)
            )
            return node_key, fallback_payload

    @classmethod
    def synthesize(cls, ticker: str) -> SupervisorSynthesisResult:
        clean_ticker = ticker.strip().upper().lstrip("$")

        # 0. Opportunistic Learning & Calibration Hook (< 300ms)
        dynamic_weights = run_opportunistic_settlement()

        # 1. Dispatch Concurrent Analytical Pipeline via ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=12) as executor:
            # GPU Predictive Subprocesses (cuda:0 & cuda:1)
            future_tfm = executor.submit(cls._execute_cli_worker, "pierre_quant/models/timesfm_engine.py", clean_ticker)
            future_chr = executor.submit(cls._execute_cli_worker, "pierre_quant/models/chronos_engine.py", clean_ticker)

            # Parallel Network & Analytical Workers
            future_stat = executor.submit(cls._safe_execute_node, "07_stat_invariance", clean_ticker, StatisticalInvarianceAgent.analyze, clean_ticker)
            future_mom = executor.submit(cls._safe_execute_node, "08_momentum", clean_ticker, MomentumVectorAgent.analyze, clean_ticker)
            future_sentry = executor.submit(cls._safe_execute_node, "09_visual_sentry", clean_ticker, VisualSentryAgent.analyze, clean_ticker)
            future_money = executor.submit(cls._safe_execute_node, "10_smart_money", clean_ticker, SmartMoneyAgent.analyze, clean_ticker)
            future_timeframe = executor.submit(cls._safe_execute_node, "11_timeframe", clean_ticker, TimeframeMatrixAgent.analyze, clean_ticker)
            future_fund = executor.submit(cls._safe_execute_node, "12_fundamentals", clean_ticker, CorporateFundamentalsAgent.evaluate, clean_ticker)
            future_sec = executor.submit(cls._safe_execute_node, "13_sec_watchdog", clean_ticker, SECWatchdogAgent.evaluate, clean_ticker)
            future_sector = executor.submit(cls._safe_execute_node, "14_sector_rotation", clean_ticker, SectorRotationAgent.evaluate, clean_ticker)
            future_macro = executor.submit(cls._safe_execute_node, "15_macro", clean_ticker, MacroEnvironmentAgent.evaluate, clean_ticker)
            future_sent = executor.submit(cls._safe_execute_node, "16_sentiment", clean_ticker, SentimentHarvesterAgent.harvest, clean_ticker)
            future_risk = executor.submit(cls._safe_execute_node, "02_risk", clean_ticker, PortfolioGuardAgent.calculate_stops, clean_ticker)

            # Collect GPU Predictive Results with timeout
            try:
                res_timesfm = future_tfm.result(timeout=cls.NODE_TIMEOUT_SECONDS)
            except Exception:
                res_timesfm = {"status": "FAILED", "directional_bias": "NEUTRAL", "confidence_score": 50.0, "spot_price": 0.0, "metrics": {"forecast_delta_pct": 0.0, "opacity_penalty": True}}

            try:
                res_chronos = future_chr.result(timeout=cls.NODE_TIMEOUT_SECONDS)
            except Exception:
                res_chronos = {"status": "FAILED", "directional_bias": "NEUTRAL", "confidence_score": 50.0, "spot_price": 0.0, "metrics": {"forecast_delta_pct": 0.0, "opacity_penalty": True}}

            # Collect Analytical Worker Results
            analytical_futures = [
                future_stat, future_mom, future_sentry, future_money, future_timeframe,
                future_fund, future_sec, future_sector, future_macro, future_sent, future_risk
            ]

            payload_map: Dict[str, AgentExecutionPayload] = {}
            for fut in as_completed(analytical_futures, timeout=cls.NODE_TIMEOUT_SECONDS + 2.0):
                try:
                    k, payload = fut.result()
                    payload_map[k] = payload
                except Exception as err:
                    logger.warning(f"Future collection error: {err}")

        # Fallback mappings if any specific future failed collection
        p_stat = payload_map.get("07_stat_invariance") or StatisticalInvarianceAgent.analyze(clean_ticker)
        p_mom = payload_map.get("08_momentum") or MomentumVectorAgent.analyze(clean_ticker)
        p_sentry = payload_map.get("09_visual_sentry") or VisualSentryAgent.analyze(clean_ticker)
        p_money = payload_map.get("10_smart_money") or SmartMoneyAgent.analyze(clean_ticker)
        p_timeframe = payload_map.get("11_timeframe") or TimeframeMatrixAgent.analyze(clean_ticker)
        p_fund = payload_map.get("12_fundamentals") or CorporateFundamentalsAgent.evaluate(clean_ticker)
        p_sec = payload_map.get("13_sec_watchdog") or SECWatchdogAgent.evaluate(clean_ticker)
        p_sector = payload_map.get("14_sector_rotation") or SectorRotationAgent.evaluate(clean_ticker)
        p_macro = payload_map.get("15_macro") or MacroEnvironmentAgent.evaluate(clean_ticker)
        p_sent = payload_map.get("16_sentiment") or SentimentHarvesterAgent.harvest(clean_ticker)
        p_risk = payload_map.get("02_risk") or PortfolioGuardAgent.calculate_stops(clean_ticker)

        spot = res_timesfm.get("spot_price") or res_chronos.get("spot_price") or p_sentry.spot_price

        # 2. Predictive Dual-Model Divergence Resolution
        t_ok = res_timesfm.get("status") == "SUCCESS" and not res_timesfm.get("metrics", {}).get("opacity_penalty")
        c_ok = res_chronos.get("status") == "SUCCESS" and not res_chronos.get("metrics", {}).get("opacity_penalty")

        t_delta = res_timesfm.get("metrics", {}).get("forecast_delta_pct", 0.0) if t_ok else 0.0
        c_delta = res_chronos.get("metrics", {}).get("forecast_delta_pct", 0.0) if c_ok else 0.0
        pred_spread = round(t_delta - c_delta, 2) if (t_ok and c_ok) else (t_delta if t_ok else c_delta)
        
        t_bias = res_timesfm.get("directional_bias", "NEUTRAL")
        c_bias = res_chronos.get("directional_bias", "NEUTRAL")

        if t_ok and c_ok:
            is_pred_conflict = (t_bias != c_bias) or (abs(pred_spread) > 1.5)
            pred_regime = "CONFLICTING_REGIME" if is_pred_conflict else "CONVERGENT_REGIME"
        else:
            is_pred_conflict = False
            pred_regime = "SINGLE_MODEL_OPACITY" if (t_ok or c_ok) else "PREDICTIVE_BLINDSPOT"

        # 3. Weighted Confluence Vote Engine
        bull_weight, bear_weight, total_weight = 0.0, 0.0, 0.0
        vote_table: Dict[str, Dict[str, Any]] = {}

        # Ingest Predictive Payloads
        for key, res, is_valid in [("06a_timesfm", res_timesfm, t_ok), ("06b_chronos", res_chronos, c_ok)]:
            if not is_valid:
                vote_table[key] = {
                    "bias": "NEUTRAL",
                    "confidence": 50.0,
                    "effective_weight": 0.0,
                    "metrics": res.get("metrics", {"opacity_penalty": True})
                }
                continue

            base_conf = float(res.get("confidence_score", 80.0))
            raw_conf = max(10.0, min(100.0, float(dynamic_weights.get(key, base_conf))))
            discount = 0.80 if is_pred_conflict else 1.0
            eff_wt = raw_conf * discount
            total_weight += eff_wt
            bias_val = res.get("directional_bias", "NEUTRAL")
            if bias_val == "BULLISH":
                bull_weight += eff_wt
            elif bias_val == "BEARISH":
                bear_weight += eff_wt
            vote_table[key] = {
                "bias": bias_val,
                "confidence": raw_conf,
                "effective_weight": round(eff_wt, 2),
                "metrics": res.get("metrics", {})
            }

        # Ingest Standard Analytical Nodes
        standard_map = {
            "07_stat_invariance": p_stat, "08_momentum": p_mom, "09_visual_sentry": p_sentry,
            "10_smart_money": p_money, "11_timeframe": p_timeframe, "12_fundamentals": p_fund,
            "13_sec_watchdog": p_sec, "14_sector_rotation": p_sector, "15_macro": p_macro, "16_sentiment": p_sent
        }

        for key, p in standard_map.items():
            if p.status != ExecutionStatus.SUCCESS or p.metrics.get("opacity_penalty"):
                vote_table[key] = {
                    "bias": p.directional_bias.value if p.status == ExecutionStatus.SUCCESS else "NEUTRAL",
                    "confidence": p.confidence_score,
                    "effective_weight": 0.0,
                    "metrics": p.metrics
                }
                continue

            base_conf = float(p.confidence_score)
            raw_conf = max(10.0, min(100.0, float(dynamic_weights.get(key, base_conf))))
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
                "bias": p.directional_bias.value,
                "confidence": raw_conf,
                "effective_weight": round(eff_wt, 2),
                "metrics": p.metrics
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

        # 4. Record live forecast batch to SQLite DAG for future settlement
        record_forecast_batch(clean_ticker, spot, vote_table, horizon_bars=16)

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
