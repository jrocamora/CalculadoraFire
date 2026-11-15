"""
Inputs bidireccionals i gestor d'actius de la cartera.
Port fidel de BiDirectionalInputs.tsx.
"""
from __future__ import annotations

import streamlit as st
from ui.keys import k
from config.translations import Language, t
from models.types import CalculationMode, PortfolioAsset


def render_bidirectional_inputs(
    mode: CalculationMode,
    target_monthly_income: float,
    assets: list[PortfolioAsset],
    monthly_savings: float,
    annual_savings_increase_rate: float,
    current_age: int,
    target_retirement_age: int,
    life_expectancy: int,
    lang: Language,
) -> tuple[
    CalculationMode,
    float,
    list[PortfolioAsset],
    float,
    float,
    int,
    int,
    int,
]:
    """Renderitza el panell interactiu d'entrada de dades amb suport bidireccional."""
    total_assets = sum(a.current_amount for a in assets)

    st.markdown(
        f"""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;">
            <div>
                <h3 style="margin: 0; font-size: 1.1rem; font-weight: 800; color: #0f172a;">
                    {t('inputModeTitle', lang)}
                </h3>
                <p style="margin: 2px 0 0 0; font-size: 0.75rem; color: #64748b;">
                    {t('inputModeSubtitle', lang)}
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Selector de mode (Pills / Radio estilitzat)
    mode_options = ["target_spending", "current_portfolio"]
    mode_labels = {
        "target_spending": t("modeTargetSpending", lang),
        "current_portfolio": t("modeCurrentPortfolio", lang),
    }

    selected_mode = st.radio(
        "Calculation Mode" if lang == "en" else "Mode de càlcul",
        options=mode_options,
        format_func=lambda x: mode_labels[x],
        index=0 if mode == "target_spending" else 1,
        horizontal=True,
        label_visibility="collapsed",
        key=k("calc_mode_radio"),
    )

    new_target_income = target_monthly_income

    if selected_mode == "target_spending":
        st.markdown(
            f"""
            <div style="
                background: #fffbeb;
                border: 1px solid #fde68a;
                border-radius: 14px;
                padding: 16px;
                margin: 12px 0;
            ">
                <div style="font-size: 0.82rem; font-weight: 700; color: #b45309; margin-bottom: 4px;">
                    {t('targetDisposableQuestion', lang)}
                </div>
                <div style="font-size: 0.74rem; color: #78350f; margin-bottom: 12px;">
                    {t('targetDisposableHelp', lang)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # The exact-value box is the source of truth (it has the wider range); the slider and
        # the preset buttons write into it through callbacks so the three always agree.
        input_key = k("target_monthly_income_input")
        slider_key = k("target_monthly_income_slider")
        slider_min, slider_max = 800.0, 12000.0

        def _clamp_to_slider(val: float) -> float:
            return min(slider_max, max(slider_min, float(val)))

        def _set_target(val: float):
            st.session_state[input_key] = float(val)
            st.session_state[slider_key] = _clamp_to_slider(val)

        def _on_input_change():
            st.session_state[slider_key] = _clamp_to_slider(st.session_state[input_key])

        def _on_slider_change():
            st.session_state[input_key] = float(st.session_state[slider_key])

        # These two widgets are written to from callbacks, so they are seeded through session
        # state (not `value=`): mixing both makes Streamlit log a warning.
        if input_key not in st.session_state:
            st.session_state[input_key] = min(30000.0, max(500.0, float(target_monthly_income)))
        if slider_key not in st.session_state:
            st.session_state[slider_key] = _clamp_to_slider(st.session_state[input_key])

        col_preset1, col_preset2, col_val = st.columns([1, 1, 2])
        label_2500 = "€2,500 " if lang == "en" else "2.500 € "
        label_5000 = "€5,000 " if lang == "en" else "5.000 € "
        with col_preset1:
            st.button(
                label_2500 + t("commonTarget", lang).split("(")[-1].replace(")", ""),
                key=k("preset_2500"),
                width="stretch",
                on_click=_set_target,
                args=(2500.0,),
            )
        with col_preset2:
            st.button(
                label_5000 + t("fatFire", lang).split("(")[-1].replace(")", ""),
                key=k("preset_5000"),
                width="stretch",
                on_click=_set_target,
                args=(5000.0,),
            )
        with col_val:
            new_target_income = st.number_input(
                t("enterExactValue", lang),
                min_value=500.0,
                max_value=30000.0,
                step=100.0,
                key=input_key,
                on_change=_on_input_change,
            )

        mo_suffix = "(€/mo)" if lang == "en" else "(€/mes)"
        st.slider(
            f"{t('disposableIncomeTitle', lang)} {mo_suffix}",
            min_value=slider_min,
            max_value=slider_max,
            step=50.0,
            key=slider_key,
            on_change=_on_slider_change,
        )

    # Secció d'actius de la cartera (Portfolio Assets)
    with st.expander(
        f"💼 {t('portfolioTotal', lang)} {total_assets:,.0f} € — {len(assets)} {t('assetsCount', lang)}",
        expanded=True,
    ):
        st.caption(t("portfolioAssetSubtitle", lang))

        category_icons = {
            "budget_2027_account": "🌟 " + t("categoryBudget2027Account", lang),
            "index_funds": "📈 " + t("categoryIndexFunds", lang),
            "individual_stocks": "🏢 " + t("categoryIndividualStocks", lang),
            "cash_deposits": "💶 " + t("categoryCashDeposits", lang),
            "private_pension": "🛡️ " + t("categoryPrivatePension", lang),
            "my_future_fund": "🏛️ " + t("categoryMyFutureFund", lang),
            "real_estate_other": "🏡 " + t("categoryRealEstateOther", lang),
        }

        st.markdown(
            """
            <style>
            /* Hide +/- stepper buttons on Cost Basis number inputs */
            div[data-testid="stNumberInput"]:has(input[aria-label*="Cost"]) button,
            div[data-testid="stNumberInput"]:has(input[aria-label*="adquisició"]) button,
            div[data-testid="stNumberInput"]:has(input[aria-label*="Cost"]) div[data-testid="stNumberInputStepDown"],
            div[data-testid="stNumberInput"]:has(input[aria-label*="Cost"]) div[data-testid="stNumberInputStepUp"],
            div[data-testid="stNumberInput"]:has(input[aria-label*="adquisició"]) div[data-testid="stNumberInputStepDown"],
            div[data-testid="stNumberInput"]:has(input[aria-label*="adquisició"]) div[data-testid="stNumberInputStepUp"] {
                display: none !important;
            }

            div[data-testid="stNumberInput"]:has(input[aria-label*="Cost"]) input,
            div[data-testid="stNumberInput"]:has(input[aria-label*="adquisició"]) input {
                padding-right: 12px !important;
            }

            div[data-testid="stNumberInput"]:has(input[aria-label*="Cost"]) input::-webkit-outer-spin-button,
            div[data-testid="stNumberInput"]:has(input[aria-label*="Cost"]) input::-webkit-inner-spin-button,
            div[data-testid="stNumberInput"]:has(input[aria-label*="adquisició"]) input::-webkit-outer-spin-button,
            div[data-testid="stNumberInput"]:has(input[aria-label*="adquisició"]) input::-webkit-inner-spin-button {
                -webkit-appearance: none !important;
                margin: 0 !important;
            }

            div[data-testid="stNumberInput"]:has(input[aria-label*="Cost"]) input[type=number],
            div[data-testid="stNumberInput"]:has(input[aria-label*="adquisició"]) input[type=number] {
                -moz-appearance: textfield !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        def _sync_cost_basis(asset_id: str):
            """Resets cost basis to match current capital when capital is adjusted."""
            new_val = st.session_state.get(k(f"asset_amount_{asset_id}"))
            if new_val is not None:
                st.session_state[k(f"asset_cost_{asset_id}")] = float(new_val)

        updated_assets: list[PortfolioAsset] = []
        for i, a in enumerate(assets):
            st.markdown(f"**{category_icons.get(a.category, a.name)}**")
            c_amt, c_ret, c_cost = st.columns([2, 1.2, 1.2])
            with c_amt:
                amt = st.number_input(
                    f"{t('currentCapital', lang)}",
                    min_value=0.0,
                    max_value=20000000.0,
                    value=float(a.current_amount),
                    step=1000.0,
                    key=k(f"asset_amount_{a.id}"),
                    on_change=_sync_cost_basis,
                    args=(a.id,),
                )
            with c_ret:
                ret = st.number_input(
                    f"{t('expectedReturn', lang)} (%)",
                    min_value=-5.0,
                    max_value=25.0,
                    value=float(a.expected_return_annual),
                    step=0.5,
                    key=k(f"asset_ret_{a.id}"),
                )
            with c_cost:
                if a.category == "cash_deposits":
                    cost = amt  # Cash balance has zero capital gain; interest subject to DIRT
                    st.caption("Tax Status" if lang == "en" else "Estat fiscal")
                    st.markdown(
                        """
                        <div style="
                            background: #f8fafc;
                            border: 1px solid #e2e8f0;
                            border-radius: 8px;
                            padding: 7px 8px;
                            font-size: 0.72rem;
                            font-weight: 700;
                            color: #475569;
                            text-align: center;
                            line-height: 1.3;
                            margin-top: 2px;
                        " title="Cash deposits and savings are exempt from Capital Gains Tax. Only interest earned is subject to DIRT (33%), so cost basis is not applicable.">
                            💶 0% CGT (DIRT)
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    cost_help = (
                        "Original purchase cost / money deposited into this asset. "
                        "Used by Revenue to compute taxable capital gains (Profit = Market Value - Cost Basis) "
                        "vs. tax-free return of your original principal."
                        if lang == "en"
                        else "Preu d'adquisició o diners dipositats originalment en aquest actiu. "
                        "La hisenda tributària el fa servir per calcular les plusvàlues subjectes a impost "
                        "(Guany = Valor de mercat - Cost d'adquisició) enfront del retorn exempt del teu propi capital."
                    )
                    cost = st.number_input(
                        "Cost basis (€)",
                        min_value=0.0,
                        max_value=20000000.0,
                        value=float(a.cost_basis),
                        step=1000.0,
                        key=k(f"asset_cost_{a.id}"),
                        help=cost_help,
                    )
            updated_assets.append(
                PortfolioAsset(
                    id=a.id,
                    category=a.category,
                    name=a.name,
                    current_amount=amt,
                    expected_return_annual=ret,
                    cost_basis=cost,
                )
            )

    # Estalvi mensual i paràmetres temporals
    st.markdown("---")
    st.markdown(f"**⏳ {t('horizonLabel', lang)} & {t('monthlySavingsLabel', lang)}**")

    col_sav, col_inc = st.columns(2)
    with col_sav:
        mo_suffix = "(€/mo)" if lang == "en" else "(€/mes)"
        new_monthly_savings = st.number_input(
            f"{t('monthlySavingsLabel', lang)} {mo_suffix}",
            min_value=0.0,
            max_value=50000.0,
            value=float(monthly_savings),
            step=50.0,
            key=k("monthly_savings_input"),
        )
        annual_sav_val = new_monthly_savings * 12
        annual_sav_fmt = f"€{annual_sav_val:,.0f}" if lang == "en" else f"{annual_sav_val:,.0f} €".replace(",", ".")
        st.caption(f"= {annual_sav_fmt} {t('monthlySavingsHelp', lang)}")

    with col_inc:
        new_savings_inc = st.number_input(
            f"{t('annualSavingsIncreaseRateLabel', lang)} (%)",
            min_value=0.0,
            max_value=15.0,
            value=float(annual_savings_increase_rate),
            step=0.5,
            key=k("savings_increase_rate_input"),
        )

    col_age, col_ret_age, col_exp = st.columns(3)
    with col_age:
        new_current_age = st.number_input(
            f"{t('currentAgeLabel', lang)} {t('todayAge', lang)}",
            min_value=18,
            max_value=90,
            value=int(current_age),
            step=1,
            key=k("current_age_input"),
        )
    with col_ret_age:
        # Keep an already-entered retirement age valid when the current age is raised past it
        ret_key = k("target_ret_age_input")
        if ret_key in st.session_state and st.session_state[ret_key] < int(new_current_age):
            st.session_state[ret_key] = int(new_current_age)
        new_ret_age = st.number_input(
            f"{t('targetRetirementAgeLabel', lang)}",
            min_value=int(new_current_age),
            max_value=95,
            value=max(int(new_current_age), int(target_retirement_age)),
            step=1,
            key=k("target_ret_age_input"),
        )
    with col_exp:
        life_key = k("life_expectancy_input")
        life_min = max(int(new_ret_age) + 1, 75)
        if life_key in st.session_state and st.session_state[life_key] < life_min:
            st.session_state[life_key] = life_min
        new_life_exp = st.number_input(
            f"{t('lifeExpectancyLabel', lang)}",
            min_value=max(int(new_ret_age) + 1, 75),
            max_value=110,
            value=max(int(new_ret_age) + 1, int(life_expectancy)),
            step=1,
            key=k("life_expectancy_input"),
        )

    return (
        selected_mode,
        new_target_income,
        updated_assets,
        new_monthly_savings,
        new_savings_inc,
        new_current_age,
        new_ret_age,
        new_life_exp,
    )
