"""Streamlit entry-point — wires together all UI components and services."""

from __future__ import annotations

from frontend.config.styles import apply_styles

# Styles must be applied before any st.* calls so the custom theme takes effect.
apply_styles()

import streamlit as st

from frontend.components.duplicates import render_duplicates
from frontend.components.graph_view import render_graph_view
from frontend.components.header import render_header
from frontend.components.project_picker import get_current_project, render_project_picker
from frontend.components.sidebar import render_sidebar
from frontend.services.state import init_state
from frontend.services.thought_processor import process_new_thoughts

init_state()
render_header()

project = get_current_project()

if project is None:
    render_project_picker()
    st.stop()

st.caption(f"Project: **{project.name}**")

if st.button("← Switch project", key="switch_project"):
    st.session_state.current_project = None
    st.session_state.graph_data = None
    st.session_state.thoughts = []
    st.session_state.pending_duplicates = []
    st.rerun()

sidebar = render_sidebar()

if sidebar.add_btn and sidebar.thought_input.strip():
    process_new_thoughts(sidebar.thought_input)

render_duplicates()
render_graph_view()
