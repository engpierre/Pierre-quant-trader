import os
import json
import google.generativeai as genai

class CriticAgent:
    def __init__(self, ticker):
        self.ticker = ticker.upper()
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None

        self.system_prompt = """
        You are the Adversarial Auditor for Google Anti-gravity. 
        Your primary directive is to prevent 'Alpha Hallucination' by identifying structural weaknesses in bullish arguments.

        Your Constraints:
        1. Mathematical Supremacy: Prioritize Bearish Divergences (Price Higher-High vs. RSI Lower-High) and Volume Decay.
        2. Cynicism: Assume every 'breakout' is a 'bull trap' until proven otherwise by institutional flow.
        3. The Rebuttal: You must explicitly challenge the Technical and Sentiment agents. If they see 'Hype,' you see 'Exit Liquidity.'

        Output Format:
        Return STRICT valid JSON with exactly this structure (no markdown wrapping):
        {
          "critique_score": 85, 
          "rebuttal": "RSI is extended and Volume is decaying indicating a severe bull trap.",
          "delta": "Bearish Divergence"
        }
        (Note: critique_score is 0-100, where 100 = MAXIMUM RISK/DANGER of trade failure).
        """

    def review(self, swarm_payload):
        print(f"[*] Dispatching Adversarial Critic for {self.ticker}...")
        if not self.model:
            return {"critique_score": 0, "rebuttal": "API Key missing. Critic offline.", "delta": "Blind"}
            
        try:
            prompt = f"{self.system_prompt}\n\nTear apart this Bullish Swarm Payload for {self.ticker}:\n{swarm_payload}"
            response = self.model.generate_content(prompt)
            cleaned = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)
        except Exception as e:
            return {"critique_score": 0, "rebuttal": f"Critic parsing error: {str(e)}", "delta": "Error"}

if __name__ == "__main__":
    agent = CriticAgent("AAPL")
    print(agent.review("Technical Agent says RSI is 40 and volume is normal."))
