"""
pierre_quant/models/chronos_engine.py
Agent 06b: Amazon Chronos-Bolt Forecasting Worker (cuda:1 / optimized runtime).
"""
from __future__ import annotations
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pierre_quant.forecasting.chronos_agent import (
    ChronosForecastingAgent, main as chronos_main
)

if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Agent 06b: Chronos-Bolt Forecasting Worker CLI")
    parser.add_argument("--ticker", type=str, required=True, help="Holding symbol to forecast")
    parser.add_argument("--period", type=str, default="6mo", help="Lookback period")
    parser.add_argument("--json", action="store_true", help="Output pure JSON")
    args = parser.parse_args()

    payload = ChronosForecastingAgent.forecast(args.ticker, period=args.period)

    if args.json:
        out = {
            "agent_id": payload.agent_id,
            "ticker": payload.ticker,
            "status": payload.status.value,
            "directional_bias": payload.directional_bias.value,
            "confidence_score": payload.confidence_score,
            "spot_price": payload.spot_price,
            "metrics": payload.metrics,
            "error_message": payload.error_message
        }
        print(json.dumps(out))
    else:
        print(f"Holding: {payload.ticker:<8} | Status: {payload.status.value:<7} | Spot: ${payload.spot_price:<9.2f} | End:${payload.metrics.get('terminal_price', 0):<9.2f} (Δ={payload.metrics.get('forecast_delta_pct', 0)}%) | Bias: {payload.directional_bias.value:<7} | Device: {payload.metrics.get('device', 'N/A')}")
