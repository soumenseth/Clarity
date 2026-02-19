from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from backend.graph.graph_manager import GraphManager

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

_GM_CACHE_KEY = "_gm_cache"


def init_state() -> None:
    if "graph_data" not in st.session_state:
        st.session_state.graph_data = None
    if "pending_duplicates" not in st.session_state:
        st.session_state.pending_duplicates = []
    st.session_state.pop(_GM_CACHE_KEY, None)


def get_gm() -> GraphManager:
    if st.session_state.graph_data is None:
        gm = GraphManager()
        save_gm(gm)
        return gm
    if _GM_CACHE_KEY in st.session_state:
        return st.session_state[_GM_CACHE_KEY]
    gm = GraphManager.from_dict(st.session_state.graph_data)
    st.session_state[_GM_CACHE_KEY] = gm
    return gm


def save_gm(gm: GraphManager) -> None:
    st.session_state.graph_data = gm.to_dict()
    st.session_state[_GM_CACHE_KEY] = gm


@st.cache_resource
def get_client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key or api_key == "your-api-key-here":
        st.error("Set OPENAI_API_KEY in the .env file to use Clarity.")
        st.stop()
    return OpenAI(api_key=api_key)
