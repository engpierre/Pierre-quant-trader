"""
Pierre Quant Runners Package
============================
Orchestrators and execution harnesses for Division III predictive swarms and Sentry Recon.
Decoupled from eager web framework dependencies.
"""

from pierre_quant.runners.predictive_dispatcher import (
    PredictiveDispatcher,
    execute_dual_forecast,
    build_sentry_dossier,
    get_predictive_dispatcher,
)

__all__ = [
    "PredictiveDispatcher",
    "execute_dual_forecast",
    "build_sentry_dossier",
    "get_predictive_dispatcher",
]
