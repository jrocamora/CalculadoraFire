"""
Widget keys with a reset generation ("nonce").

Every widget key is suffixed with the current generation. Bumping the generation
(reset to defaults, loading a plan from a file) makes Streamlit create brand-new
widgets that take their initial value from the model in session state, instead of
keeping whatever the previous widgets held.
"""
from __future__ import annotations

import streamlit as st


def k(name: str) -> str:
    """Returns the session-state key of widget `name` for the current generation."""
    return f"{name}__{st.session_state.get('ui_nonce', 0)}"


def reset_widgets() -> None:
    """Discards the state of every widget so they re-read their values from the model."""
    st.session_state.ui_nonce = st.session_state.get("ui_nonce", 0) + 1
