from __future__ import annotations

from frontend.config.styles import apply_styles

apply_styles()

import streamlit as st

from frontend.components.duplicates import render_duplicates
from frontend.components.graph_view import render_graph_view
from frontend.components.header import render_header
from frontend.components.sidebar import render_sidebar
from frontend.services.state import init_state
from frontend.services.thought_processor import process_new_thoughts

init_state()
render_header()

sidebar = render_sidebar()

if sidebar.add_btn and sidebar.thought_input.strip():
    process_new_thoughts(sidebar.thought_input)

render_duplicates()
render_graph_view()
