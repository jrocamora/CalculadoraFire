"""
Pilar de pensions irlandeses: Private Pension (PRSA / Occupational) i MyFutureFund (Auto-Enrolment).
Permet modelar el creixement lliure d'impostos, l'aportació d'empresa i Estat, i el pont FIRE.
"""
from __future__ import annotations

import streamlit as st
from ui.keys import k
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
        <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #e2e8f0; padding-bottom: 12px; margin-bottom: 14px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="
                    background: #f0fdf4; border: 1px solid #bbf7d0;
                    color: #059669; padding: 8px; border-radius: 12px; font-size: 1.1rem;
                ">🛡️</div>
                <div>
                    <h3 style="margin: 0; font-size: 1.05rem; font-weight: 800; color: #0f172a;">
                        {t('pensionSectionTitle', lang)}
                    </h3>
                    <p style="margin: 2px 0 0 0; font-size: 0.74rem; color: #64748b;">
                        {t('pensionSectionSubtitle', lang)}
                    </p>
                </div>
            </div>
            <span style="
                background: #ecfdf5; color: #059669; border: 1px solid #a7f3d0;
                border-radius: 9999px; padding: 3px 8px; font-size: 0.70rem; font-weight: 700;
            ">
                Multi-Pillar Irish FIRE
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_state, tab_private, tab_mff, tab_bridge = st.tabs(
        [
            "🏛️ " + t("statePensionTitle", lang).split("(")[0].strip(),
            "🛡️ " + t("privatePensionTitle", lang).split("(")[0].strip(),
            "🏢 MyFutureFund",
            "🌉 " + t("pensionBridgeStrategyTitle", lang).split(":")[0].strip(),
        ]
    )

    # 1. State Pension (Pillar 1 - Contributory)
    with tab_state:
        sp_enabled = st.checkbox(
            t("statePensionEnableCheckbox", lang),
            value=bool(getattr(pension_settings, "state_pension_enabled", False)),
            key=k("pension_state_enabled"),
        )

        st.caption(t("statePensionDesc", lang))

        # Preset buttons row (callbacks run before the number input below is created)
        sp_key = k("pension_state_mo_input")

        def _set_sp(amount: float):
            st.session_state[sp_key] = amount

        if sp_key not in st.session_state:
            st.session_state[sp_key] = float(getattr(pension_settings, "state_pension_monthly_amount", 1340.0))

        col_pr1, col_pr2, col_pr3, col_pr4 = st.columns(4)
        for col, label, amount, key in (
            (col_pr1, t("statePensionFullRate", lang), 1340.0, "preset_sp_full"),
            (col_pr2, t("statePension75Rate", lang), 1005.0, "preset_sp_75"),
            (col_pr3, t("statePension50Rate", lang), 670.0, "preset_sp_50"),
            (col_pr4, t("statePensionCoupleRate", lang), 2680.0, "preset_sp_couple"),
        ):
            with col:
                st.button(
                    label,
                    key=k(key),
                    disabled=not sp_enabled,
                    width="stretch",
                    on_click=_set_sp,
                    args=(amount,),
                )

        col_sp_val, col_sp_age = st.columns(2)
        with col_sp_val:
            new_sp_mo = st.number_input(
                f"{t('statePensionMonthlyLabel', lang)} (€/mo)",
                min_value=0.0,
                max_value=15000.0,
                step=50.0,
                key=k("pension_state_mo_input"),
                disabled=not sp_enabled,
                help="Full contributory rate is €309.30/week from January 2027 (~€1,340/month). Adjust it to your expected entitlement, an international pro-rata amount, or a couple total.",
            )
            annual_sp = new_sp_mo * 12.0
            st.caption(
                f"= €{annual_sp:,.0f} / year" if lang == "en" else f"= {annual_sp:,.0f} € / any".replace(",", ".")
            )

        with col_sp_age:
            new_sp_age = st.slider(
                t("statePensionAccessAgeLabel", lang),
                min_value=65,
                max_value=70,
                value=int(getattr(pension_settings, "state_pension_access_age", 66)),
                step=1,
                key=k("pension_state_age_slider"),
                disabled=not sp_enabled,
                help="Standard statutory retirement age in Ireland is 66. You can choose to defer up to age 70 for enhanced weekly rates under Irish pension reform.",
            )

        if sp_enabled:
            st.markdown(
                f"""
                <div style="
                    background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px;
                    padding: 10px 14px; margin-top: 8px; font-size: 0.73rem; color: #334155; line-height: 1.5;
                ">
                    🏛️ <strong>{"Guaranteed Income Floor" if lang == "en" else "Marge d'Ingressos Garantit"}:</strong> 
                    {"From age" if lang == "en" else "A partir dels"} <strong>{new_sp_age}</strong> {"years, the State pays you" if lang == "en" else "anys, l'Estat et pagarà"} <strong>€{new_sp_mo:,.0f}/mo</strong> (<strong>€{new_sp_mo * 12:,.0f}/year</strong>).
                    {"This directly lowers your required portfolio withdrawal by that amount!" if lang == "en" else "Això redueix directament la retirada que has de fer de la teva cartera privada en aquest mateix import!"}
                </div>
                """,
                unsafe_allow_html=True,
            )

    # 2. Private Pension (PRSA / Workplace Pension)
    with tab_private:
        p_enabled = st.checkbox(
            "Enable Private Pension / PRSA",
            value=bool(getattr(pension_settings, "private_pension_enabled", False)),
            key=k("pension_private_enabled"),
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
                key=k("pension_private_bal_input"),
                disabled=not p_enabled,
            )
        with col_mo:
            new_p_mo = st.number_input(
                f"{t('privatePensionMonthlyLabel', lang)} (€/mo)",
                min_value=0.0,
                max_value=20000.0,
                value=float(pension_settings.private_pension_monthly_contribution),
                step=50.0,
                key=k("pension_private_mo_input"),
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
                key=k("pension_private_ret_input"),
                disabled=not p_enabled,
            )
        with col_acc:
            new_p_acc = st.slider(
                f"{t('privatePensionAccessAgeLabel', lang)}",
                min_value=50,
                max_value=65,
                value=int(pension_settings.private_pension_access_age),
                step=1,
                key=k("pension_private_acc_slider"),
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

    # 3. MyFutureFund (Auto-Enrolment NAERSA)
    with tab_mff:
        mff_enabled = st.checkbox(
            "Enable MyFutureFund (National Auto-Enrolment)",
            value=bool(getattr(pension_settings, "my_future_fund_enabled", False)),
            key=k("pension_mff_enabled"),
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
                key=k("pension_mff_bal_input"),
                disabled=not mff_enabled,
            )
        with col_mff_emp:
            new_mff_emp = st.number_input(
                f"{t('myFutureFundEmployeeMonthlyLabel', lang)} (€/mo)",
                min_value=0.0,
                max_value=4000.0,
                value=float(pension_settings.my_future_fund_employee_monthly),
                step=25.0,
                key=k("pension_mff_emp_input"),
                disabled=not mff_enabled,
            )

        # Calculate tripartite match
        match_employer = new_mff_emp if mff_enabled else 0.0
        topup_state = (new_mff_emp / 3.0) if mff_enabled else 0.0
        total_mff_inflow = (new_mff_emp + match_employer + topup_state) if mff_enabled else 0.0

        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #f0fdf4 0%, #ecfeff 100%);
                border: 1px solid #a7f3d0; border-radius: 12px;
                padding: 12px 14px; margin: 10px 0;
            ">
                <div style="font-size: 0.74rem; font-weight: 800; color: #047857; margin-bottom: 6px;">
                    {t('myFutureFundTotalMonthlyLabel', lang)} <strong>{total_mff_inflow:,.0f} € / month</strong>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; font-size: 0.70rem; color: #334155;">
                    <div>• You save: <strong>{new_mff_emp:,.0f} €</strong></div>
                    <div>• Employer match: <strong style="color: #0284c7;">+{match_employer:,.0f} €</strong></div>
                    <div>• State top-up: <strong style="color: #7c3aed;">+{topup_state:,.0f} €</strong></div>
                </div>
                <div style="font-size: 0.68rem; color: #64748b; margin-top: 6px;">
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
                key=k("pension_mff_ret_input"),
                disabled=not mff_enabled,
            )
        with col_mff_age:
            st.markdown(
                f"""
                <div style="padding-top: 4px;">
                    <div style="font-size: 0.78rem; font-weight: 600; color: #64748b;">
                        {t('myFutureFundAccessAgeLabel', lang)}
                    </div>
                    <div style="font-size: 1.15rem; font-weight: 800; color: #0f172a; margin-top: 4px;">
                        Age 66 (State Pension)
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Income tax on pension drawdowns (ARF / MyFutureFund). The 25% lump sums stay tax-free.
    new_pension_tax = st.number_input(
        "Income tax on pension drawdowns (%)",
        min_value=0.0,
        max_value=55.0,
        value=float(getattr(pension_settings, "pension_income_tax_rate", 20.0)),
        step=1.0,
        key=k("pension_income_tax_input"),
        disabled=not (p_enabled or mff_enabled),
        help="Effective rate (income tax + USC) applied to ARF and MyFutureFund withdrawals, which are taxed as "
        "income in Ireland. The State Pension is not taxed in this model. Adjust to your own situation.",
    )

    # 4. Bridge Strategy Overview
    with tab_bridge:
        st.markdown(
            f"""
            <div style="font-size: 0.76rem; color: #334155; line-height: 1.6; margin-bottom: 12px;">
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
                "Budget 2027 & ETFs",
            )
        with c2:
            st.metric(
                "2. Private Pension",
                f"Age {new_p_acc} Unlocks",
                "25% Lump Sum + ARF Drawdown",
            )
        with c3:
            st.metric(
                "3. State & MFF",
                f"Age {new_sp_age} Unlocks",
                f"€{new_sp_mo:,.0f}/mo State + MFF" if sp_enabled else "MyFutureFund",
            )

    # Values are kept even while a pillar is switched off (the *_enabled flags decide whether the
    # simulation uses them), so re-enabling a pillar or reloading the form does not show zeros.
    return PensionSettings(
        private_pension_enabled=p_enabled,
        private_pension_balance=new_p_bal,
        private_pension_monthly_contribution=new_p_mo,
        private_pension_expected_return=new_p_ret,
        private_pension_access_age=new_p_acc,
        private_pension_tax_free_lump_sum_pct=25.0,
        my_future_fund_enabled=mff_enabled,
        my_future_fund_balance=new_mff_bal,
        my_future_fund_employee_monthly=new_mff_emp,
        my_future_fund_employer_match_monthly=match_employer if mff_enabled else 0.0,
        my_future_fund_state_topup_monthly=topup_state if mff_enabled else 0.0,
        my_future_fund_expected_return=new_mff_ret,
        my_future_fund_access_age=66,
        my_future_fund_tax_free_lump_sum_pct=25.0,
        state_pension_enabled=sp_enabled,
        state_pension_monthly_amount=new_sp_mo,
        state_pension_access_age=new_sp_age,
        pension_income_tax_rate=new_pension_tax,
    )
