from __future__ import annotations

import json

from openai import OpenAI

from backend.models import Cluster, Connection, DuplicateCheck
from backend.analysis.prompts import CLUSTER_THOUGHTS, DUPLICATE_CHECK, FIND_CONNECTIONS


class ThoughtAnalyzer:
    def __init__(self, client: OpenAI, model: str = "gpt-4o-mini") -> None:
        self._client = client
        self._model = model

    def _call(self, system: str, user: str) -> dict:
        resp = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        return json.loads(resp.choices[0].message.content)

    def check_duplicate(
        self,
        new_thought: str,
        existing_thoughts: list[str],
    ) -> DuplicateCheck:
        if not existing_thoughts:
            return DuplicateCheck(is_duplicate=False)

        user_msg = (
            f"New thought: \"{new_thought}\"\n\n"
            f"Existing thoughts:\n"
            + "\n".join(f"- \"{t}\"" for t in existing_thoughts)
        )
        data = self._call(DUPLICATE_CHECK, user_msg)
        return DuplicateCheck(**data)

    def find_connections(
        self,
        new_thought_id: str,
        new_thought_text: str,
        existing_thoughts: list[dict[str, str]],
    ) -> list[Connection]:
        """Find connections between a new thought and existing ones.

        existing_thoughts: list of {"id": ..., "text": ...}
        """
        if not existing_thoughts:
            return []

        existing_str = "\n".join(
            f"- [{t['id']}] \"{t['text']}\"" for t in existing_thoughts
        )
        user_msg = (
            f"New thought [{new_thought_id}]: \"{new_thought_text}\"\n\n"
            f"Existing thoughts:\n{existing_str}"
        )
        data = self._call(FIND_CONNECTIONS, user_msg)
        return [Connection(**c) for c in data.get("connections", [])]

    def cluster_thoughts(
        self,
        thoughts: list[dict[str, str]],
    ) -> list[Cluster]:
        """Cluster all thoughts.

        thoughts: list of {"id": ..., "text": ...}
        """
        if len(thoughts) < 2:
            return []

        thoughts_str = "\n".join(f"- [{t['id']}] \"{t['text']}\"" for t in thoughts)
        user_msg = f"Thoughts:\n{thoughts_str}"
        data = self._call(CLUSTER_THOUGHTS, user_msg)
        return [Cluster(**c) for c in data.get("clusters", [])]
