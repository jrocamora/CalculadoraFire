"""
Component de capçalera i estils CSS globals per a la Calculadora FIRE Irlanda.
"""
from __future__ import annotations

import streamlit as st
from config.translations import Language, t
from models.types import CountryCode


def inject_custom_css():
    """Injecta estils CSS moderns, fons fosc premium, glassmorphism i tipografia."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header[data-testid="stHeader"] {background: transparent;}

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(17, 24, 39, 0.75) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 16px !important;
            backdrop-filter: blur(12px) !important;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3) !important;
            margin-bottom: 16px !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            padding: 14px 18px !important;
        }

        .metric-card-fire {
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.12) 0%, rgba(234, 88, 12, 0.08) 50%, rgba(15, 23, 42, 0.9) 100%);
            border: 1px solid rgba(245, 158, 11, 0.3);
            border-radius: 18px;
            padding: 20px;
            position: relative;
            box-shadow: 0 12px 30px -8px rgba(245, 158, 11, 0.15);
        }

        .metric-card-time {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(20, 184, 166, 0.08) 50%, rgba(15, 23, 42, 0.9) 100%);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 18px;
            padding: 20px;
            position: relative;
            box-shadow: 0 12px 30px -8px rgba(16, 185, 129, 0.15);
        }

        .metric-card-income {
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.12) 0%, rgba(59, 130, 246, 0.08) 50%, rgba(15, 23, 42, 0.9) 100%);
            border: 1px solid rgba(6, 182, 212, 0.3);
            border-radius: 18px;
            padding: 20px;
            position: relative;
            box-shadow: 0 12px 30px -8px rgba(6, 182, 212, 0.15);
        }

        .metric-card-tax {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(14, 165, 233, 0.08) 50%, rgba(15, 23, 42, 0.9) 100%);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 18px;
            padding: 20px;
            position: relative;
            box-shadow: 0 12px 30px -8px rgba(16, 185, 129, 0.15);
        }

        .metric-title {
            font-size: 0.72rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 6px;
        }

        .metric-value {
            font-size: 1.85rem;
            font-weight: 900;
            color: #ffffff;
            letter-spacing: -0.03em;
            line-height: 1.15;
        }

        .metric-subtitle {
            font-size: 0.75rem;
            color: #cbd5e1;
            margin-top: 8px;
            font-weight: 500;
        }

        .metric-footer {
            font-size: 0.70rem;
            color: #94a3b8;
            margin-top: 10px;
            padding-top: 8px;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(
    current_country: CountryCode,
    lang: Language,
    on_lang_change,
    on_reset_defaults,
):
    """Renderitza la barra de navegació superior adaptada a Irlanda."""
    inject_custom_css()

    col_title, col_badge, col_lang, col_reset = st.columns([5.5, 2.5, 1.8, 1.2])

    with col_title:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                <div style="
                    background: linear-gradient(135deg, #10b981, #059669, #0284c7);
                    width: 44px; height: 44px; border-radius: 12px;
                    display: flex; align-items: center; justify-content: center;
                    font-size: 22px; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35);
                ">🇮🇪</div>
                <div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1.35rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
                            {t('appName', lang)}
                        </span>
                        <span style="
                            background: linear-gradient(90deg, #34d399, #10b981);
                            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                            font-size: 1.3rem; font-weight: 900;
                        ">{t('appBadge', lang)}</span>
                        <span style="
                            font-size: 0.68rem; font-weight: 700; padding: 2px 7px; border-radius: 9999px;
                            background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3);
                        ">Budget 2027</span>
                    </div>
                    <div style="font-size: 0.76rem; color: #94a3b8; font-weight: 500;">
                        {t('appSubtitle', lang)}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_badge:
        st.markdown(
            f"""
            <div style="
                background: rgba(16, 185, 129, 0.1);
                border: 1px solid rgba(16, 185, 129, 0.3);
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 0.75rem;
                font-weight: 600;
                color: #34d399;
                display: flex; align-items: center; gap: 6px;
                margin-top: 6px;
            ">
                <span>🇮🇪</span>
                <span>Jurisdiction: <strong>Ireland (Revenue)</strong></span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_lang:
        selected_lang = st.selectbox(
            "Language",
            options=["en", "ca"],
            format_func=lambda x: "🇬🇧 English" if x == "en" else "🏴󠁥󠁳󠁣󠁴󠁿 Català",
            index=0 if lang == "en" else 1,
            key="header_lang_select",
            label_visibility="collapsed",
        )
        if selected_lang != lang:
            on_lang_change(selected_lang)

    with col_reset:
        if st.button("↺ " + t("resetValues", lang), key="reset_button_header", use_container_width=True):
            on_reset_defaults()
