# TokyoOS Phase 3 Entry Rules

**Date:** 2026-06-21
**Applies to:** Phase 3 development start

## Mandatory Gates

Phase 3 SHALL NOT start unless ALL Phase 2.1 tests pass:

- [ ] `scripts/test_phase_1_professional_core.py` — 100%
- [ ] `scripts/test_phase_1_regression_guard.py` — 100%
- [ ] `scripts/test_phase_2_read_only_data_layer.py` — 100%
- [ ] `scripts/test_phase_2_regression_guard.py` — 100%
- [ ] `scripts/runtime_validate_phase_2_read_only_data_layer.py` — 100%
- [ ] `scripts/runtime_validate_phase_2_checkpoint.py` — 100%

---

## Phase 3 Development Rules

### Rule 1: API Real Read-Only First

Sistema Siberian real API connection MUST:
- Start in `read_only` mode
- Only execute GET operations
- No POST/PUT/PATCH/DELETE initially
- Return `source: sistema_siberian_api` on all data
- Return `validation_status: pending_validation` initially
- Never expose API keys in responses or logs
- Gracefully handle connection failures

### Rule 2: Upload Real Activation

When spreadsheet upload is activated:
- Files saved as COPY with timestamp
- NEVER overwrite original
- Metadata registered in imported/finance/
- All parsed data marked `source: spreadsheet_upload`
- All parsed data marked `validation_status: pending_validation`
- .xlsm/.exe/.zip/scripts remain BLOCKED

### Rule 3: No Fabricated Data

- Every financial value MUST have `source`
- Every financial value MUST have `validation_status`
- Never display calculated results as "real" without source
- Reference spreadsheets remain `reference_only`
- Empty/unknown values display as `—`

### Rule 4: Scope Attribution

Every financial/sales data point MUST specify scope:
- `riverside` — Loja Riverside
- `teresina` — Loja Teresina
- `bunny_dreams` — Consolidated Bunny Dreams
- `bunny_siberian` — Bunny Siberian B2B
- `grupsbunny` — Consolidated holding
- `sistema_siberian` — ERP product

### Rule 5: Conflict Resolution

When data from different sources conflicts (e.g., API vs spreadsheet):
- Generate WARNING, not overwrite
- Show both values with their sources
- Let user decide which to trust
- Audit log the conflict

### Rule 6: Safety Gate

Any future write operation to external systems requires:
1. Safety gate confirmation
2. Explicit user authorization
3. Audit log entry
4. `source` and `validation_status` updated

### Rule 7: Token Security

- API keys never in frontend/logs/errors
- `token_exposed: false` on ALL endpoints
- Secret masking in audit logs
- .env excluded from all packages

### Rule 8: Voice Preservation

- `agent.py` NOT modified
- `prompts.py` NOT modified
- LiveKit voice agent preserved

### Rule 9: Regression Protection

- ALL Phase 1 + Phase 2 tests must pass before Phase 3 sign-off
- Finance engine calculations unchanged unless fixing bugs
- Siberian connector mode stays `read_only` in Phase 3

### Rule 10: Rollback Point

- Phase 2.1 release package is the rollback baseline
- If Phase 3 introduces regressions, rollback to Phase 2.1

---

## Phase 3 Breach Handling

If any rule is violated:
1. Development pauses
2. Violation documented
3. Fix applied
4. Full test suite re-run
5. New checkpoint created before continuing
