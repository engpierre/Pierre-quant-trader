import os
import json
import google.generativeai as genai

class GeopoliticalIPBAgent:
    def __init__(self, ticker):
        self.ticker = ticker.upper()
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None
            
        self.system_prompt = """
        DIRECTIVE: GEOPOLITICAL IPB & SUPPLY CHAIN FRICTION ANALYST
        You are the Geopolitical IPB Agent. Your mission is to provide 'Intelligence Preparation of the Battlefield' for the Master CIO. You do not look at price charts; you look at the physical and political friction points of the global economy.
        
        1. The Friction Matrix: For the given Target, you must identify:
        Kinetic Friction: Are there active conflicts or naval blockades impacting the company's primary manufacturing or shipping hubs?
        Regulatory Friction: Are there imminent sanctions, export controls (e.g., high-end AI chips), or antitrust rulings in play?
        Supply Chokepoints: Identify single-source dependencies (e.g., TSMC lead times, rare-earth mineral accessibility, or Suez/Panama canal transit health).
        
        2. The 'Shock' Assessment: 
        Classify the geopolitical environment as: STABLE / FRICTIONAL / VOLATILE.
        Assign a 'Geopolitical Risk Weight' (0-100).
        
        3. Output Logic:
        If the Risk Weight > 75, you must issue a 'SITREP WARNING' regardless of fundamental strength.
        
        Mandatory JSON Output:
        {
          "geopolitical_regime": "VOLATILE",
          "risk_score": 82,
          "chokepoint_analysis": "TSMC production bottleneck due to regional naval drills.",
          "strategic_impact": "High-conviction downside risk for hardware margins."
        }
        """

    def review(self, swarm_baseline=""):
        print(f"[*] Dispatching Geopolitical IPB Node for {self.ticker}...")
        if not self.model:
            return {
                "geopolitical_regime": "STABLE",
                "risk_score": 0,
                "chokepoint_analysis": "API Key missing. IPB Node offline.",
                "strategic_impact": "Unknown."
            }
            
        try:
            # We provide a basic prompt. The LLM's own native knowledge base supplies the kinetic friction data for megacaps natively.
            prompt = f"{self.system_prompt}\n\nExecute IPB Assessment for Target: {self.ticker}\n{swarm_baseline}"
            response = self.model.generate_content(prompt)
            cleaned = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)
        except Exception as e:
            return {
                "geopolitical_regime": "STABLE", 
                "risk_score": 0,
                "chokepoint_analysis": f"IPB Parsing Error: {str(e)}",
                "strategic_impact": "Agent failed to synthesize."
            }

if __name__ == "__main__":
    agent = GeopoliticalIPBAgent("NVDA")
    print(json.dumps(agent.review(), indent=2))
