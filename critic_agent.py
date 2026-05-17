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
        import json
        import os
        import re
        
        manifest_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "health_manifest.json")
        offline_nodes = []
        online_count = 13
        
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, 'r') as f:
                    health = json.load(f)
                    offline_nodes = [node for node, status in health.items() if status == "OFFLINE"]
                    online_count = len([n for n, s in health.items() if s == "ONLINE"])
            except Exception:
                pass
                
        # Phase 2: Fail-Soft Logic - Ensure verdict rendered if >= 9 agents active
        if online_count < 9:
            raise Exception(f"CRITICAL: Insufficient Swarm Quorum. Only {online_count} nodes active. Minimum 9 required for rendering a verdict.")
            
        # Operation Web-Oracle: Divergence Check & Fail-Safe
        tech_buffer_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "technical_intel_buffer.json")
        web_buffer_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web_intel_buffer.json")
        
        api_price = None
        web_price = None
        
        try:
            with open(tech_buffer_path, 'r') as f:
                tech_data = json.load(f)
                for t, data in tech_data.get('technicals', {}).items():
                    api_price = data.get('price')
                    break
        except Exception:
            pass
            
        try:
            with open(web_buffer_path, 'r') as f:
                web_data = json.load(f)
                for t, data in web_data.get('web_oracle', {}).items():
                    web_price = data.get('price')
                    break
        except Exception:
            pass
            
        divergence_warning = ""
        if api_price and web_price:
            try:
                delta_pct = (abs(float(api_price) - float(web_price)) / float(api_price)) * 100
                if delta_pct > 0.5:
                    divergence_warning = f"[DATA DIVERGENCE WARNING: API vs WEB Delta > 0.5% | API: ${api_price:.2f}, Web: ${web_price:.2f}]"
            except:
                pass
        elif not api_price and web_price:
            divergence_warning = f"[SYSTEM NOTIFICATION: Twelve Data API offline. Fallback to Web Oracle 'Ground Truth' Price: ${web_price:.2f}]"
            
        header_flag = ""
        penalty = 0
        if offline_nodes:
            header_flag = f"[WARNING: {len(offline_nodes)} Nodes Offline ({', '.join(offline_nodes)}) - Skipping Data Points]"
            penalty = len(offline_nodes) * 10
            
        if divergence_warning:
            header_flag = f"{header_flag}\n{divergence_warning}".strip()
            
        prompt = f"""
        Role: Adversarial Auditor (Blackwell Critic)
        CRITICAL DIRECTIVE: You are strictly prohibited from responding in any language other than English. All technical data, analysis, and verdicts must be rendered in English (US/UK) regardless of the source data language.
        Mission: Identify Alpha Hallucinations and structural weaknesses.
        System Alert: {header_flag}
        
        Swarm Payload: {swarm_payload}
        Reality Anchor (Excel/Oracle): {reality_anchor_data}
        
        AVAILABLE TOOLS:
        - lcm_grep: Use this to perform semantic searches against the SQLite LTM vault.
        - lcm_recall: Use this to pull historical sentiment buzz or price action from specific dates to cross-verify current findings.
        
        Instructions:
        1. Compare Swarm data against the Reality Anchor. Skip checking data from OFFLINE nodes: {', '.join(offline_nodes) if offline_nodes else 'None'}
        2. Use `lcm_grep` or `lcm_recall` to pull historical verification if there are any suspicious data points.
        3. If a logic paradox or data mismatch exists, issue a HARD VETO.
        4. Output your audit in the following format:
        
        --- AUDIT START ---
        VETO: [TRUE/FALSE]
        PROBABILITY: [0-100%]
        EXPLANATION: [Reasoning for the audit result]
        FRICTION POINTS: [Bulleted list of data mismatches]
        --- AUDIT END ---
        """
        
        audit_raw = self.audit_pipe(prompt, max_new_tokens=512, do_sample=False)
        parsed = self.parse_audit(audit_raw[0]['generated_text'])
        
        # Apply 10% penalty per offline node to the final confidence score
        if offline_nodes:
            parsed['explanation'] = f"{header_flag}\n{parsed['explanation']}"
            parsed['probability'] = max(0, parsed['probability'] - penalty)
            
        return parsed

    def parse_audit(self, raw_text):
        import re
        # Extracts structured data for the Supervisor XO
        report = {
            "is_veto": "VETO: TRUE" in raw_text.upper(),
            "probability": 100,
            "explanation": "No audit explanation provided."
        }
        
        prob_match = re.search(r"PROBABILITY:\s*(\d+)", raw_text)
        if prob_match:
            report["probability"] = int(prob_match.group(1))
        
        if "EXPLANATION:" in raw_text:
            report["explanation"] = raw_text.split("EXPLANATION:")[1].split("FRICTION POINTS:")[0].strip()
        
        return report
