"""
Plan serialization and deserialization for URL sharing and local JSON export/import.
The plan lives in the link or the file the user keeps; the app does not persist it.
Loaded values are clamped to the ranges the input widgets accept, so a hand-edited
link or file cannot crash the page.
"""
from __future__ import annotations

import base64
import json
import zlib
from typing import Any

from models.types import MacroScenario, PensionSettings, PortfolioAsset, TaxSettings


def _num(value: Any, lo: float, hi: float, default: float) -> float:
    """Parses a number and clamps it to [lo, hi]; falls back to `default` if it is not a finite number."""
    try:
        val = float(value)
    except (TypeError, ValueError):
        return default
    if val != val or val in (float("inf"), float("-inf")):
        return default
    return min(hi, max(lo, val))


def plan_to_dict(
    mode: str,
    target_monthly_income: float,
    current_age: int,
    target_retirement_age: int,
    life_expectancy: int,
    monthly_savings: float,
    annual_savings_increase_rate: float,
    safe_withdrawal_rate: float,
    assets: list[PortfolioAsset],
    pension_settings: PensionSettings,
    tax_settings: TaxSettings,
    scenario: MacroScenario,
) -> dict[str, Any]:
    """Serializes the complete FIRE calculator state into a clean dictionary."""
    return {
        "version": 1,
        "mode": mode,
        "target_monthly_income": float(target_monthly_income),
        "current_age": int(current_age),
        "target_retirement_age": int(target_retirement_age),
        "life_expectancy": int(life_expectancy),
        "monthly_savings": float(monthly_savings),
        "annual_savings_increase_rate": float(annual_savings_increase_rate),
        "safe_withdrawal_rate": float(safe_withdrawal_rate),
        "assets": [
            {
                "id": a.id,
                "category": a.category,
                "name": a.name,
                "current_amount": float(a.current_amount),
                "expected_return_annual": float(a.expected_return_annual),
                "cost_basis": float(a.cost_basis),
            }
            for a in assets
        ],
        "pension_settings": {
            "private_pension_enabled": pension_settings.private_pension_enabled,
            "private_pension_balance": float(pension_settings.private_pension_balance),
            "private_pension_monthly_contribution": float(pension_settings.private_pension_monthly_contribution),
            "private_pension_expected_return": float(pension_settings.private_pension_expected_return),
            "private_pension_access_age": int(pension_settings.private_pension_access_age),
            "private_pension_tax_free_lump_sum_pct": float(pension_settings.private_pension_tax_free_lump_sum_pct),
            "my_future_fund_enabled": pension_settings.my_future_fund_enabled,
            "my_future_fund_balance": float(pension_settings.my_future_fund_balance),
            "my_future_fund_employee_monthly": float(pension_settings.my_future_fund_employee_monthly),
            "my_future_fund_employer_match_monthly": float(pension_settings.my_future_fund_employer_match_monthly),
            "my_future_fund_state_topup_monthly": float(pension_settings.my_future_fund_state_topup_monthly),
            "my_future_fund_expected_return": float(pension_settings.my_future_fund_expected_return),
            "my_future_fund_access_age": int(pension_settings.my_future_fund_access_age),
            "my_future_fund_tax_free_lump_sum_pct": float(pension_settings.my_future_fund_tax_free_lump_sum_pct),
            "state_pension_enabled": bool(getattr(pension_settings, "state_pension_enabled", True)),
            "state_pension_monthly_amount": float(getattr(pension_settings, "state_pension_monthly_amount", 1253.0)),
            "state_pension_access_age": int(getattr(pension_settings, "state_pension_access_age", 66)),
            "pension_income_tax_rate": float(getattr(pension_settings, "pension_income_tax_rate", 20.0)),
        },
        "tax_settings": {
            "country": tax_settings.country,
            "ireland_asset_type": tax_settings.ireland_asset_type,
            "ireland_simulate_deemed_disposal": tax_settings.ireland_simulate_deemed_disposal,
            "ireland_deemed_disposal_mode": tax_settings.ireland_deemed_disposal_mode,
            "ireland_exit_tax_rate": float(getattr(tax_settings, "ireland_exit_tax_rate", 35.0)),
            "ireland_cgt_rate": float(getattr(tax_settings, "ireland_cgt_rate", 31.0)),
            "ireland_investment_account_threshold": float(getattr(tax_settings, "ireland_investment_account_threshold", 50000.0)),
            "ireland_investment_account_rate": float(getattr(tax_settings, "ireland_investment_account_rate", 1.0)),
            "tax_reform_change_rate": float(tax_settings.tax_reform_change_rate or 0.0),
        },
        "scenario": {
            "id": scenario.id,
            "name": scenario.name,
            "description": scenario.description,
            "nominal_return": float(scenario.nominal_return),
            "inflation_rate": float(scenario.inflation_rate),
            "stress_drop_first_years": float(scenario.stress_drop_first_years) if scenario.stress_drop_first_years else None,
        },
    }


def encode_plan_to_token(plan_dict: dict[str, Any]) -> str:
    """Compresses and base64url-encodes a plan dict for inclusion in URL query params."""
    raw_json = json.dumps(plan_dict, separators=(",", ":")).encode("utf-8")
    compressed = zlib.compress(raw_json, level=9)
    return base64.urlsafe_b64encode(compressed).decode("ascii")


def decode_token_to_plan(token: str) -> dict[str, Any] | None:
    """Decodes and decompresses a plan token from URL query params. Returns None if invalid."""
    try:
        compressed = base64.urlsafe_b64decode(token.strip().encode("ascii"))
        raw_json = zlib.decompress(compressed).decode("utf-8")
        return json.loads(raw_json)
    except Exception:
        return None


def dict_to_session_state(plan: dict[str, Any], session_state) -> bool:
    """Applies a decoded plan dictionary into the Streamlit session state.

    Only the model objects are written. The caller must call `ui.keys.reset_widgets()`
    afterwards so the input widgets pick the new values up.
    """
    try:
        if not isinstance(plan, dict):
            return False
        if plan.get("mode") in ("target_spending", "current_portfolio"):
            session_state.mode = plan["mode"]
        if "target_monthly_income" in plan:
            session_state.target_monthly_income = _num(plan["target_monthly_income"], 500, 30000, 2500.0)
        if "current_age" in plan:
            session_state.current_age = int(_num(plan["current_age"], 18, 90, 32))
        if "target_retirement_age" in plan:
            session_state.target_retirement_age = int(_num(plan["target_retirement_age"], 18, 95, 48))
        if "life_expectancy" in plan:
            session_state.life_expectancy = int(_num(plan["life_expectancy"], 75, 110, 88))
        if "monthly_savings" in plan:
            session_state.monthly_savings = _num(plan["monthly_savings"], 0, 50000, 900.0)
        if "annual_savings_increase_rate" in plan:
            session_state.annual_savings_increase_rate = _num(plan["annual_savings_increase_rate"], 0, 15, 2.0)
        if "safe_withdrawal_rate" in plan:
            session_state.safe_withdrawal_rate = _num(plan["safe_withdrawal_rate"], 2.5, 5.5, 3.5)

        valid_categories = (
            "budget_2027_account", "index_funds", "individual_stocks", "cash_deposits", "real_estate_other",
        )
        if "assets" in plan and isinstance(plan["assets"], list):
            loaded_assets = []
            for i, a in enumerate(plan["assets"][:20]):
                if not isinstance(a, dict) or a.get("category") not in valid_categories:
                    continue
                amount = _num(a.get("current_amount"), 0, 20_000_000, 0.0)
                loaded_assets.append(
                    PortfolioAsset(
                        id=f"asset-{i}",
                        category=a["category"],
                        name=str(a.get("name", "Asset"))[:80],
                        current_amount=amount,
                        expected_return_annual=_num(a.get("expected_return_annual"), -5, 25, 7.0),
                        cost_basis=_num(a.get("cost_basis"), 0, 20_000_000, amount),
                    )
                )
            if loaded_assets:
                session_state.assets = loaded_assets

        if isinstance(plan.get("pension_settings"), dict):
            ps = plan["pension_settings"]
            session_state.pension_settings = PensionSettings(
                private_pension_enabled=bool(ps.get("private_pension_enabled", False)),
                private_pension_balance=_num(ps.get("private_pension_balance"), 0, 10_000_000, 0.0),
                private_pension_monthly_contribution=_num(ps.get("private_pension_monthly_contribution"), 0, 20000, 0.0),
                private_pension_expected_return=_num(ps.get("private_pension_expected_return"), 0, 15, 7.0),
                private_pension_access_age=int(_num(ps.get("private_pension_access_age"), 50, 65, 50)),
                private_pension_tax_free_lump_sum_pct=25.0,
                my_future_fund_enabled=bool(ps.get("my_future_fund_enabled", False)),
                my_future_fund_balance=_num(ps.get("my_future_fund_balance"), 0, 5_000_000, 0.0),
                my_future_fund_employee_monthly=_num(ps.get("my_future_fund_employee_monthly"), 0, 4000, 0.0),
                my_future_fund_employer_match_monthly=_num(ps.get("my_future_fund_employer_match_monthly"), 0, 4000, 0.0),
                my_future_fund_state_topup_monthly=_num(ps.get("my_future_fund_state_topup_monthly"), 0, 4000, 0.0),
                my_future_fund_expected_return=_num(ps.get("my_future_fund_expected_return"), 0, 15, 7.0),
                my_future_fund_access_age=66,
                my_future_fund_tax_free_lump_sum_pct=25.0,
                state_pension_enabled=bool(ps.get("state_pension_enabled", False)),
                state_pension_monthly_amount=_num(ps.get("state_pension_monthly_amount"), 0, 15000, 1253.0),
                state_pension_access_age=int(_num(ps.get("state_pension_access_age"), 65, 70, 66)),
                pension_income_tax_rate=_num(ps.get("pension_income_tax_rate"), 0, 55, 20.0),
            )

        if isinstance(plan.get("tax_settings"), dict):
            ts = plan["tax_settings"]
            asset_type = ts.get("ireland_asset_type")
            if asset_type not in ("budget_2027_account", "etf_exit_tax", "individual_shares_cgt"):
                asset_type = "budget_2027_account"
            dd_mode = ts.get("ireland_deemed_disposal_mode")
            if dd_mode not in ("staggered_rolling_eighth", "lump_sum_8y"):
                dd_mode = "staggered_rolling_eighth"
            session_state.tax_settings = TaxSettings(
                country="IE",
                ireland_asset_type=asset_type,
                ireland_simulate_deemed_disposal=bool(ts.get("ireland_simulate_deemed_disposal", True)),
                ireland_deemed_disposal_mode=dd_mode,
                ireland_exit_tax_rate=_num(ts.get("ireland_exit_tax_rate"), 20, 45, 35.0),
                ireland_cgt_rate=_num(ts.get("ireland_cgt_rate"), 20, 40, 31.0),
                ireland_investment_account_threshold=_num(ts.get("ireland_investment_account_threshold"), 0, 200000, 50000.0),
                ireland_investment_account_rate=_num(ts.get("ireland_investment_account_rate"), 0, 5, 1.0),
                catalonia_capital_gains_ratio=50.0,
                catalonia_apply_wealth_tax=False,
                andorra_exempt_listed_securities=True,
                tax_reform_change_rate=_num(ts.get("tax_reform_change_rate"), -5, 10, 0.0),
                planned_relocation_country="none",
                planned_relocation_year=None,
            )

        if isinstance(plan.get("scenario"), dict):
            sc = plan["scenario"]
            scenario_id = sc.get("id")
            if scenario_id not in ("base", "optimistic", "conservative", "stress_test", "custom"):
                scenario_id = "custom"
            stress = sc.get("stress_drop_first_years")
            session_state.scenario = MacroScenario(
                id=scenario_id,
                name=str(sc.get("name", "Scenario"))[:80],
                description=str(sc.get("description", ""))[:300],
                nominal_return=_num(sc.get("nominal_return"), 2, 15, 7.0),
                inflation_rate=_num(sc.get("inflation_rate"), 0.5, 8, 2.5),
                stress_drop_first_years=_num(stress, 0, 90, 0.0) or None if stress is not None else None,
            )
        return True
    except Exception:
        return False
