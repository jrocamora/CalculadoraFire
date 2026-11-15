"""Tests of the year-by-year simulation engine."""
from __future__ import annotations

import pytest

from config.defaults import (
    get_initial_assets,
    get_initial_pension_settings,
    get_initial_scenario,
    get_initial_tax_settings,
)
from engine.fire_simulation import account_contribution_cap, simulate_fire
from models.types import FireInputs

REGIMES = ("budget_2027_account", "etf_exit_tax", "individual_shares_cgt")


def make_inputs(**overrides) -> FireInputs:
    data = dict(
        mode="target_spending",
        current_age=32,
        target_retirement_age=48,
        life_expectancy=88,
        target_monthly_disposable_income=2500.0,
        assets=get_initial_assets(),
        monthly_savings=900.0,
        annual_savings_increase_rate=2.0,
        safe_withdrawal_rate=3.5,
        scenario=get_initial_scenario(),
        tax_settings=get_initial_tax_settings(),
        pension_settings=get_initial_pension_settings(),
    )
    data.update(overrides)
    return FireInputs(**data)


def tax_settings(regime: str, **changes):
    ts = get_initial_tax_settings()
    ts.ireland_asset_type = regime
    for key, value in changes.items():
        setattr(ts, key, value)
    return ts


def retired_years(result):
    return [p for p in result.projections if p.is_retired]


@pytest.mark.parametrize("regime", REGIMES)
def test_retires_only_when_projected_portfolio_reaches_target(regime):
    r = simulate_fire(make_inputs(tax_settings=tax_settings(regime)), "en")
    assert r.fire_reachable
    first = retired_years(r)[0]
    assert first.age == r.age_at_fire
    assert first.starting_portfolio >= r.fire_number_nominal * first.inflation_factor
    before = r.projections[r.years_to_fire - 1]
    assert before.starting_portfolio < r.fire_number_nominal * before.inflation_factor


@pytest.mark.parametrize("regime", REGIMES)
def test_every_retired_year_pays_exactly_the_target_net_income(regime):
    r = simulate_fire(make_inputs(tax_settings=tax_settings(regime)), "en")
    target = r.monthly_disposable_target * 12.0
    assert target == pytest.approx(30_000.0, abs=1)
    for p in retired_years(r):
        assert p.net_disposable_income == pytest.approx(target * p.inflation_factor, rel=1e-4)
        assert p.gross_withdrawal - p.tax_paid == pytest.approx(p.net_disposable_income, abs=0.01)


def test_summary_breakdown_adds_up():
    r = simulate_fire(make_inputs(), "en")
    parts = (
        r.retirement_year_account_charge
        + r.retirement_year_exit_tax
        + r.retirement_year_cgt
        + r.retirement_year_pension_tax
    )
    assert parts == pytest.approx(r.annual_tax_at_retirement, abs=0.01)
    assert r.retirement_year_gross - r.annual_tax_at_retirement == pytest.approx(30_000.0, abs=1)


def test_account_contribution_cap():
    assert account_contribution_cap(2026) == 0
    assert account_contribution_cap(2027) == 6_000
    assert account_contribution_cap(2030) == 12_000


def test_deemed_disposal_never_taxes_contributions():
    """With zero growth there are no gains, so deemed disposal must collect nothing."""
    assets = get_initial_assets()
    for a in assets:
        a.expected_return_annual = 7.0
        a.cost_basis = a.current_amount
    scenario = get_initial_scenario()
    scenario.nominal_return = 0.0  # shifts every asset from 7% to 0%
    scenario.inflation_rate = 0.0
    r = simulate_fire(make_inputs(assets=assets, scenario=scenario, tax_settings=tax_settings("etf_exit_tax")), "en")
    assert all(not p.deemed_disposal_tax_paid for p in r.projections)


def test_deemed_disposal_can_be_switched_off():
    on = simulate_fire(make_inputs(tax_settings=tax_settings("etf_exit_tax")), "en")
    off = simulate_fire(
        make_inputs(tax_settings=tax_settings("etf_exit_tax", ireland_simulate_deemed_disposal=False)), "en"
    )
    assert any(p.deemed_disposal_tax_paid for p in on.projections)
    assert not any(p.deemed_disposal_tax_paid for p in off.projections)
    assert off.years_to_fire <= on.years_to_fire


def test_reform_slider_does_not_change_the_account_charge():
    base = simulate_fire(make_inputs(), "en")
    reformed = simulate_fire(make_inputs(tax_settings=tax_settings("budget_2027_account", tax_reform_change_rate=10.0)), "en")
    assert reformed.retirement_year_account_charge == pytest.approx(
        base.retirement_year_account_charge, rel=0.25
    )
    assert reformed.is_sustainable


def test_unreachable_target_is_reported():
    scenario = get_initial_scenario()
    scenario.nominal_return = 2.0
    scenario.inflation_rate = 3.0
    r = simulate_fire(make_inputs(target_monthly_disposable_income=12_000.0, monthly_savings=0.0, scenario=scenario), "en")
    assert not r.fire_reachable
    assert not r.is_sustainable
    assert not any(p.is_retired for p in r.projections)


def test_asset_returns_and_cost_basis_matter():
    base = simulate_fire(make_inputs(), "en")
    assets = get_initial_assets()
    for a in assets:
        a.expected_return_annual = 10.0
    assert simulate_fire(make_inputs(assets=assets), "en").years_to_fire < base.years_to_fire

    ts = tax_settings("individual_shares_cgt")
    low_basis = get_initial_assets()
    for a in low_basis:
        a.cost_basis = 0.0
    assert (
        simulate_fire(make_inputs(assets=low_basis, tax_settings=ts), "en").annual_tax_at_retirement
        > simulate_fire(make_inputs(tax_settings=ts), "en").annual_tax_at_retirement
    )


def test_pension_lump_sum_reaches_the_liquid_portfolio():
    ps = get_initial_pension_settings()
    ps.private_pension_enabled = True
    ps.private_pension_balance = 400_000.0
    ps.private_pension_monthly_contribution = 0.0
    ps.private_pension_access_age = 60
    r = simulate_fire(make_inputs(pension_settings=ps, mode="current_portfolio", target_retirement_age=59), "en")
    unlock = next(p for p in r.projections if p.age == 60)
    before = next(p for p in r.projections if p.age == 59)
    assert unlock.tax_free_lump_sum_received == pytest.approx(200_000.0)
    # The lump sum moves from the pension into the liquid ("bridge") portfolio
    assert unlock.bridge_portfolio > before.bridge_portfolio
    assert r.tax_free_lump_sum_total == pytest.approx(200_000.0)


def _locked_pension_case(monthly_savings: float):
    ps = get_initial_pension_settings()
    ps.private_pension_enabled = True
    ps.private_pension_balance = 1_500_000.0
    ps.private_pension_monthly_contribution = 0.0
    ps.private_pension_access_age = 60
    assets = get_initial_assets()
    for a in assets:
        a.current_amount = 0.0
        a.cost_basis = 0.0
    return make_inputs(pension_settings=ps, assets=assets, monthly_savings=monthly_savings, current_age=40)


def test_does_not_retire_on_locked_pension_money():
    """The total is above the target from day one, but nothing is accessible until 60."""
    r = simulate_fire(_locked_pension_case(monthly_savings=0.0), "en")
    assert r.waited_for_pension_unlock
    assert r.age_at_fire == 60
    assert not r.has_income_shortfall
    assert r.is_sustainable


def test_retires_once_liquid_savings_bridge_the_gap():
    r = simulate_fire(_locked_pension_case(monthly_savings=1500.0), "en")
    assert r.waited_for_pension_unlock
    assert 40 < r.age_at_fire < 60
    assert not r.has_income_shortfall
    target = r.monthly_disposable_target * 12.0
    for p in retired_years(r):
        assert p.net_disposable_income == pytest.approx(target * p.inflation_factor, rel=1e-4)
    # Retiring one year earlier would have left a gap before the pension unlocks
    earlier = r.projections[r.years_to_fire - 1]
    assert earlier.starting_portfolio >= r.fire_number_nominal * earlier.inflation_factor


def test_without_pensions_nothing_waits():
    r = simulate_fire(make_inputs(), "en")
    assert not r.waited_for_pension_unlock


def test_pension_drawdowns_are_taxed():
    ps = get_initial_pension_settings()
    ps.private_pension_enabled = True
    ps.private_pension_balance = 1_500_000.0
    ps.private_pension_monthly_contribution = 0.0
    ps.private_pension_access_age = 50
    assets = get_initial_assets()
    for a in assets:
        a.current_amount = 0.0
        a.cost_basis = 0.0
    r = simulate_fire(
        make_inputs(pension_settings=ps, assets=assets, monthly_savings=0.0, current_age=60), "en"
    )
    assert r.retirement_year_pension_tax > 0
