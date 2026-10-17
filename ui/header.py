"""
Header component and global light-theme CSS styles for FIRE Calculator Ireland.
"""
from __future__ import annotations

import streamlit as st
from config.translations import Language, t
from models.types import CountryCode


def inject_custom_css():
    """Injects modern, premium light-theme CSS styling, crisp borders, and clean typography."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #0f172a;
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header[data-testid="stHeader"] {background: transparent;}

        /* Modern light-mode card containers */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 16px !important;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05) !important;
            margin-bottom: 16px !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            padding: 16px 20px !important;
        }

        /* Metric Cards: Light Theme Gradients */
        .metric-card-fire {
            background: linear-gradient(135deg, #fffdfa 0%, #fffbeb 50%, #fef3c7 100%);
            border: 1px solid #fde68a;
            border-radius: 16px;
            padding: 18px 20px;
            position: relative;
            box-shadow: 0 4px 6px -1px rgba(245, 158, 11, 0.08);
        }

        .metric-card-time {
            background: linear-gradient(135deg, #fafffc 0%, #ecfdf5 50%, #d1fae5 100%);
            border: 1px solid #a7f3d0;
            border-radius: 16px;
            padding: 18px 20px;
            position: relative;
            box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.08);
        }

        .metric-card-income {
            background: linear-gradient(135deg, #f9fcff 0%, #f0f9ff 50%, #e0f2fe 100%);
            border: 1px solid #bae6fd;
            border-radius: 16px;
            padding: 18px 20px;
            position: relative;
            box-shadow: 0 4px 6px -1px rgba(6, 182, 212, 0.08);
        }

        .metric-card-tax {
            background: linear-gradient(135deg, #fdfaff 0%, #faf5ff 50%, #f3e8ff 100%);
            border: 1px solid #e9d5ff;
            border-radius: 16px;
            padding: 18px 20px;
            position: relative;
            box-shadow: 0 4px 6px -1px rgba(168, 85, 247, 0.08);
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
            color: #0f172a;
            letter-spacing: -0.03em;
            line-height: 1.15;
        }

        .metric-subtitle {
            font-size: 0.75rem;
            color: #475569;
            margin-top: 8px;
            font-weight: 500;
        }

        .metric-footer {
            font-size: 0.70rem;
            color: #64748b;
            margin-top: 10px;
            padding-top: 8px;
            border-top: 1px solid rgba(0, 0, 0, 0.06);
        }

        /* Streamlit Tabs styling for light mode */
        button[data-baseweb="tab"] {
            font-weight: 600 !important;
            font-size: 0.90rem !important;
            color: #475569 !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #059669 !important;
            border-bottom-color: #059669 !important;
            font-weight: 700 !important;
        }

        /* Streamlit radio pills / buttons */
        div[role="radiogroup"] {
            gap: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(
    current_country: CountryCode,
    lang: Language = "en",
    on_reset_defaults=None,
):
    """Renders the top navigation bar with Ireland branding, light theme styling, and privacy guarantee."""
    inject_custom_css()

    col_title, col_privacy, col_reset = st.columns([6.2, 4.0, 1.8], gap="small")

    with col_title:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 4px;">
                <div style="
                    background: linear-gradient(135deg, #10b981, #059669, #0284c7);
                    width: 44px; height: 44px; border-radius: 12px;
                    display: flex; align-items: center; justify-content: center;
                    font-size: 22px; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
                ">🇮🇪</div>
                <div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1.35rem; font-weight: 800; color: #0f172a; letter-spacing: -0.02em;">
                            {t('appName', lang)}
                        </span>
                        <span style="
                            background: linear-gradient(90deg, #059669, #0284c7);
                            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                            font-size: 1.3rem; font-weight: 900;
                        ">{t('appBadge', lang)}</span>
                        <span style="
                            font-size: 0.68rem; font-weight: 700; padding: 2px 8px; border-radius: 9999px;
                            background: #ecfdf5; color: #059669; border: 1px solid #a7f3d0;
                        ">Budget 2027</span>
                    </div>
                    <div style="font-size: 0.76rem; color: #64748b; font-weight: 500;">
                        {t('appSubtitle', lang)}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_privacy:
        st.markdown(
            f"""
            <div style="
                background: #f0fdf4;
                border: 1px solid #bbf7d0;
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 0.74rem;
                display: flex; align-items: center; gap: 8px;
                margin-top: 4px;
            ">
                <span style="font-size: 1rem;">🔒</span>
                <div>
                    <div style="font-weight: 700; color: #166534;">
                        100% Client-Side Privacy
                    </div>
                    <div style="font-size: 0.68rem; color: #15803d;">
                        All calculations run locally • Zero data sent to any server
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_reset:
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        if st.button("↺ " + t("resetValues", lang), key="reset_button_header", use_container_width=True):
            if on_reset_defaults:
                on_reset_defaults()
