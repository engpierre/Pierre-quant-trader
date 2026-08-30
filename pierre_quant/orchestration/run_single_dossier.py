"""
pierre_quant/orchestration/run_single_dossier.py
Direct CLI harness that generates and prints the pre-formatted Markdown Dossier.
"""
import argparse
import sys
from pathlib import Path

# Force UTF-8 output on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.platform == "win32" and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Environment setup
VENV_SITE_PACKAGES = Path(r"C:\Users\Pierre\.openclaw\workspace\Julie-Core\.venv\Lib\site-packages")
if VENV_SITE_PACKAGES.exists() and str(VENV_SITE_PACKAGES) not in sys.path:
    sys.path.insert(0, str(VENV_SITE_PACKAGES))

PROJECT_ROOT = Path(r"C:\Users\Pierre\.openclaw\workspace\pierre-quant")
if PROJECT_ROOT.exists() and str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pierre_quant.orchestration.supervisor import SupervisorOrchestrator


def main():
    parser = argparse.ArgumentParser(description="Generate Target Deep-Dive Dossier Markdown")
    parser.add_argument("--ticker", type=str, required=True, help="Ticker symbol to synthesize")
    args = parser.parse_args()

    res = SupervisorOrchestrator.synthesize(args.ticker)

    # Format Markdown directly in Python
    markdown_output = f"""# 🎯 Target Deep-Dive Dossier: ${res.ticker}

### 1. Target Symbol & Spot Price
* **Symbol:** `{res.ticker}`
* **Spot Price:** `${res.spot_price:.2f}`

---

### 2. Consensus Bias & Predictive Regime
* **Consensus Bias:** `{res.consensus_bias.value}`
* **Net Confluence Score:** `{res.net_confluence_score:+5.2f}%`
* **Dual-Predictive Spread Regime:** `{res.predictive_spread_pct:+5.2f}%` ({res.predictive_regime})
* **Action Directive:** **`{res.action_directive}`**

---

### 3. Quant & Structural Vectors
| Agent / Discipline | Bias Flag | Confidence | Effective Wt | Metric Summary |
| :--- | :--- | :--- | :--- | :--- |"""

    for node, data in res.vote_breakdown.items():
        metrics_str = str(data.get("metrics", {}))[:45].replace("|", "/")
        markdown_output += f"\n| **{node}** | `{data['bias']}` | {data['confidence']:.1f}% | {data['effective_weight']:.1f} | `{metrics_str}` |"

    markdown_output += f"""

---

### 4. Dynamic Invalidation Floor (Agent 02)
* **🛡️ Risk Stop Floor:** `${res.risk_invalidation_floor:.2f}`
"""

    print(markdown_output)


if __name__ == "__main__":
    main()
