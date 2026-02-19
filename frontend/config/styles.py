from __future__ import annotations

import streamlit as st

from frontend.config.theme import BG_PRIMARY, BG_SIDEBAR, BORDER, TEXT_PRIMARY


def apply_styles() -> None:
    st.set_page_config(page_title="Clarity", page_icon="🔮", layout="wide")
    st.markdown(
        f"""
        <style>
        [data-testid="stSidebar"] {{background-color: {BG_SIDEBAR};}}
        .stApp {{background-color: {BG_PRIMARY}; color: {TEXT_PRIMARY};}}
        h1, h2, h3 {{color: {TEXT_PRIMARY} !important;}}
        .stTextArea textarea {{background-color: {BG_SIDEBAR}; color: {TEXT_PRIMARY}; border-color: {BORDER};}}
        .stTextInput input {{background-color: {BG_SIDEBAR}; color: {TEXT_PRIMARY}; border-color: {BORDER};}}
        </style>
        """,
        unsafe_allow_html=True,
    )
