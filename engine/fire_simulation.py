"""
Motor de simulació per a la independència financera (FIRE) a Irlanda.
Model de múltiples pilars: Cartera Pont (Budget 2027 / ETFs) + Pensió Privada (PRSA) + MyFutureFund (Auto-enrolment).
"""
from __future__ import annotations

import copy
from datetime import datetime
from typing import Optional

from models.types import (
    FireCalculationResult,
    FireInputs,
    TaxSettings,
    YearProjection,
)
from engine.tax_calculators import (
    calculate_catalonia_wealth_tax,
    calculate_gross_needed_for_net_income,
    compute_annual_tax_for_withdrawal,
)


def simulate_fire(inputs: FireInputs, lang: str = "ca") -> FireCalculationResult:
    is_en = lang == "en"
    current_year = datetime.now().year

    mode = inputs.mode
    current_age = inputs.current_age
    target_retirement_age = inputs.target_retirement_age
    life_expectancy = inputs.life_expectancy or 88
    target_monthly_disposable_income = inputs.target_monthly_disposable_income
    assets = inputs.assets
    monthly_savings = inputs.monthly_savings
    annual_savings_increase_rate = inputs.annual_savings_increase_rate
    safe_withdrawal_rate = inputs.safe_withdrawal_rate
    scenario = inputs.scenario
    tax_settings = inputs.tax_settings
    pension_settings = inputs.pension_settings

    # 1. Separar la Cartera Pont (accessible) de les Pensions (bloquejades fins a l'edat d'accés)
    bridge_assets = [a for a in assets if a.category not in ("private_pension", "my_future_fund")]
    bridge_capital_initial = sum(float(a.current_amount or 0.0) for a in bridge_assets)

    # Identificar fons de pensions des d'assets o des de pension_settings
    asset_p_pension = next((a for a in assets if a.category == "private_pension"), None)
    asset_mff = next((a for a in assets if a.category == "my_future_fund"), None)

    if asset_p_pension:
        private_pension_initial = float(asset_p_pension.current_amount or 0.0)
    elif pension_settings and pension_settings.private_pension_enabled:
        private_pension_initial = float(pension_settings.private_pension_balance or 0.0)
    else:
        private_pension_initial = 0.0

    if asset_mff:
        mff_initial = float(asset_mff.current_amount or 0.0)
    elif pension_settings and pension_settings.my_future_fund_enabled:
        mff_initial = float(pension_settings.my_future_fund_balance or 0.0)
    else:
        mff_initial = 0.0

    current_total_net_worth = bridge_capital_initial + private_pension_initial + mff_initial
    swr_decimal = max(0.01, safe_withdrawal_rate / 100.0)

    # Rendibilitats i inflació
    nominal_rate = scenario.nominal_return / 100.0
    inflation_rate = scenario.inflation_rate / 100.0

    p_pension_return = (
        pension_settings.private_pension_expected_return / 100.0
        if pension_settings
        else nominal_rate
    )
    mff_return = (
        pension_settings.my_future_fund_expected_return / 100.0
        if pension_settings
        else nominal_rate
    )

    p_pension_access_age = (
        int(pension_settings.private_pension_access_age)
        if (pension_settings and pension_settings.private_pension_enabled)
        else 50
    )
    mff_access_age = 66  # Edat de la Pensió Estatal d'Irlanda

    # Variables calculades objectiu
    target_annual_net_income = 0.0
    gross_withdrawal_needed = 0.0
    fire_number_nominal = 0.0

    if mode == "target_spending":
        target_annual_net_income = target_monthly_disposable_income * 12.0
        tax_res = calculate_gross_needed_for_net_income(
            target_annual_net_income, tax_settings, current_total_net_worth, lang
        )
        gross_withdrawal_needed = tax_res.gross_withdrawal
        fire_number_nominal = gross_withdrawal_needed / swr_decimal
    else:
        simulated_capital = current_total_net_worth
        years_to_sim_target = max(0, target_retirement_age - current_age)
        current_annual_savings = monthly_savings * 12.0
        p_annual_savings = (
            pension_settings.private_pension_monthly_contribution * 12.0
            if (pension_settings and pension_settings.private_pension_enabled)
            else 0.0
        )
        mff_annual_savings = (
            (
                pension_settings.my_future_fund_employee_monthly
                + pension_settings.my_future_fund_employer_match_monthly
                + pension_settings.my_future_fund_state_topup_monthly
            )
            * 12.0
            if (pension_settings and pension_settings.my_future_fund_enabled)
            else 0.0
        )
        total_annual_inflow = current_annual_savings + p_annual_savings + mff_annual_savings

        for _ in range(years_to_sim_target):
            simulated_capital = simulated_capital * (1.0 + nominal_rate) + total_annual_inflow
            total_annual_inflow *= 1.0 + (annual_savings_increase_rate or 0.0) / 100.0

        fire_number_nominal = simulated_capital
        gross_withdrawal_needed = fire_number_nominal * swr_decimal
        tax_res = compute_annual_tax_for_withdrawal(
            gross_withdrawal_needed, tax_settings, fire_number_nominal, lang
        )
        target_annual_net_income = tax_res.net_disposable_income

    is_already_fire = current_total_net_worth >= fire_number_nominal and fire_number_nominal > 0

    # 2. Simulació Any a Any fins a l'esperança de vida
    projections: list[YearProjection] = []
    bridge_pot = bridge_capital_initial
    p_pension_pot = private_pension_initial
    mff_pot = mff_initial

    annual_bridge_contrib = monthly_savings * 12.0
    annual_p_contrib = (
        pension_settings.private_pension_monthly_contribution * 12.0
        if (pension_settings and pension_settings.private_pension_enabled)
        else 0.0
    )
    annual_mff_contrib = (
        (
            pension_settings.my_future_fund_employee_monthly
            + pension_settings.my_future_fund_employer_match_monthly
            + pension_settings.my_future_fund_state_topup_monthly
        )
        * 12.0
        if (pension_settings and pension_settings.my_future_fund_enabled)
        else 0.0
    )

    total_years = max(1, life_expectancy - current_age)
    fire_achieved_year_index = -1
    retirement_age_actual = target_retirement_age
    deemed_disposal_basis = bridge_capital_initial

    # Determinar any FIRE si estem en mode target_spending
    if mode == "target_spending" and not is_already_fire:
        test_bridge = bridge_capital_initial
        test_p = private_pension_initial
        test_mff = mff_initial
        test_c_bridge = annual_bridge_contrib
        test_c_p = annual_p_contrib
        test_c_mff = annual_mff_contrib

        for y in range(70):
            inflation_adjustment = (1.0 + inflation_rate) ** y
            inflated_fire_number = fire_number_nominal * inflation_adjustment
            total_test = test_bridge + test_p + test_mff

            if total_test >= inflated_fire_number:
                fire_achieved_year_index = y
                break

            test_bridge = test_bridge * (1.0 + nominal_rate) + test_c_bridge
            test_p = test_p * (1.0 + p_pension_return) + test_c_p
            test_mff = test_mff * (1.0 + mff_return) + test_c_mff

            test_c_bridge *= 1.0 + (annual_savings_increase_rate or 0.0) / 100.0
            test_c_p *= 1.0 + (annual_savings_increase_rate or 0.0) / 100.0
            test_c_mff *= 1.0 + (annual_savings_increase_rate or 0.0) / 100.0
    elif is_already_fire:
        fire_achieved_year_index = 0
    else:
        fire_achieved_year_index = max(0, target_retirement_age - current_age)

    if fire_achieved_year_index != -1:
        retirement_age_actual = current_age + fire_achieved_year_index

    portfolio_survival_years = 0
    portfolio_exhausted = False
    total_tax_free_lump_sum_cum = 0.0

    p_pension_unlocked = False
    mff_unlocked = False

    for i in range(total_years + 1):
        age = current_age + i
        calendar_year = current_year + i
        is_retired = (
            (i >= fire_achieved_year_index and fire_achieved_year_index != -1)
            if mode == "target_spending"
            else (age >= target_retirement_age)
        )

        inflation_factor = (1.0 + inflation_rate) ** i
        start_of_period_portfolio = max(0.0, bridge_pot + p_pension_pot + mff_pot)

        active_tax_settings: TaxSettings = copy.copy(tax_settings)

        contribution_this_year = 0.0
        gross_withdrawal_this_year = 0.0
        tax_paid_this_year = 0.0
        net_disposable_this_year = 0.0
        deemed_disposal_tax_paid = 0.0
        ireland_account_tax_paid = 0.0
        lump_sum_this_year = 0.0
        current_return_rate = nominal_rate

        # Sequence of returns stress test
        if (
            is_retired
            and scenario.stress_drop_first_years
            and i - fire_achieved_year_index < 2
            and i >= fire_achieved_year_index
        ):
            current_return_rate = -abs(scenario.stress_drop_first_years) / 100.0

        notes: str = ""

        if not is_retired:
            # Fase d'acumulació
            contrib_bridge = annual_bridge_contrib
            contrib_p = annual_p_contrib
            contrib_mff = annual_mff_contrib

            contribution_this_year = contrib_bridge + contrib_p + contrib_mff

            annual_bridge_contrib *= 1.0 + (annual_savings_increase_rate or 0.0) / 100.0
            annual_p_contrib *= 1.0 + (annual_savings_increase_rate or 0.0) / 100.0
            annual_mff_contrib *= 1.0 + (annual_savings_increase_rate or 0.0) / 100.0

            # Rendiment sobre la cartera líquida Bridge
            bridge_pot = bridge_pot * (1.0 + current_return_rate) + contrib_bridge

            # Fiscalitat sobre la cartera líquida Bridge a Irlanda (Pressupost 2027)
            if (
                active_tax_settings.country == "IE"
                and active_tax_settings.ireland_asset_type == "budget_2027_account"
                and i > 0
            ):
                threshold = getattr(active_tax_settings, "ireland_investment_account_threshold", 50000.0)
                account_rate = max(
                    0.0,
                    (getattr(active_tax_settings, "ireland_investment_account_rate", 1.0)
                     + (active_tax_settings.tax_reform_change_rate or 0.0)) / 100.0,
                )
                taxable_above = max(0.0, bridge_pot - threshold)
                if taxable_above > 0:
                    ireland_account_tax_paid = taxable_above * account_rate
                    bridge_pot = max(0.0, bridge_pot - ireland_account_tax_paid)
                    tax_paid_this_year += ireland_account_tax_paid

            # Irlanda Deemed Disposal sobre ETFs de la cartera líquida
            if (
                active_tax_settings.country == "IE"
                and active_tax_settings.ireland_asset_type == "etf_exit_tax"
                and active_tax_settings.ireland_simulate_deemed_disposal
                and i > 0
            ):
                is_rolling = (
                    active_tax_settings.ireland_deemed_disposal_mode or "staggered_rolling_eighth"
                ) == "staggered_rolling_eighth"
                should_apply = True if is_rolling else (i % 8 == 0)
                if should_apply:
                    unrealized_gains = max(0.0, bridge_pot - deemed_disposal_basis)
                    if unrealized_gains > 0:
                        exit_rate = max(0.0, 0.35 + (active_tax_settings.tax_reform_change_rate or 0.0) / 100.0)
                        maturing_gain = unrealized_gains / 8.0 if is_rolling else unrealized_gains
                        deemed_disposal_tax_paid = maturing_gain * exit_rate
                        bridge_pot = max(0.0, bridge_pot - deemed_disposal_tax_paid)
                        if is_rolling:
                            deemed_disposal_basis += maturing_gain
                        else:
                            deemed_disposal_basis = bridge_pot
                        tax_paid_this_year += deemed_disposal_tax_paid

            # Les PENSIONS creixen 100% LLIURES D'IMPOSTOS (exempció total irlandesa)
            if p_pension_pot > 0 or contrib_p > 0:
                p_pension_pot = p_pension_pot * (1.0 + p_pension_return) + contrib_p
            if mff_pot > 0 or contrib_mff > 0:
                mff_pot = mff_pot * (1.0 + mff_return) + contrib_mff

        else:
            # Fase de jubilació (Decumulació)
            # 1. Comprovar esdeveniments de rescat de pensions
            # A) Pensió Privada (edat d'accés: p.ex. 50 anys per empresa / 60 PRSA)
            if age >= p_pension_access_age and not p_pension_unlocked and p_pension_pot > 0:
                p_pension_unlocked = True
                # 25% lump sum exempt d'impostos fins a un màxim legal de 200.000 € a Irlanda
                lump_sum_p = min(200_000.0, p_pension_pot * 0.25)
                p_pension_pot -= lump_sum_p
                bridge_pot += lump_sum_p
                lump_sum_this_year += lump_sum_p
                total_tax_free_lump_sum_cum += lump_sum_p
                notes = (
                    f"🛡️ Private Pension Unlocked at age {age}! €{round(lump_sum_p):,} Tax-Free Lump Sum (25%)"
                    if is_en
                    else f"🛡️ Rescat Pensió Privada als {age} anys! {round(lump_sum_p):,} € Capital Exempt (25%)"
                )

            # B) MyFutureFund & Pensió Estatal (als 66 anys)
            if age >= mff_access_age and not mff_unlocked and mff_pot > 0:
                mff_unlocked = True
                # 25% lump sum exempt d'impostos
                lump_sum_mff = mff_pot * 0.25
                mff_pot -= lump_sum_mff
                bridge_pot += lump_sum_mff
                lump_sum_this_year += lump_sum_mff
                total_tax_free_lump_sum_cum += lump_sum_mff
                notes = (
                    f"🏛️ MyFutureFund & State Pension Unlocked at age 66! €{round(lump_sum_mff):,} Tax-Free Lump Sum (25%)"
                    if is_en
                    else f"🏛️ MyFutureFund & Pensió d'Estat als 66 anys! {round(lump_sum_mff):,} € Capital Exempt (25%)"
                )

            # Despesa total requerida ajustada per inflació
            inflated_gross_withdrawal = gross_withdrawal_needed * inflation_factor

            # Ingressos de pensions per cobrir part o la totalitat de la despesa
            pension_drawdown_this_year = 0.0

            # Retirada de l'ARF de la Pensió Privada (si ja està desbloquejada)
            if p_pension_unlocked and p_pension_pot > 0:
                # Retirada estàndard del 4% d'ARF
                p_drawdown = min(p_pension_pot, p_pension_pot * swr_decimal)
                p_pension_pot -= p_drawdown
                pension_drawdown_this_year += p_drawdown

            # Retirada de MyFutureFund (a partir dels 66 anys)
            if mff_unlocked and mff_pot > 0:
                mff_drawdown = min(mff_pot, mff_pot * swr_decimal)
                mff_pot -= mff_drawdown
                pension_drawdown_this_year += mff_drawdown

            # El romanent es retira de la Cartera Pont (Bridge)
            withdrawal_from_bridge = max(0.0, inflated_gross_withdrawal - pension_drawdown_this_year)
            actual_bridge_withdrawal = min(bridge_pot, withdrawal_from_bridge)
            bridge_pot = max(0.0, bridge_pot - actual_bridge_withdrawal)

            gross_withdrawal_this_year = actual_bridge_withdrawal + pension_drawdown_this_year

            # Càlcul d'impostos
            tax_res = compute_annual_tax_for_withdrawal(
                gross_withdrawal_this_year, active_tax_settings, bridge_pot, lang
            )
            tax_paid_this_year = tax_res.total_tax
            net_disposable_this_year = max(0.0, gross_withdrawal_this_year - tax_paid_this_year)

            # Rendiment sobre els capitals restants
            if bridge_pot > 0:
                bridge_pot *= 1.0 + current_return_rate
            if p_pension_pot > 0:
                p_pension_pot *= 1.0 + p_pension_return
            if mff_pot > 0:
                mff_pot *= 1.0 + mff_return

        total_portfolio_year = bridge_pot + p_pension_pot + mff_pot
        if total_portfolio_year > 0:
            portfolio_survival_years += 1
        elif start_of_period_portfolio > 0:
            portfolio_exhausted = True
            if not notes:
                notes = "❌ Portfolio Depletion" if is_en else "❌ Esgotament del capital"

        ending_portfolio = max(0.0, total_portfolio_year)
        ending_portfolio_real = ending_portfolio / inflation_factor

        if not notes and i == fire_achieved_year_index and is_retired:
            notes = (
                "🎉 Financial Independence Achieved!"
                if is_en
                else "🎉 Assoliment de la Independència Financera!"
            )
        elif not notes and ireland_account_tax_paid > 0:
            notes = (
                f"🇮🇪 Irish Investment Account (1% >€50k): €{round(ireland_account_tax_paid):,}"
                if is_en
                else f"🇮🇪 Compte Inversió Irlanda (1% >50k €): {round(ireland_account_tax_paid):,} €"
            )

        projections.append(
            YearProjection(
                year_index=i,
                calendar_year=calendar_year,
                age=age,
                is_retired=is_retired,
                starting_portfolio=start_of_period_portfolio,
                gross_return=current_return_rate,
                inflation_factor=inflation_factor,
                contribution=contribution_this_year,
                gross_withdrawal=gross_withdrawal_this_year,
                tax_paid=tax_paid_this_year,
                net_disposable_income=net_disposable_this_year,
                ending_portfolio=ending_portfolio,
                ending_portfolio_real=ending_portfolio_real,
                bridge_portfolio=bridge_pot,
                pension_portfolio=p_pension_pot + mff_pot,
                private_pension_value=p_pension_pot,
                my_future_fund_value=mff_pot,
                tax_free_lump_sum_received=lump_sum_this_year,
                deemed_disposal_tax_paid=deemed_disposal_tax_paid if deemed_disposal_tax_paid > 0 else None,
                tax_notes=notes if notes else None,
            )
        )

    # Resum fiscal en l'any de jubilació
    sample_tax = compute_annual_tax_for_withdrawal(
        gross_withdrawal_needed, tax_settings, fire_number_nominal, lang
    )
    years_to_fire = 0 if is_already_fire else max(0, retirement_age_actual - current_age)
    age_at_fire = current_age if is_already_fire else retirement_age_actual
    calendar_year_at_fire = current_year + years_to_fire

    # Capital en pensions vs bridge en jubilar-se
    proj_at_fire = projections[min(len(projections) - 1, years_to_fire)] if projections else None

    return FireCalculationResult(
        fire_number_nominal=fire_number_nominal,
        fire_number_real=fire_number_nominal,
        monthly_disposable_target=target_annual_net_income / 12.0,
        annual_gross_withdrawal_needed=gross_withdrawal_needed,
        annual_tax_at_retirement=sample_tax.total_tax,
        effective_tax_rate_at_retirement=sample_tax.effective_tax_rate,
        years_to_fire=years_to_fire,
        age_at_fire=age_at_fire,
        calendar_year_at_fire=calendar_year_at_fire,
        is_already_fire=is_already_fire,
        current_total_net_worth=current_total_net_worth,
        projected_portfolio_at_fire=current_total_net_worth if is_already_fire else fire_number_nominal,
        projections=projections,
        portfolio_survival_years=portfolio_survival_years,
        final_portfolio_value=projections[-1].ending_portfolio if projections else 0.0,
        is_sustainable=not portfolio_exhausted,
        bridge_capital_at_fire=proj_at_fire.bridge_portfolio if proj_at_fire else bridge_capital_initial,
        pension_capital_at_fire=proj_at_fire.pension_portfolio if proj_at_fire else (private_pension_initial + mff_initial),
        private_pension_unlocked_age=p_pension_access_age,
        my_future_fund_unlocked_age=mff_access_age,
        tax_free_lump_sum_total=total_tax_free_lump_sum_cum,
    )
