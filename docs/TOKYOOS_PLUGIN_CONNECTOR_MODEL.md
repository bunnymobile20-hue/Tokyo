# TokyoOS Plugin / Connector Model

## Architecture

TokyoOS uses a connector-based architecture where every external tool is a connector with standardized configuration.

## Connector Schema

```json
{
  "id": "connector_id",
  "name": "Human Name",
  "category": "voice|ai_provider|memory|business_erp|business_b2b|ai_tool|protocol|llm_local|automation|web|os_agent|messaging|productivity|storage",
  "enabled": false,
  "required": false,
  "status": "not_configured|configured|active|error",
  "mode": "optional|read_only|core|core_voice",
  "safe_mode": true,
  "base_url_env": "ENV_VAR_FOR_URL",
  "api_key_env": "ENV_VAR_FOR_KEY",
  "token_env": "ENV_VAR_FOR_TOKEN",
  "healthcheck_path": "/health",
  "default_port": 8080,
  "docker_app_hint": "docker/image:tag",
  "capabilities": ["list", "of", "capabilities"],
  "preferred_llm_provider": "gemini",
  "fallback_llm_provider": "openai",
  "token_exposed": false
}
```

## Priority Rules

1. **Core Voice** (LiveKit) — Essential for voice functionality
2. **Core LLM** (Gemini/OpenAI) — Required for AI processing
3. **Optional with Read Only** (Sistema Siberian) — Business but safe
4. **Optional** (Hermes, MCP, Ollama, etc.) — Not required, can fail
5. **Planned** (Apple Agent) — Future connectors

## No External Tool Is Required

TokyoOS runs with only:
- LiveKit configured (voice)
- One LLM provider configured (Gemini OR OpenAI)
- Local file system

All other connectors default to `enabled: false` and `required: false`.

## Error Handling

If an optional connector fails:
- Log the error
- Return `status: error` for that connector
- Continue normal operation
- Do NOT crash TokyoOS
