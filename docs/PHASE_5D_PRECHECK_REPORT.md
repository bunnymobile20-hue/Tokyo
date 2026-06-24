# PHASE 5D PRECHECK REPORT

## Docker Containers
- **ollama**: Up (IP: 172.18.0.2, Network: ollama-nvidia_default)
- **hermes**: Up (IP: 172.20.0.2, Network: hermes_default)

## Ollama Models
- `qwen2.5:32b-instruct` (Downloaded successfully)
- `qwen2.5:32b`
- `hermes3:latest`

## Hermes Configuration Files
Located at:
- `/DATA/AppData/hermes/config.yaml`
- `/DATA/AppData/hermes-data/config.yaml`

Current config uses:
```yaml
model:
  default: anthropic/claude-opus-4.6
  provider: auto
  base_url: https://openrouter.ai/api/v1
```

## TokyoOS Plugin Bridge Current State
- `tokyo_plugins/hermes_bridge/config.py` is hardcoded to `active_assisted` mode.
- `interface/index.html` displays `active_assisted` UI.
- No `/lab` endpoints exist yet.

## Next Steps for Phase 5D
1. Back up Hermes `config.yaml` files.
2. Modify Hermes `config.yaml` to use Ollama (`http://192.168.1.173:11434/v1`) with model `qwen2.5:32b-instruct`.
3. Update TokyoOS `.env.example` with `lab_unlocked` environment variables.
4. Refactor TokyoOS `hermes_bridge` to switch from `active_assisted` to `lab_unlocked` and add new `/lab` endpoints.
5. Create `test_phase_5d_hermes_ollama_qwen32.py` and runtime validation scripts.
6. Build and deploy to ZimaOS.
