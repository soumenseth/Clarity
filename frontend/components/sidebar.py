from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from frontend.services.graph_ops import recluster_and_save
from frontend.services.state import get_gm, save_gm


@dataclass
class SidebarResult:
    thought_input: str
    add_btn: bool


def render_sidebar() -> SidebarResult:
    with st.sidebar:
        st.subheader("Add Thoughts")
        thought_input = st.text_area(
            "Enter thoughts (one per line)",
            height=150,
            placeholder="Each line becomes a node...",
        )
        add_btn = st.button("Add to Network", type="primary", use_container_width=True)

        st.divider()
        st.subheader("Existing Thoughts")
        _render_thought_list()

    return SidebarResult(thought_input=thought_input, add_btn=add_btn)


def _render_thought_list() -> None:
    gm = get_gm()
    thoughts = gm.get_all_thoughts()

    if not thoughts:
        st.info("No thoughts yet. Add some above!")
        return

    for t in thoughts:
        col1, col2 = st.columns([5, 1])
        col1.markdown(
            f"**{t['text'][:50]}**" if len(t["text"]) > 50 else f"**{t['text']}**"
        )
        if col2.button("✕", key=f"del_{t['id']}"):
            gm.remove_thought(t["id"])
            try:
                recluster_and_save(gm)
            except Exception as exc:
                save_gm(gm)
                st.error(f"Re-clustering failed: {exc}")
            st.rerun()
