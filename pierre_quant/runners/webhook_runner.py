"""
Pierre Quant Webhook Runner
===========================
Executes concurrent Division III dual-model evaluations (TimesFM & Kronos)
via asyncio.gather upon incoming authenticated TradingView Pro Webhooks.
"""

import asyncio
from fastapi import FastAPI, HTTPException, Header
import pandas as pd
from pierre_quant.core.integrity import verify_hmac_signature
from pierre_quant.agents.timesfm_agent import TimesFMAgent
from pierre_quant.agents.kronos_agent import KronosAgent
from pierre_quant.supervisor.synthesizer import format_predictive_intelligence_dossier

app = FastAPI(title="Pierre Quant Webhook Orchestrator", version="1.0.0")
agent_timesfm = TimesFMAgent(device="cuda:0")
agent_kronos = KronosAgent(device="cuda:1")


@app.post("/api/v1/tradingview-webhook")
async def handle_tradingview_webhook(payload: dict, x_signature: str = Header(...)):
    if not verify_hmac_signature(payload, x_signature):
        raise HTTPException(status_code=401, detail="Attestation Signature Mismatch")

    ticker: str = payload["ticker"]
    df = pd.DataFrame(payload["bars"])
    df["timestamps"] = pd.to_datetime(df["timestamps"])
    df.set_index("timestamps", inplace=True)

    loop = asyncio.get_running_loop()
    timesfm_task = loop.run_in_executor(None, agent_timesfm.evaluate, ticker, df)
    kronos_task = loop.run_in_executor(None, agent_kronos.evaluate, ticker, df)

    timesfm_report, kronos_report = await asyncio.gather(timesfm_task, kronos_task)
    report_md = format_predictive_intelligence_dossier(ticker, timesfm_report, kronos_report)

    return {"status": "SUCCESS", "report": report_md}
