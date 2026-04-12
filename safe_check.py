import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

model_path = r"C:\Users\crypt\.cache\huggingface\hub\models--google--gemma-4-26b-A4B-it\snapshots\47b6801b24d15ff9bcd8c96dfaea0be9ed3a0301"

print("--- STARTING MINIMALIST LOAD TEST ---")
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
)

try:
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        quantization_config=bnb_config,
        device_map="auto",
        low_cpu_mem_usage=True,
        local_files_only=True,
        # Force a strict VRAM limit to save 2GB for the OS
        max_memory={0: "14GiB", "cpu": "16GiB"} 
    )
    print("✅ SUCCESS: Model loaded into VRAM.")
except Exception as e:
    print(f"❌ FAIL: {e}")
