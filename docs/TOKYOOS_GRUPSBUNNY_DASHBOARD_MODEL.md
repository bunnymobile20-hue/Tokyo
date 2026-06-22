# TokyoOS GrupsBunny Dashboard Model

## Overview

The GrupsBunny Dashboard is the central business intelligence hub of TokyoOS.

## Business Structure

### GrupsBunny (Holding)
TokyoOS is the core app/hub of GrupsBunny.

### Bunny Dreams (Retail)
- **Type**: Varejo
- **Units**:
  - Loja Riverside
  - Loja Teresina
- **Modules**: Daily sales, monthly sales, targets, gaps, average ticket, calendar, tasks, stock, critical products, financial DRE, cash flow, break even, minimum cash, alerts, Tokyo IA recommendations

### Bunny Siberian (Systems Company)
- **Type**: Empresa de sistemas
- **Business Model**: Recurring Revenue (SaaS/ERP)
- **Revenue Streams**: MRR, implementation fees, support contracts
- **Metrics**: MRR, churn rate, LTV, CAC, ARPU
- **Modules**: Overview, recurring revenue, active clients, MRR, churn, support tickets, implementation, sales funnel, sold modules, API status, Siberian ERP status

### Sistema Siberian ERP (Own Product)
- **Type**: ERP system
- **Usage**: Internal (Bunny Dreams stores) + Sold to external companies via Bunny Siberian
- **Modules**: Companies, stores, sales, products, stock, finance, clients, users, reports, recurring, support

## Dashboard Status

All dashboards currently show `data_source: pending_api` with placeholder messages:
> "Dados ainda nao conectados. Configure Sistema Siberian API ou importe planilhas autorizadas."

**No fake data is displayed.**

## Future Integration

When Sistema Siberian API is connected:
- Bunny Dreams dashboards will show real sales data
- Bunny Siberian dashboards will show real MRR/churn
- Financial dashboards will populate from ERP data
- Tokyo IA will provide business recommendations based on real data

## Dashboard Tabs (UI)

| Tab | Content |
|---|---|
| Visao Geral | Voice, LLM, Security, Doctor, System status |
| GrupsBunny | Bunny Dreams, Riverside, Teresina, Bunny Siberian, Sistema Siberian |
| Financeiro | DRE, Cash Flow, Break Even, Financial Cycle, Minimum Cash |
| Integracoes | API Hub, Providers, Connectors |
| Sistema | Docker/ZimaOS, Hardware, Updates, Storage |
