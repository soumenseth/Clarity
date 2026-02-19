from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

from backend.graph.graph_manager import GraphManager
from frontend.services.state import get_gm
from frontend.services.visualizer import render_graph


def render_graph_view() -> None:
    gm = get_gm()

    if gm.node_count == 0:
        st.info("Add thoughts from the sidebar to build your network.")
        return

    html = render_graph(gm)
    components.html(html, height=620, scrolling=False)
    _render_cluster_legend(gm)


def _render_cluster_legend(gm: GraphManager) -> None:
    cluster_map: dict[str, list[str]] = {}
    for t in gm.get_all_thoughts():
        node_data = gm.graph.nodes[t["id"]]
        cname = node_data.get("cluster")
        if cname:
            cluster_map.setdefault(cname, []).append(t["text"])

    if not cluster_map:
        return

    st.subheader("Clusters")
    cols = st.columns(min(len(cluster_map), 3))
    for idx, (name, members) in enumerate(cluster_map.items()):
        with cols[idx % len(cols)]:
            st.markdown(f"**{name}**")
            for m in members:
                st.markdown(f"- {m[:60]}")
