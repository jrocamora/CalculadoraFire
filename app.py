"""
🔥 FIRE Calculator Ireland Pro — Streamlit Application.
Calibrated for the Irish tax framework including Budget 2027 reforms.
"""
from __future__ import annotations

import streamlit as st
from config.defaults import (
    get_current_year,
    get_initial_assets,
    get_initial_pension_settings,
    get_initial_scenario,
    get_initial_tax_settings,
)
from config.translations import Language, t
from engine.fire_simulation import simulate_fire
from models.types import FireInputs, IrelandAssetType
from ui import (
    render_bidirectional_inputs,
    render_country_comparison,
    render_country_tax_selector,
    render_fire_chart,
    render_header,
    render_macro_scenario_selector,
    render_metric_cards,
    render_pension_controls,
    render_swr_control,
    render_tax_breakdown_card,
    render_yearly_table,
)

# Page configuration
st.set_page_config(
    page_title="FIRE Calculator Ireland (Budget 2027)",
    page_icon="🇮🇪",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def init_session_state():
    """Initializes the session state defaults for the Irish edition."""
    if "lang" not in st.session_state:
        st.session_state.lang = "en"
    if "mode" not in st.session_state:
        st.session_state.mode = "target_spending"
    if "current_age" not in st.session_state:
        st.session_state.current_age = 32
    if "target_retirement_age" not in st.session_state:
        st.session_state.target_retirement_age = 48
    if "life_expectancy" not in st.session_state:
        st.session_state.life_expectancy = 88
    if "target_monthly_income" not in st.session_state:
        st.session_state.target_monthly_income = 2500.0
    if "assets" not in st.session_state:
        st.session_state.assets = get_initial_assets()
    if "monthly_savings" not in st.session_state:
        st.session_state.monthly_savings = 900.0
    if "annual_savings_increase_rate" not in st.session_state:
        st.session_state.annual_savings_increase_rate = 2.0
    if "safe_withdrawal_rate" not in st.session_state:
        st.session_state.safe_withdrawal_rate = 3.5
    if "scenario" not in st.session_state:
        st.session_state.scenario = get_initial_scenario()
    if "tax_settings" not in st.session_state:
        st.session_state.tax_settings = get_initial_tax_settings()
    if "pension_settings" not in st.session_state:
        st.session_state.pension_settings = get_initial_pension_settings()


def handle_reset_defaults():
    """Resets all simulation parameters to default Irish baseline values."""
    st.session_state.mode = "target_spending"
    st.session_state.current_age = 32
    st.session_state.target_retirement_age = 48
    st.session_state.life_expectancy = 88
    st.session_state.target_monthly_income = 2500.0
    st.session_state.assets = get_initial_assets()
    st.session_state.monthly_savings = 900.0
    st.session_state.annual_savings_increase_rate = 2.0
    st.session_state.safe_withdrawal_rate = 3.5
    st.session_state.scenario = get_initial_scenario()
    st.session_state.tax_settings = get_initial_tax_settings()
    st.session_state.pension_settings = get_initial_pension_settings()
    st.rerun()


def handle_lang_change(new_lang: Language):
    st.session_state.lang = new_lang
    st.rerun()


def handle_apply_scheme(scheme_id: IrelandAssetType):
    st.session_state.tax_settings.ireland_asset_type = scheme_id
    st.rerun()


def main():
    init_session_state()
    lang: Language = st.session_state.lang
    current_year = get_current_year()

    # 1. Header with Ireland branding
    render_header(
        current_country=st.session_state.tax_settings.country,
        lang=lang,
        on_lang_change=handle_lang_change,
        on_reset_defaults=handle_reset_defaults,
    )

    # 2. Simulation execution
    fire_inputs = FireInputs(
        mode=st.session_state.mode,
        current_age=st.session_state.current_age,
        target_retirement_age=st.session_state.target_retirement_age,
        life_expectancy=st.session_state.life_expectancy,
        target_monthly_disposable_income=st.session_state.target_monthly_income,
        assets=st.session_state.assets,
        monthly_savings=st.session_state.monthly_savings,
        annual_savings_increase_rate=st.session_state.annual_savings_increase_rate,
        safe_withdrawal_rate=st.session_state.safe_withdrawal_rate,
        scenario=st.session_state.scenario,
        tax_settings=st.session_state.tax_settings,
        pension_settings=st.session_state.pension_settings,
    )

    result = simulate_fire(fire_inputs, lang)

    # 3. 4 Full-Width Key Metric Cards (Ireland specific)
    render_metric_cards(
        result=result,
        safe_withdrawal_rate=st.session_state.safe_withdrawal_rate,
        country="IE",
        lang=lang,
    )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 4. Main 2-Column Layout (Configurator vs Visualization/Breakdown)
    col_inputs, col_viz = st.columns([5, 7], gap="medium")

    # Left Column: Inputs & Controls
    with col_inputs:
        # Calculation Strategy & Target (improved title)
        with st.container(border=True):
            (
                new_mode,
                new_target_inc,
                new_assets,
                new_monthly_sav,
                new_sav_inc,
                new_cur_age,
                new_ret_age,
                new_life_exp,
            ) = render_bidirectional_inputs(
                mode=st.session_state.mode,
                target_monthly_income=st.session_state.target_monthly_income,
                assets=st.session_state.assets,
                monthly_savings=st.session_state.monthly_savings,
                annual_savings_increase_rate=st.session_state.annual_savings_increase_rate,
                current_age=st.session_state.current_age,
                target_retirement_age=st.session_state.target_retirement_age,
                life_expectancy=st.session_state.life_expectancy,
                lang=lang,
            )
            st.session_state.mode = new_mode
            st.session_state.target_monthly_income = new_target_inc
            st.session_state.assets = new_assets
            st.session_state.monthly_savings = new_monthly_sav
            st.session_state.annual_savings_increase_rate = new_sav_inc
            st.session_state.current_age = new_cur_age
            st.session_state.target_retirement_age = new_ret_age
            st.session_state.life_expectancy = new_life_exp

        # Safe Withdrawal Rate (SWR) with complete untruncated benchmark explanations
        with st.container(border=True):
            st.session_state.safe_withdrawal_rate = render_swr_control(
                current_swr=st.session_state.safe_withdrawal_rate,
                lang=lang,
            )

        # Irish Pensions: Private Pension (PRSA) & MyFutureFund Auto-Enrolment
        with st.container(border=True):
            st.session_state.pension_settings = render_pension_controls(
                pension_settings=st.session_state.pension_settings,
                current_age=st.session_state.current_age,
                target_retirement_age=st.session_state.target_retirement_age,
                lang=lang,
            )
            # Sync matching assets in portfolio
            for a in st.session_state.assets:
                if a.category == "private_pension":
                    a.current_amount = st.session_state.pension_settings.private_pension_balance
                    a.expected_return_annual = st.session_state.pension_settings.private_pension_expected_return
                elif a.category == "my_future_fund":
                    a.current_amount = st.session_state.pension_settings.my_future_fund_balance
                    a.expected_return_annual = st.session_state.pension_settings.my_future_fund_expected_return

        # Irish Tax Rules & Investment Schemes (Budget 2027)
        with st.container(border=True):
            st.session_state.tax_settings = render_country_tax_selector(
                tax_settings=st.session_state.tax_settings,
                current_year=current_year,
                lang=lang,
            )

        # Macroeconomic Scenario & Market Stress
        with st.container(border=True):
            st.session_state.scenario = render_macro_scenario_selector(
                scenario=st.session_state.scenario,
                lang=lang,
            )

    # Right Column: Analysis Tabs, Plotly Trajectory Chart, Irish Tax Breakdown, Table
    with col_viz:
        tab_chart, tab_compare, tab_table = st.tabs(
            [t("tabChart", lang), t("tabComparison", lang), t("tabTable", lang)]
        )

        with tab_chart:
            with st.container(border=True):
                render_fire_chart(
                    projections=result.projections,
                    fire_number_nominal=result.fire_number_nominal,
                    retirement_age=result.age_at_fire,
                    lang=lang,
                )

            with st.container(border=True):
                render_tax_breakdown_card(
                    result=result,
                    tax_settings=st.session_state.tax_settings,
                    lang=lang,
                )

        with tab_compare:
            with st.container(border=True):
                render_country_comparison(
                    current_inputs=fire_inputs,
                    on_apply_scheme=handle_apply_scheme,
                    lang=lang,
                )

            with st.container(border=True):
                render_tax_breakdown_card(
                    result=result,
                    tax_settings=st.session_state.tax_settings,
                    lang=lang,
                )

        with tab_table:
            with st.container(border=True):
                render_yearly_table(
                    projections=result.projections,
                    lang=lang,
                )

    # 5. Footer & Legal Disclaimer
    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align: center; color: #64748b; font-size: 0.72rem; padding: 16px 0 32px 0;">
            <p style="margin: 0 0 6px 0; font-weight: 600; color: #94a3b8;">
                🛡️ {t('footerTitle', lang)}
            </p>
            <p style="margin: 0; font-size: 0.68rem; color: #64748b; max-width: 800px; margin: 0 auto;">
                {t('footerDisclaimer', lang)}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
