# TokyoOS Phase 3A — Siberian Read-Only API

**Version:** 3.0.0-phase3a
**Date:** 2026-06-21
**Status:** SAFE_TO_CONTINUE_PHASE_3A_SIBERIAN_READONLY_API

## Overview

Phase 3A connects TokyoOS to the real Sistema Siberian API in strict read-only mode using a modular connector architecture.

## Architecture

```
siberian_connector/
├── client.py       # GET-only HTTP client with auth masking
├── schemas.py      # Data normalizers (never invent data)
├── service.py      # Service layer with audit logging
├── routes.py       # FastAPI router with all endpoints
```

## Key Features

- **GET Only**: All external requests use GET. POST/PUT/PATCH/DELETE blocked
- **Graceful Degradation**: When API not configured, returns `not_configured` without error
- **Auth Masking**: Credentials never appear in logs, responses, or audit
- **Structured Responses**: All data carries `source`, `validation_status`, `scope`
- **Audit Trail**: All operations logged to `siberian_api_readonly.jsonl`
- **Timeout + Retry**: Configurable timeout and max retries

## Endpoints

| Method | Path | Source |
|---|---|---|
| GET | /tokyo/siberian/status | Internal |
| GET | /tokyo/siberian/health | Internal + API |
| GET | /tokyo/siberian/schema | Internal |
| GET | /tokyo/siberian/capabilities | Internal |
| GET | /tokyo/siberian/companies | API proxy |
| GET | /tokyo/siberian/stores | API proxy |
| GET | /tokyo/siberian/sales/summary | API proxy |
| GET | /tokyo/siberian/finance/summary | API proxy |
| GET | /tokyo/siberian/products/summary | API proxy |
| GET | /tokyo/siberian/stock/summary | API proxy |

## Configuration

```env
SIBERIAN_ENABLED=true
SIBERIAN_MODE=read_only
SIBERIAN_API_BASE_URL=https://api.siberian.example.com
SIBERIAN_API_KEY=your_key
SIBERIAN_API_TOKEN=your_token
SIBERIAN_TIMEOUT=15
SIBERIAN_MAX_RETRIES=2
```

## Data Normalization

All API responses are normalized with:
- `source: sistema_siberian_api`
- `validation_status: pending_validation`
- `scope` attribution (riverside, teresina, bunny_dreams, etc.)
- Warnings for scope mismatch

## Security

- Tokens: never logged, never in responses
- Auth: masked in audit logs
- Errors: 401/403 show "Authentication failed" without exposing key
- Timeout: safe handling with retries
