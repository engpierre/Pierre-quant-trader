import os
import json
import google.generativeai as genai

class InsiderIntegrityAuditor:
    def __init__(self, ticker):
        self.ticker = ticker.upper()
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None
            
        self.system_prompt = """
        You are the Internal Integrity Auditor for the Google Anti-gravity 8-Node Swarm.
        Your directive is to analyze the provided swarm intelligence and explicitly identify logic decoupling or temporal drift.

        The "Integrity Audit" Logic:
        1. Value vs. Sentiment: If 'Sentiment' is highly bullish but 'Fundamental' data is declining/weak, flag as a 'Contradiction: Potential Hype Trap'.
        2. Whale vs. Technical: If 'Technical' chart is bullish but 'WhaleWatcher' reports massive C-Suite/Dark Pool selling, flag as a 'Contradiction: Distributive Phase'.
        3. Unit Validation (Common Sense Filter): If the ticker's Market Cap > $500B (Megacap), any Debt-to-Equity reported > 100% must be flagged as a 'Unit Conversion Error' and discarded.
        4. Temporal Sync: Verify the Technical Report date matches the CURRENT SYSTEM DATE closely. If there is a huge discrepancy, disregard the technical metadata and use the Fetch.AI real-time price tick as the only source of truth.
        5. Price vs. Reality: If 'Fetch.AI' real-time Oracle price deviates by > 2% from the 'Technical' or 'Fundamental' entry point, trigger a 'Sync Error'.
        
        Output Format:
        Return STRICTLY a valid JSON object with a single key 'integrity_check':
        {
          "integrity_check": "CLEAR: Swarm logic is tightly coupled." # Or describe the exact contradiction / sync error mathematically flagged.
        }
        """

    def review(self, swarm_payload):
        print(f"[*] Dispatching Internal Logic Auditor for {self.ticker}...")
        if not self.model:
            return {"integrity_check": "API Key missing. Auditor offline."}
            
        try:
            prompt = f"{self.system_prompt}\n\nAnalyze this Swarm Payload for contradictions:\n{swarm_payload}"
            response = self.model.generate_content(prompt)
            cleaned = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)
        except Exception as e:
            return {"integrity_check": f"Auditor parsing error: {str(e)}"}

if __name__ == "__main__":
    agent = InsiderIntegrityAuditor("AAPL")
    print(agent.review("Technical Agent: Price = 150. Fetch.AI Oracle: Price = 149."))
