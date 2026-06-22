# TokyoOS Phase 2 — Read-Only Data Layer

**Version:** 2.0.0-phase2-readonly
**Date:** 2026-06-21
**Status:** SAFE_TO_CONTINUE_PHASE_2_READ_ONLY_DATA_LAYER

---

## Overview

Phase 2 adds a read-only data layer to TokyoOS. No writes to external APIs, ERP, or databases. All calculations return `pending_validation`. All imports are marked with source and validation status.

---

## Architecture

```
Phase 2 Additions:
├── finance_engine/              # Pure calculation engine
│   ├── __init__.py              # 6 financial modules
│   └── audit.py                 # Audit logger (JSONL)
├── app.py (extended)            # New endpoints
│   ├── /tokyo/finance/calculate/*  # Calculation POST endpoints
│   ├── /tokyo/siberian/*           # Read-only Siberian connector
│   ├── /tokyo/finance/uploads/*    # Upload center
│   ├── /tokyo/business/*           # Data layer
│   └── /tokyo/finance/audit        # Audit log
└── interface/index.html (updated)  # Phase 2 finance UI
```

## Key Principles

1. **Read-Only**: No POST/PUT/PATCH/DELETE to external APIs
2. **Pending Validation**: All calculations marked `pending_validation`
3. **Source Attribution**: Every data point has a `source` field
4. **No Fabrication**: Zero fake financial values
5. **Safety First**: Tokens never exposed, audit trails, blocked formats

## Data Sources

| Source | Status | Description |
|---|---|---|
| `sistema_siberian_api` | not_configured | Real API data (read-only only) |
| `manual_input` | available | User-provided data (pending_validation) |
| `spreadsheet_upload` | planned | Future spreadsheet import |
| `spreadsheet_reference` | recognized | Reference templates only |

## Validation Statuses

| Status | Meaning |
|---|---|
| `pending_validation` | Data received but not yet reviewed |
| `validated` | Data reviewed and approved |
| `warning` | Calculation has warnings |

## What's New in Phase 2

- 6 financial calculation modules (DRE, Cash Flow, Break Even, Operational Cycle, Financial Cycle, Minimum Cash)
- 8 Siberian read-only connector endpoints
- 3 spreadsheet upload center endpoints
- 3 business data layer endpoints
- 1 audit log endpoint
- 6 calculation POST endpoints
- Comprehensive audit logging
- Enhanced finance UI with data source tracking
