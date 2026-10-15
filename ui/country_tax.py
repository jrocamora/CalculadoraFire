"""
Configurador fiscal d'Irlanda i esquemes d'inversió (Pressupost 2027).
Centrat exclusivament en Irlanda, amagant Catalunya i Andorra.
"""
from __future__ import annotations

import streamlit as st
from config.translations import Language, t
from models.types import IrelandAssetType, TaxSettings


def render_country_tax_selector(
    tax_settings: TaxSettings,
    current_year: int,
    lang: Language,
) -> TaxSettings:
    """Renderitza el selector de fiscalitat irlandesa amb suport per al Pressupost 2027."""
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 12px; margin-bottom: 14px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="
                    background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.25);
                    color: #10b981; padding: 8px; border-radius: 12px; font-size: 1.1rem;
                ">🇮🇪</div>
                <div>
                    <h3 style="margin: 0; font-size: 1.05rem; font-weight: 800; color: #ffffff;">
                        {t('countryTaxTitle', lang)}
                    </h3>
                    <p style="margin: 2px 0 0 0; font-size: 0.74rem; color: #94a3b8;">
                        {t('countryTaxSubtitle', lang)}
                    </p>
                </div>
            </div>
            <span style="
                background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3);
                border-radius: 9999px; padding: 3px 8px; font-size: 0.70rem; font-weight: 700;
            ">
                Budget 2027 Verified
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    new_settings = TaxSettings(
        country="IE",
        ireland_asset_type=tax_settings.ireland_asset_type,
        ireland_simulate_deemed_disposal=tax_settings.ireland_simulate_deemed_disposal,
        ireland_deemed_disposal_mode=tax_settings.ireland_deemed_disposal_mode,
        ireland_exit_tax_rate=getattr(tax_settings, "ireland_exit_tax_rate", 35.0),
        ireland_cgt_rate=getattr(tax_settings, "ireland_cgt_rate", 31.0),
        ireland_investment_account_threshold=getattr(tax_settings, "ireland_investment_account_threshold", 50000.0),
        ireland_investment_account_rate=getattr(tax_settings, "ireland_investment_account_rate", 1.0),
        catalonia_capital_gains_ratio=50.0,
        catalonia_apply_wealth_tax=False,
        andorra_exempt_listed_securities=True,
        tax_reform_change_rate=tax_settings.tax_reform_change_rate,
        planned_relocation_country="none",
        planned_relocation_year=None,
    )

    scheme_options: list[IrelandAssetType] = [
        "budget_2027_account",
        "etf_exit_tax",
        "individual_shares_cgt",
    ]

    scheme_labels = {
        "budget_2027_account": t("irelandBudget2027Account", lang),
        "etf_exit_tax": t("irelandEtfsExitTax", lang),
        "individual_shares_cgt": t("irelandIndividualShares", lang),
    }

    selected_scheme = st.radio(
        t("irelandInvestmentType", lang),
        options=scheme_options,
        format_func=lambda x: scheme_labels[x],
        index=scheme_options.index(new_settings.ireland_asset_type) if new_settings.ireland_asset_type in scheme_options else 0,
        key="ireland_scheme_radio",
    )
    new_settings.ireland_asset_type = selected_scheme

    # Panell de detall de l'esquema seleccionat
    if selected_scheme == "budget_2027_account":
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(6, 182, 212, 0.08) 100%);
                border: 1px solid rgba(16, 185, 129, 0.35);
                border-radius: 12px; padding: 14px; margin: 10px 0;
            ">
                <div style="font-size: 0.82rem; font-weight: 800; color: #34d399; margin-bottom: 4px;">
                    {t('irelandBudget2027Account', lang)}
                </div>
                <div style="font-size: 0.74rem; color: #e2e8f0; line-height: 1.5; margin-bottom: 10px;">
                    {t('irelandBudget2027AccountSub', lang)}
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.72rem; color: #94a3b8; border-top: 1px solid rgba(255, 255, 255, 0.08); padding-top: 8px;">
                    <div>• <strong>€50,000:</strong> 0% Tax (Tax-Free Allowance)</div>
                    <div>• <strong>Balance >€50k:</strong> Flat 1% Annual Tax</div>
                    <div>• <strong>Withdrawals:</strong> 0% CGT / 0% Exit Tax</div>
                    <div>• <strong>Deemed Disposal:</strong> EXEMPT (0%)</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_thresh, col_pct = st.columns(2)
        with col_thresh:
            new_settings.ireland_investment_account_threshold = st.number_input(
                "Tax-Free Threshold (€)",
                min_value=0.0,
                max_value=200000.0,
                value=float(new_settings.ireland_investment_account_threshold),
                step=5000.0,
                key="ie_budget2027_threshold",
            )
        with col_pct:
            new_settings.ireland_investment_account_rate = st.number_input(
                "Annual Tax on Balance >€50k (%)",
                min_value=0.0,
                max_value=5.0,
                value=float(new_settings.ireland_investment_account_rate),
                step=0.25,
                key="ie_budget2027_rate",
            )

    elif selected_scheme == "etf_exit_tax":
        st.markdown(
            f"""
            <div style="
                background: rgba(245, 158, 11, 0.06);
                border: 1px solid rgba(245, 158, 11, 0.25);
                border-radius: 12px; padding: 14px; margin: 10px 0;
            ">
                <div style="font-size: 0.82rem; font-weight: 800; color: #fbbf24; margin-bottom: 4px;">
                    {t('irelandEtfsExitTax', lang)}
                </div>
                <div style="font-size: 0.74rem; color: #cbd5e1; line-height: 1.5; margin-bottom: 8px;">
                    {t('irelandEtfsExitTaxSub', lang)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_exit_rate, col_deemed = st.columns([1.5, 2.5])
        with col_exit_rate:
            new_settings.ireland_exit_tax_rate = st.slider(
                "Exit Tax Rate (%)",
                min_value=20.0,
                max_value=45.0,
                value=float(new_settings.ireland_exit_tax_rate),
                step=1.0,
                key="ie_exit_rate_slider",
                help="Budget 2027 reduced Exit Tax to 35% (effective Jan 1, 2027). Legacy rate was 41%.",
            )

        with col_deemed:
            new_settings.ireland_simulate_deemed_disposal = st.checkbox(
                t("irelandDeemedDisposalTitle", lang),
                value=bool(new_settings.ireland_simulate_deemed_disposal),
                key="ie_deemed_disposal_checkbox",
            )

        if new_settings.ireland_simulate_deemed_disposal:
            st.markdown(f"**{t('irelandDeemedDisposalModelLabel', lang)}**")
            mode_choice = st.radio(
                "Deemed disposal model",
                options=["staggered_rolling_eighth", "lump_sum_8y"],
                format_func=lambda x: (
                    f"{t('irelandDeemedDisposalRolling', lang)}: {t('irelandDeemedDisposalRollingDesc', lang)}"
                    if x == "staggered_rolling_eighth"
                    else f"{t('irelandDeemedDisposalLumpSum', lang)}: {t('irelandDeemedDisposalLumpSumDesc', lang)}"
                ),
                index=0 if new_settings.ireland_deemed_disposal_mode == "staggered_rolling_eighth" else 1,
                label_visibility="collapsed",
                key="ie_deemed_mode_radio",
            )
            new_settings.ireland_deemed_disposal_mode = mode_choice  # type: ignore

    elif selected_scheme == "individual_shares_cgt":
        st.markdown(
            f"""
            <div style="
                background: rgba(59, 130, 246, 0.06);
                border: 1px solid rgba(59, 130, 246, 0.25);
                border-radius: 12px; padding: 14px; margin: 10px 0;
            ">
                <div style="font-size: 0.82rem; font-weight: 800; color: #60a5fa; margin-bottom: 4px;">
                    {t('irelandIndividualShares', lang)}
                </div>
                <div style="font-size: 0.74rem; color: #cbd5e1; line-height: 1.5;">
                    {t('irelandIndividualSharesSub', lang)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        new_settings.ireland_cgt_rate = st.slider(
            "Capital Gains Tax (CGT) Rate (%)",
            min_value=20.0,
            max_value=40.0,
            value=float(new_settings.ireland_cgt_rate),
            step=1.0,
            key="ie_cgt_rate_slider",
            help="Budget 2027 reduced CGT to 31% (effective Oct 7, 2026). Legacy rate was 33%.",
        )

    # Sensibilitat a reformes fiscals
    st.markdown("---")
    st.markdown(f"**⚙️ {t('taxReformTitle', lang)}**")
    st.caption(t("taxReformDesc", lang))
    new_settings.tax_reform_change_rate = st.slider(
        "Tax Rate Adjustment (%)",
        min_value=-5.0,
        max_value=10.0,
        value=float(new_settings.tax_reform_change_rate or 0.0),
        step=1.0,
        key="tax_reform_slider",
    )

    return new_settings
