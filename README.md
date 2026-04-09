# 🚀 Pierre Quant Agent (Anti-gravity)

**Pierre Quant Agent** is an advanced, autonomous algorithmic quantitative research desk engineered for cloud-capable AgentFi execution. By leveraging a multi-agent AI framework powered natively by Google Generative AI (Gemini), the system continuously monitors, synthesizes, and evaluates market data across multiple critical dimensions—technicals, fundamentals, sentiment, and dark pool integrity—to generate mathematically structured trading signals.

---

## ⚡ Features

- **Dual-Mode Discovery Engine**: The system can operate Reactively (scanning a user-provided ticker) or Proactively (using mathematical Mansfield Relative Strength to autonomously scan the S&P 100 proxy for high-conviction breakouts).
- **Multi-Agent Adversarial Swarm**: Eleven specially crafted tactical nodes analyzing strict fundamental, technical, geopolitical, and alternative data pillars.
- **Master Synthesizer (Judicial Loop)**: Instead of a flat aggregator, the orchestrator triggers an adversarial sequence: constructing a Bull case via the internal swarm, then immediately forcing a specialized Critic Agent to ruthlessly attack the thesis.
- **Backtest Validator (AAR Ledger)**: Eliminates static execution by introducing a persistent SQLite intelligence loop mapping every $T+24$ paper-trade performance directly against the system's historical verdicts.
- **Recursive Self-Optimization**: The Swarm acts as an independent learning organism. The CIO queries the SQLite AAR Database dynamically at runtime adjusting Node Trust Coefficients—mathematically amplifying the Adversarial Critic's veto weight if systemic LLM hallucinations drag the Win Rate below 50%.
- **Dynamic Regime Anchor**: The system natively calculates the overarching macroeconomic regime (Trending-Bull vs Volatile-Bear) using FRED Yield Curve / Asset grids, automatically scaling the Red Team's mathematical veto power based on structural vulnerability.
- **Algorithmic Covariance Locks**: The Proactive Scanner enforces strict Force Composition metrics natively discarding positively correlated ($R > 0.85$) targets to guarantee perfectly uncoupled Alpha.
- **High-Density 'War Room' Dashboard**: A completely re-engineered Streamlit UI utilizing 'Adaptive Wide' CSS container configurations, bespoke HTML metric bounds (`.quant-metric-box`), and an ultra-condensed Print Protocol for flawless 1-page PDF Executive board reporting.
- **AgentFi Cloud Architecture**: Completely containerized for decentralized smart-contract integration, exporting dynamic `Signal_Report_Intent.json` files while running dual-duty alongside an MCP-wrapped localized Ground Truth Oracle Server.
- **Alternative Data Rules Protocol**: Enforces quantitative mechanics like ATR-based stops and Mansfield Relative Strength—ignoring "vibes" in favor of strict empirical data points.

---

## 🏗️ Architecture

The algorithmic framework relies on a decentralized, modular python agent hierarchy:

1. **Scout Agent (`discovery_engine.py`)**: The Proactive Scanner. Mathematically models subsets against a SPY benchmark to isolate Top 10 explosive breakouts via Mansfield Relative Strength ($MRS$).
2. **Covariance Agent (`covariance_agent.py`)**: The Diversification Lock. Prevents structural exposure by forcing the Scout to re-roll and decouple highly correlated tickers ($R>0.85$) using 60-day Pearson iteration loops prior to CIO execution.
3. **Supervisor Agent (`supervisor_agent.py`)**: The overarching Natural Language judge. It triggers the continuous execution loop: `(Swarm Phase -> Geopolitical Interception -> Auditor Loop -> Critic Attack Phase -> Judicial Master Synthesis -> AAR Persistence Dump)`.
4. **Optimizer Engine (`optimizer_engine.py`)**: Calculates dynamic $Global Trust$ arrays querying standard accuracy directly injecting mathematical Red Team boosts into the System Prompt.
5. **Backtest Validator (`backtest_validator.py`)**: The ACID compliant overarching SQLite constructor defining the Mission Logs and Agent Attribution persistence ledgers.
6. **Critic Agent (`critic_agent.py`)**: The Adversarial Auditor. Deployed explicitly to hunt for "Alpha Hallucination" by identifying structural weaknesses, Bear traps, and Volume Expansions inside the broader Swarm's reports. Includes **BlackwellCritic**, a 4-bit quantized local transformer (`google/gemma-4-26b-A4B-it`) specifically optimized via `BitsAndBytesConfig` for execution on RTX 5060 Ti `sm_120` architectures.
7. **Geopolitical IPB Agent (`geopolitical_agent.py`)**: The Kinetic Friction Mapper. Calculates active supply chain chokepoints and physical trade vulnerabilities natively injecting 1.5x mathematical boosters into the Red Team if the global structure is deemed `VOLATILE`.
8. **Whale-Watcher Agent (`whale_agent.py`)**: The Intelligence Officer. Maps Dark Pool blocks, Congressional sweeps, and overarching macro regimes utilizing strictly mapped FRED Yield Curve hooks.
9. **Insider Integrity Auditor (`insider_agent.py`)**: The Logic Decoupler. Specifically isolates the Swarm payload hunting internal hallucination paradoxes natively.
10. **Fundamental Agent (`fundamental_agent.py`)**: Scrapes trailing P/E, institutional margins, while explicitly trapping incorrect Megacap Debt ratios natively via the Reality Anchor.
11. **Sentiment Agent (`sentiment_agent.py`)**: Queries live networks to monitor extreme retail panic surges (e.g. VIX spikes > 10%).
12. **Technical Agent (`technical_agent.py`)**: Mathematically targets specific Price vs. RSI disparities while generating native structural timestamp arrays halting temporal drift protocols.
13. **Fetch.AI Agent (`fetch_ai_agent.py`)**: Operating natively as a hyper-fast localized quantitative True Price Oracle.

---

## 🚦 Getting Started

### Prerequisites
- Python 3.10+
- A valid Google Gemini API Key
- *(Optional)* Fetch.AI `uAgent` Network hook Endpoint

### Installation
Install the necessary quantitative backend packages and the Streamlit frontend natively:

```bash
pip install streamlit google-generativeai requests beautifulsoup4 praw yfinance pandas numpy fredapi torch transformers bitsandbytes accelerate
```

*(Alternatively, the entire stack including the AAR SQLite ledger is containerized for AgentFi cloud deployments. Simply run `docker-compose up -d` to securely launch the persistent execution loop.)*

### Environment Setup
You must initialize your Google Generative AI API Key before running the quantitative desk:
```powershell
$env:GEMINI_API_KEY="your-gemini-key-here"
```
*(Note: As of recent architectural shifts, the Master Oracle relies on a localized yfinance Model Context Protocol payload.)*

---

## 💻 Usage

To launch the centralized visual dashboard locally:

```bash
streamlit run app.py
```

This command will initialize the local server and instantly open the user interface in your default browser. 

1. **Command Center Toggle**: The dashboard features an active sidebar mapping three explicit operational states.
2. **Manual Audit (Reactive)**: Type any stock ticker and hit Execute to instantly spin up the Swarm targeted precisely at your request.
3. **Autonomous Recon (Proactive)**: The app will autonomously boot the Scout Agent, calculate mathematical rankings across the S&P proxy universe, bypass standard Covariance correlations ($R>0.85$), and strictly pipeline structurally diversified targets directly into the Judicial Execution Courtrooms.
4. **AAR Ledger (Backtest)**: View the overarching Database persistence layers physically auditing recursive Self-Correction Trust algorithms mapping the Red Team's active override strength dynamically.
