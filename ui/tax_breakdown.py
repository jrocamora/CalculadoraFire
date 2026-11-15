"""
Targeta de desglossament del primer any de jubilació sota la fiscalitat irlandesa.
Les xifres surten de la mateixa simulació any a any (en euros d'avui), de manera que
brut - impostos = net quadra amb les targetes i la taula.
"""
from __future__ import annotations

import streamlit as st
from config.translations import Language, t
from models.types import FireCalculationResult, TaxSettings


def _eur(val: float) -> str:
    return f"€{round(val):,}"


def render_tax_breakdown_card(
    result: FireCalculationResult,
    tax_settings: TaxSettings,
    lang: Language,
):
    """Renderitza el desglossament de cada euro retirat el primer any de jubilació."""
    annual_gross = result.retirement_year_gross
    annual_tax = result.annual_tax_at_retirement
    annual_net = max(0.0, annual_gross - annual_tax)

    gross_denom = max(1.0, annual_gross)
    net_ratio = min(100.0, max(0.0, (annual_net / gross_denom) * 100.0))
    tax_ratio = min(100.0, max(0.0, (annual_tax / gross_denom) * 100.0))

    st.markdown(
        f"""
        <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #e2e8f0; padding-bottom: 12px; margin-bottom: 14px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="
                    background: #f0fdf4; border: 1px solid #bbf7d0;
                    color: #059669; padding: 8px; border-radius: 12px; font-size: 1.1rem;
                ">🧾</div>
                <div>
                    <h3 style="margin: 0; font-size: 1.05rem; font-weight: 800; color: #0f172a;">
                        {t('breakdownTitle', lang)}
                    </h3>
                    <p style="margin: 2px 0 0 0; font-size: 0.74rem; color: #64748b;">
                        {t('breakdownSubtitle', lang)}
                    </p>
                </div>
            </div>
            <div style="text-align: right;">
                <span style="font-size: 0.72rem; color: #64748b; display: block;">{t('grossAnnualWithdrawal', lang)}</span>
                <span style="font-size: 1.15rem; font-weight: 800; color: #0f172a; font-family: monospace;">
                    {_eur(annual_gross)}{t('perYear', lang)}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div style="margin: 12px 0;">
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; font-weight: 700; margin-bottom: 6px;">
                <span style="color: #059669;">
                    🪙 {t('netInPocket', lang)} {net_ratio:.1f}% ({_eur(annual_net)})
                </span>
                <span style="color: #e11d48;">
                    📉 {t('taxesPaid', lang)} {tax_ratio:.1f}% ({_eur(annual_tax)})
                </span>
            </div>
            <div style="
                width: 100%; height: 16px; background: #e2e8f0;
                border: 1px solid #cbd5e1; border-radius: 9999px;
                overflow: hidden; display: flex;
            ">
                <div style="width: {net_ratio}%; height: 100%; background: linear-gradient(90deg, #10b981, #059669);"></div>
                <div style="width: {tax_ratio}%; height: 100%; background: linear-gradient(90deg, #f43f5e, #e11d48);"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if result.fire_reachable:
        when = f"your first year of retirement (age {result.age_at_fire})"
    else:
        when = "an estimate, because the target is not reached within the plan"
    threshold = float(getattr(tax_settings, "ireland_investment_account_threshold", 50000.0))
    acct_rate = float(getattr(tax_settings, "ireland_investment_account_rate", 1.0))
    exit_rate = float(getattr(tax_settings, "ireland_exit_tax_rate", 35.0)) + (tax_settings.tax_reform_change_rate or 0.0)
    cgt_rate = float(getattr(tax_settings, "ireland_cgt_rate", 31.0)) + (tax_settings.tax_reform_change_rate or 0.0)
    st.markdown(
        f"""
        <div style="
            background: #f8fafc; border: 1px solid #e2e8f0;
            border-radius: 12px; padding: 14px; margin-top: 10px;
        ">
            <div style="font-size: 0.78rem; color: #334155; line-height: 1.5;">
                ℹ️ Figures for {when}, in today's euros. Withdrawals come first from the Investment Account
                (no tax on withdrawal; {acct_rate:g}% a year on the balance above {_eur(threshold)}), then from shares
                and other assets ({cgt_rate:g}% CGT on the gain, €1,270 yearly exemption), then from ETFs
                ({exit_rate:g}% Exit Tax on the gain). Pension drawdowns are taxed as income; the State Pension is not
                taxed in this model.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Investment Account charge", _eur(result.retirement_year_account_charge))
    with c2:
        st.metric("CGT (shares & other)", _eur(result.retirement_year_cgt))
    with c3:
        st.metric("Exit Tax (ETFs)", _eur(result.retirement_year_exit_tax))
    with c4:
        st.metric("Income tax on pensions", _eur(result.retirement_year_pension_tax))
