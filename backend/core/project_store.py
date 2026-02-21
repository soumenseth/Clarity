from __future__ import annotations

import json
import shutil
from pathlib import Path

from backend.models import ProjectMeta

_DATA_DIR = Path(__file__).resolve().parents[2] / "data"
_REGISTRY = _DATA_DIR / "projects.json"
_PROJECTS_DIR = _DATA_DIR / "projects"


def _ensure_dirs() -> None:
    _DATA_DIR.mkdir(exist_ok=True)
    _PROJECTS_DIR.mkdir(exist_ok=True)
    if not _REGISTRY.exists():
        _REGISTRY.write_text("[]", encoding="utf-8")


class ProjectStore:
    def __init__(self) -> None:
        _ensure_dirs()

    def _read_registry(self) -> list[dict]:
        return json.loads(_REGISTRY.read_text(encoding="utf-8"))

    def _write_registry(self, data: list[dict]) -> None:
        _REGISTRY.write_text(json.dumps(data, default=str, indent=2), encoding="utf-8")

    def _project_dir(self, project_id: str) -> Path:
        return _PROJECTS_DIR / project_id

    # ── Project CRUD ─────────────────────────────────────────

    def list_projects(self) -> list[ProjectMeta]:
        return [ProjectMeta(**entry) for entry in self._read_registry()]

    def create_project(self, name: str) -> ProjectMeta:
        meta = ProjectMeta(name=name)
        pdir = self._project_dir(meta.id)
        pdir.mkdir(parents=True, exist_ok=True)
        (pdir / "thoughts.json").write_text("[]", encoding="utf-8")
        (pdir / "graph.json").write_text("{}", encoding="utf-8")

        registry = self._read_registry()
        registry.append(meta.model_dump(mode="json"))
        self._write_registry(registry)
        return meta

    def delete_project(self, project_id: str) -> None:
        pdir = self._project_dir(project_id)
        if pdir.exists():
            shutil.rmtree(pdir)

        registry = [e for e in self._read_registry() if e["id"] != project_id]
        self._write_registry(registry)

    # ── Thoughts ─────────────────────────────────────────────

    def load_thoughts(self, project_id: str) -> list[dict]:
        path = self._project_dir(project_id) / "thoughts.json"
        if not path.exists():
            return []
        return json.loads(path.read_text(encoding="utf-8"))

    def save_thoughts(self, project_id: str, thoughts: list[dict]) -> None:
        path = self._project_dir(project_id) / "thoughts.json"
        path.write_text(json.dumps(thoughts, default=str, indent=2), encoding="utf-8")

    # ── Graph ────────────────────────────────────────────────

    def load_graph(self, project_id: str) -> dict:
        path = self._project_dir(project_id) / "graph.json"
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def save_graph(self, project_id: str, data: dict) -> None:
        path = self._project_dir(project_id) / "graph.json"
        path.write_text(json.dumps(data, default=str, indent=2), encoding="utf-8")
