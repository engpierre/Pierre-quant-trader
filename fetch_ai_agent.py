import os
import requests
import json

class FetchAIAgentConnector:
    """
    Dedicated agent for managing connection and data exchange with the Fetch.AI network.
    It proactively initiates queries to other agents, receives a percentage score consensus, 
    and translates it into a clear BUY or SELL signal.
    """
    def __init__(self, endpoint_url=None):
        # Default endpoint for local uAgent or Agentverse webhook
        self.endpoint_url = endpoint_url or os.getenv("FETCH_AI_ENDPOINT", "http://localhost:8000/consensus")
        
    def dispatch_task(self, ticker, task_payload):
        print(f"[*] (Fetch.AI Connector) Initiating consensus query for {ticker}...")
        
        payload = {
            "ticker": ticker,
            "request_type": "consensus_score_query",
            "internal_desk_data": task_payload
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('FETCH_AI_API_KEY', '')}"
        }
        
        try:
            # Proactively interact with the network with strict connection timeout handling
            response = requests.post(
                self.endpoint_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            # The agent expects to receive data representing a percentage score
            data = response.json()
            score = data.get("consensus_score")
            
            if score is None:
                return "FETCH.AI ERROR: Expected 'consensus_score' in response payload, but none found."
                
            # Parse the percentage score into a clear output signal
            try:
                score_val = float(score)
            except ValueError:
                return f"FETCH.AI ERROR: Invalid score format received: {score}"
                
            signal = "NEUTRAL"
            if score_val >= 75:
                signal = "STRONG BUY"
            elif score_val <= 25:
                signal = "STRONG SELL"
            elif score_val > 50:
                signal = "BUY"
            elif score_val < 50:
                signal = "SELL"
                
            return f"FETCH.AI CONSENSUS SCORE: {score_val:.1f}% -> FINAL NETWORK SIGNAL: {signal}"
            
        except requests.exceptions.Timeout:
            return "FETCH.AI ERROR: Connection to external agent network timed out (10s)."
        except requests.exceptions.ConnectionError:
            return "FETCH.AI ERROR: Connection failed. Ensure Fetch.AI endpoint is running."
        except ValueError:
            # Catching JSON decoding issues
            return "FETCH.AI ERROR: Invalid JSON response format from network."
        except requests.exceptions.RequestException as e:
            return f"FETCH.AI ERROR: Network exception occurred - {str(e)}"

if __name__ == "__main__":
    # Internal test execution
    agent = FetchAIAgentConnector()
    print(agent.dispatch_task("AAPL", {"hypothesis": "Accumulation detected"}))
