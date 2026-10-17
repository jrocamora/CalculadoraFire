"""
Plan serialization and deserialization for URL sharing and local JSON export/import.
Guarantees 100% client-side privacy: all calculations and data stay local to the user's browser.
"""
from __future__ import annotations

import base64
import json
import zlib
from typing import Any

from models.types import MacroScenario, PensionSettings, PortfolioAsset, TaxSettings


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
    """Applies a decoded plan dictionary into the Streamlit session state."""
    try:
        if "mode" in plan:
            session_state.mode = plan["mode"]
        if "target_monthly_income" in plan:
            session_state.target_monthly_income = float(plan["target_monthly_income"])
        if "current_age" in plan:
            session_state.current_age = int(plan["current_age"])
        if "target_retirement_age" in plan:
            session_state.target_retirement_age = int(plan["target_retirement_age"])
        if "life_expectancy" in plan:
            session_state.life_expectancy = int(plan["life_expectancy"])
        if "monthly_savings" in plan:
            session_state.monthly_savings = float(plan["monthly_savings"])
        if "annual_savings_increase_rate" in plan:
            session_state.annual_savings_increase_rate = float(plan["annual_savings_increase_rate"])
        if "safe_withdrawal_rate" in plan:
            session_state.safe_withdrawal_rate = float(plan["safe_withdrawal_rate"])

        if "assets" in plan and isinstance(plan["assets"], list):
            session_state.assets = [
                PortfolioAsset(
                    id=a.get("id", f"asset-{i}"),
                    category=a.get("category", "index_funds"),
                    name=a.get("name", "Asset"),
                    current_amount=float(a.get("current_amount", 0.0)),
                    expected_return_annual=float(a.get("expected_return_annual", 7.0)),
                    cost_basis=float(a.get("cost_basis", 0.0)),
                )
                for i, a in enumerate(plan["assets"])
            ]

        if "pension_settings" in plan:
            ps = plan["pension_settings"]
            session_state.pension_settings = PensionSettings(
                private_pension_enabled=bool(ps.get("private_pension_enabled", True)),
                private_pension_balance=float(ps.get("private_pension_balance", 0.0)),
                private_pension_monthly_contribution=float(ps.get("private_pension_monthly_contribution", 0.0)),
                private_pension_expected_return=float(ps.get("private_pension_expected_return", 7.0)),
                private_pension_access_age=int(ps.get("private_pension_access_age", 50)),
                private_pension_tax_free_lump_sum_pct=float(ps.get("private_pension_tax_free_lump_sum_pct", 25.0)),
                my_future_fund_enabled=bool(ps.get("my_future_fund_enabled", True)),
                my_future_fund_balance=float(ps.get("my_future_fund_balance", 0.0)),
                my_future_fund_employee_monthly=float(ps.get("my_future_fund_employee_monthly", 0.0)),
                my_future_fund_employer_match_monthly=float(ps.get("my_future_fund_employer_match_monthly", 0.0)),
                my_future_fund_state_topup_monthly=float(ps.get("my_future_fund_state_topup_monthly", 0.0)),
                my_future_fund_expected_return=float(ps.get("my_future_fund_expected_return", 7.0)),
                my_future_fund_access_age=int(ps.get("my_future_fund_access_age", 66)),
                my_future_fund_tax_free_lump_sum_pct=float(ps.get("my_future_fund_tax_free_lump_sum_pct", 25.0)),
            )

        if "tax_settings" in plan:
            ts = plan["tax_settings"]
            session_state.tax_settings = TaxSettings(
                country="IE",
                ireland_asset_type=ts.get("ireland_asset_type", "budget_2027_account"),
                ireland_simulate_deemed_disposal=bool(ts.get("ireland_simulate_deemed_disposal", True)),
                ireland_deemed_disposal_mode=ts.get("ireland_deemed_disposal_mode", "staggered_rolling_eighth"),
                ireland_exit_tax_rate=float(ts.get("ireland_exit_tax_rate", 35.0)),
                ireland_cgt_rate=float(ts.get("ireland_cgt_rate", 31.0)),
                ireland_investment_account_threshold=float(ts.get("ireland_investment_account_threshold", 50000.0)),
                ireland_investment_account_rate=float(ts.get("ireland_investment_account_rate", 1.0)),
                catalonia_capital_gains_ratio=50.0,
                catalonia_apply_wealth_tax=False,
                andorra_exempt_listed_securities=True,
                tax_reform_change_rate=float(ts.get("tax_reform_change_rate", 0.0)),
                planned_relocation_country="none",
                planned_relocation_year=None,
            )

        if "scenario" in plan:
            sc = plan["scenario"]
            session_state.scenario = MacroScenario(
                id=sc.get("id", "base"),
                name=sc.get("name", "Base Scenario"),
                description=sc.get("description", ""),
                nominal_return=float(sc.get("nominal_return", 7.0)),
                inflation_rate=float(sc.get("inflation_rate", 2.5)),
                stress_drop_first_years=sc.get("stress_drop_first_years"),
            )
        return True
    except Exception:
        return False
