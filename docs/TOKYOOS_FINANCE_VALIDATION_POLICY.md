# TokyoOS Finance Validation Policy

## Core Principle

**No financial data shall be displayed as "real" without explicit source attribution and validation status.**

## Data Source Labels

Every financial data point must carry one of these labels:

| Source | Meaning |
|---|---|
| `sistema_siberian_api` | Retrieved from real API (read-only) |
| `manual_input` | Entered by user manually |
| `spreadsheet_upload` | Imported from uploaded spreadsheet |
| `spreadsheet_reference` | From reference template (NOT real data) |
| `pending_api` | Waiting for API connection |
| `manual_upload_future` | Planned for future upload |
| `calculated` | Derived by financial engine |

## Validation Statuses

| Status | Meaning |
|---|---|
| `pending_validation` | Data not yet reviewed by user |
| `validated` | Data reviewed and confirmed |
| `warning` | Calculation produced warnings |
| `error` | Calculation failed |

## Rules

1. All imports default to `pending_validation`
2. All calculations default to `pending_validation`
3. Reference spreadsheets are `reference_only` — never treated as real
4. Values from API are `sistema_siberian_api` with `mode: read_only`
5. Manual input must be explicitly marked by user
6. No value may be displayed without a source

## UI Requirements

- Every financial value must show its source
- Every financial value must show validation status
- When no data exists, show: "Dados financeiros ainda nao conectados."
- Never show `R$ 0,00` as if it's real data
- Use placeholders: `—` or `pending`

## Prohibited

- Fabricating financial values
- Showing `R$ 0` when data source is `pending_api`
- Hiding the data source from the user
- Treating reference spreadsheets as real company data
