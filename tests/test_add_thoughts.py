"""Unit tests for the add-thought-and-submit flow."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from backend.graph.graph_manager import GraphManager
from backend.models import Connection, DuplicateCheck, Thought


class FakeSessionState(dict):
    """Minimal dict subclass that supports attribute access like st.session_state."""

    def __getattr__(self, key: str):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key: str, value):
        self[key] = value

    def __delattr__(self, key: str):
        del self[key]


def _fresh_session_state(**overrides) -> FakeSessionState:
    state = FakeSessionState(
        current_project=None,
        graph_data=None,
        thoughts=[],
        pending_duplicates=[],
        thought_slots=[""],
    )
    state.update(overrides)
    return state


# ---------------------------------------------------------------------------
# process_new_thoughts
# ---------------------------------------------------------------------------

@patch("frontend.services.thought_processor.st")
@patch("frontend.services.thought_processor.save_thoughts")
@patch("frontend.services.thought_processor.recluster_and_save")
@patch("frontend.services.thought_processor.save_gm")
@patch("frontend.services.thought_processor.get_gm")
@patch("frontend.services.thought_processor.get_client")
def test_single_thought_added_to_graph(
    mock_get_client,
    mock_get_gm,
    mock_save_gm,
    mock_recluster,
    mock_save_thoughts,
    mock_st,
):
    """A single non-duplicate thought should end up in the graph."""
    gm = GraphManager()
    mock_get_gm.return_value = gm
    mock_get_client.return_value = MagicMock()

    state = _fresh_session_state()
    mock_st.session_state = state
    mock_st.sidebar.progress.return_value = MagicMock()

    not_dup = DuplicateCheck(is_duplicate=False)

    with patch(
        "frontend.services.thought_processor.ThoughtAnalyzer"
    ) as MockAnalyzer:
        analyzer = MockAnalyzer.return_value
        analyzer.check_duplicate.return_value = not_dup
        analyzer.find_connections.return_value = []

        from frontend.services.thought_processor import process_new_thoughts

        process_new_thoughts("Learn about graphs")

    assert gm.node_count == 1
    texts = gm.get_all_thought_texts()
    assert texts == ["Learn about graphs"]

    assert len(state["thoughts"]) == 1
    assert state["thoughts"][0]["text"] == "Learn about graphs"

    mock_recluster.assert_called_once_with(gm)
    mock_save_thoughts.assert_called_once()
    assert state["thought_slots"] == [""]


@patch("frontend.services.thought_processor.st")
@patch("frontend.services.thought_processor.save_thoughts")
@patch("frontend.services.thought_processor.recluster_and_save")
@patch("frontend.services.thought_processor.save_gm")
@patch("frontend.services.thought_processor.get_gm")
@patch("frontend.services.thought_processor.get_client")
def test_multiple_thoughts_added(
    mock_get_client,
    mock_get_gm,
    mock_save_gm,
    mock_recluster,
    mock_save_thoughts,
    mock_st,
):
    """Multiple newline-separated thoughts should each become a node."""
    gm = GraphManager()
    mock_get_gm.return_value = gm
    mock_get_client.return_value = MagicMock()

    state = _fresh_session_state()
    mock_st.session_state = state
    mock_st.sidebar.progress.return_value = MagicMock()

    not_dup = DuplicateCheck(is_duplicate=False)

    with patch(
        "frontend.services.thought_processor.ThoughtAnalyzer"
    ) as MockAnalyzer:
        analyzer = MockAnalyzer.return_value
        analyzer.check_duplicate.return_value = not_dup
        analyzer.find_connections.return_value = []

        from frontend.services.thought_processor import process_new_thoughts

        process_new_thoughts("Alpha\nBravo\nCharlie")

    assert gm.node_count == 3
    assert set(gm.get_all_thought_texts()) == {"Alpha", "Bravo", "Charlie"}
    assert len(state["thoughts"]) == 3


@patch("frontend.services.thought_processor.st")
@patch("frontend.services.thought_processor.save_thoughts")
@patch("frontend.services.thought_processor.recluster_and_save")
@patch("frontend.services.thought_processor.save_gm")
@patch("frontend.services.thought_processor.get_gm")
@patch("frontend.services.thought_processor.get_client")
def test_duplicate_goes_to_pending(
    mock_get_client,
    mock_get_gm,
    mock_save_gm,
    mock_recluster,
    mock_save_thoughts,
    mock_st,
):
    """A thought flagged as duplicate should be appended to pending_duplicates."""
    gm = GraphManager()
    mock_get_gm.return_value = gm
    mock_get_client.return_value = MagicMock()

    state = _fresh_session_state()
    mock_st.session_state = state
    mock_st.sidebar.progress.return_value = MagicMock()

    dup_result = DuplicateCheck(
        is_duplicate=True, similar_to="existing idea", reason="same meaning"
    )

    with patch(
        "frontend.services.thought_processor.ThoughtAnalyzer"
    ) as MockAnalyzer:
        analyzer = MockAnalyzer.return_value
        analyzer.check_duplicate.return_value = dup_result

        from frontend.services.thought_processor import process_new_thoughts

        process_new_thoughts("duplicate idea")

    assert gm.node_count == 0
    assert len(state["pending_duplicates"]) == 1
    assert state["pending_duplicates"][0].text == "duplicate idea"


@patch("frontend.services.thought_processor.st")
@patch("frontend.services.thought_processor.save_thoughts")
@patch("frontend.services.thought_processor.recluster_and_save")
@patch("frontend.services.thought_processor.save_gm")
@patch("frontend.services.thought_processor.get_gm")
@patch("frontend.services.thought_processor.get_client")
def test_connections_are_added(
    mock_get_client,
    mock_get_gm,
    mock_save_gm,
    mock_recluster,
    mock_save_thoughts,
    mock_st,
):
    """Connections returned by the analyzer should be added to the graph."""
    gm = GraphManager()
    existing = Thought(id="aaa", text="existing node")
    gm.add_thought(existing)
    mock_get_gm.return_value = gm
    mock_get_client.return_value = MagicMock()

    state = _fresh_session_state(thoughts=[existing.model_dump(mode="json")])
    mock_st.session_state = state
    mock_st.sidebar.progress.return_value = MagicMock()

    not_dup = DuplicateCheck(is_duplicate=False)

    with patch(
        "frontend.services.thought_processor.ThoughtAnalyzer"
    ) as MockAnalyzer:
        analyzer = MockAnalyzer.return_value
        analyzer.check_duplicate.return_value = not_dup

        def _fake_connections(new_id, new_text, existing_thoughts):
            return [
                Connection(
                    source_id=new_id, target_id="aaa", relationship="related"
                )
            ]

        analyzer.find_connections.side_effect = _fake_connections

        from frontend.services.thought_processor import process_new_thoughts

        process_new_thoughts("new linked idea")

    assert gm.node_count == 2
    edges = list(gm.graph.edges(data=True))
    assert len(edges) == 1
    assert edges[0][2]["relationship"] == "related"


@patch("frontend.services.thought_processor.st")
@patch("frontend.services.thought_processor.save_thoughts")
@patch("frontend.services.thought_processor.recluster_and_save")
@patch("frontend.services.thought_processor.save_gm")
@patch("frontend.services.thought_processor.get_gm")
@patch("frontend.services.thought_processor.get_client")
def test_thought_slots_reset_after_submit(
    mock_get_client,
    mock_get_gm,
    mock_save_gm,
    mock_recluster,
    mock_save_thoughts,
    mock_st,
):
    """After successful processing, thought_slots should reset to a single empty string."""
    gm = GraphManager()
    mock_get_gm.return_value = gm
    mock_get_client.return_value = MagicMock()

    state = _fresh_session_state(thought_slots=["idea one", "idea two", "idea three"])
    mock_st.session_state = state
    mock_st.sidebar.progress.return_value = MagicMock()

    not_dup = DuplicateCheck(is_duplicate=False)

    with patch(
        "frontend.services.thought_processor.ThoughtAnalyzer"
    ) as MockAnalyzer:
        analyzer = MockAnalyzer.return_value
        analyzer.check_duplicate.return_value = not_dup
        analyzer.find_connections.return_value = []

        from frontend.services.thought_processor import process_new_thoughts

        process_new_thoughts("idea one\nidea two\nidea three")

    assert state["thought_slots"] == [""]


@patch("frontend.services.thought_processor.st")
@patch("frontend.services.thought_processor.save_thoughts")
@patch("frontend.services.thought_processor.recluster_and_save")
@patch("frontend.services.thought_processor.save_gm")
@patch("frontend.services.thought_processor.get_gm")
@patch("frontend.services.thought_processor.get_client")
def test_blank_lines_are_skipped(
    mock_get_client,
    mock_get_gm,
    mock_save_gm,
    mock_recluster,
    mock_save_thoughts,
    mock_st,
):
    """Empty / whitespace-only lines in the input should be ignored."""
    gm = GraphManager()
    mock_get_gm.return_value = gm
    mock_get_client.return_value = MagicMock()

    state = _fresh_session_state()
    mock_st.session_state = state
    mock_st.sidebar.progress.return_value = MagicMock()

    not_dup = DuplicateCheck(is_duplicate=False)

    with patch(
        "frontend.services.thought_processor.ThoughtAnalyzer"
    ) as MockAnalyzer:
        analyzer = MockAnalyzer.return_value
        analyzer.check_duplicate.return_value = not_dup
        analyzer.find_connections.return_value = []

        from frontend.services.thought_processor import process_new_thoughts

        process_new_thoughts("real thought\n\n   \n  another thought  \n")

    assert gm.node_count == 2
    assert set(gm.get_all_thought_texts()) == {"real thought", "another thought"}


# ---------------------------------------------------------------------------
# SidebarResult thought_input assembly
# ---------------------------------------------------------------------------

def test_sidebar_result_joins_nonempty_slots():
    """SidebarResult.thought_input should be newline-joined non-empty slot values."""
    from frontend.components.sidebar import SidebarResult

    slots = ["hello", "", "  ", "world"]
    thought_input = "\n".join(v for v in slots if v.strip())
    result = SidebarResult(thought_input=thought_input, add_btn=True)

    assert result.thought_input == "hello\nworld"
    assert result.add_btn is True


def test_sidebar_result_empty_when_all_blank():
    """If every slot is blank the thought_input should be empty."""
    from frontend.components.sidebar import SidebarResult

    slots = ["", "  ", ""]
    thought_input = "\n".join(v for v in slots if v.strip())
    result = SidebarResult(thought_input=thought_input, add_btn=False)

    assert result.thought_input == ""
    assert result.add_btn is False
