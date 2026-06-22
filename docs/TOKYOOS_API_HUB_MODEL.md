# TokyoOS API Hub Model

## Concept

The Tokyo API Hub is a central interface for connecting external APIs to TokyoOS. Each tool/integration has:
- Endpoint / base URL
- API key / token environment variable
- Individual status
- Individual healthcheck
- Optional failure does NOT crash TokyoOS

## Principle

> Falha de ferramenta opcional nao derruba a TokyoOS.

Every external tool is an **optional connector**. Only the core (LiveKit voice, LLM provider) is needed for basic TokyoOS operation.

## Hub Endpoints

| Endpoint | Description |
|---|---|
| GET /tokyo/api-hub/status | Hub overview |
| GET /tokyo/connectors/registry | All connectors |
| GET /tokyo/integrations/registry | All integrations |
| GET /tokyo/connectors/*/health | Per-connector health (future) |

## Connector Configuration

Each connector follows this schema:

```json
{
  "id": "hermes",
  "name": "Hermes Connector",
  "category": "ai_tool",
  "enabled": false,
  "required": false,
  "status": "not_configured",
  "mode": "optional",
  "safe_mode": true,
  "base_url_env": "HERMES_BASE_URL",
  "api_key_env": "HERMES_API_KEY"
}
```

- **enabled**: Controlled by `{ID}_ENABLED` env var
- **required**: false for all external tools
- **mode**: `optional`, `read_only`, or `core`
- **safe_mode**: Always true for external tools

## Available Connectors

| Connector | Default Port | Required | Mode |
|---|---|---|---|
| LiveKit Voice | — | No | Core Voice |
| Google Gemini | — | No | Core LLM |
| OpenAI | — | No | Core LLM |
| Mem0 | — | No | Optional |
| Sistema Siberian | — | No | Read Only |
| Hermes | 8791 | No | Optional |
| MCP | 8789 | No | Optional |
| Ollama | 11434 | No | Optional |
| OpenWebUI | 3000 | No | Optional |
| Browser Use | — | No | Optional |
| Firecrawl | — | No | Optional |
| n8n | 5678 | No | Optional |
| OpenClaw | — | No | Optional |
| Apple macOS Agent | — | No | Planned |
| Telegram | — | No | Optional |
| WhatsApp | — | No | Optional |
