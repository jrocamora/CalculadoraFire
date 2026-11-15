"""
🔥 FIRE Calculator Ireland Pro — Streamlit Application.
Calibrated for the Irish tax framework including Budget 2027 reforms.
The simulation runs on the Streamlit server for the duration of the session; nothing is persisted.
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
from ui.keys import k, reset_widgets
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


def apply_defaults():
    """Writes the default Irish baseline into the model held in session state."""
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


def init_session_state():
    """Initializes the model on first run, or loads it from a shared URL / an uploaded plan."""
    if "lang" not in st.session_state:
        st.session_state.lang = "en"
    if "ui_nonce" not in st.session_state:
        st.session_state.ui_nonce = 0
    if "mode" not in st.session_state:
        apply_defaults()

    # A plan encoded in the URL (?plan=...) is applied once, when the session starts
    if "plan_loaded" not in st.session_state:
        st.session_state.plan_loaded = True
        plan_param = st.query_params.get("plan")
        if plan_param:
            decoded = decode_token_to_plan(plan_param)
            if decoded and dict_to_session_state(decoded, st.session_state):
                st.session_state.plan_notice = ("success", t("planLoadedSuccess", "en"))
            else:
                st.session_state.plan_notice = ("error", "This share link is not valid, so the default plan is shown.")

    # A plan uploaded as JSON in the previous run is applied here, before any widget is created.
    # Bumping the widget generation also empties the file uploader, so it is applied exactly once.
    pending = st.session_state.pop("pending_plan", None)
    if pending is not None:
        if dict_to_session_state(pending, st.session_state):
            st.session_state.plan_notice = ("success", "✓ Plan loaded from file.")
        else:
            st.session_state.plan_notice = ("error", "That file is not a valid plan.")
        reset_widgets()


def handle_reset_defaults():
    """Button callback: resets every simulation parameter to the default Irish baseline."""
    st.query_params.clear()
    apply_defaults()
    reset_widgets()


def render_share_panel(lang: Language):
    """Share link, JSON export and JSON import. Rendered after the inputs so it reflects the current values."""
    with st.expander("🔗 Share & Save Plan", expanded=False):
        st.markdown(
            f"""
            <div style="
                background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px;
                padding: 10px 14px; margin-bottom: 14px;
            ">
                <div style="font-size: 0.74rem; color: #475569; line-height: 1.5;">
                    ℹ️ {t('privacyGuaranteeText', lang)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_share, col_save, col_load = st.columns([2.5, 1.2, 1.3], gap="medium")

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
            st.caption("Put your current numbers into this page's address so you can copy and share it:")
            if st.button("Generate Shareable Link", key=k("btn_generate_share"), width="stretch"):
                st.query_params["plan"] = plan_token
                st.caption("✓ The address bar now holds your plan. Copy the page URL to share it.")

            st.code(f"?plan={plan_token}", language=None)
            st.caption("Or append this to the app's address. Anyone with the link can read the numbers in it.")

        with col_save:
            st.markdown(f"**💾 {t('exportJson', lang)}**")
            st.caption("Download your inputs as a local file:")
            st.download_button(
                label="⬇ Download JSON",
                data=json.dumps(current_plan, indent=2),
                file_name="ireland_fire_plan.json",
                mime="application/json",
                width="stretch",
                key=k("download_plan_json_btn"),
            )

        with col_load:
            st.markdown(f"**📂 {t('importJson', lang)}**")
            st.caption("Restore numbers from a saved file:")
            uploaded_file = st.file_uploader(
                "Upload JSON file",
                type=["json"],
                key=k("upload_plan_json"),
                label_visibility="collapsed",
            )
            if uploaded_file is not None:
                try:
                    uploaded_content = json.loads(uploaded_file.getvalue().decode("utf-8"))
                except Exception:
                    st.error("That file is not valid JSON.")
                else:
                    # Applied at the top of the next run (see init_session_state)
                    st.session_state.pending_plan = uploaded_content
                    st.rerun()


def main():
    init_session_state()
    lang: Language = "en"  # Fixed to English as requested
    current_year = get_current_year()

    # 1. Header with Ireland branding and light theme
    render_header(
        current_country=st.session_state.tax_settings.country,
        lang=lang,
        on_reset_defaults=handle_reset_defaults,
    )

    notice = st.session_state.pop("plan_notice", None)
    if notice:
        (st.success if notice[0] == "success" else st.error)(notice[1])

    # 2. Page skeleton. The share panel and the metric cards sit above the inputs on the page, but
    #    they are filled in at the end, once the inputs have been read, so they never lag behind.
    share_slot = st.container()
    cards_slot = st.container()
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    col_inputs, col_viz = st.columns([5, 7], gap="medium")

    # 3. Left column: inputs & controls. Each one updates the model in session state.
    with col_inputs:
        # Calculation Strategy & Target
        with st.container(border=True):
            (
                st.session_state.mode,
                st.session_state.target_monthly_income,
                st.session_state.assets,
                st.session_state.monthly_savings,
                st.session_state.annual_savings_increase_rate,
                st.session_state.current_age,
                st.session_state.target_retirement_age,
                st.session_state.life_expectancy,
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

        # Safe Withdrawal Rate (SWR)
        with st.container(border=True):
            st.session_state.safe_withdrawal_rate = render_swr_control(
                current_swr=st.session_state.safe_withdrawal_rate,
                lang=lang,
            )

        # Irish Pensions: State Pension, Private Pension (PRSA) & MyFutureFund Auto-Enrolment
        with st.container(border=True):
            st.session_state.pension_settings = render_pension_controls(
                pension_settings=st.session_state.pension_settings,
                current_age=st.session_state.current_age,
                target_retirement_age=st.session_state.target_retirement_age,
                lang=lang,
            )

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

    # 4. Simulation, run with the values the inputs returned in this same run
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

    # 5. Fill the slots above the inputs
    with share_slot:
        render_share_panel(lang)

    with cards_slot:
        render_metric_cards(
            result=result,
            safe_withdrawal_rate=st.session_state.safe_withdrawal_rate,
            country="IE",
            lang=lang,
        )

    # 6. Right column: chart & breakdown, year-by-year table
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
                    pension_settings=st.session_state.pension_settings,
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

    # 7. Footer & disclaimer
    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align: center; color: #64748b; font-size: 0.72rem; padding: 16px 0 32px 0;">
            <p style="margin: 0 0 6px 0; font-weight: 700; color: #475569;">
                {t('footerTitle', lang)}
            </p>
            <p style="margin: 0 0 6px 0; font-size: 0.68rem; color: #64748b; max-width: 800px; margin: 0 auto;">
                {t('footerDisclaimer', lang)}
            </p>
            <p style="margin: 4px 0 0 0; font-size: 0.68rem; color: #64748b;">
                No account needed • Inputs are not saved by this app • Budget 2027 figures, subject to legislation
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
