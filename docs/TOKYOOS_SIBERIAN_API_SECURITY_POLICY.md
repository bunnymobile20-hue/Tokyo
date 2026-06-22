# TokyoOS Siberian API Security Policy

## Credential Handling

1. **Never logged**: SIBERIAN_API_KEY, SIBERIAN_API_TOKEN, Authorization headers
2. **Never in responses**: All endpoints return `token_exposed: false`
3. **Never in audit**: Audit logger strips credential fields automatically
4. **Never in frontend**: UI shows only `configured: true/false`

## External Requests

- **Method**: GET only
- **Blocked**: POST, PUT, PATCH, DELETE
- **Timeout**: Configurable via SIBERIAN_TIMEOUT (default 15s)
- **Retries**: Configurable via SIBERIAN_MAX_RETRIES (default 2)
- **URL Validation**: Only SIBERIAN_API_BASE_URL used

## Error Handling

| Error | Response | Token Exposed |
|---|---|---|
| Not configured | `not_configured` | No |
| 401/403 | `auth_error` (generic message) | No |
| 404 | `endpoint_not_found` | No |
| Timeout | `timeout` | No |
| Invalid JSON | `invalid_response` | No |

## Audit Log

All Siberian operations logged to `data/audit/siberian_api_readonly.jsonl`:
- siberian_status_checked
- siberian_health_checked
- siberian_schema_checked
- siberian_get_requested
- siberian_get_success
- siberian_get_failed

Credentials ALWAYS redacted from audit entries.
