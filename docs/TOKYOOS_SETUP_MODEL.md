# TokyoOS Setup Model

## Overview

TokyoOS includes a Setup Wizard for first-time configuration. The wizard validates environment variables, checks API keys, and ensures the system is ready for operation.

## Setup Flow

1. Environment Validation — Check .env file
2. Credentials Status — Verify API keys
3. Integrations Status — Check all connectors
4. Providers Status — Verify LLM providers
5. Storage Check — Validate data directories
6. Voice Check — Verify LiveKit configuration
7. Security Check — Ensure safe mode
8. Docker Readiness — Prepare for ZimaOS deployment

## API Endpoints

| Endpoint | Description |
|---|---|
| GET /tokyo/setup/status | Overall setup status |
| GET /tokyo/setup/checklist | Detailed checklist |

## First Run

On first run, all items show as `pending`. Configure the `.env` file with required variables and restart.

## Example .env Configuration

```bash
TOKYO_DEFAULT_LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
LIVEKIT_URL=wss://your-instance.livekit.cloud
LIVEKIT_API_KEY=your_livekit_key
LIVEKIT_API_SECRET=your_livekit_secret
```

No other integrations are required. All optional connectors default to `enabled: false`.
