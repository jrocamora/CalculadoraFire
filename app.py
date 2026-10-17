"""
🔥 FIRE Calculator Ireland Pro — Streamlit Application.
Calibrated for the Irish tax framework including Budget 2027 reforms.
100% Client-Side Simulation: All calculations run locally in your browser.
"""
from __future__ import annotations

import json
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
from models.types import FireInputs
from ui import (
    render_bidirectional_inputs,
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
from utils.serialization import (
    decode_token_to_plan,
    dict_to_session_state,
    encode_plan_to_token,
    plan_to_dict,
)

# Page configuration
st.set_page_config(
    page_title="FIRE Calculator Ireland (Budget 2027)",
    page_icon="🇮🇪",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def init_session_state():
    """Initializes the session state defaults for the Irish edition or loads from shared URL."""
    # Check if a plan is encoded in the URL query parameters (?plan=...)
    if "plan_loaded" not in st.session_state:
        st.session_state.plan_loaded = True
        plan_param = st.query_params.get("plan")
        if plan_param:
            decoded = decode_token_to_plan(plan_param)
            if decoded:
                dict_to_session_state(decoded, st.session_state)
                st.session_state.just_loaded_from_url = True

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
    st.query_params.clear()
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


def main():
    init_session_state()
    lang: Language = "en"  # Fixed to English as requested
    current_year = get_current_year()

    # 1. Header with Ireland branding, light theme, and client-side privacy note
    render_header(
        current_country=st.session_state.tax_settings.country,
        lang=lang,
        on_reset_defaults=handle_reset_defaults,
    )

    if st.session_state.get("just_loaded_from_url"):
        st.success(t("planLoadedSuccess", lang))
        st.session_state.just_loaded_from_url = False

    # 2. Share, Save & Privacy Bar (Collapsible with clear privacy guarantee)
    with st.expander("🔗 Share Plan & Local Save (100% Private • No Server Data)", expanded=False):
        st.markdown(
            f"""
            <div style="
                background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px;
                padding: 14px; margin-bottom: 14px;
            ">
                <div style="font-size: 0.82rem; font-weight: 800; color: #166534; margin-bottom: 4px;">
                    🛡️ {t('privacyGuaranteeTitle', lang)}
                </div>
                <div style="font-size: 0.74rem; color: #15803d; line-height: 1.5;">
                    {t('privacyGuaranteeText', lang)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_share, col_save, col_load = st.columns([2.5, 1.2, 1.3], gap="medium")

        # Serialized plan dict for URL and JSON export
        current_plan = plan_to_dict(
            mode=st.session_state.mode,
            target_monthly_income=st.session_state.target_monthly_income,
            current_age=st.session_state.current_age,
            target_retirement_age=st.session_state.target_retirement_age,
            life_expectancy=st.session_state.life_expectancy,
            monthly_savings=st.session_state.monthly_savings,
            annual_savings_increase_rate=st.session_state.annual_savings_increase_rate,
            safe_withdrawal_rate=st.session_state.safe_withdrawal_rate,
            assets=st.session_state.assets,
            pension_settings=st.session_state.pension_settings,
            tax_settings=st.session_state.tax_settings,
            scenario=st.session_state.scenario,
        )
        plan_token = encode_plan_to_token(current_plan)

        with col_share:
            st.markdown(f"**🔗 {t('sharePlan', lang)}**")
            st.caption("Generate a shareable URL containing your numbers encoded in parameters:")
            if st.button("Generate Shareable Link", key="btn_generate_share", use_container_width=True):
                st.query_params["plan"] = plan_token

            st.text_input(
                t("shareUrlLabel", lang),
                value=f"?plan={plan_token}",
                key="share_url_field",
                help="Copy this link. Anyone opening it will see your exact numbers without any server storage.",
            )

        with col_save:
            st.markdown(f"**💾 {t('exportJson', lang)}**")
            st.caption("Download your inputs as a local file:")
            json_data = json.dumps(current_plan, indent=2)
            st.download_button(
                label="⬇ Download JSON",
                data=json_data,
                file_name="ireland_fire_plan.json",
                mime="application/json",
                use_container_width=True,
                key="download_plan_json_btn",
            )

        with col_load:
            st.markdown(f"**📂 {t('importJson', lang)}**")
            st.caption("Restore numbers from a saved file:")
            uploaded_file = st.file_uploader(
                "Upload JSON file",
                type=["json"],
                key="upload_plan_json",
                label_visibility="collapsed",
            )
            if uploaded_file is not None:
                try:
                    uploaded_content = json.loads(uploaded_file.getvalue().decode("utf-8"))
                    if dict_to_session_state(uploaded_content, st.session_state):
                        st.toast("Plan loaded successfully!", icon="✅")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error reading plan file: {e}")

    # 3. Simulation execution
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

    # 4. 4 Full-Width Key Metric Cards (Ireland specific)
    render_metric_cards(
        result=result,
        safe_withdrawal_rate=st.session_state.safe_withdrawal_rate,
        country="IE",
        lang=lang,
    )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 5. Main 2-Column Layout (Configurator vs Visualization/Breakdown)
    col_inputs, col_viz = st.columns([5, 7], gap="medium")

    # Left Column: Inputs & Controls
    with col_inputs:
        # Calculation Strategy & Target
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

    # Right Column: Analysis Tabs (Chart & Breakdown vs Year-by-Year Table)
    # Comparison screen tab has been removed in favor of direct portfolio option
    with col_viz:
        tab_chart, tab_table = st.tabs(
            [t("tabChart", lang), t("tabTable", lang)]
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

        with tab_table:
            with st.container(border=True):
                render_yearly_table(
                    projections=result.projections,
                    lang=lang,
                )

    # 6. Footer & Client-Side Privacy Disclaimer
    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align: center; color: #64748b; font-size: 0.72rem; padding: 16px 0 32px 0;">
            <p style="margin: 0 0 6px 0; font-weight: 700; color: #475569;">
                🛡️ {t('footerTitle', lang)}
            </p>
            <p style="margin: 0 0 6px 0; font-size: 0.68rem; color: #64748b; max-width: 800px; margin: 0 auto;">
                {t('footerDisclaimer', lang)}
            </p>
            <p style="margin: 4px 0 0 0; font-size: 0.68rem; color: #059669; font-weight: 600;">
                🔒 100% Client-Side Simulation • Zero Data Sent to Servers • Calibrated for Irish Revenue & Budget 2027
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
