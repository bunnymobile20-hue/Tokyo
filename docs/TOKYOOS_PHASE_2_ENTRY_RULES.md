# TokyoOS Phase 2 Entry Rules

**Date:** 2026-06-21
**Version:** 1.0
**Applies to:** Phase 2 development start

---

## Mandatory Gates

Phase 2 development SHALL NOT start unless ALL of these conditions are met:

### Gate 1: Phase 1.1 Tests Pass

- [ ] `scripts/test_phase_1_professional_core.py` — 100% PASS
- [ ] `scripts/test_phase_1_regression_guard.py` — 100% PASS
- [ ] `scripts/runtime_validate_phase_1_professional_core.py` — 100% PASS
- [ ] `scripts/runtime_validate_phase_1_checkpoint.py` — 100% PASS

### Gate 2: Release Package Valid

- [ ] `release/TOKYOOS_PHASE_1_MANIFEST.json` exists and valid
- [ ] `release/tokyoos_phase_1_professional_core.tar.gz` exists and extractable
- [ ] Package does NOT contain .env, tokens, secrets, venv, pycache

### Gate 3: Security Baseline

- [ ] `TOKYO_TOKEN_EXPOSED=false` confirmed in all endpoints
- [ ] No real tokens in any committed file
- [ ] Safety gates configured (write, delete, finance, stock, price)
- [ ] No destructive operations in source code

---

## Phase 2 Development Rules

### Rule 1: Read-Only First

ALL new API connections MUST start in `read_only` mode.

```
SIBERIAN_MODE=read_only
BUNNY_SIBERIAN_MODE=read_only
```

No write operation to any ERP, database, or external system without:
1. Explicit user authorization
2. Safety gate confirmation
3. Audit log entry

### Rule 2: Sistema Siberian

The Sistema Siberian connector SHALL:
- Start in `read_only` mode
- Have `required: false`
- Have `safe_mode: true`
- Never expose credentials in frontend or logs
- Never auto-connect without user confirmation

### Rule 3: Spreadsheet Upload

Any spreadsheet upload feature SHALL:
- Create a COPY of the original file
- NEVER alter the original reference spreadsheet
- Store uploaded files in Bunny Intelligence Bank
- Mark all parsed data as `imported`, `manual`, or `pending_validation`
- Require user review before using data in calculations

### Rule 4: Financial Calculations

Financial calculations SHALL:
- NEVER show results as "real" without a valid `data_source`
- Always display the data source next to any value
- Use one of these data_source labels:
  - `live_api` — Direct from working API
  - `imported_manual` — From uploaded spreadsheet, reviewed
  - `pending_validation` — Imported but not reviewed
  - `calculated_estimate` — Derived from partial data
  - `pending_api` — Waiting for API connection
  - `manual_input_pending` — Waiting for user input
- NEVER fabricate numbers
- Show "Dados financeiros ainda nao conectados" when no data exists

### Rule 5: Safety Gate

For any operation involving:
- Write to ERP/finance: **Require Safety Gate confirmation**
- Write to stock: **Require Safety Gate confirmation**
- Price changes: **Require Safety Gate confirmation**
- Delete operations: **Require Safety Gate confirmation + user typing CONFIRM**

### Rule 6: Token Security

- Tokens SHALL NEVER appear in:
  - Frontend (HTML, JS, CSS)
  - Log files
  - API responses (enforced by TOKYO_TOKEN_EXPOSED=false)
  - Error messages
  - Release packages
- API responses may only show `configured: true/false`

### Rule 7: Connector Policy

- New connectors default to `enabled: false`, `required: false`
- Connector failure SHALL NOT crash TokyoOS
- Connector errors SHALL be logged but not exposed to frontend
- Optional connectors may show `status: error` without affecting system health

### Rule 8: Voice Preservation

- `agent.py` SHALL NOT be modified without explicit approval
- `prompts.py` SHALL NOT be modified without explicit approval
- LiveKit voice functionality SHALL NOT be degraded
- Voice memory (Mem0) SHALL NOT be cleared

### Rule 9: Testing

Before Phase 2 is considered complete:
- ALL Phase 1 tests must still pass (regression guard)
- New endpoints must pass runtime validation
- No financial values may appear as real without data source

### Rule 10: Rollback Capability

If Phase 2 introduces regressions:
- Restore from Phase 1.1 release package
- Phase 1.1 checkpoint is the rollback point
- Phase 1 data volumes are preserved

---

## Violation Handling

If any Phase 2 rule is violated:
1. Development pauses
2. Violation is documented
3. Fix is applied before continuing
4. Full test suite is re-run

---

## Phase 2 Sign-Off Checklist

- [ ] All Phase 1.1 gates pass
- [ ] All new endpoints return `token_exposed: false`
- [ ] Sistema Siberian mode is `read_only`
- [ ] No fabricated financial data
- [ ] All data sources labeled correctly
- [ ] Safety gates active
- [ ] Voice preserved
- [ ] Full test suite passes
- [ ] Release package created for Phase 2 checkpoint
