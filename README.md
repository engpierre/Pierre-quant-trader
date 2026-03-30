# 🚀 Google Anti-gravity

**Google Anti-gravity** is an advanced, autonomous algorithmic quantitative research desk. By leveraging a multi-agent AI framework powered natively by Google Generative AI (Gemini), the system continuously monitors, synthesizes, and evaluates market data across multiple critical dimensions—technicals, fundamentals, sentiment, and dark pool integrity—to generate high-conviction, mathematically structured trading signals.

---

## ⚡ Features

- **Dual-Mode Discovery Engine**: The system can operate Reactively (scanning a user-provided ticker) or Proactively (using mathematical Mansfield Relative Strength to autonomously scan the S&P 100 proxy for high-conviction breakouts).
- **Multi-Agent Adversarial Swarm**: Eight specialized tracking nodes analyzing strict fundamental, technical, and alternative data pillars.
- **Master Synthesizer (Judicial Loop)**: Instead of a flat aggregator, the orchestrator triggers an adversarial sequence: constructing a Bull case via the internal swarm, then immediately forcing a specialized Critic Agent to ruthlessly attack the thesis before issuing a final output.
- **Mobile-First 'War Room' Dashboard**: A robust Streamlit UI separating the backend's internal logic into explicit 'Bull vs. Bear' `st.tabs` to eliminate cognitive confirmation bias.
- **Dynamic Charting**: Capable of integrating real-time price action visualizations and momentum trajectory graphics directly onto the dashboard.
- **Alternative Data Rules Protocol**: Enforces quantitative mechanics like ATR-based stops and Mansfield Relative Strength—ignoring "vibes" in favor of strict empirical data points.

---

## 🏗️ Architecture

The algorithmic framework relies on a decentralized, modular python agent hierarchy:

1. **Scout Agent (`discovery_engine.py`)**: The Proactive Scanner. Utilizing `pandas` and `yfinance`, it mathematically models subsets against a SPY benchmark to isolate explosive breakouts via Mansfield Relative Strength ($MRS$).
2. **Supervisor Agent (`supervisor_agent.py`)**: The overarching Natural Language judge. It triggers the continuous 3-phase execution loop: `(Swarm Phase -> Critic Attack Phase -> Judicial Master Synthesis)`, outputting the ultimate decision via dynamically generated JSON.
3. **Critic Agent (`critic_agent.py`)**: The Adversarial Auditor. Deployed explicitly to hunt for "Alpha Hallucination" by identifying structural weaknesses, Bear traps, and Volume Expansions inside the broader Swarm's reports.
4. **Whale-Watcher Agent (`whale_agent.py`)**: The "Smart Money" aggregator. Integrates with premium API networks (FMP, Quiver Quant, FRED) to chart Dark Pool block trades, Congressional sweeps, and overarching macro liquidity conditions.
5. **Fundamental Agent (`fundamental_agent.py`)**: Scrapes trailing P/E, institutional margins, and aggressive C-Suite Form 4 Accumulation trackers.
6. **Sentiment Agent (`sentiment_agent.py`)**: Queries live networks to monitor extreme macroeconomic panic surges (e.g. VIX spikes > 10%).
7. **Technical Agent (`technical_agent.py`)**: Mathematically targets specific Price vs. RSI disparities while tracking custom volatility volume anomalies (>200% over 20 SMA).
8. **Fetch.AI Agent (`fetch_ai_agent.py`)**: Operating natively as a hyper-fast localized quantitative oracle tracking basic real-time market data ticks.

---

## 🚦 Getting Started

### Prerequisites
- Python 3.10+
- A valid Google Gemini API Key
- *(Optional)* Fetch.AI `uAgent` Network hook Endpoint

### Installation
Install the necessary quantitative backend packages and the Streamlit frontend:

```bash
pip install streamlit google-generativeai requests beautifulsoup4 praw yfinance pandas numpy fredapi
```

### Environment Setup
You must initialize your Google Generative AI API Key before running the quantitative desk:
```powershell
$env:GEMINI_API_KEY="your-gemini-key-here"
```
*(Note: As of recent architectural shifts, the external Fetch.AI consensus endpoint is no longer required due to the direct local yfinance oracle migration.)*

---

## 💻 Usage

To launch the centralized visual dashboard locally:

```bash
streamlit run app.py
```

This command will initialize the local server and instantly open the user interface in your default browser. 

1. **Command Center Toggle**: The dashboard features an active sidebar to shift operational states.
2. **Manual Audit (Reactive)**: Type any stock ticker and hit Execute to instantly spin up the 8-node swarm targeted precisely at your request.
3. **Autonomous Recon (Proactive)**: Discard manual input. The app will autonomously boot the Scout Agent, calculate $MRS$ mathematical rankings across the S&P proxy universe, and pipeline the Top 3 targets directly into independent Swarm Courtrooms.
4. **Review**: Regardless of mode, the UI traps the user in a "Bull-vs-Bear" mental model utilizing mobile-optimized `st.tabs()`. You toggle between the Swarm's baseline thesis and the Critic's hostile rebuttal before concluding with the Master Verdict permanently secured at the bottom.
