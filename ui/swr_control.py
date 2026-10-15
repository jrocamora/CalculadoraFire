"""
Control de la Taxa de Retirada Segura (SWR).
Mostra les explicacions completes de cada regla sense truncar.
"""
from __future__ import annotations

import streamlit as st
from config.translations import Language, t


def render_swr_control(
    current_swr: float,
    lang: Language,
) -> float:
    """Renderitza el selector de Safe Withdrawal Rate amb presets i explicació completa."""
    current_multiplier = 100.0 / max(0.01, current_swr)

    st.markdown(
        f"""
        <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 12px; margin-bottom: 14px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="
                    background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.25);
                    color: #f59e0b; padding: 8px; border-radius: 12px; font-size: 1.1rem;
                ">🛡️</div>
                <div>
                    <h3 style="margin: 0; font-size: 1.05rem; font-weight: 800; color: #ffffff;">
                        {t('swrTitle', lang)}
                    </h3>
                    <p style="margin: 2px 0 0 0; font-size: 0.74rem; color: #94a3b8;">
                        {t('swrSubtitle', lang)}
                    </p>
                </div>
            </div>
            <div style="text-align: right;">
                <span style="font-size: 1.5rem; font-weight: 900; color: #f59e0b; letter-spacing: -0.02em;">
                    {current_swr:.1f}%
                </span>
                <span style="display: block; font-size: 0.72rem; color: #94a3b8; font-family: monospace;">
                    {current_multiplier:.1f}x {t('swrAnnualExpenses', lang)}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    new_swr = st.slider(
        "SWR (%)",
        min_value=2.5,
        max_value=5.5,
        value=float(current_swr),
        step=0.1,
        key="swr_slider",
        label_visibility="collapsed",
    )

    # 4 Presets amb les seves explicacions completes
    presets = [
        {
            "rate": 3.0,
            "badge": t("swrUltraSafe", lang),
            "desc": t("swrUltraSafeDesc", lang),
            "mul": "33.3x",
        },
        {
            "rate": 3.5,
            "badge": t("swrEuropeanFire", lang),
            "desc": t("swrEuropeanFireDesc", lang),
            "mul": "28.6x",
        },
        {
            "rate": 4.0,
            "badge": t("swrTrinityRule", lang),
            "desc": t("swrTrinityRuleDesc", lang),
            "mul": "25.0x",
        },
        {
            "rate": 4.5,
            "badge": t("swrLeanDynamic", lang),
            "desc": t("swrLeanDynamicDesc", lang),
            "mul": "22.2x",
        },
    ]

    cols = st.columns(4)
    active_preset_desc = ""
    active_preset_badge = ""

    for i, p in enumerate(presets):
        is_active = abs(new_swr - p["rate"]) < 0.05
        if is_active:
            active_preset_desc = p["desc"]
            active_preset_badge = p["badge"]

        with cols[i]:
            btn_label = f"{'★ ' if is_active else ''}{p['rate']:.1f}% ({p['mul']})"
            if st.button(
                btn_label,
                key=f"swr_preset_{p['rate']}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                new_swr = p["rate"]
                active_preset_desc = p["desc"]
                active_preset_badge = p["badge"]

    # Mostrar l'explicació completa sense cap truncament
    if not active_preset_desc:
        # Si està en un valor entremig (p.ex. 3.7%)
        active_preset_badge = f"{new_swr:.1f}% Custom Rate"
        active_preset_desc = (
            f"Custom withdrawal rate requiring {current_multiplier:.1f}x your annual living expenses. "
            f"Balances portfolio longevity against near-term purchasing power."
        )

    st.markdown(
        f"""
        <div style="
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(245, 158, 11, 0.25);
            border-radius: 12px;
            padding: 12px 14px;
            margin-top: 10px;
        ">
            <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
                <span style="font-size: 0.76rem; font-weight: 800; color: #fbbf24;">
                    🛡️ {active_preset_badge}
                </span>
                <span style="font-size: 0.72rem; color: #94a3b8; font-family: monospace;">
                    ({current_multiplier:.1f}x expenses)
                </span>
            </div>
            <div style="font-size: 0.76rem; color: #e2e8f0; line-height: 1.5;">
                {active_preset_desc}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Detall de tots els presets desglossats per a referència completa
    with st.expander("ℹ️ All SWR Benchmarks Explained", expanded=False):
        for p in presets:
            st.markdown(
                f"**{p['rate']:.1f}% — {p['badge']} ({p['mul']})**  \n"
                f"<span style='color: #cbd5e1; font-size: 0.78rem;'>{p['desc']}</span>",
                unsafe_allow_html=True,
            )

    return new_swr
