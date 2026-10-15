"""
Constants and default configuration values for the FIRE calculator.
Port faithful to src/App.tsx and component presets.
"""
from __future__ import annotations

from datetime import datetime
from models.types import MacroScenario, PensionSettings, PortfolioAsset, TaxSettings


def get_current_year() -> int:
    return datetime.now().year


def get_initial_pension_settings() -> PensionSettings:
    return PensionSettings(
        private_pension_enabled=True,
        private_pension_balance=45000.0,
        private_pension_monthly_contribution=500.0,
        private_pension_expected_return=7.0,
        private_pension_access_age=50,
        private_pension_tax_free_lump_sum_pct=25.0,
        my_future_fund_enabled=True,
        my_future_fund_balance=12000.0,
        my_future_fund_employee_monthly=200.0,
        my_future_fund_employer_match_monthly=200.0,
        my_future_fund_state_topup_monthly=66.67,
        my_future_fund_expected_return=7.0,
        my_future_fund_access_age=66,
        my_future_fund_tax_free_lump_sum_pct=25.0,
    )


def get_initial_assets() -> list[PortfolioAsset]:
    return [
        PortfolioAsset(
            id="asset-1",
            category="index_funds",
            name="Global Index Funds / UCITS ETFs",
            current_amount=65000.0,
            expected_return_annual=7.0,
            cost_basis=45000.0,
        ),
        PortfolioAsset(
            id="asset-2",
            category="individual_stocks",
            name="Individual Equities (Stocks)",
            current_amount=18000.0,
            expected_return_annual=7.0,
            cost_basis=12000.0,
        ),
        PortfolioAsset(
            id="asset-3",
            category="cash_deposits",
            name="Cash Deposits & Savings Accounts",
            current_amount=12000.0,
            expected_return_annual=3.0,
            cost_basis=12000.0,
        ),
        PortfolioAsset(
            id="asset-4",
            category="private_pension",
            name="Private Pension (PRSA / Workplace)",
            current_amount=45000.0,
            expected_return_annual=7.0,
            cost_basis=45000.0,
        ),
        PortfolioAsset(
            id="asset-5",
            category="my_future_fund",
            name="MyFutureFund (Auto-Enrolment)",
            current_amount=12000.0,
            expected_return_annual=7.0,
            cost_basis=12000.0,
        ),
        PortfolioAsset(
            id="asset-6",
            category="real_estate_other",
            name="Real Estate / Alternatives",
            current_amount=5000.0,
            expected_return_annual=5.5,
            cost_basis=5000.0,
        ),
    ]


def get_initial_tax_settings() -> TaxSettings:
    return TaxSettings(
        country="IE",
        ireland_asset_type="budget_2027_account",
        ireland_simulate_deemed_disposal=True,
        ireland_deemed_disposal_mode="staggered_rolling_eighth",
        ireland_exit_tax_rate=35.0,
        ireland_cgt_rate=31.0,
        ireland_investment_account_threshold=50000.0,
        ireland_investment_account_rate=1.0,
        catalonia_capital_gains_ratio=50.0,
        catalonia_apply_wealth_tax=False,
        andorra_exempt_listed_securities=True,
        tax_reform_change_rate=0.0,
        planned_relocation_country="none",
        planned_relocation_year=get_current_year() + 10,
    )



def get_initial_scenario() -> MacroScenario:
    return MacroScenario(
        id="base",
        name="Escenari Base",
        description="Rendiment històric mitjà de mercat global i inflació moderada.",
        nominal_return=7.0,
        inflation_rate=2.5,
    )


MACRO_PRESETS: dict[str, dict] = {
    "base": {
        "nominal_return": 7.0,
        "inflation_rate": 2.5,
        "stress_drop_first_years": None,
    },
    "optimistic": {
        "nominal_return": 9.0,
        "inflation_rate": 2.0,
        "stress_drop_first_years": None,
    },
    "conservative": {
        "nominal_return": 5.0,
        "inflation_rate": 3.5,
        "stress_drop_first_years": None,
    },
    "stress_test": {
        "nominal_return": 6.5,
        "inflation_rate": 3.0,
        "stress_drop_first_years": 15.0,
    },
}

SWR_PRESETS = [
    {
        "rate": 3.0,
        "key": "swrUltraSafe",
        "desc_key": "swrUltraSafeDesc",
        "multiplier": 33.3,
    },
    {
        "rate": 3.5,
        "key": "swrEuropeanFire",
        "desc_key": "swrEuropeanFireDesc",
        "multiplier": 28.6,
    },
    {
        "rate": 4.0,
        "key": "swrTrinityRule",
        "desc_key": "swrTrinityRuleDesc",
        "multiplier": 25.0,
    },
    {
        "rate": 4.5,
        "key": "swrLeanDynamic",
        "desc_key": "swrLeanDynamicDesc",
        "multiplier": 22.2,
    },
]
