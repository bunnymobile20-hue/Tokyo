"""
TokyoOS Financial Calculation Engine
Read-only, pure functions. No external API calls. No side effects.

All calculations return:
- success: bool
- data_source/source: where data came from
- validation_status: pending_validation | validated | warning
- module: which module this belongs to
- scope: business scope
- warnings: list of strings
- token_exposed: false
"""

from typing import Optional


def _safe_float(val, default=None):
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def calculate_dre(
    gross_revenue=None,
    deductions=None,
    cogs=None,
    fixed_expenses=None,
    variable_expenses=None,
    source="manual_input",
    scope="grupsbunny",
):
    """
    DRE — Demonstrativo do Resultado do Exercicio
    """
    warnings = []
    data = {}
    gross_revenue = _safe_float(gross_revenue)
    deductions = _safe_float(deductions)
    cogs = _safe_float(cogs)
    fixed_expenses = _safe_float(fixed_expenses)
    variable_expenses = _safe_float(variable_expenses)

    if gross_revenue is None:
        return {
            "success": False,
            "module": "dre",
            "scope": scope,
            "source": source,
            "validation_status": "pending_validation",
            "data": {},
            "warnings": ["gross_revenue is required"],
            "token_exposed": False,
        }

    data["gross_revenue"] = gross_revenue
    data["deductions"] = deductions or 0.0
    data["net_revenue"] = gross_revenue - (deductions or 0.0)
    data["cogs"] = cogs or 0.0
    data["gross_profit"] = data["net_revenue"] - (cogs or 0.0)
    data["fixed_expenses"] = fixed_expenses or 0.0
    data["variable_expenses"] = variable_expenses or 0.0
    data["operating_result"] = data["gross_profit"] - (fixed_expenses or 0.0) - (variable_expenses or 0.0)
    data["net_result"] = data["operating_result"]

    if deductions is None:
        warnings.append("deductions not provided, assuming 0")
    if cogs is None:
        warnings.append("cogs not provided, assuming 0")
    if fixed_expenses is None:
        warnings.append("fixed_expenses not provided, assuming 0")
    if variable_expenses is None:
        warnings.append("variable_expenses not provided, assuming 0")

    status = "pending_validation" if warnings else "pending_validation"

    return {
        "success": True,
        "module": "dre",
        "scope": scope,
        "source": source,
        "validation_status": status,
        "data": data,
        "warnings": warnings,
        "token_exposed": False,
    }


def calculate_cash_flow(
    opening_balance=None,
    inflows=None,
    outflows=None,
    accounts_receivable=None,
    accounts_payable=None,
    source="manual_input",
    scope="grupsbunny",
):
    """
    Fluxo de Caixa — Cash Flow
    """
    warnings = []
    opening_balance = _safe_float(opening_balance)
    inflows = _safe_float(inflows)
    outflows = _safe_float(outflows)
    accounts_receivable = _safe_float(accounts_receivable)
    accounts_payable = _safe_float(accounts_payable)

    if opening_balance is None:
        return {
            "success": False,
            "module": "cash_flow",
            "scope": scope,
            "source": source,
            "validation_status": "pending_validation",
            "data": {},
            "warnings": ["opening_balance is required"],
            "token_exposed": False,
        }

    data = {
        "opening_balance": opening_balance,
        "inflows": inflows or 0.0,
        "outflows": outflows or 0.0,
        "closing_balance": opening_balance + (inflows or 0.0) - (outflows or 0.0),
        "accounts_receivable": accounts_receivable or 0.0,
        "accounts_payable": accounts_payable or 0.0,
    }
    data["projected_balance"] = data["closing_balance"] + (accounts_receivable or 0.0) - (accounts_payable or 0.0)

    if inflows is None:
        warnings.append("inflows not provided, assuming 0")
    if outflows is None:
        warnings.append("outflows not provided, assuming 0")

    return {
        "success": True,
        "module": "cash_flow",
        "scope": scope,
        "source": source,
        "validation_status": "pending_validation",
        "data": data,
        "warnings": warnings,
        "token_exposed": False,
    }


def calculate_break_even(
    fixed_costs=None,
    contribution_margin_percent=None,
    target_profit=None,
    source="manual_input",
    scope="grupsbunny",
):
    """
    Ponto de Equilibrio — Break Even Point
    """
    warnings = []
    fixed_costs = _safe_float(fixed_costs)
    contribution_margin_percent = _safe_float(contribution_margin_percent)
    target_profit = _safe_float(target_profit)

    if fixed_costs is None:
        return {
            "success": False,
            "module": "break_even",
            "scope": scope,
            "source": source,
            "validation_status": "pending_validation",
            "data": {},
            "warnings": ["fixed_costs is required"],
            "token_exposed": False,
        }

    if contribution_margin_percent is None or contribution_margin_percent <= 0:
        return {
            "success": False,
            "module": "break_even",
            "scope": scope,
            "source": source,
            "validation_status": "pending_validation",
            "data": {},
            "warnings": ["contribution_margin_percent must be > 0"],
            "token_exposed": False,
        }

    margin = contribution_margin_percent / 100.0
    data = {
        "fixed_costs": fixed_costs,
        "contribution_margin_percent": contribution_margin_percent,
        "break_even_revenue": round(fixed_costs / margin, 2),
        "target_profit": target_profit or 0.0,
        "break_even_with_profit": round((fixed_costs + (target_profit or 0.0)) / margin, 2),
    }

    if target_profit is None:
        warnings.append("target_profit not provided, assuming 0")

    return {
        "success": True,
        "module": "break_even",
        "scope": scope,
        "source": source,
        "validation_status": "pending_validation",
        "data": data,
        "warnings": warnings,
        "token_exposed": False,
    }


def calculate_operational_cycle(
    average_inventory_days=None,
    average_receivable_days=None,
    source="manual_input",
    scope="grupsbunny",
):
    """
    Ciclo Operacional — Operational Cycle
    """
    warnings = []
    average_inventory_days = _safe_float(average_inventory_days)
    average_receivable_days = _safe_float(average_receivable_days)

    if average_inventory_days is None:
        return {
            "success": False,
            "module": "operational_cycle",
            "scope": scope,
            "source": source,
            "validation_status": "pending_validation",
            "data": {},
            "warnings": ["average_inventory_days is required"],
            "token_exposed": False,
        }

    if average_receivable_days is None:
        return {
            "success": False,
            "module": "operational_cycle",
            "scope": scope,
            "source": source,
            "validation_status": "pending_validation",
            "data": {},
            "warnings": ["average_receivable_days is required"],
            "token_exposed": False,
        }

    data = {
        "average_inventory_days": average_inventory_days,
        "average_receivable_days": average_receivable_days,
        "operational_cycle": round(average_inventory_days + average_receivable_days, 1),
    }

    return {
        "success": True,
        "module": "operational_cycle",
        "scope": scope,
        "source": source,
        "validation_status": "pending_validation",
        "data": data,
        "warnings": warnings,
        "token_exposed": False,
    }


def calculate_financial_cycle(
    average_inventory_days=None,
    average_receivable_days=None,
    average_payable_days=None,
    source="manual_input",
    scope="grupsbunny",
):
    """
    Ciclo Financeiro — Financial Cycle
    """
    warnings = []
    average_inventory_days = _safe_float(average_inventory_days)
    average_receivable_days = _safe_float(average_receivable_days)
    average_payable_days = _safe_float(average_payable_days)

    if average_inventory_days is None or average_receivable_days is None:
        return {
            "success": False,
            "module": "financial_cycle",
            "scope": scope,
            "source": source,
            "validation_status": "pending_validation",
            "data": {},
            "warnings": ["average_inventory_days and average_receivable_days are required"],
            "token_exposed": False,
        }

    apd = average_payable_days or 0.0
    operational = average_inventory_days + average_receivable_days
    financial = operational - apd

    if financial < 0:
        warnings.append(f"financial_cycle is negative ({financial:.1f} days). Company may be receiving before paying suppliers — this can be positive if sustainable.")

    data = {
        "average_inventory_days": average_inventory_days,
        "average_receivable_days": average_receivable_days,
        "average_payable_days": apd,
        "operational_cycle": round(operational, 1),
        "financial_cycle": round(financial, 1),
    }

    return {
        "success": True,
        "module": "financial_cycle",
        "scope": scope,
        "source": source,
        "validation_status": "pending_validation",
        "data": data,
        "warnings": warnings,
        "token_exposed": False,
    }


def calculate_minimum_cash(
    daily_cash_need=None,
    financial_cycle_days=None,
    safety_days=None,
    source="manual_input",
    scope="grupsbunny",
):
    """
    Caixa Minimo — Minimum Cash Reserve
    """
    warnings = []
    daily_cash_need = _safe_float(daily_cash_need)
    financial_cycle_days = _safe_float(financial_cycle_days)
    safety_days = _safe_float(safety_days)

    if daily_cash_need is None:
        return {
            "success": False,
            "module": "minimum_cash",
            "scope": scope,
            "source": source,
            "validation_status": "pending_validation",
            "data": {},
            "warnings": ["daily_cash_need is required"],
            "token_exposed": False,
        }

    if financial_cycle_days is None:
        return {
            "success": False,
            "module": "minimum_cash",
            "scope": scope,
            "source": source,
            "validation_status": "pending_validation",
            "data": {},
            "warnings": ["financial_cycle_days is required"],
            "token_exposed": False,
        }

    if safety_days is None:
        safety_days = financial_cycle_days * 0.5
        warnings.append(f"safety_days not provided, calculated as 50% of financial_cycle = {safety_days:.1f} days")

    data = {
        "daily_cash_need": daily_cash_need,
        "financial_cycle_days": financial_cycle_days,
        "safety_days": round(safety_days, 1),
        "minimum_cash": round(daily_cash_need * financial_cycle_days, 2),
        "recommended_reserve": round(daily_cash_need * (financial_cycle_days + safety_days), 2),
    }

    return {
        "success": True,
        "module": "minimum_cash",
        "scope": scope,
        "source": source,
        "validation_status": "pending_validation",
        "data": data,
        "warnings": warnings,
        "token_exposed": False,
    }
