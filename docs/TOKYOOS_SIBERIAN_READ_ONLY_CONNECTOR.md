# TokyoOS Siberian Read-Only Connector

## Status

- **enabled:** false
- **required:** false
- **mode:** read_only
- **safe_mode:** true

## Environment Variables

```env
SIBERIAN_ENABLED=false
SIBERIAN_MODE=read_only
SIBERIAN_API_BASE_URL=
SIBERIAN_API_KEY=
SIBERIAN_API_TOKEN=
```

## Configuration Check

The connector only attempts API calls when ALL of these are true:
1. `SIBERIAN_ENABLED=true`
2. `SIBERIAN_API_BASE_URL` is set
3. `SIBERIAN_API_KEY` OR `SIBERIAN_API_TOKEN` is set

If any is missing, all endpoints return `status: not_configured`.

## Allowed Operations

| Method | Allowed | Status |
|---|---|---|
| GET | Yes | Read-only data retrieval |
| POST | No | Blocked — no writes to ERP |
| PUT | No | Blocked |
| PATCH | No | Blocked |
| DELETE | No | Blocked |

## Endpoints

### Status & Health
| Method | Path | Description |
|---|---|---|
| GET | /tokyo/siberian/status | Connector status |
| GET | /tokyo/siberian/health | API health check |
| GET | /tokyo/siberian/schema | Capabilities list |
| GET | /tokyo/siberian/capabilities | Alias for schema |

### Data Proxies (only if configured)
| Method | Path | Description |
|---|---|---|
| GET | /tokyo/siberian/companies | Company list |
| GET | /tokyo/siberian/stores | Store/unit list |
| GET | /tokyo/siberian/sales/summary | Sales summary |
| GET | /tokyo/siberian/finance/summary | Finance summary |

## Not Configured Response

When API is not configured, all endpoints return:
```json
{
  "status": "not_configured",
  "data": null,
  "source": "pending_api",
  "mode": "read_only",
  "message": "Sistema Siberian API nao configurada..."
}
```

## Safety

- API keys never appear in responses
- API keys never appear in logs
- Failures do not crash TokyoOS
- Timeout: 10 seconds
- All responses include `_meta.token_exposed: false`
