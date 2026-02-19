from __future__ import annotations

import streamlit as st

from frontend.config.theme import BG_PRIMARY, TEXT_PRIMARY


def render_header() -> None:
    st.markdown(
        f"""
        <div id="clarity-header">\U0001f52e Clarity</div>
        <style>
        #clarity-header {{
            position: sticky; top: 0; z-index: 99;
            padding: 0.6rem 0;
            font-size: 1.5rem; font-weight: 700;
            color: {TEXT_PRIMARY}; background: {BG_PRIMARY};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
