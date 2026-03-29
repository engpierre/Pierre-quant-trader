# 🚀 Google Anti-gravity

**Google Anti-gravity** is an advanced, autonomous algorithmic quantitative research desk. By leveraging a multi-agent AI framework powered natively by Google Generative AI (Gemini), the system continuously monitors, synthesizes, and evaluates market data across multiple critical dimensions—technicals, fundamentals, sentiment, and dark pool integrity—to generate high-conviction, mathematically structured trading signals.

---

## ⚡ Features

- **Multi-Agent Swarm Intelligence**: Five specialized autonomous agents analyzing distinct market data pillars.
- **Master Synthesizer (Supervisor)**: Automatically aggregates raw data from the sub-agents and uses `gemini-2.5-flash` to identify strict alignment logic (e.g., correlating VIX fear spikes with Technical Bullish Divergences and C-Suite Accumulation).
- **Mobile-Optimized Dashboard**: A clean, highly responsive Streamlit UI built with collapsible metric grids and a bold 'Hero' container layout.
- **Dynamic Charting**: Capable of integrating real-time price action visualizations and momentum trajectory graphics directly onto the dashboard.
- **Alternative Data Rules Protocol**: Enforces quantitative mechanics like ATR-based stops and Mansfield Relative Strength—ignoring "vibes" in favor of strict empirical data points.

---

## 🏗️ Architecture

The algorithmic framework relies on a decentralized, modular python agent hierarchy:

1. **Supervisor Agent (`supervisor_agent.py`)**: The overarching Natural Language orchestrator. It extracts natural language tickers from human queries, triggers the underlying swarm, and outputs the final Buy/Sell/Neutral confidence score matrix across the desk.
2. **Insider Agent (`insider_agent.py`)**: Acts as the Master Synthesizer. Synchronously correlates all analytical findings into a final "High-Conviction" internal logic flow.
3. **Fundamental Agent (`fundamental_agent.py`)**: Connects to financial endpoints and OpenInsider to scrape Trailing P/E, Margins, and specific 60-day C-Suite Form 4 Accumulation metrics.
4. **Sentiment Agent (`sentiment_agent.py`)**: Queries `yfinance` to monitor Macro Fear/Panic surges (Tracking VIX > 10% movement anomalies) and parses retail narrative shifts.
5. **Technical Agent (`technical_agent.py`)**: Mathematically tracks Bullish Divergences (Price / RSI lower-low disparities) and custom Volume Anomalies (>200% over the 20 SMA).
6. **Fetch.AI Agent (`fetch_ai_agent.py`)**: A transport-layer connecting block to query decentralized external agent networks for independent macro consensus (e.g., cross-referencing systemic risk anomalies before finalizing trades).

---

## 🚦 Getting Started

### Prerequisites
- Python 3.10+
- A valid Google Gemini API Key
- *(Optional)* Fetch.AI `uAgent` Network hook Endpoint

### Installation
Install the necessary quantitative backend packages and the Streamlit frontend:

```bash
pip install streamlit google-generativeai requests beautifulsoup4 praw yfinance pandas numpy
```

### Environment Setup
You must initialize your system variables before running the quantitative desk:
```powershell
$env:GEMINI_API_KEY="your-gemini-key-here"
$env:FETCH_AI_ENDPOINT="http://your-fetch-endpoint:8000/consensus" # Optional
```

---

## 💻 Usage

To launch the centralized visual dashboard locally:

```bash
streamlit run app.py
```

This command will initialize the local server and instantly open the user interface in your default browser. 

1. **Input Ticker**: Type "AAPL", "TSLA", or any valid stock ticker into the centralized prompt box.
2. **Execute**: Tap **"Run Supervisor Audit"** to initiate the multi-agent swarm.
3. **Review**: The master trade recommendation will display dynamically in the core Hero window. To drill down into the logic forming that specific signal, tap any of the expandable accordions (e.g., *Technical Analysis* or *VIX Macro*) to reveal the raw underlying data blocks.
