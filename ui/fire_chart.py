"""
Gràfic interactiu de trajectòria de la cartera amb Plotly.
Substitueix el component SVG de 435 línies per un gràfic modern, interactiu i amb zoom/hover.
"""
from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st
from config.translations import Language, t
from models.types import YearProjection


def render_fire_chart(
    projections: list[YearProjection],
    fire_number_nominal: float,
    retirement_age: int,
    lang: Language,
):
    """Renderitza el gràfic interactiu de la trajectòria patrimonial amb Plotly."""
    if not projections:
        return

    st.markdown(
        f"""
        <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 12px; margin-bottom: 14px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="
                    background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.25);
                    color: #f59e0b; padding: 8px; border-radius: 12px; font-size: 1.1rem;
                ">📈</div>
                <div>
                    <h3 style="margin: 0; font-size: 1.05rem; font-weight: 800; color: #ffffff;">
                        {t('chartTitle', lang)}
                    </h3>
                    <p style="margin: 2px 0 0 0; font-size: 0.74rem; color: #94a3b8;">
                        {t('chartSubtitle', lang)}
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    show_real = st.toggle(
        t("chartRealPurchasingPower", lang),
        value=True,
        key="toggle_show_real_curve",
    )

    ages = [p.age for p in projections]
    nominal_vals = [p.ending_portfolio for p in projections]
    real_vals = [p.ending_portfolio_real for p in projections]

    # Custom hover text per a cada any
    custom_hover = []
    for p in projections:
        phase = t("chartPhaseRetirement", lang) if p.is_retired else t("chartPhaseAccumulation", lang)
        notes_str = f"<br><b>Nota:</b> {p.tax_notes}" if p.tax_notes else ""
        pension_str = (
            f"<br>• 🌉 <b>Bridge (Accessible):</b> {p.bridge_portfolio:,.0f} €"
            f"<br>• 🛡️ <b>Private Pension:</b> {p.private_pension_value:,.0f} €"
            f"<br>• 🏛️ <b>MyFutureFund:</b> {p.my_future_fund_value:,.0f} €"
        )
        text = (
            f"<b>{p.calendar_year} ({p.age} {t('years', lang)}) - {phase}</b><br>"
            f"• {t('chartNominalNetWorth', lang)} {p.ending_portfolio:,.0f} €<br>"
            f"• {t('chartRealNetWorth', lang)} {p.ending_portfolio_real:,.0f} €"
            f"{pension_str}<br>"
            f"• {t('chartContributionYear', lang)} {p.contribution:,.0f} €<br>"
            f"• {t('chartGrossWithdrawal', lang)} {p.gross_withdrawal:,.0f} €<br>"
            f"• {t('chartEstimatedTax', lang)} {p.tax_paid:,.0f} €<br>"
            f"• {t('chartNetDisposable', lang)} {p.net_disposable_income:,.0f} €"
            f"{notes_str}"
        )
        custom_hover.append(text)

    fig = go.Figure()

    # 1. Corba Nominal amb àrea ombrejada
    fig.add_trace(
        go.Scatter(
            x=ages,
            y=nominal_vals,
            mode="lines",
            name=t("chartNominalLegend", lang),
            line=dict(color="#f59e0b", width=3),
            fill="tozeroy",
            fillcolor="rgba(245, 158, 11, 0.08)",
            hoverinfo="text",
            hovertext=custom_hover,
        )
    )

    # 2. Corba Real ajustada a la inflació (opcional)
    if show_real:
        fig.add_trace(
            go.Scatter(
                x=ages,
                y=real_vals,
                mode="lines",
                name=t("chartRealLegend", lang),
                line=dict(color="#06b6d4", width=2.5, dash="dash"),
                hoverinfo="text",
                hovertext=custom_hover,
            )
        )

    # 3. Línia horitzontal de la Xifra FIRE Objectiu
    fig.add_hline(
        y=fire_number_nominal,
        line_dash="dot",
        line_color="#ef4444",
        line_width=2,
        annotation_text=f"{t('chartFireTargetLegend', lang)}: {fire_number_nominal:,.0f} €",
        annotation_position="top left",
        annotation_font=dict(color="#ef4444", size=11),
    )

    # 4. Línia vertical de jubilació (FIRE)
    if any(p.age == retirement_age for p in projections):
        fig.add_vline(
            x=retirement_age,
            line_dash="dash",
            line_color="#10b981",
            line_width=2,
            annotation_text=f"🚀 {t('chartRetirementAt', lang)} {retirement_age} {t('years', lang)}",
            annotation_position="bottom right",
            annotation_font=dict(color="#10b981", size=11),
        )

    # 5. Línia vertical de MyFutureFund & Pensió d'Estat (66 anys)
    if any(p.age == 66 for p in projections) and 66 != retirement_age:
        fig.add_vline(
            x=66,
            line_dash="dot",
            line_color="#38bdf8",
            line_width=1.5,
            annotation_text="🏛️ Age 66: MyFutureFund & State Pension",
            annotation_position="top right",
            annotation_font=dict(color="#38bdf8", size=10),
        )

    # Configuració de disseny fosc premium
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17, 24, 39, 0.6)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#e2e8f0"),
        xaxis=dict(
            title=dict(text=t("currentAgeLabel", lang), font=dict(size=12, color="#94a3b8")),
            gridcolor="rgba(255, 255, 255, 0.06)",
            zerolinecolor="rgba(255, 255, 255, 0.1)",
            tickmode="linear",
            dtick=5,
        ),
        yaxis=dict(
            title=dict(text="Portfolio (€)" if lang == "en" else "Patrimoni (€)", font=dict(size=12, color="#94a3b8")),
            gridcolor="rgba(255, 255, 255, 0.06)",
            zerolinecolor="rgba(255, 255, 255, 0.1)",
            tickformat=",.0f",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11),
            bgcolor="rgba(15, 23, 42, 0.7)",
            bordercolor="rgba(255, 255, 255, 0.1)",
            borderwidth=1,
        ),
        margin=dict(l=40, r=20, t=40, b=40),
        hovermode="closest",
        height=450,
    )

    st.plotly_chart(fig, use_container_width=True)
