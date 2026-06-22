# TokyoOS Financial Calculation Engine

## Overview

Pure Python module with no external dependencies beyond the standard library. All functions are deterministic, side-effect-free, and return structured results with validation metadata.

## Location

```
finance_engine/
├── __init__.py    # 6 calculation modules
└── audit.py       # Audit log writer
```

## Modules

### 1. calculate_dre()
DRE — Demonstrativo do Resultado do Exercicio

**Inputs:** gross_revenue, deductions, cogs, fixed_expenses, variable_expenses
**Formulas:**
- net_revenue = gross_revenue - deductions
- gross_profit = net_revenue - cogs
- operating_result = gross_profit - fixed_expenses - variable_expenses
- net_result = operating_result

### 2. calculate_cash_flow()
Fluxo de Caixa

**Inputs:** opening_balance, inflows, outflows, accounts_receivable, accounts_payable
**Formulas:**
- closing_balance = opening_balance + inflows - outflows
- projected_balance = closing_balance + accounts_receivable - accounts_payable

### 3. calculate_break_even()
Ponto de Equilibrio

**Inputs:** fixed_costs, contribution_margin_percent, target_profit
**Formulas:**
- break_even_revenue = fixed_costs / (contribution_margin / 100)
- break_even_with_profit = (fixed_costs + target_profit) / (contribution_margin / 100)
**Validation:** contribution_margin_percent must be > 0

### 4. calculate_operational_cycle()
Ciclo Operacional

**Inputs:** average_inventory_days, average_receivable_days
**Formula:** operational_cycle = average_inventory_days + average_receivable_days

### 5. calculate_financial_cycle()
Ciclo Financeiro

**Inputs:** average_inventory_days, average_receivable_days, average_payable_days
**Formulas:**
- operational_cycle = average_inventory_days + average_receivable_days
- financial_cycle = operational_cycle - average_payable_days
**Warning:** If financial_cycle is negative, adds informational warning

### 6. calculate_minimum_cash()
Caixa Minimo

**Inputs:** daily_cash_need, financial_cycle_days, safety_days
**Formulas:**
- minimum_cash = daily_cash_need * financial_cycle_days
- recommended_reserve = daily_cash_need * (financial_cycle_days + safety_days)
**Default:** safety_days = financial_cycle_days * 0.5 if not provided

## Return Format

All functions return:
```json
{
  "success": true/false,
  "module": "dre",
  "scope": "grupsbunny",
  "source": "manual_input",
  "validation_status": "pending_validation",
  "data": { ... },
  "warnings": [],
  "token_exposed": false
}
```

## Safety Rules

- Never divide by zero
- Never accept negative values in fields that don't allow them
- Never return values as "real" without explicit source
- Always return validation_status
- Missing fields get warnings, not errors (except required fields)
