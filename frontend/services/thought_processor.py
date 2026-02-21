"""Pipeline for processing raw thought input into graph nodes.

Each non-empty line goes through duplicate detection → connection discovery →
graph insertion.  Duplicates are parked in ``pending_duplicates`` for the user
to resolve via the duplicates panel.
"""

from __future__ import annotations

import streamlit as st

from backend.models import PendingDuplicate, Thought
from backend.analysis.thought_analyzer import ThoughtAnalyzer
from frontend.services.graph_ops import recluster_and_save
from frontend.services.state import get_client, get_gm, save_gm, save_thoughts


def process_new_thoughts(thought_input: str) -> None:
    """Process a newline-delimited string of thoughts submitted by the user.

    For each line the function:
    1. Checks for duplicates against existing thoughts.
    2. Finds AI-suggested connections to existing nodes.
    3. Adds the thought and its connections to the graph.

    After all lines are processed the graph is re-clustered, state is
    persisted, the input slots are reset, and a Streamlit rerun is triggered.

    On any AI or clustering failure the work done so far is saved and the
    function returns early so the user doesn't lose progress.
    """
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
            save_thoughts()
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
            save_thoughts()
            return

        gm.add_thought(thought)
        st.session_state.thoughts.append(thought.model_dump(mode="json"))
        for conn in connections:
            gm.add_connection(conn)

    try:
        progress.progress(0.9, text="Clustering...")
        recluster_and_save(gm)
    except Exception as exc:
        save_gm(gm)
        save_thoughts()
        st.sidebar.error(f"Clustering failed: {exc}")
        return

    save_thoughts()
    progress.progress(1.0, text="Done!")
    st.session_state.thought_slots = [""]
    st.rerun()
