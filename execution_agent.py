import os
import json
from datetime import datetime, timezone
import google.generativeai as genai

# Initialize Gemini API
# Assumes GEMINI_API_KEY is available in the environment
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

class ExecutionAgent:
    def __init__(self):
        self.system_prompt = """[C]haracter: Act as the Lead Quantitative Swing Trading Agent. Your primary function is to interpret 4-Hour time-series forecasting data from TimesFM to execute trades intended for a 3-to-4 week holding period. You are highly disciplined, prioritize capital preservation, and are completely immune to intraday noise. Your operational mandate is to avoid overtrading at all costs.

[R]equest: Ingest the data contained within the signal_intel_buffer.json file. Evaluate the 16-bar trajectory. You must only generate a BUY/LONG or SELL/SHORT signal if the TimesFM forecast indicates a strong, structural breakout or breakdown that justifies tying up capital for 21 to 30 days. If the forecast suggests sideways chop, weak momentum, or a temporary pullback, you must default to HOLD to protect the portfolio.

[E]xamples: * Input: Trajectory is BEARISH, but the 4H target price shows only a minor dip before flattening out.
Output: Action: HOLD. Rationale: Insufficient downward momentum to warrant opening a 3-week short position; high risk of getting chopped out.

Input: Trajectory is BULLISH, and the 4H target price indicates a continuous, steep upward delta breaking previous resistance.
Output: Action: BUY. Rationale: Strong 4H structural momentum detected; aligns perfectly with a multi-week long thesis.

[A]djustments: Never execute a trade based on single-candle volatility. You must demand mathematically significant momentum from the TimesFM target price before issuing an execution command. Do not hallucinate external news events or sentiment; base your execution strictly on the mathematical delta between the current price and the forecasted target. When in doubt, default to HOLD.

[T]ype of Output: Respond strictly in a machine-readable JSON format containing three keys: "execution_action", "swing_conviction_score", and "rationale". Do not wrap the JSON in markdown blocks.

[E]xtras: Ensure every execution signal is logged with a UTC timestamp and an internal tag of "holding_period_target": "21_to_30_days" for system auditing."""

        # Configure the model to enforce strictly parsed JSON output
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=self.system_prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )

    def execute_swing_trade(self):
        buffer_path = r"C:\Users\Pierre\.openclaw\workspace\pierre-quant\signal_intel_buffer.json"
        
        if not os.path.exists(buffer_path):
            print(f"[ERROR] Buffer file not found at {buffer_path}")
            return None
            
        try:
            with open(buffer_path, "r", encoding="utf-8") as f:
                intel_data = json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to read intel buffer: {e}")
            return None
            
        print("[EXECUTION AGENT] Ingesting TimesFM Flash Intel Report...")
        
        user_prompt = f"Analyze the following TimesFM 4-Hour forecasting data and issue a disciplined swing trading execution decision:\n\n{json.dumps(intel_data, indent=2)}"
        
        try:
            # Generate the decision
            response = self.model.generate_content(user_prompt)
            decision = json.loads(response.text)
            
            # Inject mandatory auditing tags and UTC timestamp
            decision["timestamp_utc"] = datetime.now(timezone.utc).isoformat()
            decision["holding_period_target"] = "21_to_30_days"
            decision["target_ticker"] = intel_data.get("ticker", "UNKNOWN")
            
            print("\n--- OPERATION EXECUTION-AGENT: SWING TRADE DECISION ---")
            print(json.dumps(decision, indent=4))
            print("-------------------------------------------------------")
            
            return decision
            
        except Exception as e:
            print(f"[EXECUTION AGENT ERROR] Failed to generate or parse trading decision: {e}")
            return None

if __name__ == "__main__":
    agent = ExecutionAgent()
    agent.execute_swing_trade()
