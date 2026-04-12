import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import json

class SupervisorXO:
    def __init__(self, model_id=r"C:\Users\crypt\.cache\huggingface\hub\models--google--gemma-4-26b-A4B-it\snapshots\47b6801b24d15ff9bcd8c96dfaea0be9ed3a0301"):
        print("Initializing Reasoning XO on RTX 5060 Ti...")
        
        # Blackwell-optimized quantization
        self.bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            llm_int8_enable_fp32_cpu_offload=True
        )
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_id, 
            local_files_only=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            quantization_config=self.bnb_config,
            device_map="auto",
            # Hard-limit the GPU to 13GB to leave room for the OS and KV Cache
            max_memory={0: "13GiB", "cpu": "24GiB"}, 
            local_files_only=True,
            low_cpu_mem_usage=True,
            trust_remote_code=True
        )
        
        self.system_doctrine = """
        You are the Reasoning XO. Follow Phase 1 Doctrine:
        1. Always perform a Reasoning Trace before answering.
        2. If the Blackwell Critic issues a Veto, stop and provide a Forensic Audit.
        3. Provide Dual-Stream output: A professional verbal report and a hidden JSON block.
        4. Crucially, evaluate the historical AAR Ledger Insights (Trust Scores) provided to you to determine which agent to trust and dynamically weigh your decisions.
        """

    def generate_response(self, task, swarm_data=None, critic_report=None):
        from aar_interface import get_agent_performance
        try:
            # Pull the latest AAR math
            trust_scores = get_agent_performance()
        except:
            trust_scores = "AAR DB Offline"
        
        # Inject historical context into the Reasoning Trace
        history_context = f"AAR Ledger Insights: {trust_scores}"
        
        prompt = f"""
        {self.system_doctrine}
        {history_context}
        Swarm Data: {swarm_data}
        Critic Audit: {critic_report}
        Task: {task}
        XO Reasoning:
        """
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda")
        
        # Generation with CoT support
        outputs = self.model.generate(
            **inputs, 
            max_new_tokens=1024,
            temperature=0.7,
            do_sample=True
        )
        
        full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return self.parse_dual_stream(full_text)

    def parse_dual_stream(self, text):
        # Splits the reasoning/verbal report from the machine JSON
        verbal_report = text.split("XO Reasoning:")[-1].split("```json")[0].strip()
        
        json_payload = None
        if "```json" in text:
            try:
                json_str = text.split("```json")[1].split("```")[0].strip()
                json_payload = json.loads(json_str)
            except:
                pass
                
        return verbal_report, json_payload

    def execute(self, ticker, mode="manual"):
        """ Bridge to support the Streamlit UI's execute loop """
        print(f"[XO Bridge] Routing GUI Request for {ticker} ({mode})")
        from oracle_server import MarketOracle
        from critic_agent import BlackwellCritic
        
        # 1. Oracle fetch
        try:
            ground_truth = MarketOracle().get_ticker_telemetry(ticker)
        except:
            ground_truth = "Telemetry offline"
            
        # 2. Mock swarm data for bridge translation
        swarm_data = {"ticker": ticker, "technical_score": 88, "signal": "BUY inferred"}
        
        # 3. Critic Audit
        audit = BlackwellCritic().audit_swarm(swarm_data, ground_truth)
        
        # 4. Generate XO verdict
        report, json_intent = self.generate_response(f"GUI Execution: {ticker}", swarm_data, audit)
        
        # Construct exact JSON expected by Streamlit's render_audit_card
        gui_json = {
            "ticker": ticker,
            "verdict": {
                "action": "VETOED" if audit.get("is_veto") else "BUY",
                "logic": report or "Processing Logic..."
            },
            "swarm_score": 88,
            "conviction_delta": "-5%" if audit.get("is_veto") else "+12%",
            "geopolitical": {"geopolitical_regime": "STABLE"},
            "critic_score": 90 if audit.get("is_veto") else 10,
            "critic": {"rebuttal": audit.get("explanation", "")}
        }
        
        mock_raw = {
            "Technical": "Engineered UI payload active.",
            "FetchAI (Oracle)": str(ground_truth)
        }
        return [gui_json], [mock_raw]

# Interactive XO Command Loop
def run_interactive_session():
    xo = SupervisorXO()
    
    while True:
        task = input("\n[MWO Command] (or 'exit'): ")
        if task.lower() == 'exit': break
        
        # Phase 3/4 Mock: In a real run, these would call your agent files
        print(f"XO: Processing task '{task}' through 11-node swarm...")
        
        # --- CRITICAL DOCTRINE STEP ---
        # Supervisor runs swarm -> Critic Audits -> Supervisor Checks Veto
        # If critic_report.is_veto == True: presentation changes to Forensic Audit
        
        report, signal = xo.generate_response(task)
        print(f"\n--- XO EXECUTIVE SUMMARY ---\n{report}")
        
        if signal:
            print(f"\n[INTERNAL] Signal_Report_Intent.json generated successfully.")

if __name__ == "__main__":
    run_interactive_session()
