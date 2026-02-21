"""Session-state management, graph persistence, and OpenAI client setup.

This module owns all reads/writes of ``st.session_state`` keys used by the
application and provides helper functions to load, cache, and persist the
:class:`GraphManager` and thought list via :class:`ProjectStore`.
"""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

from backend.core.project_store import ProjectStore
from backend.graph.graph_manager import GraphManager

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

_GM_CACHE_KEY = "_gm_cache"
_store = ProjectStore()


def _current_project_id() -> str | None:
    """Return the active project's id, or ``None`` if no project is selected."""
    proj = st.session_state.get("current_project")
    if proj is None:
        return None
    return proj["id"]


class _SessionDefaults(BaseModel):
    """Declares every session-state key and its initial value.

    Adding a new key to the app is a one-line field addition here —
    ``init_state`` picks it up automatically.
    """

    current_project: dict | None = None
    graph_data: dict | None = None
    thoughts: list[dict] = Field(default_factory=list)
    pending_duplicates: list = Field(default_factory=list)
    thought_slots: list[str] = Field(default_factory=lambda: [""])


def init_state() -> None:
    """Ensure every required session-state key exists with a sensible default.

    On the first run for a given project the graph and thought list are
    hydrated from disk.  The in-memory :class:`GraphManager` cache is
    always cleared so it is rebuilt from the latest ``graph_data`` dict.
    """
    for key, value in _SessionDefaults().model_dump().items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Always invalidate the cached GraphManager so it is lazily rebuilt
    # from the authoritative graph_data dict on the next get_gm() call.
    st.session_state.pop(_GM_CACHE_KEY, None)

    pid = _current_project_id()
    if pid and st.session_state.graph_data is None:
        graph_data = _store.load_graph(pid)
        if graph_data:
            st.session_state.graph_data = graph_data
        st.session_state.thoughts = _store.load_thoughts(pid)


def get_gm() -> GraphManager:
    """Return the current :class:`GraphManager`, creating one if needed.

    The manager is cached in session state to avoid repeated deserialisation
    within a single Streamlit script run.
    """
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
    """Persist the graph manager to session state and, if a project is active, to disk."""
    st.session_state.graph_data = gm.to_dict()
    st.session_state[_GM_CACHE_KEY] = gm

    pid = _current_project_id()
    if pid:
        _store.save_graph(pid, st.session_state.graph_data)


def save_thoughts() -> None:
    """Persist the thought list to disk for the active project (no-op without a project)."""
    pid = _current_project_id()
    if pid:
        _store.save_thoughts(pid, st.session_state.thoughts)


@st.cache_resource
def get_client() -> OpenAI:
    """Return a cached OpenAI client, halting the app if the API key is missing."""
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key or api_key == "your-api-key-here":
        st.error("Set OPENAI_API_KEY in the .env file to use Clarity.")
        st.stop()
    return OpenAI(api_key=api_key)
