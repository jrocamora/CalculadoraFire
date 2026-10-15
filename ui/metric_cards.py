"""
Targetes de mètriques principals (FIRE Number, Temps, Ingressos Nets, Fiscalitat).
Port fidel de MetricCards.tsx.
"""
from __future__ import annotations

import streamlit as st
from config.translations import Language, t
from models.types import CountryCode, FireCalculationResult


def format_eur(val: float, lang: Language) -> str:
    """Formata un valor numèric en format de moneda català o anglès."""
    rounded = round(val)
    if lang == "ca":
        return f"{rounded:,.0f} €".replace(",", ".")
    return f"€{rounded:,.0f}"


def render_metric_cards(
    result: FireCalculationResult,
    safe_withdrawal_rate: float,
    country: CountryCode,
    lang: Language,
):
    """Renderitza les 4 mètriques destacades amb disseny visual modern."""
    fire_num = result.fire_number_nominal
    current_nw = result.current_total_net_worth
    nw_pct = (current_nw / (fire_num or 1.0)) * 100.0
    swr_multiplier = 100.0 / max(0.01, safe_withdrawal_rate)

    country_names = {
        "CAT": "Catalonia 🏴󠁥󠁳󠁣󠁴󠁿" if lang == "en" else "Catalunya 🏴󠁥󠁳󠁣󠁴󠁿",
        "IE": "Ireland 🇮🇪" if lang == "en" else "Irlanda 🇮🇪",
        "AD": "Andorra 🇦🇩",
    }
    c_name = country_names.get(country, "Catalunya 🏴󠁥󠁳󠁣󠁴󠁿")

    col1, col2, col3, col4 = st.columns(4)

    # 1. FIRE NUMBER
    with col1:
        st.markdown(
            f"""
            <div class="metric-card-fire">
                <div style="position: absolute; top: 14px; right: 14px; font-size: 1.25rem;">🔥</div>
                <div class="metric-title" style="color: #f59e0b;">{t('fireNumberTitle', lang)}</div>
                <div class="metric-value">{format_eur(fire_num, lang)}</div>
                <div class="metric-subtitle">
                    <span style="color: #fbbf24; font-weight: 700;">{safe_withdrawal_rate:.1f}% SWR</span>
                    <span style="color: #64748b; margin: 0 4px;">•</span>
                    <span>{swr_multiplier:.1f}x {t('swrMultiplierSuffix', lang)}</span>
                </div>
                <div class="metric-footer" style="border-color: rgba(245, 158, 11, 0.2);">
                    <div>{t('currentNetWorthLabel', lang)} <strong>{format_eur(current_nw, lang)}</strong> ({nw_pct:.0f}%)</div>
                    <div style="font-size: 0.66rem; color: #cbd5e1; margin-top: 4px;">
                        🌉 Bridge: <strong>{format_eur(result.bridge_capital_at_fire, lang)}</strong> • 🛡️ Pension: <strong>{format_eur(result.pension_capital_at_fire, lang)}</strong>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 2. TIME TO FIRE
    with col2:
        if result.is_already_fire:
            time_display = f"<span style='color: #34d399;'>{t('alreadyFire', lang)}</span>"
            time_sub = t("canRetireNow", lang)
        else:
            time_display = f"{result.years_to_fire} <span style='font-size: 1.1rem; font-weight: 600;'>{t('years', lang)}</span>"
            time_sub = (
                f"{t('retireAtAge', lang)} <strong>{result.age_at_fire} {t('years', lang)}</strong> "
                f"({t('inYear', lang)} <strong>{result.calendar_year_at_fire}</strong>)"
            )

        lump_sum_html = (
            f"<div style='font-size: 0.66rem; color: #34d399; margin-top: 4px;'>🎁 25% Tax-Free Lump Sums: <strong>{format_eur(result.tax_free_lump_sum_total, lang)}</strong></div>"
            if result.tax_free_lump_sum_total > 0
            else ""
        )

        st.markdown(
            f"""
            <div class="metric-card-time">
                <div style="position: absolute; top: 14px; right: 14px; font-size: 1.25rem;">📅</div>
                <div class="metric-title" style="color: #10b981;">{t('timeToFireTitle', lang)}</div>
                <div class="metric-value">{time_display}</div>
                <div class="metric-subtitle">{time_sub}</div>
                <div class="metric-footer" style="border-color: rgba(16, 185, 129, 0.2);">
                    <div>{t('survivalEstimated', lang)} <strong>{result.portfolio_survival_years} {t('planYears', lang)}</strong></div>
                    {lump_sum_html}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 3. DISPOSABLE INCOME
    with col3:
        monthly_net = result.monthly_disposable_target
        annual_net = monthly_net * 12.0
        st.markdown(
            f"""
            <div class="metric-card-income">
                <div style="position: absolute; top: 14px; right: 14px; font-size: 1.25rem;">🪙</div>
                <div class="metric-title" style="color: #06b6d4;">{t('disposableIncomeTitle', lang)}</div>
                <div class="metric-value">
                    {format_eur(monthly_net, lang)}
                    <span style="font-size: 0.85rem; font-weight: 500; color: #94a3b8;">{t('perMonth', lang)}</span>
                </div>
                <div class="metric-subtitle">
                    = {format_eur(annual_net, lang)} {t('netPerYear', lang)}
                </div>
                <div class="metric-footer" style="border-color: rgba(6, 182, 212, 0.2);">
                    {t('grossWithdrawalNeeded', lang)} <strong>{format_eur(result.annual_gross_withdrawal_needed, lang)}</strong>{t('perYear', lang)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 4. TAXATION
    with col4:
        tax_val = result.annual_tax_at_retirement
        eff_rate = result.effective_tax_rate_at_retirement * 100.0
        status_html = (
            f"<span style='color: #34d399; font-weight: 700;'>✓ {t('sustainable', lang)}</span>"
            if result.is_sustainable
            else f"<span style='color: #f43f5e; font-weight: 700;'>⚠ {t('depletionRisk', lang)}</span>"
        )

        st.markdown(
            f"""
            <div class="metric-card-tax">
                <div style="position: absolute; top: 14px; right: 14px; font-size: 1.25rem;">🧾</div>
                <div class="metric-title" style="color: #a855f7;">{t('taxationTitle', lang)} ({c_name})</div>
                <div class="metric-value">
                    {format_eur(tax_val, lang)}
                    <span style="font-size: 0.85rem; font-weight: 500; color: #94a3b8;">{t('perYear', lang)}</span>
                </div>
                <div class="metric-subtitle">
                    {t('effectiveTaxRate', lang)} <strong style="color: #c084fc;">{eff_rate:.1f}%</strong>
                </div>
                <div class="metric-footer" style="border-color: rgba(168, 85, 247, 0.2); display: flex; justify-content: space-between;">
                    <span>{t('planStatus', lang)}</span>
                    {status_html}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
