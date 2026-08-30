"""
Pierre Quant Supervisor: Predictive Intelligence Dossier Synthesizer
===================================================================
Standardized to render the 5-section Target Deep-Dive Dossier across all 16 Specialist Nodes.
"""
from typing import Dict, Any, Optional
from pierre_quant.core.contracts import SubAgentForecastReport, PriceVerificationPayload
from pierre_quant.orchestration.supervisor import SupervisorOrchestrator


def generate_recon_markdown(
    ticker: str,
    price: float = 0.0,
    recon_res: Optional[Dict[str, Any]] = None,
    timesfm_report: Optional[SubAgentForecastReport] = None,
    kronos_report: Optional[SubAgentForecastReport] = None,
    source: str = "TRADINGVIEW_LIVE",
    verification: Optional[PriceVerificationPayload] = None,
    atr: float = 0.45,
    sigma: float = 1.45,
) -> str:
    """Renders comprehensive 5-section Target Deep-Dive Dossier using SupervisorOrchestrator."""
    clean_ticker = ticker.strip().upper().lstrip("$")
    res = SupervisorOrchestrator.synthesize(clean_ticker)

    lines = [
        f"# 🎯 Target Deep-Dive Dossier: ${res.ticker}\n",
        "### 1. Target Symbol & Spot Price",
        f"* **Symbol:** `{res.ticker}`",
        f"* **Spot Price:** `${res.spot_price:.2f}`\n",
        "---",
        "### 2. Consensus Bias & Predictive Regime",
        f"* **Consensus Bias:** `{res.consensus_bias.value}`",
        f"* **Confluence Score:** `{res.net_confluence_score:+5.2f}%`",
        f"* **Dual-Predictive Spread Regime:** `{res.predictive_spread_pct:+5.2f}%` ({res.predictive_regime})",
        f"* **Action Directive:** **`{res.action_directive}`**\n",
        "---",
        "### 3. Quant & Structural Vectors",
        "| Agent | Bias | Raw Conf | Eff Wt | Key Metric Summary |",
        "| :--- | :--- | :--- | :--- | :--- |"
    ]

    for node, data in res.vote_breakdown.items():
        metrics_clean = str(data.get("metrics", {}))[:55].replace("|", "/")
        lines.append(
            f"| **{node}** | `{data['bias']}` | {data['confidence']:.1f}% | {data['effective_weight']:.1f} | `{metrics_clean}` |"
        )

    lines.extend([
        "\n---",
        "### 4. Dynamic Invalidation Floor (Agent 02)",
        f"* **🛡️ Risk Stop Floor (ATR):** `${res.risk_invalidation_floor:.2f}`\n"
    ])

    return "\n".join(lines)


def format_predictive_intelligence_dossier(
    ticker: str,
    timesfm_report: SubAgentForecastReport,
    kronos_report: SubAgentForecastReport,
) -> str:
    """Formats predictive cross-examination between TimesFM and Chronos/Kronos engines."""
    return generate_recon_markdown(ticker=ticker)
