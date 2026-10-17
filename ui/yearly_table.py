"""
Taula de projecció any a any amb filtres i descàrrega CSV.
Port fidel de YearlyProjectionTable.tsx.
"""
from __future__ import annotations

import io
import pandas as pd
import streamlit as st
from config.translations import Language, t
from models.types import YearProjection


def render_yearly_table(
    projections: list[YearProjection],
    lang: Language,
):
    """Renderitza la taula detallada exercici a exercici amb filtres de fase i export CSV."""
    if not projections:
        return

    st.markdown(
        f"""
        <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #e2e8f0; padding-bottom: 12px; margin-bottom: 14px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="
                    background: #f1f5f9; border: 1px solid #cbd5e1;
                    color: #475569; padding: 8px; border-radius: 12px; font-size: 1.1rem;
                ">📋</div>
                <div>
                    <h3 style="margin: 0; font-size: 1.05rem; font-weight: 800; color: #0f172a;">
                        {t('tableTitle', lang)}
                    </h3>
                    <p style="margin: 2px 0 0 0; font-size: 0.74rem; color: #64748b;">
                        {t('tableSubtitle', lang)}
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_filter, col_csv = st.columns([3, 2])

    with col_filter:
        filter_choice = st.radio(
            "Filtre de fase",
            options=["all", "accumulation", "retirement"],
            format_func=lambda x: {
                "all": t("tableFilterAll", lang),
                "accumulation": t("tableFilterAccumulation", lang),
                "retirement": t("tableFilterRetirement", lang),
            }[x],
            horizontal=True,
            key="yearly_table_filter",
            label_visibility="collapsed",
        )

    # Filtrar projeccions
    filtered = [
        p
        for p in projections
        if filter_choice == "all"
        or (filter_choice == "accumulation" and not p.is_retired)
        or (filter_choice == "retirement" and p.is_retired)
    ]

    def format_num(val: float) -> str:
        r = round(val)
        if lang == "ca":
            return f"{r:,}".replace(",", ".")
        return f"{r:,}"

    # Crear DataFrame de Pandas
    rows = []
    age_suffix = "y" if lang == "en" else "a"

    for p in filtered:
        phase_str = (
            ("Retirement (FIRE)" if lang == "en" else "FIRE 🎉")
            if p.is_retired
            else ("Accumulation" if lang == "en" else "Estalvi 📈")
        )
        rows.append(
            {
                t("tableColYearAge", lang): f"{p.calendar_year} ({p.age}{age_suffix})",
                t("tableColPhase", lang): phase_str,
                t("tableColBridgeCapital", lang): format_num(p.bridge_portfolio),
                t("tableColPensionCapital", lang): format_num(p.pension_portfolio),
                t("tableColInitialCapital", lang): format_num(p.starting_portfolio),
                t("tableColContributionWithdrawal", lang): format_num(
                    p.contribution if not p.is_retired else -p.gross_withdrawal
                ),
                t("tableColTaxes", lang): format_num(p.tax_paid),
                t("tableColNetDisposable", lang): format_num(p.net_disposable_income),
                t("tableColEndingCapital", lang): format_num(p.ending_portfolio),
                t("tableColRealCapital", lang): format_num(p.ending_portfolio_real),
                t("tableColNotes", lang): p.tax_notes or "",
            }
        )

    df = pd.DataFrame(rows)

    # Exportador CSV
    csv_rows = []
    for p in projections:
        csv_rows.append(
            {
                "Year": p.calendar_year,
                "Age": p.age,
                "Phase": "Retirement" if p.is_retired else "Accumulation",
                "Bridge_Capital": round(p.bridge_portfolio),
                "Pension_Capital": round(p.pension_portfolio),
                "Starting_Capital": round(p.starting_portfolio),
                "Contribution": round(p.contribution),
                "Gross_Withdrawal": round(p.gross_withdrawal),
                "Taxes": round(p.tax_paid),
                "Net_Disposable": round(p.net_disposable_income),
                "Ending_Capital": round(p.ending_portfolio),
                "Real_Capital": round(p.ending_portfolio_real),
                "Notes": p.tax_notes or "",
            }
        )
    df_csv = pd.DataFrame(csv_rows)
    csv_buffer = io.StringIO()
    df_csv.to_csv(csv_buffer, index=False)

    with col_csv:
        st.download_button(
            label="⬇ " + t("tableExportCsv", lang),
            data=csv_buffer.getvalue(),
            file_name=f"fire_projection.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_csv_btn",
        )

    # Mostrar la taula paginada / interactiva de Streamlit
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=450,
    )
