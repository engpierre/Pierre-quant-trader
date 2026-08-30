"""
pierre_quant/execution/circuit_breaker.py
Pre-execution circuit breakers and risk validation gates.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True, frozen=True)
class CircuitBreakerStatus:
    is_halted: bool
    halt_reason: str
    gate_name: str


class ExecutionCircuitBreaker:
    MAX_DAILY_DRAWDOWN_PCT = 0.03  # Max 3.0% daily loss before halt
    MAX_SPREAD_TOLERANCE_PCT = 0.0035  # Max 0.35% bid/ask spread
    MAX_PREDICTIVE_CONFLICT_SPREAD = 1.5  # Max 1.5% delta divergence

    @classmethod
    def validate_pre_trade(
        cls,
        portfolio_daily_pnl_pct: float,
        predictive_spread_pct: float,
        predictive_regime: str,
        bid_ask_spread_pct: float = 0.0010,
        has_opacity_penalty: bool = False,
    ) -> CircuitBreakerStatus:
        # Gate 1: Max Daily Drawdown
        if portfolio_daily_pnl_pct <= -cls.MAX_DAILY_DRAWDOWN_PCT:
            return CircuitBreakerStatus(
                is_halted=True,
                halt_reason=f"Daily drawdown limit exceeded ({portfolio_daily_pnl_pct * 100:.2f}% <= -3.00%)",
                gate_name="GATE_1_DAILY_DRAWDOWN"
            )

        # Gate 2: Predictive Conflict Gate
        if predictive_regime == "CONFLICTING_REGIME" and abs(predictive_spread_pct) > cls.MAX_PREDICTIVE_CONFLICT_SPREAD:
            return CircuitBreakerStatus(
                is_halted=True,
                halt_reason=f"Neural predictive spread divergence critical ({predictive_spread_pct:+.2f}% > ±1.50%)",
                gate_name="GATE_2_PREDICTIVE_CONFLICT"
            )

        # Gate 3: Spread & Liquidity Gate
        if bid_ask_spread_pct > cls.MAX_SPREAD_TOLERANCE_PCT:
            return CircuitBreakerStatus(
                is_halted=True,
                halt_reason=f"Excessive market bid/ask spread ({bid_ask_spread_pct * 100:.2f}% > 0.35%)",
                gate_name="GATE_3_LIQUIDITY_SPREAD"
            )

        # Gate 4: Data Opacity Gate
        if has_opacity_penalty:
            return CircuitBreakerStatus(
                is_halted=True,
                halt_reason="Data opacity penalty active on primary feed",
                gate_name="GATE_4_DATA_OPACITY"
            )

        return CircuitBreakerStatus(
            is_halted=False,
            halt_reason="All pre-trade gates clear",
            gate_name="NONE"
        )
