"""
Selector d'escenaris macroeconòmics (Rendibilitat, inflació i estrès).
Port fidel de MacroScenarioSelector.tsx.
"""
from __future__ import annotations

import streamlit as st
from ui.keys import k
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
        <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #e2e8f0; padding-bottom: 12px; margin-bottom: 14px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="
                    background: #faf5ff; border: 1px solid #e9d5ff;
                    color: #7e22ce; padding: 8px; border-radius: 12px; font-size: 1.1rem;
                ">📊</div>
                <div>
                    <h3 style="margin: 0; font-size: 1.05rem; font-weight: 800; color: #0f172a;">
                        {t('macroTitle', lang)}
                    </h3>
                    <p style="margin: 2px 0 0 0; font-size: 0.74rem; color: #64748b;">
                        {t('macroSubtitle', lang)}
                    </p>
                </div>
            </div>
            <div style="
                background: #faf5ff; border: 1px solid #e9d5ff;
                border-radius: 10px; padding: 6px 12px; font-size: 0.75rem; color: #475569;
            ">
                <span>{t('realReturnLabel', lang)}</span>
                <strong style="color: {'#047857' if real_return >= 4.5 else '#0369a1' if real_return >= 2.5 else '#b45309'}; font-size: 0.95rem; margin-left: 6px;">
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

    def _apply_preset(p: dict):
        # Runs before the script reruns: stores the preset and moves both sliders to it.
        st.session_state.scenario = MacroScenario(
            id=p["id"],  # type: ignore
            name=p["name"],
            description=p["desc"],
            nominal_return=p["nom"],
            inflation_rate=p["inf"],
            stress_drop_first_years=p["stress"],
        )
        st.session_state[k("macro_nominal_slider")] = float(p["nom"])
        st.session_state[k("macro_inflation_slider")] = float(p["inf"])

    cols = st.columns(4)
    active_scenario = scenario

    for i, p in enumerate(presets):
        with cols[i]:
            is_active = scenario.id == p["id"]
            st.button(
                f"{'★ ' if is_active else ''}{p['name']}",
                key=k(f"macro_preset_{p['id']}"),
                width="stretch",
                type="primary" if is_active else "secondary",
                on_click=_apply_preset,
                args=(p,),
            )
            stress_txt = f" / -{p['stress']:.0f}% crash" if p["stress"] else ""
            st.caption(f"{p['nom']}% nom. / {p['inf']}% inf.{stress_txt}")

    # Controls d'ajust fi (sliders)
    # Seeded through session state because the preset buttons write to these sliders
    if k("macro_nominal_slider") not in st.session_state:
        st.session_state[k("macro_nominal_slider")] = min(15.0, max(2.0, float(scenario.nominal_return)))
    if k("macro_inflation_slider") not in st.session_state:
        st.session_state[k("macro_inflation_slider")] = min(8.0, max(0.5, float(scenario.inflation_rate)))
    col_nom, col_inf = st.columns(2)
    with col_nom:
        new_nom = st.slider(
            t("nominalReturnLabel", lang) + " (%)",
            min_value=2.0,
            max_value=15.0,
            step=0.25,
            key=k("macro_nominal_slider"),
        )
    with col_inf:
        new_inf = st.slider(
            t("inflationLabel", lang) + " (%)",
            min_value=0.5,
            max_value=8.0,
            step=0.25,
            key=k("macro_inflation_slider"),
        )

    shift = new_nom - 7.0
    st.caption(
        "Each asset grows at its own expected return (set in the portfolio section). "
        f"This scenario shifts every asset's return by {shift:+.2f} pp relative to the 7% base case."
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
