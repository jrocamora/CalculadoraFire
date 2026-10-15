"""
Selector d'escenaris macroeconòmics (Rendibilitat, inflació i estrès).
Port fidel de MacroScenarioSelector.tsx.
"""
from __future__ import annotations

import streamlit as st
from config.translations import Language, t
from models.types import MacroScenario


def render_macro_scenario_selector(
    scenario: MacroScenario,
    lang: Language,
) -> MacroScenario:
    """Renderitza el configurador d'escenaris macroeconòmics i rendibilitat real."""
    nominal_return = scenario.nominal_return
    inflation_rate = scenario.inflation_rate
    real_return = ((1.0 + nominal_return / 100.0) / (1.0 + inflation_rate / 100.0) - 1.0) * 100.0

    st.markdown(
        f"""
        <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 12px; margin-bottom: 14px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="
                    background: rgba(168, 85, 247, 0.12); border: 1px solid rgba(168, 85, 247, 0.25);
                    color: #a855f7; padding: 8px; border-radius: 12px; font-size: 1.1rem;
                ">📊</div>
                <div>
                    <h3 style="margin: 0; font-size: 1.05rem; font-weight: 800; color: #ffffff;">
                        {t('macroTitle', lang)}
                    </h3>
                    <p style="margin: 2px 0 0 0; font-size: 0.74rem; color: #94a3b8;">
                        {t('macroSubtitle', lang)}
                    </p>
                </div>
            </div>
            <div style="
                background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px; padding: 6px 12px; font-size: 0.75rem; color: #cbd5e1;
            ">
                <span>{t('realReturnLabel', lang)}</span>
                <strong style="color: {'#34d399' if real_return >= 4.5 else '#38bdf8' if real_return >= 2.5 else '#f59e0b'}; font-size: 0.95rem; margin-left: 6px;">
                    {real_return:.2f}%
                </strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    presets = [
        {
            "id": "base",
            "name": t("scenarioBaseName", lang),
            "desc": t("scenarioBaseDesc", lang),
            "nom": 7.0,
            "inf": 2.5,
            "stress": None,
        },
        {
            "id": "optimistic",
            "name": t("scenarioOptimisticName", lang),
            "desc": t("scenarioOptimisticDesc", lang),
            "nom": 9.0,
            "inf": 2.0,
            "stress": None,
        },
        {
            "id": "conservative",
            "name": t("scenarioConservativeName", lang),
            "desc": t("scenarioConservativeDesc", lang),
            "nom": 5.0,
            "inf": 3.5,
            "stress": None,
        },
        {
            "id": "stress_test",
            "name": t("scenarioStressName", lang),
            "desc": t("scenarioStressDesc", lang),
            "nom": 7.0,
            "inf": 2.5,
            "stress": 15.0,
        },
    ]

    cols = st.columns(4)
    active_scenario = scenario

    for i, p in enumerate(presets):
        with cols[i]:
            is_active = scenario.id == p["id"]
            if st.button(
                f"{'★ ' if is_active else ''}{p['name']}",
                key=f"macro_preset_{p['id']}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                active_scenario = MacroScenario(
                    id=p["id"],  # type: ignore
                    name=p["name"],
                    description=p["desc"],
                    nominal_return=p["nom"],
                    inflation_rate=p["inf"],
                    stress_drop_first_years=p["stress"],
                )
            st.caption(f"{p['nom']}% nom. / {p['inf']}% inf.")

    # Controls d'ajust fi (sliders)
    col_nom, col_inf = st.columns(2)
    with col_nom:
        new_nom = st.slider(
            t("nominalReturnLabel", lang) + " (%)",
            min_value=2.0,
            max_value=15.0,
            value=float(active_scenario.nominal_return),
            step=0.25,
            key="macro_nominal_slider",
        )
    with col_inf:
        new_inf = st.slider(
            t("inflationLabel", lang) + " (%)",
            min_value=0.5,
            max_value=8.0,
            value=float(active_scenario.inflation_rate),
            step=0.25,
            key="macro_inflation_slider",
        )

    if new_nom != active_scenario.nominal_return or new_inf != active_scenario.inflation_rate:
        active_scenario = MacroScenario(
            id="custom",
            name=t("scenarioCustomName", lang),
            description="",
            nominal_return=new_nom,
            inflation_rate=new_inf,
            stress_drop_first_years=active_scenario.stress_drop_first_years,
        )

    return active_scenario
