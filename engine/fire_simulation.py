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
"""
from __future__ import annotations

from dataclasses import replace
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


def simulate_fire(inputs: FireInputs, lang: str = "ca") -> FireCalculationResult:
    is_en = lang == "en"
    current_year = datetime.now().year

    mode = inputs.mode
    current_age = inputs.current_age
    target_retirement_age = inputs.target_retirement_age
    life_expectancy = inputs.life_expectancy or 88
    assets = inputs.assets
    savings_growth = 1.0 + (inputs.annual_savings_increase_rate or 0.0) / 100.0
    scenario = inputs.scenario
    tax_settings = inputs.tax_settings
    ps = inputs.pension_settings
    swr_decimal = max(0.01, inputs.safe_withdrawal_rate / 100.0)

    # ── Fiscalitat ─────────────────────────────────────────────────────
    regime = tax_settings.ireland_asset_type
    reform = tax_settings.tax_reform_change_rate or 0.0
    threshold = float(getattr(tax_settings, "ireland_investment_account_threshold", 50000.0))
    account_rate = max(0.0, float(getattr(tax_settings, "ireland_investment_account_rate", 1.0)) / 100.0)
    exit_rate = max(0.0, (float(getattr(tax_settings, "ireland_exit_tax_rate", 35.0)) + reform) / 100.0)
    deemed_disposal_on = tax_settings.country == "IE" and bool(tax_settings.ireland_simulate_deemed_disposal)
    dd_rolling = (tax_settings.ireland_deemed_disposal_mode or "staggered_rolling_eighth") == "staggered_rolling_eighth"

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

    b27_pot = sum(_amount(a) for a in b27_assets)
    etf_pot = sum(_amount(a) for a in etf_assets)
    misc_pot = sum(_amount(a) for a in misc_assets)
    etf_basis = _basis(etf_assets)
    misc_basis = _basis(misc_assets)
    bridge_capital_initial = b27_pot + etf_pot + misc_pot

    asset_p_pension = next((a for a in assets if a.category == "private_pension"), None)
    asset_mff = next((a for a in assets if a.category == "my_future_fund"), None)

    p_enabled = bool(ps and ps.private_pension_enabled)
    mff_enabled = bool(ps and ps.my_future_fund_enabled)

    if p_enabled:
        p_pension_pot = float(ps.private_pension_balance or 0.0)
    elif asset_p_pension:
        p_pension_pot = _amount(asset_p_pension)
    else:
        p_pension_pot = 0.0

    if mff_enabled:
        mff_pot = float(ps.my_future_fund_balance or 0.0)
    elif asset_mff:
        mff_pot = _amount(asset_mff)
    else:
        mff_pot = 0.0

    private_pension_initial = p_pension_pot
    mff_initial = mff_pot
    current_total_net_worth = bridge_capital_initial + p_pension_pot + mff_pot

    # ── Rendibilitats i inflació ───────────────────────────────────────
    scenario_shift = (scenario.nominal_return - BASE_NOMINAL_RETURN) / 100.0
    b27_return = _weighted_return(b27_assets, scenario_shift)
    etf_return = _weighted_return(etf_assets, scenario_shift)
    misc_return = _weighted_return(misc_assets, scenario_shift)
    inflation_rate = scenario.inflation_rate / 100.0

    p_pension_return = ps.private_pension_expected_return / 100.0 if ps else scenario.nominal_return / 100.0
    mff_return = ps.my_future_fund_expected_return / 100.0 if ps else scenario.nominal_return / 100.0

    p_pension_access_age = int(ps.private_pension_access_age) if p_enabled else 50
    mff_access_age = int(getattr(ps, "my_future_fund_access_age", 66)) if ps else 66
    state_pension_enabled = bool(getattr(ps, "state_pension_enabled", True)) if ps else False
    state_pension_monthly = float(getattr(ps, "state_pension_monthly_amount", 1340.0)) if ps else 1340.0
    state_pension_access_age = int(getattr(ps, "state_pension_access_age", 66)) if ps else 66
    pension_tax_rate = max(0.0, min(0.99, float(getattr(ps, "pension_income_tax_rate", 20.0)) / 100.0)) if ps else 0.0

    annual_bridge_contrib = inputs.monthly_savings * 12.0
    annual_p_contrib = ps.private_pension_monthly_contribution * 12.0 if p_enabled else 0.0
    annual_mff_contrib = (
        (
            ps.my_future_fund_employee_monthly
            + ps.my_future_fund_employer_match_monthly
            + ps.my_future_fund_state_topup_monthly
        )
        * 12.0
        if mff_enabled
        else 0.0
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

    portfolio_survival_years = 0
    portfolio_exhausted = False
    has_income_shortfall = False
    total_tax_free_lump_sum_cum = 0.0
    p_pension_unlocked = False
    mff_unlocked = False
    bridge_at_fire = bridge_capital_initial
    pension_at_fire = p_pension_pot + mff_pot
    portfolio_at_fire = current_total_net_worth
    first_year_breakdown: dict[str, float] | None = None

    for i in range(total_years + 1):
        age = current_age + i
        calendar_year = current_year + i
        inflation_factor = (1.0 + inflation_rate) ** i
        start_of_period_portfolio = max(0.0, b27_pot + etf_pot + misc_pot + p_pension_pot + mff_pot)

        # ¿Comença la jubilació aquest any? Es decideix amb la cartera real projectada (impostos inclosos).
        if not is_retired:
            if mode == "target_spending":
                retire_now = fire_number_nominal > 0 and start_of_period_portfolio >= fire_number_nominal * inflation_factor
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
                bridge_at_fire = b27_pot + etf_pot + misc_pot
                pension_at_fire = p_pension_pot + mff_pot
                portfolio_at_fire = start_of_period_portfolio

        contribution_this_year = 0.0
        gross_withdrawal_this_year = 0.0
        state_pension_this_year = 0.0
        tax_paid_this_year = 0.0
        net_disposable_this_year = 0.0
        deemed_disposal_tax_paid = 0.0
        account_charge_paid = 0.0
        lump_sum_this_year = 0.0
        notes = ""

        r_b27, r_etf, r_misc = b27_return, etf_return, misc_return
        # Sequence of returns stress test: caiguda els dos primers anys de jubilació
        if is_retired and scenario.stress_drop_first_years and i - fire_achieved_year_index < 2:
            r_b27 = r_etf = r_misc = -abs(scenario.stress_drop_first_years) / 100.0

        if not is_retired:
            # ── Fase d'acumulació ──────────────────────────────────────
            contribution_this_year = annual_bridge_contrib + annual_p_contrib + annual_mff_contrib

            b27_pot *= 1.0 + r_b27
            etf_pot *= 1.0 + r_etf
            misc_pot *= 1.0 + r_misc

            # Destí dels estalvis nous segons el règim seleccionat
            if regime == "budget_2027_account":
                to_account = min(annual_bridge_contrib, account_contribution_cap(calendar_year))
                b27_pot += to_account
                etf_pot += annual_bridge_contrib - to_account
                etf_basis += annual_bridge_contrib - to_account
            elif regime == "individual_shares_cgt":
                misc_pot += annual_bridge_contrib
                misc_basis += annual_bridge_contrib
            else:
                etf_pot += annual_bridge_contrib
                etf_basis += annual_bridge_contrib

            if i > 0:
                account_charge_paid = max(0.0, b27_pot - threshold) * account_rate
                b27_pot -= account_charge_paid

                if deemed_disposal_on and etf_pot > 0 and (dd_rolling or i % 8 == 0):
                    unrealized_gains = max(0.0, etf_pot - etf_basis)
                    if unrealized_gains > 0:
                        taxed_gain = unrealized_gains / 8.0 if dd_rolling else unrealized_gains
                        deemed_disposal_tax_paid = taxed_gain * exit_rate
                        etf_pot = max(0.0, etf_pot - deemed_disposal_tax_paid)
                        # La plusvàlua ja gravada passa a formar part del cost d'adquisició
                        etf_basis = min(etf_pot, etf_basis + taxed_gain)

                tax_paid_this_year = account_charge_paid + deemed_disposal_tax_paid

            # Les pensions creixen lliures d'impostos
            if p_pension_pot > 0 or annual_p_contrib > 0:
                p_pension_pot = p_pension_pot * (1.0 + p_pension_return) + annual_p_contrib
            if mff_pot > 0 or annual_mff_contrib > 0:
                mff_pot = mff_pot * (1.0 + mff_return) + annual_mff_contrib

            annual_bridge_contrib *= savings_growth
            annual_p_contrib *= savings_growth
            annual_mff_contrib *= savings_growth

        else:
            # ── Fase de jubilació (decumulació) ────────────────────────
            # 1. Rescat de pensions: el 25% exempt passa a la cartera líquida (pot "altres") com a capital
            if age >= p_pension_access_age and not p_pension_unlocked and p_pension_pot > 0:
                p_pension_unlocked = True
                lump_sum_p = min(200_000.0, p_pension_pot * 0.25)  # màxim legal exempt
                p_pension_pot -= lump_sum_p
                misc_pot += lump_sum_p
                misc_basis += lump_sum_p
                lump_sum_this_year += lump_sum_p
                total_tax_free_lump_sum_cum += lump_sum_p
                notes = (
                    f"🛡️ Private Pension Unlocked at age {age}! €{round(lump_sum_p):,} Tax-Free Lump Sum (25%)"
                    if is_en
                    else f"🛡️ Rescat Pensió Privada als {age} anys! {round(lump_sum_p):,} € Capital Exempt (25%)"
                )

            if age >= mff_access_age and not mff_unlocked and mff_pot > 0:
                mff_unlocked = True
                lump_sum_mff = mff_pot * 0.25
                mff_pot -= lump_sum_mff
                misc_pot += lump_sum_mff
                misc_basis += lump_sum_mff
                lump_sum_this_year += lump_sum_mff
                total_tax_free_lump_sum_cum += lump_sum_mff
                mff_note = (
                    f"🏛️ MyFutureFund Unlocked at age {age}! €{round(lump_sum_mff):,} Tax-Free Lump Sum (25%)"
                    if is_en
                    else f"🏛️ MyFutureFund als {age} anys! {round(lump_sum_mff):,} € Capital Exempt (25%)"
                )
                notes = f"{notes} | {mff_note}" if notes else mff_note

            # 2. Ingrés net objectiu d'aquest any (ajustat per inflació)
            net_needed = target_annual_net_income * inflation_factor

            if state_pension_enabled and age >= state_pension_access_age:
                state_pension_this_year = (state_pension_monthly * 12.0) * inflation_factor
                if age == state_pension_access_age:
                    pension_note = (
                        f"🏛️ State Pension active! +€{round(state_pension_this_year):,} /yr"
                        if is_en
                        else f"🏛️ Pensió d'Estat activa! +{round(state_pension_this_year):,} €/any"
                    )
                    notes = f"{notes} | {pension_note}" if notes else pension_note
            # La pensió d'Estat no tributa en aquest model
            net_needed = max(0.0, net_needed - state_pension_this_year)

            # 3. ARF / MyFutureFund (si ja estan desbloquejats), fins a la SWR del pot
            pension_gross = 0.0

            def draw_pensions(net_wanted: float, capped: bool) -> float:
                """Retira de les pensions desbloquejades; retorna el net obtingut."""
                nonlocal p_pension_pot, mff_pot, pension_gross
                got = 0.0
                for which in ("p", "mff"):
                    unlocked = p_pension_unlocked if which == "p" else mff_unlocked
                    pot = p_pension_pot if which == "p" else mff_pot
                    if not unlocked or pot <= 0 or net_wanted - got <= 0:
                        continue
                    gross_wanted = (net_wanted - got) / (1.0 - pension_tax_rate)
                    limit = pot * swr_decimal if capped else pot
                    gross = min(pot, limit, gross_wanted)
                    if which == "p":
                        p_pension_pot -= gross
                    else:
                        mff_pot -= gross
                    pension_gross += gross
                    got += gross * (1.0 - pension_tax_rate)
                return got

            net_needed -= draw_pensions(net_needed, capped=True)

            # 4. Cartera líquida: la taxa anual del compte es paga amb una retirada extra del mateix compte
            if i > 0:
                account_charge_paid = max(0.0, b27_pot - threshold) * account_rate
            cash_needed = net_needed + account_charge_paid

            draw_b27 = min(b27_pot, cash_needed)
            b27_pot -= draw_b27
            cash_needed -= draw_b27

            # Primer les accions/altres (CGT 31% amb exempció), després els ETFs (Exit Tax 35%)
            draw_misc, tax_misc = _gross_for_net(cash_needed, misc_pot, misc_basis, ts_cgt, lang)
            if misc_pot > 0:
                misc_basis *= 1.0 - draw_misc / misc_pot
            misc_pot -= draw_misc
            cash_needed -= draw_misc - tax_misc

            draw_etf, tax_etf = _gross_for_net(cash_needed, etf_pot, etf_basis, ts_etf, lang)
            if etf_pot > 0:
                etf_basis *= 1.0 - draw_etf / etf_pot
            etf_pot -= draw_etf
            cash_needed -= draw_etf - tax_etf

            # Si la cartera líquida no arriba, es retira més de les pensions ja desbloquejades
            if cash_needed > 1.0:
                cash_needed -= draw_pensions(cash_needed, capped=False)

            pension_income_tax = pension_gross * pension_tax_rate
            gross_withdrawal_this_year = (
                draw_b27 + draw_misc + draw_etf + pension_gross + state_pension_this_year
            )
            tax_paid_this_year = account_charge_paid + tax_misc + tax_etf + pension_income_tax
            net_disposable_this_year = max(0.0, gross_withdrawal_this_year - tax_paid_this_year)

            if first_year_breakdown is None:
                first_year_breakdown = {
                    "gross": gross_withdrawal_this_year / inflation_factor,
                    "tax": tax_paid_this_year / inflation_factor,
                    "account_charge": account_charge_paid / inflation_factor,
                    "exit_tax": tax_etf / inflation_factor,
                    "cgt": tax_misc / inflation_factor,
                    "pension_tax": pension_income_tax / inflation_factor,
                    "state_pension": state_pension_this_year / inflation_factor,
                }

            # ¿S'ha pogut cobrir la despesa?
            if cash_needed > 1.0:
                has_income_shortfall = True
                if p_pension_pot + mff_pot > 0 and not notes:
                    notes = (
                        "⚠️ Income gap: liquid portfolio is empty and pensions are still locked"
                        if is_en
                        else "⚠️ Dèficit d'ingressos: cartera líquida esgotada i pensions encara bloquejades"
                    )

            # 5. Rendiment sobre els capitals restants
            b27_pot *= 1.0 + r_b27
            etf_pot *= 1.0 + r_etf
            misc_pot *= 1.0 + r_misc
            p_pension_pot *= 1.0 + p_pension_return
            mff_pot *= 1.0 + mff_return

        bridge_pot = b27_pot + etf_pot + misc_pot
        total_portfolio_year = bridge_pot + p_pension_pot + mff_pot
        if total_portfolio_year > 0.5:
            portfolio_survival_years += 1
        elif start_of_period_portfolio > 0:
            portfolio_exhausted = True
            if not notes:
                notes = "❌ Portfolio Depletion" if is_en else "❌ Esgotament del capital"

        ending_portfolio = max(0.0, total_portfolio_year)

        if not notes and i == fire_achieved_year_index:
            notes = (
                "🎉 Financial Independence Achieved!"
                if is_en
                else "🎉 Assoliment de la Independència Financera!"
            )
        elif not notes and calendar_year == ACCOUNT_OPEN_YEAR and regime == "budget_2027_account" and not is_retired:
            notes = (
                "🌟 Investment Account opens (1 July): savings go in up to €12,000/yr"
                if is_en
                else "🌟 Obre el Compte d'Inversió (1 de juliol): estalvis fins a 12.000 €/any"
            )
        elif not notes and account_charge_paid > 0:
            notes = (
                f"🇮🇪 Investment Account charge ({account_rate * 100:g}% above €{round(threshold):,}): €{round(account_charge_paid):,}"
                if is_en
                else f"🇮🇪 Taxa Compte Inversió ({account_rate * 100:g}% sobre {round(threshold):,} €): {round(account_charge_paid):,} €"
            )

        projections.append(
            YearProjection(
                year_index=i,
                calendar_year=calendar_year,
                age=age,
                is_retired=is_retired,
                starting_portfolio=start_of_period_portfolio,
                gross_return=r_etf,
                inflation_factor=inflation_factor,
                contribution=contribution_this_year,
                gross_withdrawal=gross_withdrawal_this_year,
                tax_paid=tax_paid_this_year,
                net_disposable_income=net_disposable_this_year,
                ending_portfolio=ending_portfolio,
                ending_portfolio_real=ending_portfolio / inflation_factor,
                bridge_portfolio=bridge_pot,
                pension_portfolio=p_pension_pot + mff_pot,
                private_pension_value=p_pension_pot,
                my_future_fund_value=mff_pot,
                tax_free_lump_sum_received=lump_sum_this_year,
                state_pension_received=state_pension_this_year,
                deemed_disposal_tax_paid=deemed_disposal_tax_paid if deemed_disposal_tax_paid > 0 else None,
                tax_notes=notes if notes else None,
            )
        )

    # ── Resum ──────────────────────────────────────────────────────────
    reached = fire_achieved_year_index != -1
    years_to_fire = fire_achieved_year_index if reached else 0
    is_already_fire = reached and fire_achieved_year_index == 0 and mode == "target_spending"

    if first_year_breakdown is None:
        # Objectiu no assolit: estimació amb el règim de planificació
        est = compute_annual_tax_for_withdrawal(gross_withdrawal_needed, ts_plan, fire_number_nominal, lang)
        first_year_breakdown = {
            "gross": gross_withdrawal_needed,
            "tax": est.total_tax,
            "account_charge": 0.0,
            "exit_tax": est.total_tax if ts_plan is ts_etf else 0.0,
            "cgt": est.total_tax if ts_plan is ts_cgt else 0.0,
            "pension_tax": 0.0,
            "state_pension": 0.0,
        }
    fy = first_year_breakdown
    fy_gross = fy["gross"]

    return FireCalculationResult(
        fire_number_nominal=fire_number_nominal,
        fire_number_real=fire_number_nominal,
        monthly_disposable_target=target_annual_net_income / 12.0,
        annual_gross_withdrawal_needed=gross_withdrawal_needed,
        annual_tax_at_retirement=fy["tax"],
        effective_tax_rate_at_retirement=fy["tax"] / fy_gross if fy_gross > 0 else 0.0,
        retirement_year_gross=fy_gross,
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
        current_total_net_worth=current_total_net_worth,
        projected_portfolio_at_fire=portfolio_at_fire,
        projections=projections,
        portfolio_survival_years=portfolio_survival_years,
        final_portfolio_value=projections[-1].ending_portfolio if projections else 0.0,
        is_sustainable=reached and not portfolio_exhausted and not has_income_shortfall,
        bridge_capital_at_fire=bridge_at_fire if reached else bridge_capital_initial,
        pension_capital_at_fire=pension_at_fire if reached else (private_pension_initial + mff_initial),
        private_pension_unlocked_age=p_pension_access_age,
        my_future_fund_unlocked_age=mff_access_age,
        state_pension_unlocked_age=state_pension_access_age,
        state_pension_annual_amount=(state_pension_monthly * 12.0) if state_pension_enabled else 0.0,
        tax_free_lump_sum_total=total_tax_free_lump_sum_cum,
    )
