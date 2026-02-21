"""Sidebar component: dynamic thought-input slots and the existing-thought list."""

from __future__ import annotations

import streamlit as st
from pydantic import BaseModel

from frontend.services.graph_ops import recluster_and_save
from frontend.services.state import get_gm, save_gm, save_thoughts


class SidebarResult(BaseModel):
    """Values returned by the sidebar to the main app on each Streamlit run.

    Attributes:
        thought_input: Newline-joined non-empty slot values, matching the
            contract expected by ``process_new_thoughts``.
        add_btn: Whether the *Add to Network* button was clicked this run.
    """

    thought_input: str
    add_btn: bool


def render_sidebar() -> SidebarResult:
    """Draw the sidebar and return the collected user input.

    The sidebar contains:
    * A dynamic list of ``st.text_input`` fields backed by
      ``st.session_state.thought_slots``.
    * An *Add to Network* submit button.
    * A scrollable list of existing thoughts with per-item delete buttons.
    """
    with st.sidebar:
        st.subheader("Add Thoughts")
        thought_input = _render_thought_slots()
        add_btn = st.button("Add to Network", type="primary", use_container_width=True)

        st.divider()
        st.subheader("Existing Thoughts")
        _render_thought_list()

    return SidebarResult(thought_input=thought_input, add_btn=add_btn)


# ---------------------------------------------------------------------------
# Thought-slot input fields
# ---------------------------------------------------------------------------


def _render_thought_slots() -> str:
    """Render the dynamic input slots and return the joined non-empty values.

    Slot removal is deferred until after the full loop so the list is never
    mutated mid-iteration.
    """
    slots: list[str] = st.session_state.thought_slots
    show_remove = len(slots) > 1
    slot_to_remove = _render_slot_list(slots, show_remove)

    if slot_to_remove is not None:
        slots.pop(slot_to_remove)
        st.rerun()

    if st.button("＋ Add another thought", use_container_width=True):
        slots.append("")
        st.rerun()

    return "\n".join(v for v in slots if v.strip())


def _render_slot_list(slots: list[str], show_remove: bool) -> int | None:
    """Render each slot as a text input (with optional remove button).

    Returns the index of the slot the user wants to remove, or ``None``.
    """
    slot_to_remove: int | None = None
    for i, slot_value in enumerate(slots):
        if i > 0:
            st.divider()
        slot_to_remove = _render_single_slot(i, slot_value, slots, show_remove) or slot_to_remove
    return slot_to_remove


def _render_single_slot(
    index: int,
    value: str,
    slots: list[str],
    show_remove: bool,
) -> int | None:
    """Render one text-input slot and return its index if remove was clicked."""
    if show_remove:
        col_input, col_btn = st.columns([5, 1])
    else:
        col_input, col_btn = st.container(), None

    with col_input:
        slots[index] = st.text_input(
            f"Thought {index + 1}",
            value=value,
            key=f"thought_slot_{index}",
            placeholder="Enter a thought...",
            label_visibility="collapsed",
        )

    if col_btn is not None:
        with col_btn:
            if st.button("✕", key=f"remove_slot_{index}"):
                return index
    return None


# ---------------------------------------------------------------------------
# Existing-thought list
# ---------------------------------------------------------------------------


def _render_thought_list() -> None:
    """Show every thought in the graph with a delete button beside it."""
    gm = get_gm()
    thoughts = gm.get_all_thoughts()

    if not thoughts:
        st.info("No thoughts yet. Add some above!")
        return

    for t in thoughts:
        col_text, col_del = st.columns([5, 1])
        label = _truncate(t["text"], 50)
        col_text.markdown(f"**{label}**")
        if col_del.button("✕", key=f"del_{t['id']}"):
            _delete_thought(gm, t["id"])


def _delete_thought(gm, thought_id: str) -> None:
    """Remove a thought from the graph and session state, then re-cluster.

    Persists changes and triggers a Streamlit rerun.  If re-clustering fails
    the graph is still saved so the deletion isn't lost.
    """
    gm.remove_thought(thought_id)
    st.session_state.thoughts = [
        th for th in st.session_state.thoughts if th["id"] != thought_id
    ]
    try:
        recluster_and_save(gm)
    except Exception as exc:
        save_gm(gm)
        st.error(f"Re-clustering failed: {exc}")
    save_thoughts()
    st.rerun()


def _truncate(text: str, limit: int) -> str:
    """Return *text* truncated to *limit* characters with an ellipsis if needed."""
    return f"{text[:limit]}…" if len(text) > limit else text
