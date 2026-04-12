import torch
from transformers import pipeline

class BlackwellCritic:
    def __init__(self, model_id=r"C:\Users\crypt\.cache\huggingface\hub\models--google--gemma-4-26b-A4B-it\snapshots\47b6801b24d15ff9bcd8c96dfaea0be9ed3a0301"):
        print("Initializing Blackwell Critic (Red Team) on RTX 5060 Ti...")
        
        # Consistent Blackwell quantization for the Critic node
        self.audit_pipe = pipeline(
            "text-generation",
            model=model_id,
            model_kwargs={
                "torch_dtype": torch.bfloat16,
                "load_in_4bit": True,
                "bnb_4bit_compute_dtype": torch.bfloat16,
                "bnb_4bit_quant_type": "nf4"
            },
            device_map="auto",
            # Hard-limit the GPU to 13GB to leave room for the OS and KV Cache
            max_memory={0: "13GiB", "cpu": "24GiB"}, 
            local_files_only=True,
            low_cpu_mem_usage=True,
            trust_remote_code=True
        )

    def audit_swarm(self, swarm_payload, reality_anchor_data=None):
        """
        Executes an adversarial audit of the Swarm's findings.
        """
        prompt = f"""
        Role: Adversarial Auditor (Blackwell Critic)
        Mission: Identify Alpha Hallucinations and structural weaknesses.
        
        Swarm Payload: {swarm_payload}
        Reality Anchor (Excel/Oracle): {reality_anchor_data}
        
        Instructions:
        1. Compare Swarm data against the Reality Anchor.
        2. If a logic paradox or data mismatch exists, issue a HARD VETO.
        3. Output your audit in the following format:
        
        --- AUDIT START ---
        VETO: [TRUE/FALSE]
        PROBABILITY: [0-100%]
        EXPLANATION: [Reasoning for the audit result]
        FRICTION POINTS: [Bulleted list of data mismatches]
        --- AUDIT END ---
        """
        
        audit_raw = self.audit_pipe(prompt, max_new_tokens=512, do_sample=False)
        return self.parse_audit(audit_raw[0]['generated_text'])

    def parse_audit(self, raw_text):
        # Extracts structured data for the Supervisor XO
        report = {
            "is_veto": "VETO: TRUE" in raw_text.upper(),
            "explanation": "No audit explanation provided."
        }
        
        if "EXPLANATION:" in raw_text:
            report["explanation"] = raw_text.split("EXPLANATION:")[1].split("FRICTION POINTS:")[0].strip()
        
        return report
