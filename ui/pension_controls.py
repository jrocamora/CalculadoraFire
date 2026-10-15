"""
Pilar de pensions irlandeses: Private Pension (PRSA / Occupational) i MyFutureFund (Auto-Enrolment).
Permet modelar el creixement lliure d'impostos, l'aportació d'empresa i Estat, i el pont FIRE.
"""
from __future__ import annotations

import streamlit as st
from config.translations import Language, t
from models.types import PensionSettings


def render_pension_controls(
    pension_settings: PensionSettings,
    current_age: int,
    target_retirement_age: int,
    lang: Language,
) -> PensionSettings:
    """Renderitza el configurador avançat de pensions irlandeses."""
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 12px; margin-bottom: 14px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="
                    background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.25);
                    color: #10b981; padding: 8px; border-radius: 12px; font-size: 1.1rem;
                ">🛡️</div>
                <div>
                    <h3 style="margin: 0; font-size: 1.05rem; font-weight: 800; color: #ffffff;">
                        {t('pensionSectionTitle', lang)}
                    </h3>
                    <p style="margin: 2px 0 0 0; font-size: 0.74rem; color: #94a3b8;">
                        {t('pensionSectionSubtitle', lang)}
                    </p>
                </div>
            </div>
            <span style="
                background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3);
                border-radius: 9999px; padding: 3px 8px; font-size: 0.70rem; font-weight: 700;
            ">
                Multi-Pillar Irish FIRE
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_private, tab_mff, tab_bridge = st.tabs(
        ["🛡️ " + t("privatePensionTitle", lang).split("(")[0].strip(),
         "🏛️ MyFutureFund",
         "🌉 " + t("pensionBridgeStrategyTitle", lang).split(":")[0].strip()]
    )

    # 1. Private Pension (PRSA / Workplace Pension)
    with tab_private:
        p_enabled = st.checkbox(
            "Enable Private Pension / PRSA",
            value=bool(pension_settings.private_pension_balance > 0 or pension_settings.private_pension_monthly_contribution > 0),
            key="pension_private_enabled",
        )

        st.caption(t("privatePensionDesc", lang))

        col_bal, col_mo = st.columns(2)
        with col_bal:
            new_p_bal = st.number_input(
                f"{t('privatePensionBalanceLabel', lang)} (€)",
                min_value=0.0,
                max_value=10000000.0,
                value=float(pension_settings.private_pension_balance),
                step=2500.0,
                key="pension_private_bal_input",
                disabled=not p_enabled,
            )
        with col_mo:
            new_p_mo = st.number_input(
                f"{t('privatePensionMonthlyLabel', lang)} (€/mo)",
                min_value=0.0,
                max_value=20000.0,
                value=float(pension_settings.private_pension_monthly_contribution),
                step=50.0,
                key="pension_private_mo_input",
                disabled=not p_enabled,
            )

        col_ret, col_acc = st.columns(2)
        with col_ret:
            new_p_ret = st.number_input(
                "Expected Return (%/yr)",
                min_value=0.0,
                max_value=15.0,
                value=float(pension_settings.private_pension_expected_return),
                step=0.5,
                key="pension_private_ret_input",
                disabled=not p_enabled,
            )
        with col_acc:
            new_p_acc = st.slider(
                f"{t('privatePensionAccessAgeLabel', lang)}",
                min_value=50,
                max_value=65,
                value=int(pension_settings.private_pension_access_age),
                step=1,
                key="pension_private_acc_slider",
                disabled=not p_enabled,
                help="Occupational schemes typically permit access from age 50 upon leaving employment; PRSAs typically from age 60.",
            )

        bridge_gap_p = max(0, new_p_acc - target_retirement_age)
        if bridge_gap_p > 0:
            st.info(
                f"💡 **Bridge Gap: {bridge_gap_p} years.** If you retire early at age {target_retirement_age}, "
                f"your taxable bridge accounts must fund your expenses until this Private Pension unlocks at age {new_p_acc}."
            )
        else:
            st.success(
                f"✓ Private Pension unlocks at or before your target retirement age ({target_retirement_age}). "
                f"Funds will be accessible immediately at FIRE."
            )

    # 2. MyFutureFund (Auto-Enrolment NAERSA)
    with tab_mff:
        mff_enabled = st.checkbox(
            "Enable MyFutureFund (National Auto-Enrolment)",
            value=bool(pension_settings.my_future_fund_balance > 0 or pension_settings.my_future_fund_employee_monthly > 0),
            key="pension_mff_enabled",
        )

        st.caption(t("myFutureFundDesc", lang))

        col_mff_bal, col_mff_emp = st.columns(2)
        with col_mff_bal:
            new_mff_bal = st.number_input(
                f"{t('myFutureFundBalanceLabel', lang)} (€)",
                min_value=0.0,
                max_value=5000000.0,
                value=float(pension_settings.my_future_fund_balance),
                step=1000.0,
                key="pension_mff_bal_input",
                disabled=not mff_enabled,
            )
        with col_mff_emp:
            new_mff_emp = st.number_input(
                f"{t('myFutureFundEmployeeMonthlyLabel', lang)} (€/mo)",
                min_value=0.0,
                max_value=4000.0,
                value=float(pension_settings.my_future_fund_employee_monthly),
                step=25.0,
                key="pension_mff_emp_input",
                disabled=not mff_enabled,
            )

        # Calculate tripartite match
        match_employer = new_mff_emp if mff_enabled else 0.0
        topup_state = (new_mff_emp / 3.0) if mff_enabled else 0.0
        total_mff_inflow = (new_mff_emp + match_employer + topup_state) if mff_enabled else 0.0

        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(6, 182, 212, 0.08) 100%);
                border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px;
                padding: 12px 14px; margin: 10px 0;
            ">
                <div style="font-size: 0.74rem; font-weight: 800; color: #34d399; margin-bottom: 6px;">
                    {t('myFutureFundTotalMonthlyLabel', lang)} <strong>{total_mff_inflow:,.0f} € / month</strong>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; font-size: 0.70rem; color: #cbd5e1;">
                    <div>• You save: <strong>{new_mff_emp:,.0f} €</strong></div>
                    <div>• Employer match: <strong style="color: #38bdf8;">+{match_employer:,.0f} €</strong></div>
                    <div>• State top-up: <strong style="color: #a78bfa;">+{topup_state:,.0f} €</strong></div>
                </div>
                <div style="font-size: 0.68rem; color: #94a3b8; margin-top: 6px;">
                    🎯 For every €1.00 you contribute, €2.33 is deposited into your MyFutureFund pot.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_mff_ret, col_mff_age = st.columns(2)
        with col_mff_ret:
            new_mff_ret = st.number_input(
                "Lifecycle Expected Return (%/yr)",
                min_value=0.0,
                max_value=15.0,
                value=float(pension_settings.my_future_fund_expected_return),
                step=0.5,
                key="pension_mff_ret_input",
                disabled=not mff_enabled,
            )
        with col_mff_age:
            st.markdown(
                f"""
                <div style="padding-top: 4px;">
                    <div style="font-size: 0.78rem; font-weight: 600; color: #94a3b8;">
                        {t('myFutureFundAccessAgeLabel', lang)}
                    </div>
                    <div style="font-size: 1.15rem; font-weight: 800; color: #ffffff; margin-top: 4px;">
                        Age 66 (State Pension)
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # 3. Bridge Strategy Overview
    with tab_bridge:
        st.markdown(
            f"""
            <div style="font-size: 0.76rem; color: #e2e8f0; line-height: 1.6; margin-bottom: 12px;">
                {t('pensionBridgeStrategyDesc', lang)}
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(
                "1. Taxable Bridge",
                f"Age {current_age} → {target_retirement_age}",
                "Funded by Budget 2027 & ETFs",
            )
        with c2:
            st.metric(
                "2. Private Pension",
                f"Age {new_p_acc} Unlocks",
                "25% Lump Sum + ARF Drawdown",
            )
        with c3:
            st.metric(
                "3. MyFutureFund",
                "Age 66 Unlocks",
                "25% Lump Sum + State Pension",
            )

    return PensionSettings(
        private_pension_enabled=p_enabled,
        private_pension_balance=new_p_bal if p_enabled else 0.0,
        private_pension_monthly_contribution=new_p_mo if p_enabled else 0.0,
        private_pension_expected_return=new_p_ret if p_enabled else 7.0,
        private_pension_access_age=new_p_acc if p_enabled else 50,
        private_pension_tax_free_lump_sum_pct=25.0,
        my_future_fund_enabled=mff_enabled,
        my_future_fund_balance=new_mff_bal if mff_enabled else 0.0,
        my_future_fund_employee_monthly=new_mff_emp if mff_enabled else 0.0,
        my_future_fund_employer_match_monthly=match_employer if mff_enabled else 0.0,
        my_future_fund_state_topup_monthly=topup_state if mff_enabled else 0.0,
        my_future_fund_expected_return=new_mff_ret if mff_enabled else 7.0,
        my_future_fund_access_age=66,
        my_future_fund_tax_free_lump_sum_pct=25.0,
    )
