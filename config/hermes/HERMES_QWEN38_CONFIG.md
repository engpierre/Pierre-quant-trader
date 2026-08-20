# Hermes Agent :: Qwen 3.8 27B Local Architecture & Configuration

## Environment & Topology
- **Host:** AMD Ryzen 9 9950X / Dual NVIDIA RTX 5060 Ti (32 GiB VRAM)
- **Hermes Version:** v0.20.4 (upstream 2eb0b3b2)
- **Primary Model:** `qwen3.8:27b` (via local Ollama `http://localhost:11434/v1`)
- **Isolation Boundaries:** Fully decoupled from OpenClaw Sentry Swarm and Julie Core HUD.

## Model Configuration (`config.yaml`)
```yaml
model:
  default: qwen3.8:27b
  provider: custom
  base_url: http://localhost:11434/v1
  max_tokens: 4096
  temperature: 0.2
```

## Key Architectural Fixes Applied
1. **Ollama Transport Serialization:** Patched `convert_messages()` in `chat_completions.py` to enforce string content, close unclosed tool call tails, and maintain strict role alternation to prevent HTTP 500 errors.
2. **Mandatory Pre-Flight Live Price Ingestion:** Bound Agent 05 (`fetch_live_quote`) directly to prevent reading stale cached lookback values.
3. **Dynamic Spot Price Anchoring:** Chronos-Bolt / TimesFM 1-sigma probability envelopes anchor directly to live market spot data.
