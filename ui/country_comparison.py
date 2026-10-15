"""
Vista comparativa dels 3 règims d'inversió a Irlanda (Pressupost 2027).
Substitueix la comparativa territorial per una comparativa d'esquemes irlandesos.
"""
from __future__ import annotations

import streamlit as st
from config.translations import Language, t
from engine.fire_simulation import simulate_fire
from models.types import FireInputs, IrelandAssetType, TaxSettings


def render_country_comparison(
    current_inputs: FireInputs,
    on_apply_scheme,
    lang: Language,
):
    """Renderitza la comparativa dels 3 esquemes d'inversió disponibles a Irlanda sota el Pressupost 2027."""
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 12px; margin-bottom: 14px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="
                    background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.25);
                    color: #10b981; padding: 8px; border-radius: 12px; font-size: 1.1rem;
                ">⚖️</div>
                <div>
                    <h3 style="margin: 0; font-size: 1.05rem; font-weight: 800; color: #ffffff;">
                        {t('compareTitle', lang)}
                    </h3>
                    <p style="margin: 2px 0 0 0; font-size: 0.74rem; color: #94a3b8;">
                        {t('compareSubtitle', lang)}
                    </p>
                </div>
            </div>
            <span style="
                background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3);
                border-radius: 9999px; padding: 4px 10px; font-size: 0.72rem; font-weight: 700;
            ">
                {t('compareSameGoalBadge', lang)}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    schemes: list[dict] = [
        {
            "id": "budget_2027_account",
            "name": "New Investment Account (Budget 2027)",
            "badge": "🌟 Recommended",
            "badge_color": "rgba(16, 185, 129, 0.2)",
            "badge_text": "#34d399",
            "summary": "First €50k 100% tax-free. Flat 1% annual tax above €50k. 0% Exit Tax & NO Deemed Disposal.",
            "tax_settings": TaxSettings(
                country="IE",
                ireland_asset_type="budget_2027_account",
                ireland_investment_account_threshold=50000.0,
                ireland_investment_account_rate=1.0,
                catalonia_apply_wealth_tax=False,
            ),
        },
        {
            "id": "etf_exit_tax",
            "name": "UCITS ETFs (Exit Tax Regime)",
            "badge": "📈 Traditional Funds",
            "badge_color": "rgba(245, 158, 11, 0.2)",
            "badge_text": "#fbbf24",
            "summary": "35% Exit Tax (Budget 2027 rate) on gains + 8-year Deemed Disposal drag outside the new scheme.",
            "tax_settings": TaxSettings(
                country="IE",
                ireland_asset_type="etf_exit_tax",
                ireland_exit_tax_rate=35.0,
                ireland_simulate_deemed_disposal=True,
                ireland_deemed_disposal_mode=current_inputs.tax_settings.ireland_deemed_disposal_mode,
                catalonia_apply_wealth_tax=False,
            ),
        },
        {
            "id": "individual_shares_cgt",
            "name": "Individual Equities (CGT Regime)",
            "badge": "🏢 Stocks & Shares",
            "badge_color": "rgba(59, 130, 246, 0.2)",
            "badge_text": "#60a5fa",
            "summary": "31% CGT (Budget 2027 rate) on gains above €1,270 annual personal exemption. No deemed disposal.",
            "tax_settings": TaxSettings(
                country="IE",
                ireland_asset_type="individual_shares_cgt",
                ireland_cgt_rate=31.0,
                catalonia_apply_wealth_tax=False,
            ),
        },
    ]

    cols = st.columns(3)

    for i, s in enumerate(schemes):
        scheme_id: IrelandAssetType = s["id"]
        custom_tax = s["tax_settings"]

        sim_inputs = FireInputs(
            mode=current_inputs.mode,
            current_age=current_inputs.current_age,
            target_retirement_age=current_inputs.target_retirement_age,
            life_expectancy=current_inputs.life_expectancy,
            target_monthly_disposable_income=current_inputs.target_monthly_disposable_income,
            assets=current_inputs.assets,
            monthly_savings=current_inputs.monthly_savings,
            annual_savings_increase_rate=current_inputs.annual_savings_increase_rate,
            safe_withdrawal_rate=current_inputs.safe_withdrawal_rate,
            scenario=current_inputs.scenario,
            tax_settings=custom_tax,
        )

        res = simulate_fire(sim_inputs, lang)
        is_active = current_inputs.tax_settings.ireland_asset_type == scheme_id

        with cols[i]:
            card_border = "#10b981" if is_active else "rgba(255, 255, 255, 0.1)"
            card_bg = "rgba(16, 185, 129, 0.08)" if is_active else "rgba(15, 23, 42, 0.7)"

            st.markdown(
                f"""
                <div style="
                    background: {card_bg}; border: 1px solid {card_border};
                    border-radius: 14px; padding: 16px; margin-bottom: 12px;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                        <span style="font-size: 0.95rem; font-weight: 800; color: #ffffff; line-height: 1.3;">
                            {s['name']}
                        </span>
                    </div>
                    <div style="margin-bottom: 8px;">
                        <span style="
                            font-size: 0.68rem; font-weight: 700; color: {s['badge_text']};
                            background: {s['badge_color']}; padding: 2px 7px; border-radius: 9999px;
                        ">{s['badge']}</span>
                        {'<span style="font-size: 0.68rem; font-weight: 700; color: #34d399; background: rgba(16, 185, 129, 0.25); padding: 2px 7px; border-radius: 9999px; margin-left: 4px;">★ Active</span>' if is_active else ''}
                    </div>
                    <div style="font-size: 0.72rem; color: #94a3b8; line-height: 1.4; margin-bottom: 12px; min-height: 38px;">
                        {s['summary']}
                    </div>
                    <div style="margin-bottom: 6px;">
                        <span style="font-size: 0.70rem; color: #94a3b8; display: block;">{t('compareRequiredFireCapital', lang)}</span>
                        <span style="font-size: 1.3rem; font-weight: 900; color: #f59e0b;">{res.fire_number_nominal:,.0f} €</span>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 10px; font-size: 0.75rem;">
                        <div>
                            <span style="color: #94a3b8; display: block;">{t('compareYearsToFire', lang)}</span>
                            <strong style="color: #ffffff;">{res.years_to_fire} {t('years', lang)}</strong>
                        </div>
                        <div>
                            <span style="color: #94a3b8; display: block;">{t('compareRetirementAge', lang)}</span>
                            <strong style="color: #ffffff;">{res.age_at_fire} {t('years', lang)}</strong>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.75rem; border-top: 1px solid rgba(255, 255, 255, 0.08); padding-top: 8px; margin-bottom: 12px;">
                        <div>
                            <span style="color: #94a3b8; display: block;">{t('compareAnnualTaxes', lang)}</span>
                            <strong style="color: #f43f5e;">{res.annual_tax_at_retirement:,.0f} €</strong>
                        </div>
                        <div>
                            <span style="color: #94a3b8; display: block;">{t('compareEffectiveRate', lang)}</span>
                            <strong style="color: #38bdf8;">{(res.effective_tax_rate_at_retirement * 100):.1f}%</strong>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if not is_active:
                if st.button(
                    f"👉 {t('compareActivateTaxation', lang)}",
                    key=f"apply_scheme_{scheme_id}",
                    use_container_width=True,
                ):
                    on_apply_scheme(scheme_id)
