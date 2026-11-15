"""
Configurador fiscal d'Irlanda i esquemes d'inversió (Pressupost 2027).
Centrat exclusivament en Irlanda. L'opció triada decideix on van els estalvis nous.
"""
from __future__ import annotations

import streamlit as st
from ui.keys import k
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
        <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #e2e8f0; padding-bottom: 12px; margin-bottom: 14px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="
                    background: #f0fdf4; border: 1px solid #bbf7d0;
                    color: #059669; padding: 8px; border-radius: 12px; font-size: 1.1rem;
                ">🇮🇪</div>
                <div>
                    <h3 style="margin: 0; font-size: 1.05rem; font-weight: 800; color: #0f172a;">
                        {t('countryTaxTitle', lang)}
                    </h3>
                    <p style="margin: 2px 0 0 0; font-size: 0.74rem; color: #64748b;">
                        {t('countryTaxSubtitle', lang)}
                    </p>
                </div>
            </div>
            <span style="
                background: #ecfdf5; color: #059669; border: 1px solid #a7f3d0;
                border-radius: 9999px; padding: 3px 8px; font-size: 0.70rem; font-weight: 700;
            ">
                Budget 2027 · subject to legislation
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
        "Where do your new monthly savings go?",
        options=scheme_options,
        format_func=lambda x: scheme_labels[x],
        index=scheme_options.index(new_settings.ireland_asset_type) if new_settings.ireland_asset_type in scheme_options else 0,
        key=k("ireland_scheme_radio"),
        help="Existing assets keep their own tax treatment: the Investment Account pays the yearly balance charge, "
        "index funds / ETFs pay Exit Tax (and Deemed Disposal), and shares, cash and other assets pay CGT on gains.",
    )
    new_settings.ireland_asset_type = selected_scheme

    threshold = float(new_settings.ireland_investment_account_threshold)
    acct_rate = float(new_settings.ireland_investment_account_rate)

    # Panell de detall de l'opció seleccionada
    if selected_scheme == "budget_2027_account":
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #f0fdf4 0%, #ecfeff 100%);
                border: 1px solid #a7f3d0;
                border-radius: 12px; padding: 14px; margin: 10px 0;
            ">
                <div style="font-size: 0.82rem; font-weight: 800; color: #047857; margin-bottom: 4px;">
                    {t('irelandBudget2027Account', lang)}
                </div>
                <div style="font-size: 0.74rem; color: #166534; line-height: 1.5; margin-bottom: 10px;">
                    Opens on 1 July 2027. Savings go into the account up to €12,000 a year (€6,000 in 2027);
                    anything above the limit, and everything saved before it opens, goes into ETFs.
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.72rem; color: #334155; border-top: 1px solid #bbf7d0; padding-top: 8px;">
                    <div>• <strong>First €{threshold:,.0f}:</strong> no tax</div>
                    <div>• <strong>Balance above:</strong> {acct_rate:g}% a year</div>
                    <div>• <strong>Withdrawals:</strong> no CGT / Exit Tax</div>
                    <div>• <strong>Deemed Disposal:</strong> does not apply</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif selected_scheme == "etf_exit_tax":
        st.markdown(
            f"""
            <div style="
                background: #fffbeb;
                border: 1px solid #fde68a;
                border-radius: 12px; padding: 14px; margin: 10px 0;
            ">
                <div style="font-size: 0.82rem; font-weight: 800; color: #b45309; margin-bottom: 4px;">
                    {t('irelandEtfsExitTax', lang)}
                </div>
                <div style="font-size: 0.74rem; color: #78350f; line-height: 1.5;">
                    {t('irelandEtfsExitTaxSub', lang)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div style="
                background: #eff6ff;
                border: 1px solid #bfdbfe;
                border-radius: 12px; padding: 14px; margin: 10px 0;
            ">
                <div style="font-size: 0.82rem; font-weight: 800; color: #1d4ed8; margin-bottom: 4px;">
                    {t('irelandIndividualShares', lang)}
                </div>
                <div style="font-size: 0.74rem; color: #1e40af; line-height: 1.5;">
                    {t('irelandIndividualSharesSub', lang)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Deemed Disposal: s'aplica als ETFs que tinguis, sigui quina sigui l'opció d'estalvi
    new_settings.ireland_simulate_deemed_disposal = st.checkbox(
        t("irelandDeemedDisposalTitle", lang) + " (ETFs)",
        value=bool(new_settings.ireland_simulate_deemed_disposal),
        key=k("ie_deemed_disposal_checkbox"),
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
            key=k("ie_deemed_mode_radio"),
        )
        new_settings.ireland_deemed_disposal_mode = mode_choice  # type: ignore

    with st.expander("⚙️ Tax rates used in the simulation", expanded=False):
        st.caption(
            "Budget 2027 figures as announced in October 2026. They still depend on the Finance Bill, "
            "so check them against Revenue before relying on them."
        )
        col_thresh, col_pct = st.columns(2)
        with col_thresh:
            new_settings.ireland_investment_account_threshold = st.number_input(
                "Investment Account tax-free threshold (€)",
                min_value=0.0,
                max_value=200000.0,
                value=float(new_settings.ireland_investment_account_threshold),
                step=5000.0,
                key=k("ie_budget2027_threshold"),
            )
        with col_pct:
            new_settings.ireland_investment_account_rate = st.number_input(
                "Investment Account yearly charge above threshold (%)",
                min_value=0.0,
                max_value=5.0,
                value=float(new_settings.ireland_investment_account_rate),
                step=0.25,
                key=k("ie_budget2027_rate"),
            )
        col_exit, col_cgt = st.columns(2)
        with col_exit:
            new_settings.ireland_exit_tax_rate = st.slider(
                "Exit Tax on ETFs (%)",
                min_value=20.0,
                max_value=45.0,
                value=float(new_settings.ireland_exit_tax_rate),
                step=1.0,
                key=k("ie_exit_rate_slider"),
                help="Budget 2027: 35% from 1 January 2027 (38% in 2026).",
            )
        with col_cgt:
            new_settings.ireland_cgt_rate = st.slider(
                "Capital Gains Tax (%)",
                min_value=20.0,
                max_value=40.0,
                value=float(new_settings.ireland_cgt_rate),
                step=1.0,
                key=k("ie_cgt_rate_slider"),
                help="Budget 2027: 31% on disposals from 7 October 2026 (previously 33%).",
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
        key=k("tax_reform_slider"),
    )

    return new_settings
