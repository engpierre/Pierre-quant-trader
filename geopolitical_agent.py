import os
import json
import requests
from bs4 import BeautifulSoup
from local_inference import LocalInferenceEngine

class GeopoliticalIPBAgent:
    def __init__(self, ticker):
        self.ticker = ticker.upper()
        self.model = LocalInferenceEngine()
            
        self.system_prompt = """
        DIRECTIVE: GEOPOLITICAL IPB & SUPPLY CHAIN FRICTION ANALYST
        You are the Geopolitical IPB Agent. Your mission is to provide 'Intelligence Preparation of the Battlefield' for the Master CIO. You do not look at price charts; you look at the physical and political friction points of the global economy.
        
        CRITICAL DIRECTIVE: You will actively utilize an integrated search tool, like Google Search, to fetch current news and analyses pertinent to the target. Analyze these reports for geopolitical risk factors that could impact the stock, and incorporate those findings into your response.
        
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
        
        CRITICAL DIRECTIVE: You are strictly prohibited from responding in any language other than English. All technical data, analysis, and verdicts must be rendered in English (US/UK) regardless of the source data language.
        """

    def _fetch_live_news(self):
        try:
            url = f"https://news.google.com/rss/search?q={self.ticker}+geopolitics"
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.content, features="xml")
            items = soup.findAll('item')
            news_context = []
            for item in items[:5]:
                news_context.append(f"- {item.title.text}")
            return "\n".join(news_context)
        except Exception:
            return "Unable to fetch live news at this time."

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
            # We fetch real-time news to satisfy the active surveillance directive
            live_news = self._fetch_live_news()
            
            prompt = f"{self.system_prompt}\n\n[LIVE SEARCH RESULTS for {self.ticker}]\n{live_news}\n\nExecute IPB Assessment for Target: {self.ticker}\n{swarm_baseline}"
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
