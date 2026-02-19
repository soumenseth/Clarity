from __future__ import annotations

import streamlit as st

from backend.models import PendingDuplicate, Thought
from backend.analysis.thought_analyzer import ThoughtAnalyzer
from frontend.services.graph_ops import recluster_and_save
from frontend.services.state import get_client, get_gm, save_gm


def process_new_thoughts(thought_input: str) -> None:
    analyzer = ThoughtAnalyzer(get_client())
    gm = get_gm()
    lines = [l.strip() for l in thought_input.strip().splitlines() if l.strip()]

    progress = st.sidebar.progress(0, text="Processing thoughts...")
    for idx, line in enumerate(lines):
        progress.progress(idx / len(lines), text=f"Checking: {line[:30]}...")

        try:
            dup = analyzer.check_duplicate(line, gm.get_all_thought_texts())
        except Exception as exc:
            st.sidebar.error(f"AI call failed: {exc}")
            save_gm(gm)
            return

        if dup.is_duplicate:
            st.session_state.pending_duplicates.append(
                PendingDuplicate(text=line, similar_to=dup.similar_to, reason=dup.reason)
            )
            continue

        try:
            thought = Thought(text=line)
            connections = analyzer.find_connections(
                thought.id, thought.text, gm.get_all_thoughts()
            )
        except Exception as exc:
            st.sidebar.error(f"AI call failed: {exc}")
            save_gm(gm)
            return

        gm.add_thought(thought)
        for conn in connections:
            gm.add_connection(conn)

    try:
        progress.progress(0.9, text="Clustering...")
        recluster_and_save(gm)
    except Exception as exc:
        save_gm(gm)
        st.sidebar.error(f"Clustering failed: {exc}")
        return

    progress.progress(1.0, text="Done!")
    st.rerun()
