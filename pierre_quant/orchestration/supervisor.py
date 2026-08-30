"""
pierre_quant/orchestration/supervisor.py
Agent 01 (Supervisor Orchestrator Worker) - Master Multi-Agent Confluence Engine.
"""
from __future__ import annotations
import argparse
import json
import logging
import sys
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict

# Force UTF-8 output on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pierre_quant.core.agent_contract import (
    AgentExecutionPayload, DirectionalBias, ExecutionStatus
)
from pierre_quant.models.timesfm_engine import TimesFMForecastingAgent
from pierre_quant.models.chronos_engine import ChronosForecastingAgent
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
    def synthesize(cls, ticker: str) -> SupervisorSynthesisResult:
        clean_ticker = ticker.strip().upper().lstrip("$")

        # 1. Execute Unified Analytical Pipeline (Divisions III–V)
        p_timesfm = TimesFMForecastingAgent.forecast(clean_ticker)
        p_chronos = ChronosForecastingAgent.forecast(clean_ticker)
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

        payload_map: Dict[str, AgentExecutionPayload] = {
            "06a_timesfm": p_timesfm,
            "06b_chronos": p_chronos,
            "07_stat_invariance": p_stat,
            "08_momentum": p_mom,
            "09_visual_sentry": p_sentry,
            "10_smart_money": p_money,
            "11_timeframe": p_timeframe,
            "12_fundamentals": p_fund,
            "13_sec_watchdog": p_sec,
            "14_sector_rotation": p_sector,
            "15_macro": p_macro,
            "16_sentiment": p_sent,
        }

        spot = p_timesfm.spot_price if p_timesfm.spot_price > 0 else p_sentry.spot_price

        # 2. Predictive Dual-Model Divergence Resolution
        t_delta = p_timesfm.metrics.get("forecast_delta_pct", 0.0)
        c_delta = p_chronos.metrics.get("forecast_delta_pct", 0.0)
        pred_spread = round(t_delta - c_delta, 2)
        
        is_pred_conflict = (p_timesfm.directional_bias != p_chronos.directional_bias) or (abs(pred_spread) > 1.5)
        pred_regime = "CONFLICTING_REGIME" if is_pred_conflict else "CONVERGENT_REGIME"

        # 3. Weighted Confluence Vote Engine
        bull_weight, bear_weight, total_weight = 0.0, 0.0, 0.0
        vote_table: Dict[str, Dict[str, Any]] = {}

        for key, p in payload_map.items():
            if p.status != ExecutionStatus.SUCCESS:
                continue

            raw_conf = p.confidence_score
            discount = 1.0

            # Rule: 20% haircut for predictive divergence
            if key in ("06a_timesfm", "06b_chronos") and is_pred_conflict:
                discount *= 0.80

            # Rule: 50% discount for retail sentiment counter to institutional flow
            if key == "16_sentiment" and p_money.directional_bias == DirectionalBias.BEARISH and p.directional_bias == DirectionalBias.BULLISH:
                discount *= 0.50

            effective_weight = raw_conf * discount
            total_weight += effective_weight

            if p.directional_bias == DirectionalBias.BULLISH:
                bull_weight += effective_weight
            elif p.directional_bias == DirectionalBias.BEARISH:
                bear_weight += effective_weight

            vote_table[key] = {
                "bias": p.directional_bias.value,
                "confidence": raw_conf,
                "effective_weight": round(effective_weight, 2),
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

        invalidation_floor = p_risk.metrics.get("proposed_stop", p_sentry.metrics.get("nearest_support", 0.0))

        return SupervisorSynthesisResult(
            ticker=clean_ticker,
            spot_price=spot,
            consensus_bias=consensus,
            net_confluence_score=net_confluence,
            predictive_spread_pct=pred_spread,
            predictive_regime=pred_regime,
            risk_invalidation_floor=invalidation_floor,
            vote_breakdown=vote_table,
            action_directive=directive
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent 01: Supervisor Master Harness CLI")
    parser.add_argument("--ticker", required=True, help="Ticker symbol to synthesize")
    parser.add_argument("--json", action="store_true", help="Output pure JSON")
    args = parser.parse_args()

    result = SupervisorOrchestrator.synthesize(args.ticker)
    
    if args.json:
        print(json.dumps({
            "ticker": result.ticker,
            "spot_price": result.spot_price,
            "consensus_bias": result.consensus_bias.value,
            "net_confluence_score": result.net_confluence_score,
            "predictive_spread_pct": result.predictive_spread_pct,
            "predictive_regime": result.predictive_regime,
            "risk_invalidation_floor": result.risk_invalidation_floor,
            "action_directive": result.action_directive,
            "vote_breakdown": result.vote_breakdown
        }))
    else:
        print(f"\n" + "=" * 80)
        print(f"🛡️ PIERRE QUANT :: SUPERVISOR SYNTHESIS DOSSIER ({result.ticker})")
        print(f"=" * 80)
        print(f"Spot Price: ${result.spot_price:.2f} | Consensus: {result.consensus_bias.value} | Confluence: {result.net_confluence_score:+5.2f}%")
        print(f"Dual-Predictive Spread: {result.predictive_spread_pct:+5.2f}% ({result.predictive_regime}) | Stop Floor: ${result.risk_invalidation_floor:.2f}")
        print(f"Action Directive: {result.action_directive}")
        print(f"-" * 80)
        print(f"{'Node ID':<22} | {'Bias':<8} | {'Conf':<5} | {'Weight':<6} | Key Metric Summary")
        print(f"-" * 80)
        for node, data in result.vote_breakdown.items():
            print(f"{node:<22} | {data['bias']:<8} | {data['confidence']:<5.1f} | {data['effective_weight']:<6.1f} | {str(data['metrics'])[:45]}")
        print(f"=" * 80 + "\n")
