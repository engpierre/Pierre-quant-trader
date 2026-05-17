try:
    import torch
    from transformers import pipeline, BitsAndBytesConfig
except ImportError:
    torch = None
    pipeline = None
    BitsAndBytesConfig = None

import logging
import warnings

# Suppress standard transformers verbosity
warnings.filterwarnings("ignore")

class MockResponse:
    def __init__(self, text):
        self.text = text

class LocalInferenceEngine:
    _instance = None
    _pipe = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LocalInferenceEngine, cls).__new__(cls)
            if torch is None:
                logging.warning("[INFERENCE] Torch not found. Running in headless data-only mode.")
                return cls._instance
                
            logging.info("[INFERENCE] Initializing Gemma-4 26B Air-Gapped Engine... Please wait.")
            
            # Optimized for RTX 5060 Ti sm_120
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_quant_type="nf4",              
                bnb_4bit_use_double_quant=True,
                llm_int8_enable_fp32_cpu_offload=True   
            )

            # Boot the singleton pipeline once across the entire workspace
            cls._pipe = pipeline(
                "text-generation",
                model="google/gemma-4-26b-A4B-it",
                model_kwargs={"torch_dtype": torch.bfloat16, "quantization_config": bnb_config},
                device_map="auto"
            )
            logging.info("[INFERENCE] VRAM Allocated. Engine Ready.")
        return cls._instance

    def generate_content(self, prompt, max_new_tokens=600):
        """ Acts identically to genai.model.generate_content for seamless integration """
        if not self._pipe: return MockResponse("Inference Engine Offline.")
        
        # Structure as a standard chat instruction 
        messages = [{"role": "user", "content": prompt}]
        
        try:
            out = self._pipe(messages, max_new_tokens=max_new_tokens)
            generated = out[0]['generated_text']
            
            if isinstance(generated, list):
                response_text = generated[-1]['content']
            else:
                response_text = str(generated)
                
            return MockResponse(response_text)
            
        except Exception as e:
            logging.error(f"[INFERENCE ENGINE ERROR]: {e}")
            return MockResponse(str(e))
