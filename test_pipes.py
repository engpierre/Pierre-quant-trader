import asyncio
import json
import sys
import os

# Ensure the pierre-quant directory is in the path
sys.path.append(r"c:\Users\Pierre\.openclaw\workspace\pierre-quant")

from twelve_data_ingestor import fetch_technical_data
from tv_pull_agent import TVPullAgent

# Windows platform specific fix for asyncio
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def run_test():
    ticker = "GLW"
    print(f"--- Testing Twelve Data for {ticker} ---")
    td_result = await fetch_technical_data(ticker)
    print(json.dumps(td_result, indent=2))

    print(f"\n--- Testing TradingView for {ticker} ---")
    tv_agent = TVPullAgent(buffer_path=r'c:\Users\Pierre\.openclaw\workspace\pierre-quant\test_technical_buffer.json')
    tv_result = tv_agent.fetch_technicals(ticker)
    print(json.dumps(tv_result, indent=2))

if __name__ == "__main__":
    asyncio.run(run_test())
