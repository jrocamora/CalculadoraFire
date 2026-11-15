"""
Motor de simulació per a la independència financera (FIRE) a Irlanda.
Model de múltiples pilars: Cartera Pont (Compte d'Inversió / ETFs / altres) + Pensió Privada (PRSA) + MyFutureFund.

Cartera líquida ("bridge"), tres pots amb la seva pròpia fiscalitat:
- Compte d'Inversió (Budget 2027): obre l'1 de juliol de 2027, aportacions limitades a 12.000 €/any.
  Taxa anual sobre el saldo que supera el llindar (50.000 €); les retirades no tributen.
- ETFs / fons UCITS (categoria index_funds): Exit Tax sobre la plusvàlua en retirar i, opcionalment,
  Deemed Disposal durant l'acumulació.
- Altres (accions, efectiu, immobles): CGT sobre la plusvàlua en retirar, amb l'exempció anual.

El règim seleccionat (`ireland_asset_type`) decideix on van els estalvis mensuals nous:
- budget_2027_account   -> al Compte d'Inversió fins al límit anual; l'excés va a ETFs.
- etf_exit_tax          -> a ETFs.
- individual_shares_cgt -> a accions individuals (pot "altres").

Els impostos de l'acumulació es resten de la cartera. En jubilació, cada any es retira el brut necessari
perquè, després d'impostos (i de pagar la taxa del compte), quedi exactament l'ingrés net objectiu.
El rendiment de cada pot és la mitjana ponderada del rendiment esperat dels seus actius, desplaçada
per l'escenari macro (rendiment nominal de l'escenari - 7% base).

Quan jubilar-se (mode "target_spending"): el primer any en què la cartera total arriba al FIRE number
I la jubilació és viable, és a dir, la cartera líquida pot pagar la despesa sense quedar curta abans que
les pensions es desbloquegin. Es comprova assajant la jubilació sobre una còpia de l'estat.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field, replace
from datetime import datetime

from models.types import (
    FireCalculationResult,
    FireInputs,
    PortfolioAsset,
    TaxSettings,
    YearProjection,
)
from engine.tax_calculators import compute_annual_tax_for_withdrawal

BASE_NOMINAL_RETURN = 7.0  # % de referència dels escenaris macro
PENSION_CATEGORIES = ("private_pension", "my_future_fund")
ACCOUNT_OPEN_YEAR = 2027  # el Compte d'Inversió obre l'1 de juliol de 2027
ACCOUNT_ANNUAL_CAP = 12_000.0  # aportació màxima anual
LUMP_SUM_TAX_FREE_CAP = 200_000.0


def account_contribution_cap(calendar_year: int) -> float:
    """Aportació màxima al Compte d'Inversió en un any natural (mig any el 2027)."""
    if calendar_year < ACCOUNT_OPEN_YEAR:
        return 0.0
    if calendar_year == ACCOUNT_OPEN_YEAR:
        return ACCOUNT_ANNUAL_CAP / 2.0
    return ACCOUNT_ANNUAL_CAP


def _amount(a: PortfolioAsset) -> float:
    return max(0.0, float(a.current_amount or 0.0))


def _weighted_return(assets: list[PortfolioAsset], shift: float) -> float:
    """Rendiment anual (decimal) ponderat per import, més el desplaçament de l'escenari."""
    total = sum(_amount(a) for a in assets)
    if total <= 0:
        return BASE_NOMINAL_RETURN / 100.0 + shift
    weighted = sum(_amount(a) * float(a.expected_return_annual or 0.0) for a in assets)
    return weighted / total / 100.0 + shift


def _basis(assets: list[PortfolioAsset]) -> float:
    """Cost d'adquisició (mai superior al valor de mercat de cada actiu)."""
    return sum(min(max(0.0, float(a.cost_basis or 0.0)), _amount(a)) for a in assets)


def _gross_for_net(net_wanted: float, pot: float, basis: float, ts: TaxSettings, lang: str) -> tuple[float, float]:
    """Brut a vendre d'un pot perquè, després d'impostos, quedi `net_wanted`. Retorna (brut, impost)."""
    if net_wanted <= 0 or pot <= 0:
        return 0.0, 0.0
    gain_ratio = max(0.0, 1.0 - basis / pot)

    def tax_of(gross: float) -> float:
        return compute_annual_tax_for_withdrawal(gross, ts, pot, lang, gain_ratio=gain_ratio).total_tax

    if pot - tax_of(pot) <= net_wanted:
        return pot, tax_of(pot)
    lo, hi = net_wanted, pot
    for _ in range(50):
        mid = (lo + hi) / 2.0
        if mid - tax_of(mid) < net_wanted:
            lo = mid
        else:
            hi = mid
    return hi, tax_of(hi)


@dataclass
class _Config:
    """Paràmetres fixos de la simulació."""
    lang: str
    regime: str
    threshold: float
    account_rate: float
    exit_rate: float
    deemed_disposal_on: bool
    dd_rolling: bool
    ts_etf: TaxSettings
    ts_cgt: TaxSettings
    savings_growth: float
    swr: float
    inflation_rate: float
    b27_return: float
    etf_return: float
    misc_return: float
    p_pension_return: float
    mff_return: float
    stress_drop: float  # caiguda (decimal positiu) els dos primers anys de jubilació, o 0
    p_access_age: int
    mff_access_age: int
    state_pension_enabled: bool
    state_pension_annual: float  # en euros d'avui
    state_pension_age: int
    pension_tax_rate: float


@dataclass
class _State:
    """Saldos i aportacions que evolucionen any a any."""
    b27: float
    etf: float
    misc: float
    etf_basis: float
    misc_basis: float
    p_pension: float
    mff: float
    contrib_bridge: float
    contrib_p: float
    contrib_mff: float
    p_unlocked: bool = False
    mff_unlocked: bool = False

    @property
    def liquid(self) -> float:
        return self.b27 + self.etf + self.misc

    @property
    def pensions(self) -> float:
        return self.p_pension + self.mff

    @property
    def total(self) -> float:
        return max(0.0, self.liquid + self.pensions)


@dataclass
class _YearOutcome:
    contribution: float = 0.0
    gross: float = 0.0
    tax: float = 0.0
    net: float = 0.0
    state_pension: float = 0.0
    account_charge: float = 0.0
    deemed_disposal: float = 0.0
    exit_tax: float = 0.0
    cgt: float = 0.0
    pension_tax: float = 0.0
    lump_p: float = 0.0
    lump_mff: float = 0.0
    shortfall: float = 0.0
    return_used: float = 0.0
    notes: list[str] = field(default_factory=list)


def _accumulate_year(s: _State, c: _Config, i: int, calendar_year: int) -> _YearOutcome:
    out = _YearOutcome(contribution=s.contrib_bridge + s.contrib_p + s.contrib_mff, return_used=c.etf_return)

    s.b27 *= 1.0 + c.b27_return
    s.etf *= 1.0 + c.etf_return
    s.misc *= 1.0 + c.misc_return

    # Destí dels estalvis nous segons el règim seleccionat
    if c.regime == "budget_2027_account":
        to_account = min(s.contrib_bridge, account_contribution_cap(calendar_year))
        s.b27 += to_account
        s.etf += s.contrib_bridge - to_account
        s.etf_basis += s.contrib_bridge - to_account
    elif c.regime == "individual_shares_cgt":
        s.misc += s.contrib_bridge
        s.misc_basis += s.contrib_bridge
    else:
        s.etf += s.contrib_bridge
        s.etf_basis += s.contrib_bridge

    if i > 0:
        out.account_charge = max(0.0, s.b27 - c.threshold) * c.account_rate
        s.b27 -= out.account_charge

        if c.deemed_disposal_on and s.etf > 0 and (c.dd_rolling or i % 8 == 0):
            unrealized_gains = max(0.0, s.etf - s.etf_basis)
            if unrealized_gains > 0:
                taxed_gain = unrealized_gains / 8.0 if c.dd_rolling else unrealized_gains
                out.deemed_disposal = taxed_gain * c.exit_rate
                s.etf = max(0.0, s.etf - out.deemed_disposal)
                # La plusvàlua ja gravada passa a formar part del cost d'adquisició
                s.etf_basis = min(s.etf, s.etf_basis + taxed_gain)

        out.tax = out.account_charge + out.deemed_disposal

    # Les pensions creixen lliures d'impostos
    if s.p_pension > 0 or s.contrib_p > 0:
        s.p_pension = s.p_pension * (1.0 + c.p_pension_return) + s.contrib_p
    if s.mff > 0 or s.contrib_mff > 0:
        s.mff = s.mff * (1.0 + c.mff_return) + s.contrib_mff

    s.contrib_bridge *= c.savings_growth
    s.contrib_p *= c.savings_growth
    s.contrib_mff *= c.savings_growth
    return out


def _draw_pensions(s: _State, c: _Config, net_wanted: float, capped: bool) -> tuple[float, float]:
    """Retira de les pensions desbloquejades. Retorna (net obtingut, brut retirat)."""
    got, gross_total = 0.0, 0.0
    for which in ("p", "mff"):
        unlocked = s.p_unlocked if which == "p" else s.mff_unlocked
        pot = s.p_pension if which == "p" else s.mff
        if not unlocked or pot <= 0 or net_wanted - got <= 0:
            continue
        gross_wanted = (net_wanted - got) / (1.0 - c.pension_tax_rate)
        gross = min(pot, pot * c.swr if capped else pot, gross_wanted)
        if which == "p":
            s.p_pension -= gross
        else:
            s.mff -= gross
        gross_total += gross
        got += gross * (1.0 - c.pension_tax_rate)
    return got, gross_total


def _retire_year(
    s: _State, c: _Config, i: int, age: int, inflation_factor: float, years_retired: int, target_net: float
) -> _YearOutcome:
    out = _YearOutcome()
    stressed = c.stress_drop > 0 and years_retired < 2
    r_b27, r_etf, r_misc = (-c.stress_drop,) * 3 if stressed else (c.b27_return, c.etf_return, c.misc_return)
    out.return_used = r_etf

    # 1. Rescat de pensions: el 25% exempt passa a la cartera líquida (pot "altres") com a capital
    if age >= c.p_access_age and not s.p_unlocked and s.p_pension > 0:
        s.p_unlocked = True
        out.lump_p = min(LUMP_SUM_TAX_FREE_CAP, s.p_pension * 0.25)
        s.p_pension -= out.lump_p
        s.misc += out.lump_p
        s.misc_basis += out.lump_p

    if age >= c.mff_access_age and not s.mff_unlocked and s.mff > 0:
        s.mff_unlocked = True
        out.lump_mff = s.mff * 0.25
        s.mff -= out.lump_mff
        s.misc += out.lump_mff
        s.misc_basis += out.lump_mff

    # 2. Ingrés net objectiu d'aquest any; la pensió d'Estat no tributa en aquest model
    net_needed = target_net * inflation_factor
    if c.state_pension_enabled and age >= c.state_pension_age:
        out.state_pension = c.state_pension_annual * inflation_factor
    net_needed = max(0.0, net_needed - out.state_pension)

    # 3. ARF / MyFutureFund desbloquejats, fins a la SWR del pot
    got, pension_gross = _draw_pensions(s, c, net_needed, capped=True)
    net_needed -= got

    # 4. Cartera líquida: la taxa anual del compte es paga amb una retirada extra del mateix compte
    if i > 0:
        out.account_charge = max(0.0, s.b27 - c.threshold) * c.account_rate
    cash_needed = net_needed + out.account_charge

    draw_b27 = min(s.b27, cash_needed)
    s.b27 -= draw_b27
    cash_needed -= draw_b27

    # Primer les accions/altres (CGT amb exempció), després els ETFs (Exit Tax)
    draw_misc, out.cgt = _gross_for_net(cash_needed, s.misc, s.misc_basis, c.ts_cgt, c.lang)
    if s.misc > 0:
        s.misc_basis *= 1.0 - draw_misc / s.misc
    s.misc -= draw_misc
    cash_needed -= draw_misc - out.cgt

    draw_etf, out.exit_tax = _gross_for_net(cash_needed, s.etf, s.etf_basis, c.ts_etf, c.lang)
    if s.etf > 0:
        s.etf_basis *= 1.0 - draw_etf / s.etf
    s.etf -= draw_etf
    cash_needed -= draw_etf - out.exit_tax

    # Si la cartera líquida no arriba, es retira més de les pensions ja desbloquejades
    if cash_needed > 1.0:
        got_extra, gross_extra = _draw_pensions(s, c, cash_needed, capped=False)
        cash_needed -= got_extra
        pension_gross += gross_extra

    out.pension_tax = pension_gross * c.pension_tax_rate
    out.gross = draw_b27 + draw_misc + draw_etf + pension_gross + out.state_pension
    out.tax = out.account_charge + out.cgt + out.exit_tax + out.pension_tax
    out.net = max(0.0, out.gross - out.tax)
    out.shortfall = max(0.0, cash_needed) if cash_needed > 1.0 else 0.0

    # 5. Rendiment sobre els capitals restants
    s.b27 *= 1.0 + r_b27
    s.etf *= 1.0 + r_etf
    s.misc *= 1.0 + r_misc
    s.p_pension *= 1.0 + c.p_pension_return
    s.mff *= 1.0 + c.mff_return
    return out


def _bridge_holds_until_pensions_unlock(
    s: _State, c: _Config, i: int, current_age: int, inflation_rate: float, target_net: float, last_index: int
) -> bool:
    """Assaja la jubilació a partir de l'any `i` sobre una còpia de l'estat. És viable si no hi ha cap any
    curt mentre encara queden pensions bloquejades. Un dèficit posterior és un tema de sostenibilitat
    (el mostra "Depletion risk"), no de quan et pots jubilar."""
    trial = copy.copy(s)
    for j in range(i, last_index + 1):
        age = current_age + j
        locked_before = (trial.p_pension > 0 and not trial.p_unlocked) or (trial.mff > 0 and not trial.mff_unlocked)
        if not locked_before:
            return True
        out = _retire_year(trial, c, j, age, (1.0 + inflation_rate) ** j, j - i, target_net)
        if out.shortfall > 0:
            return False
    return True


def simulate_fire(inputs: FireInputs, lang: str = "ca") -> FireCalculationResult:
    is_en = lang == "en"
    current_year = datetime.now().year

    mode = inputs.mode
    current_age = inputs.current_age
    target_retirement_age = inputs.target_retirement_age
    life_expectancy = inputs.life_expectancy or 88
    assets = inputs.assets
    scenario = inputs.scenario
    tax_settings = inputs.tax_settings
    ps = inputs.pension_settings
    swr_decimal = max(0.01, inputs.safe_withdrawal_rate / 100.0)

    # ── Fiscalitat ─────────────────────────────────────────────────────
    regime = tax_settings.ireland_asset_type
    reform = tax_settings.tax_reform_change_rate or 0.0
    ts_etf = replace(tax_settings, ireland_asset_type="etf_exit_tax")
    ts_cgt = replace(tax_settings, ireland_asset_type="individual_shares_cgt")
    # Per dimensionar l'objectiu s'assumeix que les retirades tributen com el pot "de fora" del compte
    # on van els estalvis (prudent: les retirades del Compte d'Inversió no tributen).
    ts_plan = ts_cgt if regime == "individual_shares_cgt" else ts_etf

    # ── Pots inicials ──────────────────────────────────────────────────
    bridge_assets = [a for a in assets if a.category not in PENSION_CATEGORIES]
    b27_assets = [a for a in bridge_assets if a.category == "budget_2027_account"]
    etf_assets = [a for a in bridge_assets if a.category == "index_funds"]
    misc_assets = [a for a in bridge_assets if a.category not in ("budget_2027_account", "index_funds")]

    asset_p_pension = next((a for a in assets if a.category == "private_pension"), None)
    asset_mff = next((a for a in assets if a.category == "my_future_fund"), None)
    p_enabled = bool(ps and ps.private_pension_enabled)
    mff_enabled = bool(ps and ps.my_future_fund_enabled)

    if p_enabled:
        p_pension_initial = float(ps.private_pension_balance or 0.0)
    elif asset_p_pension:
        p_pension_initial = _amount(asset_p_pension)
    else:
        p_pension_initial = 0.0

    if mff_enabled:
        mff_initial = float(ps.my_future_fund_balance or 0.0)
    elif asset_mff:
        mff_initial = _amount(asset_mff)
    else:
        mff_initial = 0.0

    s = _State(
        b27=sum(_amount(a) for a in b27_assets),
        etf=sum(_amount(a) for a in etf_assets),
        misc=sum(_amount(a) for a in misc_assets),
        etf_basis=_basis(etf_assets),
        misc_basis=_basis(misc_assets),
        p_pension=p_pension_initial,
        mff=mff_initial,
        contrib_bridge=inputs.monthly_savings * 12.0,
        contrib_p=ps.private_pension_monthly_contribution * 12.0 if p_enabled else 0.0,
        contrib_mff=(
            (
                ps.my_future_fund_employee_monthly
                + ps.my_future_fund_employer_match_monthly
                + ps.my_future_fund_state_topup_monthly
            )
            * 12.0
            if mff_enabled
            else 0.0
        ),
    )
    bridge_capital_initial = s.liquid
    current_total_net_worth = s.total

    # ── Rendibilitats, pensions i inflació ─────────────────────────────
    scenario_shift = (scenario.nominal_return - BASE_NOMINAL_RETURN) / 100.0
    state_pension_enabled = bool(getattr(ps, "state_pension_enabled", True)) if ps else False
    state_pension_monthly = float(getattr(ps, "state_pension_monthly_amount", 1340.0)) if ps else 1340.0
    c = _Config(
        lang=lang,
        regime=regime,
        threshold=float(getattr(tax_settings, "ireland_investment_account_threshold", 50000.0)),
        account_rate=max(0.0, float(getattr(tax_settings, "ireland_investment_account_rate", 1.0)) / 100.0),
        exit_rate=max(0.0, (float(getattr(tax_settings, "ireland_exit_tax_rate", 35.0)) + reform) / 100.0),
        deemed_disposal_on=tax_settings.country == "IE" and bool(tax_settings.ireland_simulate_deemed_disposal),
        dd_rolling=(tax_settings.ireland_deemed_disposal_mode or "staggered_rolling_eighth") == "staggered_rolling_eighth",
        ts_etf=ts_etf,
        ts_cgt=ts_cgt,
        savings_growth=1.0 + (inputs.annual_savings_increase_rate or 0.0) / 100.0,
        swr=swr_decimal,
        inflation_rate=scenario.inflation_rate / 100.0,
        b27_return=_weighted_return(b27_assets, scenario_shift),
        etf_return=_weighted_return(etf_assets, scenario_shift),
        misc_return=_weighted_return(misc_assets, scenario_shift),
        p_pension_return=ps.private_pension_expected_return / 100.0 if ps else scenario.nominal_return / 100.0,
        mff_return=ps.my_future_fund_expected_return / 100.0 if ps else scenario.nominal_return / 100.0,
        stress_drop=abs(scenario.stress_drop_first_years or 0.0) / 100.0,
        p_access_age=int(ps.private_pension_access_age) if p_enabled else 50,
        mff_access_age=int(getattr(ps, "my_future_fund_access_age", 66)) if ps else 66,
        state_pension_enabled=state_pension_enabled,
        state_pension_annual=state_pension_monthly * 12.0,
        state_pension_age=int(getattr(ps, "state_pension_access_age", 66)) if ps else 66,
        pension_tax_rate=max(0.0, min(0.99, float(getattr(ps, "pension_income_tax_rate", 20.0)) / 100.0)) if ps else 0.0,
    )

    # ── Objectiu (en euros d'avui) ─────────────────────────────────────
    target_annual_net_income = 0.0
    gross_withdrawal_needed = 0.0
    fire_number_nominal = 0.0

    def plan_net_for_gross(gross: float) -> float:
        return compute_annual_tax_for_withdrawal(gross, ts_plan, gross / swr_decimal, lang).net_disposable_income

    if mode == "target_spending":
        target_annual_net_income = inputs.target_monthly_disposable_income * 12.0
        low, high = target_annual_net_income, max(1.0, target_annual_net_income) * 3.0
        for _ in range(60):
            mid = (low + high) / 2.0
            if plan_net_for_gross(mid) < target_annual_net_income:
                low = mid
            else:
                high = mid
        gross_withdrawal_needed = high
        fire_number_nominal = gross_withdrawal_needed / swr_decimal

    # ── Simulació any a any fins a l'esperança de vida ─────────────────
    projections: list[YearProjection] = []
    total_years = max(1, life_expectancy - current_age)
    fire_achieved_year_index = -1
    is_retired = False
    waited_for_pensions = False  # el FIRE number ja es complia però calia esperar el desbloqueig

    portfolio_survival_years = 0
    portfolio_exhausted = False
    has_income_shortfall = False
    total_tax_free_lump_sum = 0.0
    bridge_at_fire = bridge_capital_initial
    pension_at_fire = s.pensions
    portfolio_at_fire = current_total_net_worth
    first_year: _YearOutcome | None = None
    first_year_inflation = 1.0

    for i in range(total_years + 1):
        age = current_age + i
        calendar_year = current_year + i
        inflation_factor = (1.0 + c.inflation_rate) ** i
        start_of_period_portfolio = s.total

        # ¿Comença la jubilació aquest any?
        if not is_retired:
            if mode == "target_spending":
                retire_now = fire_number_nominal > 0 and start_of_period_portfolio >= fire_number_nominal * inflation_factor
                if retire_now and not _bridge_holds_until_pensions_unlock(
                    s, c, i, current_age, c.inflation_rate, target_annual_net_income, total_years
                ):
                    retire_now = False
                    waited_for_pensions = True
            else:
                retire_now = age >= target_retirement_age
                if retire_now:
                    # El FIRE number és el que realment hi haurà a la cartera, expressat en euros d'avui
                    fire_number_nominal = start_of_period_portfolio / inflation_factor
                    gross_withdrawal_needed = fire_number_nominal * swr_decimal
                    target_annual_net_income = plan_net_for_gross(gross_withdrawal_needed)
            if retire_now:
                is_retired = True
                fire_achieved_year_index = i
                bridge_at_fire = s.liquid
                pension_at_fire = s.pensions
                portfolio_at_fire = start_of_period_portfolio

        if not is_retired:
            out = _accumulate_year(s, c, i, calendar_year)
        else:
            out = _retire_year(
                s, c, i, age, inflation_factor, i - fire_achieved_year_index, target_annual_net_income
            )
            if first_year is None:
                first_year, first_year_inflation = out, inflation_factor
            if out.shortfall > 0:
                has_income_shortfall = True

        # Notes de l'any
        notes: list[str] = []
        if out.lump_p > 0:
            notes.append(
                f"🛡️ Private Pension Unlocked at age {age}! €{round(out.lump_p):,} Tax-Free Lump Sum (25%)"
                if is_en
                else f"🛡️ Rescat Pensió Privada als {age} anys! {round(out.lump_p):,} € Capital Exempt (25%)"
            )
        if out.lump_mff > 0:
            notes.append(
                f"🏛️ MyFutureFund Unlocked at age {age}! €{round(out.lump_mff):,} Tax-Free Lump Sum (25%)"
                if is_en
                else f"🏛️ MyFutureFund als {age} anys! {round(out.lump_mff):,} € Capital Exempt (25%)"
            )
        if is_retired and c.state_pension_enabled and age == c.state_pension_age:
            notes.append(
                f"🏛️ State Pension active! +€{round(out.state_pension):,} /yr"
                if is_en
                else f"🏛️ Pensió d'Estat activa! +{round(out.state_pension):,} €/any"
            )
        if out.shortfall > 0 and s.pensions > 0 and not notes:
            notes.append(
                "⚠️ Income gap: liquid portfolio is empty and pensions are still locked"
                if is_en
                else "⚠️ Dèficit d'ingressos: cartera líquida esgotada i pensions encara bloquejades"
            )

        total_portfolio_year = s.liquid + s.pensions
        if total_portfolio_year > 0.5:
            portfolio_survival_years += 1
        elif start_of_period_portfolio > 0:
            portfolio_exhausted = True
            if not notes:
                notes.append("❌ Portfolio Depletion" if is_en else "❌ Esgotament del capital")

        if not notes and i == fire_achieved_year_index:
            notes.append(
                "🎉 Financial Independence Achieved!" if is_en else "🎉 Assoliment de la Independència Financera!"
            )
        elif not notes and calendar_year == ACCOUNT_OPEN_YEAR and regime == "budget_2027_account" and not is_retired:
            notes.append(
                "🌟 Investment Account opens (1 July): savings go in up to €12,000/yr"
                if is_en
                else "🌟 Obre el Compte d'Inversió (1 de juliol): estalvis fins a 12.000 €/any"
            )
        elif not notes and out.account_charge > 0:
            notes.append(
                f"🇮🇪 Investment Account charge ({c.account_rate * 100:g}% above €{round(c.threshold):,}): €{round(out.account_charge):,}"
                if is_en
                else f"🇮🇪 Taxa Compte Inversió ({c.account_rate * 100:g}% sobre {round(c.threshold):,} €): {round(out.account_charge):,} €"
            )

        ending_portfolio = max(0.0, total_portfolio_year)
        total_tax_free_lump_sum += out.lump_p + out.lump_mff
        projections.append(
            YearProjection(
                year_index=i,
                calendar_year=calendar_year,
                age=age,
                is_retired=is_retired,
                starting_portfolio=start_of_period_portfolio,
                gross_return=out.return_used,
                inflation_factor=inflation_factor,
                contribution=out.contribution,
                gross_withdrawal=out.gross,
                tax_paid=out.tax,
                net_disposable_income=out.net,
                ending_portfolio=ending_portfolio,
                ending_portfolio_real=ending_portfolio / inflation_factor,
                bridge_portfolio=s.liquid,
                pension_portfolio=s.pensions,
                private_pension_value=s.p_pension,
                my_future_fund_value=s.mff,
                tax_free_lump_sum_received=out.lump_p + out.lump_mff,
                state_pension_received=out.state_pension,
                deemed_disposal_tax_paid=out.deemed_disposal if out.deemed_disposal > 0 else None,
                tax_notes=" | ".join(notes) if notes else None,
            )
        )

    # ── Resum ──────────────────────────────────────────────────────────
    reached = fire_achieved_year_index != -1
    years_to_fire = fire_achieved_year_index if reached else 0
    is_already_fire = reached and fire_achieved_year_index == 0 and mode == "target_spending"

    if first_year is not None:
        f = first_year_inflation
        fy = {
            "gross": first_year.gross / f,
            "tax": first_year.tax / f,
            "account_charge": first_year.account_charge / f,
            "exit_tax": first_year.exit_tax / f,
            "cgt": first_year.cgt / f,
            "pension_tax": first_year.pension_tax / f,
            "state_pension": first_year.state_pension / f,
        }
    else:
        # Objectiu no assolit: estimació amb el règim de planificació
        est = compute_annual_tax_for_withdrawal(gross_withdrawal_needed, ts_plan, fire_number_nominal, lang)
        fy = {
            "gross": gross_withdrawal_needed,
            "tax": est.total_tax,
            "account_charge": 0.0,
            "exit_tax": est.total_tax if ts_plan is ts_etf else 0.0,
            "cgt": est.total_tax if ts_plan is ts_cgt else 0.0,
            "pension_tax": 0.0,
            "state_pension": 0.0,
        }

    return FireCalculationResult(
        fire_number_nominal=fire_number_nominal,
        fire_number_real=fire_number_nominal,
        monthly_disposable_target=target_annual_net_income / 12.0,
        annual_gross_withdrawal_needed=gross_withdrawal_needed,
        annual_tax_at_retirement=fy["tax"],
        effective_tax_rate_at_retirement=fy["tax"] / fy["gross"] if fy["gross"] > 0 else 0.0,
        retirement_year_gross=fy["gross"],
        retirement_year_account_charge=fy["account_charge"],
        retirement_year_exit_tax=fy["exit_tax"],
        retirement_year_cgt=fy["cgt"],
        retirement_year_pension_tax=fy["pension_tax"],
        retirement_year_state_pension=fy["state_pension"],
        years_to_fire=years_to_fire,
        age_at_fire=current_age + years_to_fire if reached else 0,
        calendar_year_at_fire=current_year + years_to_fire if reached else 0,
        is_already_fire=is_already_fire,
        fire_reachable=reached,
        has_income_shortfall=has_income_shortfall,
        waited_for_pension_unlock=reached and waited_for_pensions,
        current_total_net_worth=current_total_net_worth,
        projected_portfolio_at_fire=portfolio_at_fire,
        projections=projections,
        portfolio_survival_years=portfolio_survival_years,
        final_portfolio_value=projections[-1].ending_portfolio if projections else 0.0,
        is_sustainable=reached and not portfolio_exhausted and not has_income_shortfall,
        bridge_capital_at_fire=bridge_at_fire if reached else bridge_capital_initial,
        pension_capital_at_fire=pension_at_fire if reached else (p_pension_initial + mff_initial),
        private_pension_unlocked_age=c.p_access_age,
        my_future_fund_unlocked_age=c.mff_access_age,
        state_pension_unlocked_age=c.state_pension_age,
        state_pension_annual_amount=c.state_pension_annual if state_pension_enabled else 0.0,
        tax_free_lump_sum_total=total_tax_free_lump_sum,
    )
