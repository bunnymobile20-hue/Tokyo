# Sistema Siberian Connector Model

## Overview

Sistema Siberian is the **main ERP system** of GrupsBunny. It serves dual purpose:
1. Internal ERP for Bunny Dreams stores (Riverside, Teresina)
2. Commercial product sold by Bunny Siberian to other companies

## Connector Configuration

```env
SIBERIAN_ENABLED=false
SIBERIAN_MODE=read_only
SIBERIAN_API_BASE_URL=
SIBERIAN_API_KEY=
SIBERIAN_API_TOKEN=
```

## Connector Status

| Property | Value |
|---|---|
| enabled | false |
| required | false |
| status | not_configured |
| mode | read_only |
| safe_mode | true |

## Planned Capabilities

| Capability | Description |
|---|---|
| companies | Multi-company management |
| stores | Store/unit management |
| sales | Sales tracking and reporting |
| products | Product catalog |
| stock | Inventory management |
| finance | Financial module (DRE, cash flow, etc.) |
| clients | Customer management |
| users | User/employee management |
| modules | ERP modules registry |
| reports | Business intelligence reports |
| recurring | Recurring revenue tracking |
| support | Support ticket system |

## Current Phase (Phase 1)

- **No real API connection** — Only registry and placeholders
- **No scraping** — No web scraping of Siberian systems
- **No real credentials** — No login/password configured
- **Mock only** — .env.mock.example for local testing (synthetic data only)

## Future Phases

### Phase 2: Read-Only Integration
- Connect to real Sistema Siberian API
- Display real data in GrupsBunny dashboard
- Read-only mode only

### Phase 3: Write Operations
- Authorized write operations
- Multi-confirmation for finance, stock, price changes
- Full safety gate enforcement

## Safety Rules

1. Always start in read_only mode
2. Require explicit confirmation for writes
3. Never expose API credentials in frontend or logs
4. Finance operations require double confirmation
5. Stock operations require confirmation
6. Price changes require confirmation
