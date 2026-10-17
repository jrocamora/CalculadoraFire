"""
Dataclasses que defineixen l'estructura de dades de la Calculadora FIRE.
Port fidel de src/types/fire.ts
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional


# ---------------------------------------------------------------------------
# Tipus base (enums com a Literal)
# ---------------------------------------------------------------------------
CountryCode = Literal["CAT", "IE", "AD"]
CalculationMode = Literal["target_spending", "current_portfolio"]
AssetCategory = Literal[
    "budget_2027_account",
    "index_funds",
    "individual_stocks",
    "cash_deposits",
    "real_estate_other",
    "private_pension",
    "my_future_fund",
]
IrelandDeemedDisposalMode = Literal["lump_sum_8y", "staggered_rolling_eighth"]
MacroScenarioId = Literal["base", "optimistic", "conservative", "stress_test", "custom"]


# ---------------------------------------------------------------------------
# Pensions irlandeses (Private Pension / PRSA i MyFutureFund Auto-Enrolment)
# ---------------------------------------------------------------------------
@dataclass
class PensionSettings:
    # Private Pension (Occupational Pension / PRSA / Personal Pension)
    private_pension_enabled: bool = True
    private_pension_balance: float = 45000.0
    private_pension_monthly_contribution: float = 500.0  # Empleat + Empresa (€/mes)
    private_pension_expected_return: float = 7.0  # % anual
    private_pension_access_age: int = 50  # 50 per a pensions d'empresa, 60 per a PRSA
    private_pension_tax_free_lump_sum_pct: float = 25.0  # 25% exempt d'impostos (fins a 200k)

    # MyFutureFund (Sistema Nacional d'Auto-Enrolment d'Irlanda - NAERSA)
    my_future_fund_enabled: bool = True
    my_future_fund_balance: float = 12000.0
    my_future_fund_employee_monthly: float = 200.0  # Aportació empleat (€/mes)
    my_future_fund_employer_match_monthly: float = 200.0  # 100% aportació empresa
    my_future_fund_state_topup_monthly: float = 66.67  # Estat: 1 € per cada 3 € guardats
    my_future_fund_expected_return: float = 7.0  # % anual
    my_future_fund_access_age: int = 66  # Edat de la Pensió d'Estat a Irlanda
    my_future_fund_tax_free_lump_sum_pct: float = 25.0  # 25% exempt d'impostos



# ---------------------------------------------------------------------------
# Actiu dins la cartera
# ---------------------------------------------------------------------------
@dataclass
class PortfolioAsset:
    id: str
    category: AssetCategory
    name: str
    current_amount: float
    expected_return_annual: float  # p.ex. 7.0 (%)
    cost_basis: float  # Per al càlcul de plusvàlues


# ---------------------------------------------------------------------------
IrelandAssetType = Literal["budget_2027_account", "etf_exit_tax", "individual_shares_cgt"]

# ---------------------------------------------------------------------------
# Configuració fiscal
# ---------------------------------------------------------------------------
@dataclass
class TaxSettings:
    country: CountryCode = "IE"
    # Irlanda
    ireland_asset_type: IrelandAssetType = "budget_2027_account"
    ireland_simulate_deemed_disposal: bool = True
    ireland_deemed_disposal_mode: IrelandDeemedDisposalMode = "staggered_rolling_eighth"
    ireland_exit_tax_rate: float = 35.0  # Budget 2027 rate: 35% (previously 38%/41%)
    ireland_cgt_rate: float = 31.0  # Budget 2027 rate: 31% (previously 33%)
    ireland_investment_account_threshold: float = 50000.0  # First €50k tax-free
    ireland_investment_account_rate: float = 1.0  # 1% flat annual tax on excess above €50k
    # Catalunya (intern per compatibilitat)
    catalonia_capital_gains_ratio: float = 50.0
    catalonia_apply_wealth_tax: bool = False
    catalonia_primary_residence_exemption: float = 0.0
    # Andorra (intern per compatibilitat)
    andorra_exempt_listed_securities: bool = True
    # Reforma fiscal futura
    tax_reform_change_rate: float = 0.0
    planned_relocation_country: Optional[str] = "none"
    planned_relocation_year: Optional[int] = None



# ---------------------------------------------------------------------------
# Escenari macroeconòmic
# ---------------------------------------------------------------------------
@dataclass
class MacroScenario:
    id: MacroScenarioId = "base"
    name: str = "Escenari Base"
    description: str = "Rendiment històric mitjà de mercat global i inflació moderada."
    nominal_return: float = 7.0  # %
    inflation_rate: float = 2.5  # %
    stress_drop_first_years: Optional[float] = None  # % drop in year 1-2


# ---------------------------------------------------------------------------
# Inputs complets de la simulació FIRE
# ---------------------------------------------------------------------------
@dataclass
class FireInputs:
    mode: CalculationMode = "target_spending"
    current_age: int = 32
    target_retirement_age: int = 48
    life_expectancy: int = 88
    target_monthly_disposable_income: float = 2500.0
    assets: list[PortfolioAsset] = field(default_factory=list)
    monthly_savings: float = 900.0
    annual_savings_increase_rate: float = 2.0
    safe_withdrawal_rate: float = 3.5
    scenario: MacroScenario = field(default_factory=MacroScenario)
    tax_settings: TaxSettings = field(default_factory=TaxSettings)
    pension_settings: PensionSettings = field(default_factory=PensionSettings)


# ---------------------------------------------------------------------------
# Projecció d'un any
# ---------------------------------------------------------------------------
@dataclass
class YearProjection:
    year_index: int
    calendar_year: int
    age: int
    is_retired: bool
    starting_portfolio: float
    gross_return: float
    inflation_factor: float
    contribution: float
    gross_withdrawal: float
    tax_paid: float
    net_disposable_income: float
    ending_portfolio: float
    ending_portfolio_real: float  # ajustat a inflació
    bridge_portfolio: float = 0.0  # Fons accessibles lliures (Bridge)
    pension_portfolio: float = 0.0  # Total en pensions (bloquejat o en ARF)
    private_pension_value: float = 0.0  # Valor del pla privat
    my_future_fund_value: float = 0.0  # Valor de MyFutureFund
    tax_free_lump_sum_received: float = 0.0  # 25% lump sum cobrat aquest any
    deemed_disposal_tax_paid: Optional[float] = None
    tax_notes: Optional[str] = None


# ---------------------------------------------------------------------------
# Resultat complet de la simulació
# ---------------------------------------------------------------------------
@dataclass
class FireCalculationResult:
    fire_number_nominal: float = 0.0
    fire_number_real: float = 0.0
    monthly_disposable_target: float = 0.0
    annual_gross_withdrawal_needed: float = 0.0
    annual_tax_at_retirement: float = 0.0
    effective_tax_rate_at_retirement: float = 0.0

    years_to_fire: int = 0
    age_at_fire: int = 0
    calendar_year_at_fire: int = 0
    is_already_fire: bool = False

    current_total_net_worth: float = 0.0
    projected_portfolio_at_fire: float = 0.0

    projections: list[YearProjection] = field(default_factory=list)
    portfolio_survival_years: int = 0
    final_portfolio_value: float = 0.0
    is_sustainable: bool = True

    bridge_capital_at_fire: float = 0.0
    pension_capital_at_fire: float = 0.0
    private_pension_unlocked_age: int = 50
    my_future_fund_unlocked_age: int = 66
    tax_free_lump_sum_total: float = 0.0


# ---------------------------------------------------------------------------
# Resultat d'un càlcul fiscal
# ---------------------------------------------------------------------------
@dataclass
class TaxComputationResult:
    gross_withdrawal: float = 0.0
    taxable_gains: float = 0.0
    total_tax: float = 0.0
    irpf_tax: float = 0.0
    wealth_tax: float = 0.0
    net_disposable_income: float = 0.0
    effective_tax_rate: float = 0.0
    marginal_tax_rate: float = 0.0
    explanation: str = ""


# ---------------------------------------------------------------------------
# Detalls d'un país
# ---------------------------------------------------------------------------
@dataclass
class CountryDetails:
    code: CountryCode
    name: str
    flag: str
    currency: str
    summary: str
    highlights: list[str] = field(default_factory=list)
