"""
Pierre Quant Agents Package
===========================
Exports TimesFMAgent (cuda:0), KronosAgent (cuda:1), Sentry Nodes 01-16 evaluators,
and live API quote ingestion.
"""

from pierre_quant.agents.timesfm_agent import TimesFMAgent
from pierre_quant.agents.chronos_agent import ChronosAgent
from pierre_quant.agents.kronos_agent import KronosAgent
from pierre_quant.agents.live_api_ingestion import (
    fetch_live_quote,
    verify_live_price_boundary,
)
from pierre_quant.agents.sentry_nodes import (
    evaluate_risk_guard,
    evaluate_momentum_vector,
    evaluate_sec_watchdog,
    evaluate_stat_invariance,
)

__all__ = [
    "TimesFMAgent",
    "ChronosAgent",
    "KronosAgent",
    "fetch_live_quote",
    "verify_live_price_boundary",
    "evaluate_risk_guard",
    "evaluate_momentum_vector",
    "evaluate_sec_watchdog",
    "evaluate_stat_invariance",
]
