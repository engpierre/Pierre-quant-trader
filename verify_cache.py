import os
import json

path = r"C:\Users\crypt\.cache\huggingface\hub\models--google--gemma-4-26b-A4B-it\snapshots\47b6801b24d15ff9bcd8c96dfaea0be9ed3a0301"

print(f"Checking Snapshot Integrity...")
if os.path.exists(path):
    files = os.listdir(path)
    print(f"Total files found: {len(files)}")

    # Look for the index file
    if "model.safetensors.index.json" in files:
        with open(os.path.join(path, "model.safetensors.index.json"), 'r') as f:
            data = json.load(f)
            actual_shards = set(data['weight_map'].values())
            print(f"Index expects {len(actual_shards)} shards.")
    else:
        print("CRITICAL: model.safetensors.index.json is missing!")
else:
    print("CRITICAL: Snapshot directory does not exist!")
