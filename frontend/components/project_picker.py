from __future__ import annotations

import streamlit as st

from backend.core.project_store import ProjectStore
from backend.models import ProjectMeta

_store = ProjectStore()


def render_project_picker() -> ProjectMeta | None:
    """Render the project management UI. Returns the selected project or None."""

    st.markdown("### Projects")

    # ── Create ────────────────────────────────────────────
    with st.form("create_project", clear_on_submit=True):
        name = st.text_input("New project name", placeholder="My project…")
        submitted = st.form_submit_button("Create Project", use_container_width=True)
        if submitted and name.strip():
            meta = _store.create_project(name.strip())
            st.session_state.current_project = meta.model_dump(mode="json")
            st.rerun()

    # ── Open / Delete existing ────────────────────────────
    projects = _store.list_projects()

    if not projects:
        st.info("No projects yet — create one above to get started.")
        return None

    st.markdown("#### Open an existing project")

    for proj in projects:
        col_name, col_open, col_del = st.columns([4, 1, 1])
        col_name.markdown(f"**{proj.name}**")

        if col_open.button("Open", key=f"open_{proj.id}"):
            st.session_state.current_project = proj.model_dump(mode="json")
            st.rerun()

        if col_del.button("🗑", key=f"del_{proj.id}"):
            st.session_state[f"confirm_del_{proj.id}"] = True

        if st.session_state.get(f"confirm_del_{proj.id}"):
            st.warning(f'Delete **{proj.name}**? This cannot be undone.')
            c1, c2 = st.columns(2)
            if c1.button("Yes, delete", key=f"yes_del_{proj.id}"):
                _store.delete_project(proj.id)
                if (
                    st.session_state.get("current_project", {}).get("id") == proj.id
                ):
                    st.session_state.current_project = None
                st.session_state.pop(f"confirm_del_{proj.id}", None)
                st.rerun()
            if c2.button("Cancel", key=f"cancel_del_{proj.id}"):
                st.session_state.pop(f"confirm_del_{proj.id}", None)
                st.rerun()

    return None


def get_current_project() -> ProjectMeta | None:
    raw = st.session_state.get("current_project")
    if raw is None:
        return None
    return ProjectMeta(**raw)
