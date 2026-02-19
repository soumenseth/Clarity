from __future__ import annotations

DUPLICATE_CHECK = (
    "You compare a new thought against a list of existing thoughts. "
    "Determine if the new thought is semantically equivalent to any existing thought "
    "(same core meaning, even if worded differently). "
    'Respond with JSON: {"is_duplicate": bool, "similar_to": str|null, "reason": str|null}. '
    "similar_to should be the text of the existing thought that is duplicated, or null."
)

FIND_CONNECTIONS = (
    "You are given a new thought and a list of existing thoughts (each with an id). "
    "Identify every meaningful relationship between the new thought and an existing thought. "
    "Use labels like: supports, contradicts, extends, is prerequisite of, "
    "is example of, generalizes, refines, is alternative to. "
    'Return JSON: {"connections": [{"source_id": str, "target_id": str, "relationship": str}]}. '
    "source_id is the new thought's id; target_id is the existing thought's id."
)

CLUSTER_THOUGHTS = (
    "You are given a list of thoughts (each with id and text). "
    "Group related thoughts into named clusters. A thought may belong to at most one cluster. "
    'Return JSON: {"clusters": [{"name": str, "thought_ids": [str]}]}.'
)
