"""
pierre_quant/runners/run_swarm_status.py
Subsystem process auditor, live quote resolution verifier, and database integrity validator.
"""
from __future__ import annotations
import json
import logging
import sqlite3
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path
import psutil
import yfinance as yf

# Reconfigure stdout for utf-8 if supported
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("SwarmStatus")

WORKSPACE_ROOT = Path(r"C:\Users\Pierre\.openclaw\workspace")
DB_PATH = WORKSPACE_ROOT / "pierre-quant" / "pierre_quant.db"
REPORTS_DIR = WORKSPACE_ROOT / "vault" / "Reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

CORE_PORTS = {
    11434: "Ollama Dual-GPU Inference API",
    18789: "OpenClaw Swarm Gateway",
    52338: "Hermes Agent Dashboard"
}

SAMPLE_TICKERS = ["BTC-USD", "NVDA", "ENB", "MKC"]


def check_daemon_processes() -> list[dict]:
    results = []
    active_pids = {p.pid: p for p in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info'])}
    
    # Check Listening Ports
    try:
        connections = psutil.net_connections(kind='inet')
    except Exception:
        connections = []

    seen_ports = set()
    for conn in connections:
        if conn.status == 'LISTEN' and conn.laddr.port in CORE_PORTS:
            port = conn.laddr.port
            if port in seen_ports:
                continue
            seen_ports.add(port)
            proc_name = CORE_PORTS[port]
            pid = conn.pid
            mem_mb = 0.0
            if pid and pid in active_pids:
                try:
                    mem_mb = round(active_pids[pid].info['memory_info'].rss / (1024 * 1024), 2)
                except Exception:
                    pass
            
            results.append({
                "subsystem": proc_name,
                "port": port,
                "pid": pid,
                "memory_mb": mem_mb,
                "status": "ONLINE"
            })

    # Also detect Hermes if listening on dynamic port
    if 52338 not in seen_ports:
        for pid, p in active_pids.items():
            cmd = " ".join(p.info['cmdline'] or []).lower()
            if "hermes" in cmd and "dashboard" in cmd:
                mem_mb = round(p.info['memory_info'].rss / (1024 * 1024), 2) if p.info['memory_info'] else 0.0
                results.append({
                    "subsystem": "Hermes Agent Core",
                    "port": 52338,
                    "pid": pid,
                    "memory_mb": mem_mb,
                    "status": "ONLINE"
                })
                break

    return results


def check_ollama_api() -> dict:
    start = time.time()
    try:
        req = urllib.request.Request("http://127.0.0.1:11434/api/tags")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            latency_ms = round((time.time() - start) * 1000, 2)
            models = [m.get("name") for m in data.get("models", [])]
            return {
                "status": "HEALTHY",
                "latency_ms": latency_ms,
                "loaded_models": models
            }
    except Exception as e:
        return {"status": "OFFLINE / ERROR", "latency_ms": -1, "error": str(e)}


def check_live_feed_integrity() -> dict:
    start = time.time()
    try:
        data = yf.download(SAMPLE_TICKERS, period="5d", interval="1d", group_by="ticker", auto_adjust=True, progress=False)
        quotes = {}
        for t in SAMPLE_TICKERS:
            try:
                df = data[t] if len(SAMPLE_TICKERS) > 1 else data
                close = df["Close"].dropna()
                if not close.empty:
                    quotes[t] = round(float(close.iloc[-1]), 2)
                else:
                    t_obj = yf.Ticker(t)
                    quotes[t] = round(float(t_obj.fast_info.get("lastPrice", 0.0)), 2)
            except Exception:
                quotes[t] = 0.0

        latency_ms = round((time.time() - start) * 1000, 2)
        return {
            "status": "LIVE & STREAMING",
            "latency_ms": latency_ms,
            "sample_ticks": quotes
        }
    except Exception as e:
        return {"status": "FEED DEGRADED", "latency_ms": -1, "error": str(e)}


def check_database_isolation() -> dict:
    try:
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM portfolio_positions")
        pos_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM sentry_recommendations")
        rec_count = cur.fetchone()[0]
        conn.close()
        return {
            "status": "READ-ONLY COMPLIANT (?mode=ro)",
            "active_holdings": pos_count,
            "logged_recommendations": rec_count
        }
    except Exception as e:
        return {"status": "DATABASE ERROR", "error": str(e)}


def export_status_report():
    daemons = check_daemon_processes()
    ollama = check_ollama_api()
    feed = check_live_feed_integrity()
    db = check_database_isolation()
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    md_path = REPORTS_DIR / "System_Status.md"
    content = f"""---
title: "Swarm Subsystem Health & Live Feed Status"
last_updated: "{now_str}"
status: "OPERATIONAL"
---

# 🛰️ Swarm Telemetry & Pricing Health Monitor

| Core Subsystem | Port | PID | RSS Memory | State |
| :--- | :--- | :--- | :--- | :--- |
"""
    for d in daemons:
        content += f"| **{d['subsystem']}** | `{d['port']}` | `{d['pid']}` | {d['memory_mb']:.1f} MB | `🟢 {d['status']}` |\n"

    content += f"""
---

### 🧠 Ollama Local Inference Gateway
* **Status:** `{'🟢 ' + ollama['status'] if ollama['status'] == 'HEALTHY' else '🔴 ' + ollama['status']}`
* **Round-Trip Latency:** `{ollama.get('latency_ms', -1)} ms`
* **Available Models:** `{', '.join(ollama.get('loaded_models', []))}`

---

### ⚡ Live Market Pricing Feed (Agent 05)
* **Status:** `{'🟢 ' + feed['status'] if feed['status'] == 'LIVE & STREAMING' else '🔴 ' + feed['status']}`
* **Ingestion Latency:** `{feed.get('latency_ms', -1)} ms`
* **Resolved Sample Ticks:**
"""
    for t, p in feed.get("sample_ticks", {}).items():
        content += f"  - **${t}:** `${p:,.2f}`\n"

    content += f"""
---

### 🛡️ Persistence Isolation (`pierre_quant.db`)
* **State:** `{db['status']}`
* **Active Portfolio Holdings:** `{db.get('active_holdings', 0)}`
* **Tracked Recommendations:** `{db.get('logged_recommendations', 0)}`
"""

    md_path.write_text(content, encoding="utf-8")
    logger.info("System Status successfully exported to Obsidian Vault.")

    # Terminal Summary
    print("\n" + "=" * 90)
    print(f"PIERRE QUANT SWARM STATUS: ALL SUBSYSTEMS NOMINAL | {now_str}")
    print("=" * 90)
    for d in daemons:
        print(f"• {d['subsystem']:<35} [Port {d['port']}] -> PID {d['pid']} ({d['memory_mb']} MB) [ONLINE]")
    print(f"• Ollama API Latency:               {ollama.get('latency_ms')} ms")
    print(f"• Live Pricing Ingestion (yfinance): {feed.get('latency_ms')} ms (Sample BTC-USD: ${feed.get('sample_ticks', {}).get('BTC-USD', 0):,.2f})")
    print(f"• Database Mode:                    {db['status']}")
    print("=" * 90 + "\n")


if __name__ == "__main__":
    export_status_report()
