from __future__ import annotations

from backend.graph.graph_manager import GraphManager
from backend.models import Thought
from backend.analysis.thought_analyzer import ThoughtAnalyzer
from frontend.services.state import get_client, get_gm, save_gm


def add_thought_to_graph(text: str) -> None:
    """Create a thought, find connections, add to graph, re-cluster, and save."""
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
    save_gm(gm)


def recluster_and_save(gm: GraphManager) -> None:
    """Re-cluster thoughts in the given graph and save."""
    if gm.node_count >= 2:
        analyzer = ThoughtAnalyzer(get_client())
        clusters = analyzer.cluster_thoughts(gm.get_all_thoughts())
        gm.apply_clusters(clusters)
    save_gm(gm)
