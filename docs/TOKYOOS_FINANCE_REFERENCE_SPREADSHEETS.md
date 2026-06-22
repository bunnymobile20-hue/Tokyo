# TokyoOS Finance Reference Spreadsheets

## Overview

The TokyoOS financial module was designed based on reference spreadsheets provided by GrupsBunny. These spreadsheets are treated as **business models**, not as actual financial data.

## Reference Files

The following files (located in `reference_materials/finance/`) were used as structural references:

| # | File | Purpose |
|---|---|---|
| 1 | Modelo+de+DRE.xlsx | DRE (Income Statement) template |
| 2 | Estrutura+de+DRE.xlsx | DRE detailed structure |
| 3 | Estrutura+de+Fluxo+de+Caixa.xlsx | Cash Flow structure |
| 4 | Ponto de Equilibrio.xlsx | Break Even analysis template |
| 5 | Ciclo Operaciona, Financeiro e Caixa Minimo.xlsx | Operational/Financial Cycle analysis |
| 6 | Ciclo Operaciona, Financeiro e Caixa Minimo (1).xlsx | Minimum Cash calculation |

## What Was Extracted

From each spreadsheet, the following was analyzed to create the financial module schemas:

- Sheet/tab names and structure
- Column headers and field names
- Categories (revenue, costs, expenses, etc.)
- Formulas and relationships between fields
- Period groupings (daily, weekly, monthly)

## What Was NOT Done

- No spreadsheet content was copied as real data
- No values from spreadsheets were used as actual financial figures
- No spreadsheets were modified, overwritten, or deleted
- No financial values were fabricated

## Policy

1. These files are reference/business models only
2. No alterations to original files
3. No overwrite of original files
4. No use of values as real company data
5. Names, tabs, categories, fields, and financial logic used ONLY for schema design

## Result

The financial module schemas (config/finance_models.example.json) contain:
- Field names derived from spreadsheet structures
- Planned formulas derived from spreadsheet logic
- All fields marked `data_source: pending_api`
- All models marked `status: planned`
- No actual financial values

The dashboard UI shows placeholder messages, never fake numbers.
