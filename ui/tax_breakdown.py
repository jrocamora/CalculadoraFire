"""
Targeta de desglossament de la retirada anual i impacte fiscal irlandès.
Elimina qualsevol menció de Catalunya o Wealth Tax quan s'aplica Irlanda.
"""
from __future__ import annotations

import streamlit as st
from config.translations import Language, t
from engine.tax_calculators import compute_annual_tax_for_withdrawal
from models.types import FireCalculationResult, TaxSettings


def render_tax_breakdown_card(
    result: FireCalculationResult,
    tax_settings: TaxSettings,
    lang: Language,
):
    """Renderitza el desglossament de cada euro retirat en fase de jubilació sota la fiscalitat irlandesa."""
    annual_gross = result.annual_gross_withdrawal_needed
    annual_tax = result.annual_tax_at_retirement
    annual_net = result.monthly_disposable_target * 12.0

    gross_denom = max(1.0, annual_gross)
    net_ratio = min(100.0, max(0.0, (annual_net / gross_denom) * 100.0))
    tax_ratio = min(100.0, max(0.0, (annual_tax / gross_denom) * 100.0))

    tax_comp = compute_annual_tax_for_withdrawal(
        annual_gross,
        tax_settings,
        result.fire_number_nominal,
        lang,
    )

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
                    {annual_gross:,.0f} €{t('perYear', lang)}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Barra visual proporcional
    st.markdown(
        f"""
        <div style="margin: 12px 0;">
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; font-weight: 700; margin-bottom: 6px;">
                <span style="color: #059669;">
                    🪙 {t('netInPocket', lang)} {net_ratio:.1f}% ({annual_net:,.0f} €)
                </span>
                <span style="color: #e11d48;">
                    📉 {t('taxesPaid', lang)} {tax_ratio:.1f}% ({annual_tax:,.0f} €)
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

    # Explicació narrativa oficial
    st.markdown(
        f"""
        <div style="
            background: #f8fafc; border: 1px solid #e2e8f0;
            border-radius: 12px; padding: 14px; margin-top: 10px;
        ">
            <div style="font-size: 0.78rem; color: #334155; line-height: 1.5; margin-bottom: 4px;">
                ℹ️ {tax_comp.explanation}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)

    if tax_settings.ireland_asset_type == "budget_2027_account":
        with c1:
            st.metric("Tax-Free Allowance", "€50,000")
        with c2:
            st.metric("Annual 1% Charge (>€50k)", f"{tax_comp.total_tax:,.0f} €")
        with c3:
            st.metric("CGT / Exit Tax on Growth", "0.0 € (Exempt)")
        with c4:
            st.metric("Effective Drag", f"{tax_comp.effective_tax_rate * 100.0:.1f}%")

    elif tax_settings.ireland_asset_type == "etf_exit_tax":
        exit_rate_label = f"{getattr(tax_settings, 'ireland_exit_tax_rate', 35.0):.0f}%"
        with c1:
            st.metric(t("taxableGains", lang), f"{tax_comp.taxable_gains:,.0f} €")
        with c2:
            st.metric(f"Exit Tax ({exit_rate_label})", f"{tax_comp.total_tax:,.0f} €")
        with c3:
            st.metric("Deemed Disposal", "Active (8-Year)" if tax_settings.ireland_simulate_deemed_disposal else "Disabled")
        with c4:
            st.metric(t("totalEffectiveRate", lang), f"{tax_comp.effective_tax_rate * 100.0:.1f}%")

    else:
        # individual_shares_cgt
        cgt_rate_label = f"{getattr(tax_settings, 'ireland_cgt_rate', 31.0):.0f}%"
        with c1:
            st.metric(t("taxableGains", lang), f"{tax_comp.taxable_gains:,.0f} €")
        with c2:
            st.metric(f"CGT Quota ({cgt_rate_label})", f"{tax_comp.total_tax:,.0f} €")
        with c3:
            st.metric("Personal Exemption", "€1,270 / yr")
        with c4:
            st.metric(t("totalEffectiveRate", lang), f"{tax_comp.effective_tax_rate * 100.0:.1f}%")
