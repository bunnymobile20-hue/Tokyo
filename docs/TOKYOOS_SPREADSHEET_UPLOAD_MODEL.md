# TokyoOS Spreadsheet Upload Model

## Status

**Current:** `planned` — Upload parser pending
**Phase 2 Deliverable:** Structure created, endpoints available, upload not yet activated

## Directory Structure

```
/data/tokyo/
├── uploads/finance/      # Original copies with timestamp
├── imported/finance/     # Processed metadata (JSON)
├── audit/finance/        # Audit trail (JSONL)
└── reports/finance/      # Generated reports (future)
```

## Accepted Formats

| Format | Status |
|---|---|
| `.xlsx` | Accepted |
| `.csv` | Accepted |

## Blocked Formats

| Format | Reason |
|---|---|
| `.xlsm` | Macro-enabled — security risk |
| `.exe` | Executable |
| `.zip` | Unknown archive |
| `.sh`, `.py`, `.bat`, `.ps1` | Scripts |

## Upload Rules

1. **NEVER** overwrite original file
2. Save COPY with timestamp: `{name}_{timestamp}.{ext}`
3. Register metadata in imported/finance/
4. No macro execution
5. No formula trust without validation
6. All data marked `source: spreadsheet_upload`
7. All data marked `validation_status: pending_validation`
8. Never expose file paths containing sensitive info

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | /tokyo/finance/uploads/status | Upload center status |
| GET | /tokyo/finance/uploads/registry | List of imported files |
| POST | /tokyo/finance/uploads/validate | Validate file before upload |

## Future: Actual Upload

When `upload_enabled` becomes `true`:
- `POST /tokyo/finance/uploads` will accept multipart form data
- Files saved to uploads/finance/
- Parser will be implemented in Phase 2.x

## Security

- Paths never exposed in UI
- Macro files rejected
- Executable files rejected
- Unknown formats rejected
- Audit trail for every validation
