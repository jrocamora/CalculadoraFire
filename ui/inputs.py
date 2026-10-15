"""
Inputs bidireccionals i gestor d'actius de la cartera.
Port fidel de BiDirectionalInputs.tsx.
"""
from __future__ import annotations

import streamlit as st
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
                <h3 style="margin: 0; font-size: 1.1rem; font-weight: 800; color: #ffffff;">
                    {t('inputModeTitle', lang)}
                </h3>
                <p style="margin: 2px 0 0 0; font-size: 0.75rem; color: #94a3b8;">
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
        key="calc_mode_radio",
    )

    new_target_income = target_monthly_income

    if selected_mode == "target_spending":
        st.markdown(
            f"""
            <div style="
                background: rgba(245, 158, 11, 0.05);
                border: 1px solid rgba(245, 158, 11, 0.2);
                border-radius: 14px;
                padding: 16px;
                margin: 12px 0;
            ">
                <div style="font-size: 0.82rem; font-weight: 700; color: #fbbf24; margin-bottom: 4px;">
                    {t('targetDisposableQuestion', lang)}
                </div>
                <div style="font-size: 0.74rem; color: #cbd5e1; margin-bottom: 12px;">
                    {t('targetDisposableHelp', lang)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_preset1, col_preset2, col_val = st.columns([1, 1, 2])
        label_2500 = "€2,500 " if lang == "en" else "2.500 € "
        label_5000 = "€5,000 " if lang == "en" else "5.000 € "
        with col_preset1:
            if st.button(label_2500 + t("commonTarget", lang).split("(")[-1].replace(")", ""), key="preset_2500", use_container_width=True):
                new_target_income = 2500.0
        with col_preset2:
            if st.button(label_5000 + t("fatFire", lang).split("(")[-1].replace(")", ""), key="preset_5000", use_container_width=True):
                new_target_income = 5000.0
        with col_val:
            new_target_income = st.number_input(
                t("enterExactValue", lang),
                min_value=500.0,
                max_value=30000.0,
                value=float(new_target_income),
                step=100.0,
                key="target_monthly_income_input",
            )

        mo_suffix = "(€/mo)" if lang == "en" else "(€/mes)"
        new_target_income = st.slider(
            f"{t('disposableIncomeTitle', lang)} {mo_suffix}",
            min_value=800.0,
            max_value=12000.0,
            value=float(new_target_income),
            step=50.0,
            key="target_monthly_income_slider",
        )

    # Secció d'actius de la cartera (Portfolio Assets)
    with st.expander(
        f"💼 {t('portfolioTotal', lang)} {total_assets:,.0f} € — {len(assets)} {t('assetsCount', lang)}",
        expanded=True,
    ):
        st.caption(t("portfolioAssetSubtitle", lang))

        category_icons = {
            "index_funds": "📈 " + t("categoryIndexFunds", lang),
            "individual_stocks": "🏢 " + t("categoryIndividualStocks", lang),
            "cash_deposits": "💶 " + t("categoryCashDeposits", lang),
            "private_pension": "🛡️ " + t("categoryPrivatePension", lang),
            "my_future_fund": "🏛️ " + t("categoryMyFutureFund", lang),
            "real_estate_other": "🏡 " + t("categoryRealEstateOther", lang),
        }

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
                    key=f"asset_amount_{a.id}",
                )
            with c_ret:
                ret = st.number_input(
                    f"{t('expectedReturn', lang)} (%)",
                    min_value=-5.0,
                    max_value=25.0,
                    value=float(a.expected_return_annual),
                    step=0.5,
                    key=f"asset_ret_{a.id}",
                )
            with c_cost:
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
                    key=f"asset_cost_{a.id}",
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
            key="monthly_savings_input",
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
            key="savings_increase_rate_input",
        )

    col_age, col_ret_age, col_exp = st.columns(3)
    with col_age:
        new_current_age = st.number_input(
            f"{t('currentAgeLabel', lang)} {t('todayAge', lang)}",
            min_value=18,
            max_value=90,
            value=int(current_age),
            step=1,
            key="current_age_input",
        )
    with col_ret_age:
        new_ret_age = st.number_input(
            f"{t('targetRetirementAgeLabel', lang)}",
            min_value=int(new_current_age),
            max_value=95,
            value=max(int(new_current_age), int(target_retirement_age)),
            step=1,
            key="target_ret_age_input",
        )
    with col_exp:
        new_life_exp = st.number_input(
            f"{t('lifeExpectancyLabel', lang)}",
            min_value=max(int(new_ret_age) + 1, 75),
            max_value=110,
            value=max(int(new_ret_age) + 1, int(life_expectancy)),
            step=1,
            key="life_expectancy_input",
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
