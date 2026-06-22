# TokyoOS Provider Model

## LLM Gateway

TokyoOS uses a multi-provider LLM Gateway pattern:

```
Default Provider (gemini)
    |
    v
Fallback Provider (openai)
    |
    v
Local/Compatible (optional)
```

## Providers

### Primary Providers (Tested & Working)

| Provider | ID | Voice | Realtime | Vision |
|---|---|---|---|---|
| Google Gemini | gemini | Yes | Yes | Yes |
| OpenAI | openai | Yes | No | Yes |

### Secondary Providers (Optional)

| Provider | ID | Required | Default Port |
|---|---|---|---|
| Ollama | ollama | No | 11434 |
| OpenWebUI | openwebui | No | 3000 |
| OpenAI-Compatible | openai_compatible | No | — |

## Provider Configuration

Each provider can be configured via environment variables:

```bash
TOKYO_DEFAULT_LLM_PROVIDER=gemini
TOKYO_FALLBACK_LLM_PROVIDER=openai

GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.5-flash

OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o
```

## Per-Connector Providers

In the future, each connector may have its own preferred LLM:

- **Sistema Siberian**: Provider for business analytics
- **Bunny Intelligence Bank**: Provider for document processing
- **MCP**: Provider for tool reasoning
- **Firecrawl**: Provider for web research
- **Browser Use**: Provider for navigation
- **OpenClaw**: External agent provider

## Local LLM

Local LLM (Ollama, OpenWebUI, llama.cpp) is NOT a priority in Phase 1. It enters later as an optional connector.

```bash
OLLAMA_ENABLED=false    # Optional
OPENWEBUI_ENABLED=false  # Optional
LLAMA_CPP_ENABLED=false  # Optional
```

No local LLM is required for TokyoOS to function.
