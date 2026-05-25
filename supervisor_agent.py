import os
import json
import google.generativeai as genai

env_path = r"C:\Users\Pierre\.openclaw\workspace\pierre-quant\.env"
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                os.environ["GEMINI_API_KEY"] = line.split("=", 1)[1].strip()

class SupervisorXO:
    def __init__(self):
        # Ensure API key is configured
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            
        self.system_prompt = """You are the SupervisorXO (Reasoning XO) Orchestrator for the OpenClaw Swarm.
Your task is to ingest and synthesize pre-calculated data streams from the Sentiment, Insider Trading, and Government Contract sub-agent buffers.
You must construct a final executive summary encapsulating all available telemetry.
Your output MUST be strictly a machine-readable JSON object representing the synthesized report.
Include keys for "executive_summary", "sentiment_status", "insider_activity", and "gov_contract_activity".
Do NOT wrap the response in markdown blocks."""
        
        # Explicitly setting the model to gemini-3.5-flash as per the directive
        self.model = genai.GenerativeModel(
            model_name="gemini-3.5-flash",
            system_instruction=self.system_prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )

    def load_buffer(self, filename):
        path = os.path.join(r"C:\Users\Pierre\.openclaw\workspace\pierre-quant", filename)
        if not os.path.exists(path):
            return {"status": "Buffer missing or offline"}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return {"status": "Error reading buffer", "error": str(e)}

    def execute_synthesis(self):
        print("[SUPERVISOR XO] Polling sub-agent intelligence buffers...")
        
        # Read the explicitly requested buffers gracefully
        buffers = {
            "sentiment_intel": self.load_buffer("sentiment_intel_buffer.json"),
            "insider_intel": self.load_buffer("sec_intel_buffer.json"), # standard sec/insider buffer
            "gov_contract_intel": self.load_buffer("gov_contract_buffer.json")
        }
        
        prompt = f"Analyze the following sub-agent telemetry and generate a final synthesized JSON report:\n\n{json.dumps(buffers, indent=2)}"
        
        try:
            response = self.model.generate_content(prompt)
            # The generation config guarantees JSON structure
            decision = json.loads(response.text)
            
            print(json.dumps(decision, indent=4))
            
            return decision
        except Exception as e:
            print(f"[SUPERVISOR ERROR] Failed to generate or parse executive report: {e}")
            return {"error": str(e)}

if __name__ == "__main__":
    xo = SupervisorXO()
    xo.execute_synthesis()
