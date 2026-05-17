import os
import json
import time
from datetime import datetime

# Define the 13 critical nodes expected in the active workspace
NODES = {
    "COVARIANCE": "covariance_agent.py",
    "CRITIC": "critic_agent.py",
    "FETCH_AI": "fetch_ai_agent.py",
    "FUNDAMENTAL": "fundamental_agent.py",
    "GEOPOLITICAL": "geopolitical_agent.py",
    "INSIDER": "insider_agent.py",
    "SENTIMENT": "sentiment_agent.py",
    "SUPERVISOR": "supervisor_agent.py",
    "TECHNICAL": "technical_agent.py",
    "WHALE": "whale_watcher_agent.py",
    "FINNHUB_INGESTOR": "finnhub_sentiment_ingestor.py",
    "SEC_INGESTOR": "sec_edgar_ingestor.py",
    "TWELVE_DATA_INGESTOR": "twelve_data_ingestor.py"
}

# Define corresponding buffers that must be fresh (within 10 minutes)
BUFFERS = {
    "TECHNICAL": "technical_intel_buffer.json",
    "SENTIMENT": "sentiment_intel_buffer.json",
    "SEC_INGESTOR": "sec_intel_buffer.json"
}

def check_heartbeat():
    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    health_manifest = {}
    current_time = time.time()
    
    print("Initiating Swarm Heartbeat Monitor...")
    
    for node_name, file_name in NODES.items():
        file_path = os.path.join(workspace_dir, file_name)
        status = "ONLINE"
        
        # 1. Check if the script exists
        if not os.path.exists(file_path):
            status = "OFFLINE"
        
        # 2. If it produces a buffer, check the buffer's freshness
        if status == "ONLINE" and node_name in BUFFERS:
            buffer_path = os.path.join(workspace_dir, BUFFERS[node_name])
            if not os.path.exists(buffer_path):
                status = "OFFLINE"
            else:
                mtime = os.path.getmtime(buffer_path)
                # Check if buffer is older than 10 minutes (600 seconds)
                if (current_time - mtime) > 600:
                    status = "OFFLINE"
                    
        health_manifest[node_name] = status
        print(f"[{node_name}] {status}")
        
    output_path = os.path.join(workspace_dir, "health_manifest.json")
    try:
        with open(output_path, "w") as f:
            json.dump(health_manifest, f, indent=4)
        print(f"\nSuccessfully generated health manifest: {output_path}")
    except IOError as e:
        print(f"Failed to write to {output_path}: {e}")

if __name__ == "__main__":
    check_heartbeat()
