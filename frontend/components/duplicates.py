"""Duplicates panel — lets the user resolve thoughts flagged as potential duplicates.

Each pending duplicate can be added anyway, skipped, or merged into the
existing thought it was matched against.
"""

from __future__ import annotations

import streamlit as st

from backend.models import PendingDuplicate
from frontend.services.graph_ops import add_thought_to_graph
from frontend.services.state import get_gm, save_gm, save_thoughts


def render_duplicates() -> None:
    """Display an expandable card for every unresolved duplicate.

    Each card offers three actions:

    * **Add Anyway** — insert the thought as a new node.
    * **Skip** — silently discard it.
    * **Merge** — append its text to the existing similar thought.
    """
    pending: list[PendingDuplicate] = st.session_state.pending_duplicates
    if not pending:
        return

    st.warning(f"**{len(pending)} potential duplicate(s) detected**")

    for i, dup in enumerate(pending):
        with st.expander(f'Duplicate: "{dup.text[:60]}"', expanded=True):
            st.write(f'**Similar to:** "{dup.similar_to}"')
            if dup.reason:
                st.write(f"**Reason:** {dup.reason}")

            c1, c2, c3 = st.columns(3)

            if c1.button("Add Anyway", key=f"dup_add_{i}"):
                try:
                    add_thought_to_graph(dup.text)
                except Exception as exc:
                    st.error(f"AI call failed: {exc}")
                st.session_state.pending_duplicates.pop(i)
                st.rerun()

            if c2.button("Skip", key=f"dup_skip_{i}"):
                st.session_state.pending_duplicates.pop(i)
                st.rerun()

            if c3.button("Merge", key=f"dup_merge_{i}"):
                _merge_into_existing(dup)
                st.session_state.pending_duplicates.pop(i)
                st.rerun()


def _merge_into_existing(dup: PendingDuplicate) -> None:
    """Append the duplicate's text to the existing similar thought.

    Updates both the networkx graph node and the JSON-serialisable
    ``st.session_state.thoughts`` list so the two stay in sync.
    """
    if not dup.similar_to:
        return
    gm = get_gm()
    for nid, data in gm.graph.nodes(data=True):
        if data.get("text") == dup.similar_to:
            merged = f"{data['text']} — {dup.text}"
            gm.graph.nodes[nid]["text"] = merged
            for th in st.session_state.thoughts:
                if th["id"] == nid:
                    th["text"] = merged
                    break
            save_gm(gm)
            save_thoughts()
            return
