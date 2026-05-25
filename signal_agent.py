import json
import os
import subprocess

class SignalAgent:
    def __init__(self):
        # Local inference abandoned. Agent acts purely as an API data formatter.
        pass

    def process_webhook(self, payload):
        ticker = payload.get("ticker", "UNKNOWN")
        print(f"[SIGNAL AGENT] Formatting webhook alert for {ticker}...")
        
        # Invoke timesfm predictor to get forecast
        timesfm_output = "No forecast generated."
        dry_run_warning = ""
        try:
            # We use subprocess to capture the stdout of the predictor since it prints the report
            # The predictor expects the ticker as a CLI arg
            result = subprocess.run(
                ["python", "timesfm_predictor.py", ticker],
                capture_output=True,
                text=True,
                cwd=r"C:\Users\Pierre\.openclaw\workspace\pierre-quant"
            )
            timesfm_output = result.stdout
            if "Dry-Run mode" in timesfm_output or "headless environment lacks these tensor" in timesfm_output:
                dry_run_warning = "\n[WARNING: TIMESFM DRY-RUN - FORECAST INVALID]\n"
        except Exception as e:
            timesfm_output = f"TimesFM Execution Error: {e}"

        # Combine payload and forecast cleanly for central API evaluation
        formatted_data = f"--- TRADINGVIEW WEBHOOK PAYLOAD ---\n{json.dumps(payload, indent=2)}\n\n--- TIMESFM FORECAST ---\n{timesfm_output}"
        
        # Append Warning if applicable
        final_report = f"{dry_run_warning}{formatted_data}"
        
        # Save to buffer instantly without LLM latency
        buffer_path = r"C:\Users\Pierre\.openclaw\workspace\pierre-quant\signal_intel_buffer.json"
        buffer_data = {
            "ticker": ticker,
            "timestamp": payload.get("timestamp", ""),
            "flash_intel_report": final_report,
            "dry_run": bool(dry_run_warning)
        }
        
        try:
            with open(buffer_path, "w", encoding="utf-8") as f:
                json.dump(buffer_data, f, indent=4)
            print(f"[SIGNAL AGENT] Formatted Intel Data saved to {buffer_path}")
        except Exception as e:
            print(f"[SIGNAL AGENT] Failed to save buffer: {e}")

if __name__ == "__main__":
    # Test execution
    agent = SignalAgent()
    agent.process_webhook({"ticker": "NVDA", "window_size": 32, "prices": [100, 101, 102], "timestamp": "2026-05-24T12:00:00Z"})
