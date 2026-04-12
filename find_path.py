import os
cache_dir = os.path.expanduser("~/.cache/huggingface/hub/models--google--gemma-4-26b-A4B-it/snapshots")
if os.path.exists(cache_dir):
    snapshots = os.listdir(cache_dir)
    if snapshots:
        print(f"FOUND SNAPSHOT: {os.path.join(cache_dir, snapshots[0])}")
    else:
        print("Snapshot folder is empty.")
else:
    print("Cache directory not found.")
