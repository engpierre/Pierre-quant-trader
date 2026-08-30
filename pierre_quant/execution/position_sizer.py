"""
pierre_quant/execution/position_sizer.py
Fractional Kelly and dynamic ATR risk-budget allocation engine.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class SizingBracket:
    ticker: str
    target_shares: int
    dollar_allocation: float
    risk_stop_floor: float
    max_capital_loss: float
    kelly_fraction: float
    execution_verdict: str


class PositionSizer:
    MAX_PORTFOLIO_RISK_PCT = 0.02  # Max 2% loss of total book per trade
    MAX_POSITION_CAP_PCT = 0.15    # Max 15% capital in single stock
    KELLY_SHRINKAGE = 0.35         # Fractional Kelly scalar

    @classmethod
    def calculate_sizing(
        cls,
        ticker: str,
        spot_price: float,
        confluence_score: float,
        atr_stop_floor: float,
        total_portfolio_cash: float,
        calibrated_confidence: float = 0.70
    ) -> SizingBracket:
        if confluence_score < 25.0 or spot_price <= 0 or atr_stop_floor >= spot_price:
            return SizingBracket(
                ticker=ticker,
                target_shares=0,
                dollar_allocation=0.0,
                risk_stop_floor=atr_stop_floor,
                max_capital_loss=0.0,
                kelly_fraction=0.0,
                execution_verdict="REJECT_INSUFFICIENT_CONFLUENCE"
            )

        # 1. Calculate Per-Share Risk
        per_share_risk = spot_price - atr_stop_floor
        dollar_risk_cap = total_portfolio_cash * cls.MAX_PORTFOLIO_RISK_PCT

        # 2. Compute Fractional Kelly
        # Expected return approx: 2x risk envelope
        b = 2.0
        p = calibrated_confidence
        q = 1.0 - p
        raw_kelly = max(0.0, (p * b - q) / b)
        kelly_fraction = min(raw_kelly * cls.KELLY_SHRINKAGE, cls.MAX_POSITION_CAP_PCT)

        # 3. Share sizing bound by risk budget and max capital cap
        max_shares_by_risk = int(dollar_risk_cap / per_share_risk) if per_share_risk > 0 else 0
        max_shares_by_cap = int((total_portfolio_cash * kelly_fraction) / spot_price)
        final_shares = max(0, min(max_shares_by_risk, max_shares_by_cap))

        final_dollar_cost = round(final_shares * spot_price, 2)
        total_risk_loss = round(final_shares * per_share_risk, 2)

        return SizingBracket(
            ticker=ticker,
            target_shares=final_shares,
            dollar_allocation=final_dollar_cost,
            risk_stop_floor=round(atr_stop_floor, 2),
            max_capital_loss=total_risk_loss,
            kelly_fraction=round(kelly_fraction, 4),
            execution_verdict="APPROVED_ACCUMULATE" if final_shares > 0 else "REJECT_RISK_CAP_EXCEEDED"
        )
