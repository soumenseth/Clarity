from __future__ import annotations

from pyvis.network import Network

from backend.graph.graph_manager import GraphManager
from frontend.config.theme import (
    BG_PRIMARY,
    CLUSTER_COLORS,
    DEFAULT_NODE_COLOR,
    EDGE_COLOR,
    TEXT_MUTED,
    TEXT_PRIMARY,
)


def render_graph(gm: GraphManager, height: str = "600px") -> str:
    """Render the graph as an interactive HTML string."""
    net = Network(
        height=height,
        width="100%",
        bgcolor=BG_PRIMARY,
        font_color=TEXT_PRIMARY,
        directed=False,
    )
    net.barnes_hut(
        gravity=-3000,
        central_gravity=0.3,
        spring_length=150,
        spring_strength=0.05,
    )

    g = gm.graph
    cluster_names: list[str] = []
    for _, data in g.nodes(data=True):
        cname = data.get("cluster")
        if cname and cname not in cluster_names:
            cluster_names.append(cname)

    color_map: dict[str | None, str] = {
        name: CLUSTER_COLORS[i % len(CLUSTER_COLORS)]
        for i, name in enumerate(cluster_names)
    }

    for nid, data in g.nodes(data=True):
        cluster = data.get("cluster")
        color = color_map.get(cluster, DEFAULT_NODE_COLOR)
        label = data.get("text", nid)
        display_label = label if len(label) <= 40 else label[:37] + "..."
        net.add_node(
            nid,
            label=display_label,
            title=f"{label}\n\nCluster: {cluster or 'None'}",
            color=color,
            size=25,
            font={"size": 14, "color": TEXT_PRIMARY},
            borderWidth=2,
            borderWidthSelected=4,
        )

    for u, v, data in g.edges(data=True):
        rel = data.get("relationship", "")
        net.add_edge(
            u,
            v,
            title=rel,
            label=rel,
            color={"color": EDGE_COLOR, "highlight": TEXT_PRIMARY},
            font={"size": 10, "color": TEXT_MUTED, "strokeWidth": 0},
            width=2,
        )

    return net.generate_html()
