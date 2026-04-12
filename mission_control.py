import sys
from supervisor_agent import SupervisorXO
from critic_agent import BlackwellCritic
from oracle_server import MarketOracle
from voice_processor import VoiceInterface
# Import your tactical nodes here (simplified for logic flow)
# from discovery_engine import ScoutAgent 
# from technical_agent import TechAgent

class AntigravityMissionControl:
    def __init__(self):
        print("--- LOADING ANTIGRAVITY MISSION CONTROL ---")
        self.xo = SupervisorXO()
        self.critic = BlackwellCritic()
        self.oracle = MarketOracle()
        self.reality_anchor = "antigravity_aar.db" # Link to your SQLite/Oracle
        
    def execute_tactical_run(self, task):
        """
        The Full Judicial Loop: Task -> Swarm -> Audit -> XO Report
        """
        # 1. XO Extracts Ticker from Task (e.g., 'NVDA')
        print(f"\n[XO] Analyzing Mission Task: {task}")
        ticker = "NVDA" # Simplified for logic flow
        
        # 2. Oracle Fetches Ground Truth
        ground_truth = self.oracle.get_ticker_telemetry(ticker)
        
        # 3. Swarm Generates Analysis
        # In practice: swarm_data = self.run_11_node_swarm(task)
        swarm_data = {"ticker": "NVDA", "signal": "Strong Buy", "technical_score": 0.92}
        print(f"[Swarm] 11-Node Intelligence Synthesis Complete.")

        # 4. Blackwell Critic Audits the Delta
        # The Critic now has the raw Oracle data to hunt for hallucinations
        audit = self.critic.audit_swarm(swarm_data, reality_anchor_data=ground_truth)

        # 5. Judicial Review & Hard Veto Handling
        if audit["is_veto"]:
            print("\n!!! CRITICAL ALERT: HARD VETO ISSUED BY RED TEAM !!!")
            self.handle_veto(task, swarm_data, audit)
        else:
            # 5. Dual-Stream Success Output
            report, json_intent = self.xo.generate_response(task, swarm_data, audit)
            print(f"\n--- EXECUTIVE SUMMARY ---\n{report}")
            self.export_signal(json_intent)

    def handle_veto(self, task, swarm_data, audit):
        """
        Doctrine Phase 1: MWO-in-the-Loop Veto Debrief
        """
        # XO generates the Forensic Audit explanation
        forensic_report, _ = self.xo.generate_response(
            f"DEBRIEF VETO: {task}", 
            swarm_data=swarm_data, 
            critic_report=audit
        )
        
        print(f"\n--- FORENSIC AUDIT (VETO DEBRIEF) ---\n{forensic_report}")
        print("\n[COMMAND DECISION REQUIRED]")
        choice = input("MWO, do you want to [A]ccept Veto & Abort, or [B]ypass and Execute? (A/B): ")
        
        if choice.lower() == 'b':
            print("[MWO] Override Accepted. Finalizing signal despite Veto.")
            # Finalize anyway...
        else:
            print("[MWO] Veto Sustained. Mission Scrubbed.")

    def export_signal(self, intent):
        if intent:
            with open("Signal_Report_Intent.json", "w") as f:
                import json
                json.dump(intent, f, indent=4)
            print("[System] Signal_Report_Intent.json exported to air-gapped vault.")

def run_war_room():
    mc = AntigravityMissionControl()
    voice = VoiceInterface()
    
    while True:
        print("\n--- COMMAND OPTIONS ---")
        print("[1] Voice Command | [2] Text Command | [EXIT]")
        mode = input("Select Mode: ").lower()

        if mode == '1' or mode == 'voice':
            cmd = voice.listen_for_command()
            if cmd:
                print(f"[MWO VOICE]: {cmd}")
                mc.execute_tactical_run(cmd)
        elif mode == '2' or mode == 'text':
            cmd = input("[MWO TEXT]: ")
            mc.execute_tactical_run(cmd)
        elif mode == 'exit':
            break

if __name__ == "__main__":
    run_war_room()
