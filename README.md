# Clarity

An AI-powered thought network builder. Add freeform thoughts and let GPT discover connections, detect duplicates, and cluster related ideas into an interactive graph you can explore in the browser.

Built with [Streamlit](https://streamlit.io), [OpenAI](https://platform.openai.com), [NetworkX](https://networkx.org), and [pyvis](https://pyvis.readthedocs.io).

## Features

- **Thought graph** -- every thought becomes a node; AI-discovered relationships become labeled edges.
- **Automatic clustering** -- thoughts are grouped into named clusters and color-coded on the graph.
- **Duplicate detection** -- before a thought is added, the AI checks for semantic duplicates. You can skip, add anyway, or merge.
- **Interactive visualization** -- the graph is rendered with pyvis (force-directed, zoomable, hoverable).
- **Batch input** -- paste multiple thoughts (one per line) and process them all at once.

## Prerequisites

- Python 3.11+
- An [OpenAI API key](https://platform.openai.com/api-keys) (the app uses `gpt-4o-mini` by default)

## Getting Started

```bash
# Clone the repository
git clone <repo-url>
cd Clarity

# Create and activate a virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install .

# Run the app
streamlit run frontend/app.py
```

The app opens at `http://localhost:8501`. Set your OpenAI API key in the `.env` file to begin.

## Project Structure

```
Clarity/
├── pyproject.toml
├── backend/
│   ├── __init__.py
│   ├── models.py                  # Pydantic data models (Thought, Connection, Cluster, ...)
│   ├── graph/
│   │   ├── __init__.py
│   │   └── graph_manager.py       # NetworkX graph wrapper (add/remove nodes, clustering, serialization)
│   └── analysis/
│       ├── __init__.py
│       ├── thought_analyzer.py    # OpenAI-backed analyzer (duplicates, connections, clustering)
│       └── prompts.py             # System prompts sent to the LLM
└── frontend/
    ├── app.py                     # Streamlit entry point
    ├── config/
    │   ├── theme.py               # Color palette constants
    │   └── styles.py              # Injects custom CSS into the Streamlit page
    ├── components/
    │   ├── sidebar.py             # Sidebar UI (API key input, thought entry, thought list)
    │   ├── graph_view.py          # Main area: renders the interactive graph + cluster legend
    │   └── duplicates.py          # Duplicate-resolution UI (add anyway / skip / merge)
    └── services/
        ├── state.py               # Session-state helpers (graph persistence, OpenAI client cache)
        ├── graph_ops.py           # High-level graph operations (add thought, recluster)
        ├── visualizer.py          # Converts GraphManager into a pyvis HTML string
        └── thought_processor.py   # Orchestrates batch thought processing with progress bar
```

### Backend

| Module | Responsibility |
|---|---|
| `models.py` | Shared Pydantic models used across both backend and frontend. |
| `graph/graph_manager.py` | Thin wrapper around a NetworkX graph. Handles node/edge CRUD, cluster assignment, and dict-based serialization for session-state storage. |
| `analysis/thought_analyzer.py` | Calls the OpenAI chat API (JSON mode) to check duplicates, find inter-thought connections, and cluster thoughts. |
| `analysis/prompts.py` | System-prompt strings consumed exclusively by the analyzer. |

### Frontend

| Module | Responsibility |
|---|---|
| `app.py` | Streamlit entry point -- wires sidebar, duplicate panel, and graph view together. |
| `config/theme.py` | Dark-mode color palette. |
| `config/styles.py` | Applies custom CSS via `st.markdown`. |
| `components/sidebar.py` | Renders the sidebar: API key input, thought text area, add button, and deletable thought list. |
| `components/graph_view.py` | Renders the pyvis graph and a cluster legend beneath it. |
| `components/duplicates.py` | Shows flagged duplicates with Add Anyway / Skip / Merge actions. |
| `services/state.py` | Manages `st.session_state` for graph data and caches the OpenAI client. |
| `services/graph_ops.py` | `add_thought_to_graph` and `recluster_and_save` -- high-level operations used by multiple components. |
| `services/visualizer.py` | Builds a pyvis `Network`, applies theme colors, and returns the generated HTML. |
| `services/thought_processor.py` | Processes a batch of newline-separated thoughts: duplicate-checks each one, finds connections, clusters, and saves. |

## How It Works

1. You enter one or more thoughts in the sidebar and click **Add to Network**.
2. Each thought is checked for semantic duplicates against existing thoughts. Duplicates are flagged for review; unique thoughts proceed.
3. For each new thought the AI identifies relationships to every existing thought (e.g., *supports*, *contradicts*, *extends*).
4. The thought is added as a graph node; discovered relationships become labeled edges.
5. Once all thoughts are processed, the AI re-clusters the entire graph and assigns color-coded cluster labels.
6. The graph is rendered as an interactive force-directed visualization in the main panel.

## Configuration

- **Model** -- `ThoughtAnalyzer` defaults to `gpt-4o-mini`. Pass a different model name to the constructor to change it.
- **Theme** -- edit `frontend/config/theme.py` to adjust colors.

## License

This project is provided as-is for personal and educational use.
