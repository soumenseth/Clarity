"""High-level graph operations used by multiple UI components.

These helpers combine AI analysis with graph mutation and persistence so that
callers (sidebar, duplicates panel, thought processor) don't repeat the same
multi-step sequences.
"""

from __future__ import annotations

import streamlit as st

from backend.graph.graph_manager import GraphManager
from backend.models import Thought
from backend.analysis.thought_analyzer import ThoughtAnalyzer
from frontend.services.state import get_client, get_gm, save_gm, save_thoughts


def add_thought_to_graph(text: str) -> None:
    """Create a single thought node, wire it into the graph, and persist.

    Used by the duplicates panel's *Add Anyway* action where each thought is
    processed individually (as opposed to the batch flow in
    ``process_new_thoughts``).  Clustering is only attempted when the graph
    has at least two nodes.
    """
    analyzer = ThoughtAnalyzer(get_client())
    gm = get_gm()
    thought = Thought(text=text)
    connections = analyzer.find_connections(thought.id, thought.text, gm.get_all_thoughts())
    gm.add_thought(thought)
    for conn in connections:
        gm.add_connection(conn)
    if gm.node_count >= 2:
        clusters = analyzer.cluster_thoughts(gm.get_all_thoughts())
        gm.apply_clusters(clusters)
    st.session_state.thoughts.append(thought.model_dump(mode="json"))
    save_gm(gm)
    save_thoughts()


def recluster_and_save(gm: GraphManager) -> None:
    """Re-cluster all thoughts in *gm* via AI and persist the result.

    Skipped when fewer than two nodes exist (clustering needs at least a pair).
    """
    if gm.node_count >= 2:
        analyzer = ThoughtAnalyzer(get_client())
        clusters = analyzer.cluster_thoughts(gm.get_all_thoughts())
        gm.apply_clusters(clusters)
    save_gm(gm)
