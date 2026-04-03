import os
import io
import sys
import json
import logging
import google.generativeai as genai

from fundamental_agent import FundamentalAgent
from sentiment_agent import SentimentAgent
from technical_agent import TechnicalAgent
from fetch_ai_agent import FetchAIAgentConnector
from insider_agent import InsiderIntegrityAuditor
from whale_agent import WhaleWatcherAgent
from critic_agent import CriticAgent
from discovery_engine import ScoutAgent
from geopolitical_agent import GeopoliticalIPBAgent

logging.basicConfig(level=logging.INFO, format='[SUPERVISOR] %(message)s')

class SupervisorAgent:
    def __init__(self):
        self.google_api_key = os.getenv("GEMINI_API_KEY")
        if self.google_api_key:
            genai.configure(api_key=self.google_api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None
            
        self.integrated_command_prompt = """
        You are the Chief Investment Officer (CIO) and Master Synthesizer for Google Anti-gravity. 
        You are presiding over an 8-node autonomous intelligence swarm. Your mission is to adjudicate conflicting reports and issue high-conviction trade orders.
        
        Judicial Rules of Engagement (ROE):
        1. Truth-First Protocol: If the Fetch.AI Oracle reports a price delta > 2% from the swarm's baseline, you must flag a 'Sync Error' and downgrade conviction.
        2. Integrity Protocol: If the Insider Auditor reports a 'Logic Decoupling', you are FORBIDDEN from issuing a 'STRONG BUY.'
        3. Generational Alpha Trigger (Technical Override): If RSI < 25 (Deep Oversold) for a blue-chip stock with positive Whale-Watcher Macro Pulse, this is a 'Generational Buy Opportunity.' You are authorized to OVERRIDE the Adversarial Critic's warning.
        4. The Cowardly Judge Correction: Do NOT default to 'CAUTION' just because the Critic exists. If the Integrated Conviction Delta is > +40, you MUST issue a BUY order.
        5. The Critic's Veto: If the Adversarial Critic identifies a 'Bearish Divergence' AND Volume Decay, you must issue a CAUTION verdict unless the WhaleWatcher confirms high-conviction Dark Pool accumulation.
        
        MANDATORY VERIFICATION: Before final JSON output, perform one internal loop: 'Does this verdict make sense for a multi-trillion dollar company with high margins and a low RSI?'. If 'No', recalculate weights.
        
        UPDATED JUDICIAL DIRECTIVE: OVERRIDE & EXPLANATION LOGIC
        You must now explicitly identify 'Judicial Overrides.' 
        1. The Trigger: If you issue a BUY verdict while the Conviction Delta is < 0 (meaning the Critic mathematically won the argument), you MUST add a new field to your JSON output: "judicial_override": true.
        2. The Justification: In the final_logic field, you must start the sentence with: 'OVERRIDE ACTIVATED:' followed by the reason (e.g., 'Generational Alpha detected at RSI 27').
        
        Output STRICTLY valid JSON. No conversational text. Schema:
        {
          "swarm_score": 88,
          "critic_score": 93,
          "conviction_delta": -5,
          "judicial_override": true,
          "verdict": {
            "action": "BUY/STRONG BUY/HOLD/CAUTION/SELL",
            "confidence": "High/Medium/Low",
            "final_logic": "OVERRIDE ACTIVATED: Extreme RSI oversold condition on a blue-chip megacap outweighs technical volume decay."
          },
          "integrity_check": "Status from Insider Auditor and Fetch.AI Sync."
        }
        """

    def extract_ticker(self, user_prompt):
        if not self.model: return "AAPL"
        try:
            prompt = f"Extract ONLY the 1-5 letter stock ticker from this text: {user_prompt}"
            response = self.model.generate_content(prompt)
            return response.text.strip().upper()
        except: return "AAPL"

    def execute_audit(self, ticker, is_proactive=False):
        """ Trigger the full 8-Node Logic Loop """
        logging.info(f"--- LAUNCHING 8-NODE CIO AUDIT: {ticker} ---")
        
        reports = {}
        # 1. ORACLE FIRST (Ground Truth Baseline)
        try: reports['FetchAI (Oracle)'] = FetchAIAgentConnector().dispatch_task(ticker, "Provide Ground Truth.")
        except Exception as e: reports['FetchAI (Oracle)'] = f"ERROR: {e}"
        
        # 2. Gather Core Swarm Intelligence
        try: reports['Technical'] = TechnicalAgent(ticker).review()
        except Exception as e: reports['Technical'] = f"ERROR: {e}"
        try: reports['Fundamental'] = FundamentalAgent(ticker).review()
        except Exception as e: reports['Fundamental'] = f"ERROR: {e}"
        try: reports['Sentiment'] = SentimentAgent(ticker).review()
        except Exception as e: reports['Sentiment'] = f"ERROR: {e}"
        try: reports['WhaleWatcher'] = WhaleWatcherAgent(ticker).review()
        except Exception as e: reports['WhaleWatcher'] = f"ERROR: {e}"
        
        swarm_payload = "\n".join([f"--- {k.upper()} ---\n{v}" for k, v in reports.items()])
        
        # --- GEOPOLITICAL IPB EXTRACTION ---
        ipb_json = GeopoliticalIPBAgent(ticker).review(swarm_payload)
        ipb_regime = ipb_json.get("geopolitical_regime", "STABLE")
        ipb_risk = ipb_json.get("risk_score", 0)
        
        # --- REGIME ANCHOR EXTRACTION ---
        regime = "Neutral"
        whale_str = reports.get('WhaleWatcher', '').upper()
        if "VOLATILE-BEAR" in whale_str:
            regime = "Volatile-Bear"
            critic_weight = 0.85
            swarm_weight = 0.15
        elif "TRENDING-BULL" in whale_str:
            regime = "Trending-Bull"
            critic_weight = 0.30
            swarm_weight = 0.70
        else:
            critic_weight = 0.50
            swarm_weight = 0.50
            
        # Geopolitical Override (1.5x Critic Power Boost if VOLATILE)
        if ipb_regime == "VOLATILE":
            regime += " | GEOPOLITICAL FRICTION (CRITIC BOOSTED)"
            critic_weight = min(critic_weight * 1.5, 1.0)
            swarm_weight = 1.0 - critic_weight
        
        # 3. INTERVENTION NODES (Auditing & Attack)
        logging.info("Nodes 1-5 Complete. Triggering Auditor and Red Team Interventions...")
        extra_critic_context = "\nCRITIC INSTRUCTION: This target was auto-scouted via high MRS logic. VIGOROUSLY HUNT FOR EXHAUSTION AND BLOW-OFF TOPS." if is_proactive else ""
        if ipb_regime == "VOLATILE":
             extra_critic_context += f"\nCRITIC INSTRUCTION: GEOPOLITICAL FRICTION IS HIGH (Risk Score: {ipb_risk}). Integrate this vulnerability."
             
        critic_json = CriticAgent(ticker).review(swarm_payload + extra_critic_context)
        
        # The Insider Auditor now ingests exactly what the swarm produced sequentially, hunting exclusively for decoupling errors.
        insider_json = InsiderIntegrityAuditor(ticker).review(swarm_payload)
        integrity_status = insider_json.get("integrity_check", "Unknown System Health.")
        
        # --- WAR ROOM AUDIT HALT ---
        whale_data = str(reports.get('WhaleWatcher', '')).upper()
        if ("INSIDER BUY" in integrity_status.upper() or "CEO" in integrity_status.upper()) and ("SELL" in whale_data or "DISTRIBUTIVE" in whale_data):
            logging.critical(f"WAR ROOM AUDIT HALT TRIGGERED for {ticker}: Insider Buy vs Whale Sell divergence.")
            return {"verdict": {"action": "WAR ROOM HALT", "confidence": "N/A", "final_logic": "Mission halted. Divergence between Insider Buys and Dark Pool sell-offs."}}, reports

        # 4. MASTER SYNTHESIS (CIO Adjudication)
        if not self.model: return None, reports
        
        # --- RECURSIVE OPTIMIZATION HOOK ---
        try:
            from optimizer_engine import get_global_trust_weights
            dynamic_weights, trust_avg = get_global_trust_weights()
            if trust_avg < 0.50:
                critic_weight = dynamic_weights.get("Critic", critic_weight)
                swarm_weight = 1.0 - critic_weight
        except Exception as oe:
            logging.warning(f"Optimization Engine offline: {oe}")
            dynamic_weights = {}
            trust_avg = 1.0

        dynamic_roe = f"""
        6. REGIME ANCHOR ({regime}): The Macro-Regime dictates strict Tactical Stance weighting.
        
        PROTOCOL: RECURSIVE WEIGHT INJECTION
        You are the Master CIO. You are currently operating with Dynamic Weight Tuning enabled.
        Current Performance Data:
        Global Swarm Trust: {trust_avg*100:.1f}%
        Active Weight Matrix: {dynamic_weights}
        
        Constraint: If the Swarm's historical accuracy is below 50%, the Adversarial Critic has been granted a High-Intensity Veto (Weight: {critic_weight}). You must give preferential treatment to the Critic's 'Bull Trap' warnings unless the Generational Alpha trigger is active.
        
        You MUST calculate the final algorithmic Conviction Score mathematically using this exact formula:
        Final_Conviction = (Swarm_Score * {swarm_weight}) + (Critic_Score * {critic_weight})
        Apply this strictly to the 'conviction_delta'. If Regime=Volatile-Bear, the Critic natively holds veto power.
        """
            
        try:
            prompt = f"{self.integrated_command_prompt}\n{dynamic_roe}\n\nGATHERED EVIDENCE (SWARM):\n{swarm_payload}\n\nADVERSARIAL CRITIC REBUTTAL:\n{json.dumps(critic_json, indent=2)}\n\nINTERNAL INTEGRITY AUDITOR:\n{integrity_status}"
            response = self.model.generate_content(prompt)
            cleaned = response.text.replace("```json", "").replace("```", "").strip()
            final_json = json.loads(cleaned)
            final_json["ticker"] = ticker  
            
            # Pass Critic payload and Raw Integrity Status cleanly to the UI context without breaking JSON extraction
            final_json["critic"] = critic_json
            final_json["raw_integrity"] = integrity_status
            final_json["geopolitical"] = ipb_json
            
            # Phase 3 AAR Hook: Save to Persistence Ledger
            try:
                import yfinance as yf
                current_price = yf.Ticker(ticker).info.get('currentPrice', yf.Ticker(ticker).info.get('regularMarketPrice', 0.0))
                from backtest_validator import save_verdict_to_blackbox
                save_verdict_to_blackbox(final_json, ticker, current_price)
            except Exception as loop_e:
                logging.error(f"Failed to hook Blackbox DB on return: {loop_e}")
                
            # --- PHASE 2 AGENTFI INTENT EXPORT ---
            try:
                import re
                tech_report = reports.get("Technical", "")
                atr_match = re.search(r"ATR-BASED STOP LOSS:\s*([0-9.]+)", tech_report)
                stop_loss = float(atr_match.group(1)) if atr_match else 0.0
                
                intent_schema = {
                    "Ticker": ticker,
                    "Conviction_Score": final_json.get("swarm_score", 0),
                    "Stop_Loss_ATR": stop_loss,
                    "Proof_of_Analysis": f"ipfs://antigravity/artifacts/{ticker}_signal"
                }
                with open("Signal_Report_Intent.json", "w") as f:
                    json.dump(intent_schema, f, indent=4)
                logging.info(f"AgentFi Intent Protocol Exported natively for {ticker}.")
            except Exception as e:
                logging.error(f"Failed to map AgentFi Intent: {e}")
            
            return final_json, reports
        except Exception as e:
            logging.error(f"CIO Adjudication Error: {e}")
            return None, reports

    def execute(self, target_input, mode="manual"):
        """ Directs execution mode for Autonomous Array Loops vs Single Terminal Queries """
        if mode == "manual":
            ticker = self.extract_ticker(target_input)
            j, r = self.execute_audit(ticker, is_proactive=False)
            return [j], [r]
            
        elif mode == "discovery":
            logging.info("PROACTIVE MODE: Dispatching Scout Engine to locate Alpha Targets...")
            scout = ScoutAgent()
            scout_targets = scout.run_reconnaissance()
            
            # --- FORCE COMPOSITION MATRICES (COVARIANCE LOCK) ---
            from covariance_agent import CovarianceAgent
            cov_agent = CovarianceAgent()
            diversified_targets, covariance_report = cov_agent.execute_lock(scout_targets)
            
            all_jsons = []
            all_reports = []
            for t in diversified_targets:
                logging.info(f"Proactive Loop -> Actively Adjudicating Diversified Node: {t}")
                j, r = self.execute_audit(t, is_proactive=True)
                if j:
                    all_jsons.append(j)
                    # Bind the global covariance report to the first agent's raw reports for Streamlit parsing safely
                    if not all_reports:
                        r['Covariance (Diversification Matrix)'] = covariance_report
                    all_reports.append(r)
            return all_jsons, all_reports
            
        return [], []
