"""End-to-end tests of the Streamlit page, driven headlessly with AppTest."""
from __future__ import annotations

import re

import pytest
from streamlit.testing.v1 import AppTest

from config.defaults import get_initial_assets, get_initial_pension_settings, get_initial_scenario, get_initial_tax_settings
from utils.serialization import encode_plan_to_token, plan_to_dict

TIMEOUT = 60


def key(at: AppTest, name: str) -> str:
    """Widget keys carry the reset generation (see ui/keys.py)."""
    return f"{name}__{at.session_state.ui_nonce}"


def page_html(at: AppTest) -> str:
    return " ".join(m.value for m in at.markdown)


def cards(at: AppTest) -> list[str]:
    vals = re.findall(r'metric-value">\s*(.*?)\s*(?:<span|</div>)', page_html(at), flags=re.S)
    return [v.strip() for v in vals]


def start(**query) -> AppTest:
    at = AppTest.from_file("app.py", default_timeout=TIMEOUT)
    for name, value in query.items():
        at.query_params[name] = value
    at.run()
    assert not at.exception, at.exception
    return at


@pytest.fixture
def app() -> AppTest:
    return start()


@pytest.fixture(scope="module")
def default_cards() -> list[str]:
    return cards(start())


def sample_plan() -> dict:
    ts = get_initial_tax_settings()
    ts.ireland_asset_type = "etf_exit_tax"
    return plan_to_dict(
        "current_portfolio", 4200.0, 40, 55, 90, 1500.0, 3.0, 4.0,
        get_initial_assets(), get_initial_pension_settings(), ts, get_initial_scenario(),
    )


# ── Rendering ───────────────────────────────────────────────────────────

def test_time_card_html_has_no_blank_lines(app):
    """A blank line inside an HTML block makes Markdown print the rest as text (the stray </div> bug)."""
    card = next(m.value for m in app.markdown if 'class="metric-card-time"' in m.value)
    assert not re.search(r"\n\s*\n", card.strip())


def test_no_false_privacy_claims(app):
    assert not re.search(r"run locally|No data stored|100% locally|sent to the server\.", page_html(app))


def test_breakdown_net_matches_target(app):
    m = re.search(r"Net in pocket:.*?\(€([\d,]+)\)", page_html(app), re.S)
    assert m and abs(int(m.group(1).replace(",", "")) - 30_000) <= 2


# ── Results follow the inputs in the same run ───────────────────────────

def test_swr_change_applies_immediately(app, default_cards):
    app.slider(key=key(app, "swr_slider")).set_value(3.0).run()
    after = cards(app)
    app.run()
    assert after != default_cards and after == cards(app)


def test_age_change_applies_immediately(app, default_cards):
    years = int(default_cards[1])
    app.number_input(key=key(app, "current_age_input")).set_value(45).run()
    assert f"<strong>{45 + years} years</strong>" in page_html(app)


def test_regime_change_applies_immediately(app, default_cards):
    app.radio(key=key(app, "ireland_scheme_radio")).set_value("etf_exit_tax").run()
    after = cards(app)
    app.run()
    assert after != default_cards and after == cards(app)


def test_asset_return_changes_result(app, default_cards):
    app.number_input(key=key(app, "asset_ret_asset-1")).set_value(12.0).run()
    assert cards(app) != default_cards


# ── Target income: presets, box and slider stay in sync ─────────────────

def test_target_income_controls_stay_in_sync(app):
    app.button(key=key(app, "preset_5000")).click().run()
    assert app.number_input(key=key(app, "target_monthly_income_input")).value == 5000.0
    assert app.slider(key=key(app, "target_monthly_income_slider")).value == 5000.0
    assert "5,000" in cards(app)[2]

    app.slider(key=key(app, "target_monthly_income_slider")).set_value(4000.0).run()
    assert app.number_input(key=key(app, "target_monthly_income_input")).value == 4000.0
    assert "4,000" in cards(app)[2]

    app.number_input(key=key(app, "target_monthly_income_input")).set_value(20000.0).run()
    assert app.slider(key=key(app, "target_monthly_income_slider")).value == 12000.0  # slider max
    assert app.session_state.target_monthly_income == 20000.0


# ── Presets ─────────────────────────────────────────────────────────────

def test_macro_presets(app):
    app.button(key=key(app, "macro_preset_conservative")).click().run()
    app.run()
    sc = app.session_state.scenario
    assert (sc.id, sc.nominal_return, sc.inflation_rate) == ("conservative", 5.0, 3.5)
    assert app.slider(key=key(app, "macro_nominal_slider")).value == 5.0

    app.button(key=key(app, "macro_preset_stress_test")).click().run()
    assert app.session_state.scenario.stress_drop_first_years == 15.0

    app.slider(key=key(app, "macro_nominal_slider")).set_value(8.0).run()
    assert app.session_state.scenario.id == "custom"


def test_swr_preset_sticks(app):
    app.button(key=key(app, "swr_preset_4.0")).click().run()
    app.run()
    assert app.session_state.safe_withdrawal_rate == 4.0
    assert app.slider(key=key(app, "swr_slider")).value == 4.0


def test_state_pension_preset(app):
    app.checkbox(key=key(app, "pension_state_enabled")).check().run()
    app.button(key=key(app, "preset_sp_75")).click().run()
    assert app.session_state.pension_settings.state_pension_monthly_amount == 1005.0


@pytest.mark.parametrize("regime", ["budget_2027_account", "etf_exit_tax", "individual_shares_cgt"])
def test_deemed_disposal_checkbox_always_visible(app, regime):
    app.radio(key=key(app, "ireland_scheme_radio")).set_value(regime).run()
    assert any(c.key == key(app, "ie_deemed_disposal_checkbox") for c in app.checkbox)


# ── Reset ───────────────────────────────────────────────────────────────

def test_reset_restores_model_widgets_and_results(app, default_cards):
    app.number_input(key=key(app, "target_ret_age_input")).set_value(60).run()
    app.slider(key=key(app, "macro_nominal_slider")).set_value(10.0).run()
    app.radio(key=key(app, "ireland_scheme_radio")).set_value("etf_exit_tax").run()
    app.slider(key=key(app, "tax_reform_slider")).set_value(5.0).run()
    app.number_input(key=key(app, "monthly_savings_input")).set_value(2000.0).run()
    app.number_input(key=key(app, "asset_amount_asset-1")).set_value(99000.0).run()

    app.button(key=key(app, "reset_button_header")).click().run()

    ss = app.session_state
    assert ss.target_retirement_age == 48
    assert ss.scenario.nominal_return == 7.0
    assert ss.tax_settings.ireland_asset_type == "budget_2027_account"
    assert ss.monthly_savings == 900.0
    assert ss.assets[1].current_amount == 75000.0
    assert app.number_input(key=key(app, "monthly_savings_input")).value == 900.0
    assert cards(app) == default_cards


# ── Age inputs depend on each other ─────────────────────────────────────

def test_raising_current_age_past_other_ages_does_not_crash(app):
    app.radio(key=key(app, "calc_mode_radio")).set_value("current_portfolio").run()
    app.number_input(key=key(app, "current_age_input")).set_value(70).run()
    assert not app.exception and app.session_state.target_retirement_age >= 70
    app.number_input(key=key(app, "current_age_input")).set_value(88).run()
    assert not app.exception and app.session_state.life_expectancy > 88


# ── Loading plans ───────────────────────────────────────────────────────

def test_share_link_loads_plan_once():
    at = start(plan=encode_plan_to_token(sample_plan()))
    ss = at.session_state
    assert (ss.mode, ss.current_age, ss.target_retirement_age, ss.monthly_savings, ss.safe_withdrawal_rate) == (
        "current_portfolio", 40, 55, 1500.0, 4.0
    )
    assert any("Plan" in s.value for s in at.success)
    at.run()
    assert not any("Plan" in s.value for s in at.success)


def test_invalid_share_link_shows_error_and_defaults(default_cards):
    at = start(plan="garbage!!")
    assert len(at.error) == 1
    assert cards(at) == default_cards


def test_uploaded_plan_updates_model_and_widgets(app):
    app.number_input(key=key(app, "monthly_savings_input")).set_value(2000.0).run()
    app.session_state.pending_plan = sample_plan()  # what the file uploader stores
    app.run()
    assert not app.exception
    assert app.session_state.monthly_savings == 1500.0
    assert app.number_input(key=key(app, "monthly_savings_input")).value == 1500.0
    assert app.radio(key=key(app, "calc_mode_radio")).value == "current_portfolio"
    assert "pending_plan" not in app.session_state
    assert any("Plan loaded" in s.value for s in app.success)


def test_hostile_plan_is_clamped(app):
    evil = dict(
        sample_plan(), current_age=500, target_monthly_income="abc", safe_withdrawal_rate=99,
        scenario={"nominal_return": 1e9, "inflation_rate": None, "id": "x"},
        assets=[{"category": "index_funds", "current_amount": 1e12, "expected_return_annual": 900}, "junk"],
    )
    app.session_state.pending_plan = evil
    app.run()
    assert not app.exception
    assert app.session_state.current_age == 90


def test_non_dict_plan_is_rejected(app):
    app.session_state.pending_plan = ["not", "a", "plan"]
    app.run()
    assert not app.exception and len(app.error) == 1


# ── Status messages ─────────────────────────────────────────────────────

def test_unreachable_target_is_shown(app):
    app.number_input(key=key(app, "target_monthly_income_input")).set_value(30000.0).run()
    app.number_input(key=key(app, "monthly_savings_input")).set_value(0.0).run()
    html = page_html(app)
    assert "Not reached" in html and "Target not reached" in html
