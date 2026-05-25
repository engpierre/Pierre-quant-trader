import os
import json
from google.cloud import pubsub_v1
from pydantic import BaseModel, field_validator
from signal_agent import SignalAgent

# Authentication
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.path.dirname(__file__), "gcp-key.json")

PROJECT_ID = "quantitative-trading-swarm"
SUBSCRIPTION_ID = "tv-alerts-sub"

# --- STRICT SCHEMA BOUNDARY ---
class TradingViewPayload(BaseModel):
    ticker: str
    window_size: int
    prices: list[float]
    volumes: list[float]

    @field_validator('window_size')
    @classmethod
    def validate_window_size(cls, v: int) -> int:
        if v != 32:
            raise ValueError(f"window_size must be exactly 32. Received: {v}")
        return v

def callback(message):
    print(f"\n[PUBSUB] Received message: {message.message_id}")
    
    # Parse raw bytes (No defensive try/catch wrappers)
    data_str = message.data.decode("utf-8")
    raw_dict = json.loads(data_str)
    
    # Strict Pydantic Validation
    validated_payload = TradingViewPayload(**raw_dict)
    
    # Swarm Handoff
    agent = SignalAgent()
    print(f"[PUBSUB] Schema verified. Dispatching payload to SignalAgent...")
    agent.process_webhook(validated_payload.model_dump())
    
    # CRITICAL: Acknowledge only after strict validation AND successful handoff
    message.ack()
    print(f"[PUBSUB] Message {message.message_id} acknowledged and removed from queue.")

def listen():
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)
    
    print(f"Listening for strictly typed messages on {subscription_path}...\n")
    
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    
    with subscriber:
        try:
            # Block the main thread indefinitely to keep listening
            streaming_pull_future.result()
        except KeyboardInterrupt:
            print("[PUBSUB] Listener stopped by user.")
            streaming_pull_future.cancel()

if __name__ == "__main__":
    listen()
