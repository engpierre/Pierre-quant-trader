import os
import json
import google.generativeai as genai

env_path = r"C:\Users\Pierre\.openclaw\workspace\pierre-quant\.env"
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                os.environ["GEMINI_API_KEY"] = line.split("=", 1)[1].strip()

class InsiderIntegrityAuditor:
    def __init__(self, ticker):
        self.ticker = ticker.upper()
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            
        self.system_prompt = """
        You are the Internal Integrity Auditor for the Google Anti-gravity 8-Node Swarm.
        Your directive is to analyze the provided swarm intelligence and explicitly identify logic decoupling or temporal drift.

        The "Integrity Audit" Logic:
        1. Value vs. Sentiment: If 'Sentiment' is highly bullish but 'Fundamental' data is declining/weak, flag as a 'Contradiction: Potential Hype Trap'.
        2. Whale vs. Technical: If 'Technical' chart is bullish but 'WhaleWatcher' reports massive C-Suite/Dark Pool selling, flag as a 'Contradiction: Distributive Phase'.
        3. Unit Validation (Common Sense Filter): If the ticker's Market Cap > $1T, a Debt-to-Equity ratio between 0.5 and 2.5 is considered 'Nominal' and should not trigger a 'Unit Conversion Error'. Otherwise, flag percentages hallucinated as raw integers.
        4. Temporal Sync: Verify the Technical Report date matches the CURRENT SYSTEM DATE closely. TEMPORAL AMENDMENT: You are authorized to accept any Technical Report with a timestamp within +/- 24 hours of the Fetch.AI Oracle 'Ground Truth'. Do not flag 'Temporal Drift' for same-day data.
        5. Price vs. Reality: If 'Fetch.AI' real-time Oracle price deviates by > 2% from the 'Technical' or 'Fundamental' entry point, trigger a 'Sync Error'.
        
        Output Format:
        Return STRICTLY a valid JSON object with a single key 'integrity_check':
        {
          "integrity_check": "CLEAR: Swarm logic is tightly coupled." # Or describe the exact contradiction / sync error mathematically flagged.
        }
        
        CRITICAL DIRECTIVE: You are strictly prohibited from responding in any language other than English. All technical data, analysis, and verdicts must be rendered in English (US/UK) regardless of the source data language.
        """

        self.model = genai.GenerativeModel(
            model_name="gemini-3.5-flash",
            system_instruction=self.system_prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )

    def write_buffer(self, payload):
        buffer_path = r"C:\Users\Pierre\.openclaw\workspace\pierre-quant\sec_intel_buffer.json"
        with open(buffer_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4)

    def review(self, swarm_payload):
        print(f"[*] Dispatching Internal Logic Auditor for {self.ticker}...")
        
        if not os.environ.get("GEMINI_API_KEY"):
            err = {"status": "offline", "error": "API Key missing. Auditor offline."}
            self.write_buffer(err)
            return err
            
        try:
            prompt = f"Analyze this Swarm Payload for contradictions regarding {self.ticker}:\n{swarm_payload}"
            response = self.model.generate_content(prompt)
            result = json.loads(response.text)
            result["ticker"] = self.ticker
            self.write_buffer(result)
            return result
        except Exception as e:
            err = {"status": "offline", "error": f"Auditor parsing error: {str(e)}"}
            self.write_buffer(err)
            return err

if __name__ == "__main__":
    agent = InsiderIntegrityAuditor("AAPL")
    print(agent.review("Technical Agent: Price = 150. Fetch.AI Oracle: Price = 149."))
