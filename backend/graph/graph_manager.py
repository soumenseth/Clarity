from __future__ import annotations

import networkx as nx

from backend.models import Cluster, Connection, Thought


class GraphManager:
    def __init__(self) -> None:
        self._g = nx.Graph()

    def add_thought(self, thought: Thought) -> None:
        self._g.add_node(
            thought.id,
            text=thought.text,
            timestamp=thought.timestamp.isoformat(),
            cluster=thought.cluster,
        )

    def add_connection(self, conn: Connection) -> None:
        self._g.add_edge(
            conn.source_id,
            conn.target_id,
            relationship=conn.relationship,
        )

    def apply_clusters(self, clusters: list[Cluster]) -> None:
        for node in self._g.nodes:
            self._g.nodes[node]["cluster"] = None
        for cluster in clusters:
            for tid in cluster.thought_ids:
                if tid in self._g.nodes:
                    self._g.nodes[tid]["cluster"] = cluster.name

    def get_all_thoughts(self) -> list[dict[str, str]]:
        return [
            {"id": nid, "text": data["text"]}
            for nid, data in self._g.nodes(data=True)
        ]

    def get_all_thought_texts(self) -> list[str]:
        return [data["text"] for _, data in self._g.nodes(data=True)]

    def remove_thought(self, thought_id: str) -> None:
        if thought_id in self._g:
            self._g.remove_node(thought_id)

    @property
    def graph(self) -> nx.Graph:
        return self._g

    @property
    def node_count(self) -> int:
        return self._g.number_of_nodes()

    def to_dict(self) -> dict:
        return {
            "nodes": [
                {"id": nid, **data}
                for nid, data in self._g.nodes(data=True)
            ],
            "edges": [
                {"source": u, "target": v, **data}
                for u, v, data in self._g.edges(data=True)
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> GraphManager:
        gm = cls()
        for node in data.get("nodes", []):
            node = {**node}
            nid = node.pop("id")
            gm._g.add_node(nid, **node)
        for edge in data.get("edges", []):
            edge = {**edge}
            src = edge.pop("source")
            tgt = edge.pop("target")
            gm._g.add_edge(src, tgt, **edge)
        return gm
