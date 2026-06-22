# TokyoOS Financial Dashboard Model

## Overview

The Financial Dashboard is a planned module within the GrupsBunny dashboard. It provides consolidated financial views across all business units.

## Modules Planned

### 1. DRE (Demonstrativo do Resultado do Exercicio)

| Field | Type |
|---|---|
| Receita Bruta | currency |
| Deducoes | currency |
| Receita Liquida | currency |
| CMV / Custo | currency |
| Margem Bruta | percentage |
| Despesas Fixas | currency |
| Despesas Variaveis | currency |
| Resultado Operacional | currency |
| Lucro/Prejuizo | currency |

Scope: GrupsBunny, Bunny Dreams, Riverside, Teresina, Bunny Siberian

### 2. Fluxo de Caixa (Cash Flow)

| Field | Type |
|---|---|
| Saldo Inicial | currency |
| Entradas | currency |
| Saidas | currency |
| Saldo Final | currency |
| Contas a Pagar | currency |
| Contas a Receber | currency |
| Projecao de Caixa | currency |

Periods: Daily, Weekly, Monthly

### 3. Ponto de Equilibrio (Break Even)

| Field | Type |
|---|---|
| Custos Fixos | currency |
| Margem de Contribuicao | percentage |
| Faturamento Minimo (PE) | currency |
| Lucro Desejado | currency |
| Faturamento com Lucro Desejado | currency |

### 4. Ciclo Financeiro (Financial Cycle)

| Field | Type |
|---|---|
| Prazo Medio de Estoque | days |
| Prazo Medio de Recebimento | days |
| Prazo Medio de Pagamento | days |
| Ciclo Operacional | days |
| Ciclo Financeiro | days |
| Necessidade de Capital de Giro | currency |

### 5. Caixa Minimo (Minimum Cash)

| Field | Type |
|---|---|
| Despesa Media Diaria | currency |
| Dias de Seguranca | number |
| Caixa Minimo Recomendado | currency |
| Reserva Recomendada | currency |

## Data Source

- **Primary**: Sistema Siberian ERP API (not connected)
- **Future**: Spreadsheet upload via Bunny Intelligence Bank
- **Current**: `data_source: pending_api`

## Reference Spreadsheets

The following spreadsheets are used as **business model references only**:

| File | Model Reference |
|---|---|
| Modelo+de+DRE.xlsx | DRE structure |
| Estrutura+de+DRE.xlsx | DRE detailed structure |
| Estrutura+de+Fluxo+de+Caixa.xlsx | Cash Flow structure |
| Ponto de Equilibrio.xlsx | Break Even structure |
| Ciclo Operaciona, Financeiro e Caixa Minimo.xlsx | Operational/Financial Cycle |
| Ciclo Operaciona, Financeiro e Caixa Minimo (1).xlsx | Minimum Cash |

**Important**: These files contain template structures, not real financial data. They are used to define the schema of the financial module, not to populate it with actual values.

## Placeholder Message

When no data is connected, the dashboard shows:
> "Dados financeiros ainda nao conectados. Configure Sistema Siberian API ou importe planilhas autorizadas."

## Future: Spreadsheet Upload

Planned area: **Bunny Intelligence Bank > Planilhas Financeiras**

Status: `upload_pending`, `parser_pending`

Accepted formats: xlsx, csv, ods

Accepted sheet types: DRE, Cash Flow, Accounts Payable, Accounts Receivable, Sales, Stock, Financial Cycle, Break Even
