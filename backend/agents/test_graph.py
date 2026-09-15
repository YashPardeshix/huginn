from graph_nodes import build_graph
from tracking import log_run

app = build_graph()

initial_state = {
    "bug_description": """
    I have this function:
    def add(a, b):
        return abs(a) + abs(b)
    When I call add(-5, -3), I expect -8, but I get 8 instead.
    """,
    "human_fix": "def add(a, b):\n    return a + b\n\nprint(add(-5, -3))"
}

config = {"configurable": {"thread_id": "test-run-1"}}

result = app.invoke(initial_state, config)
print("Pipeline paused. Current state:", result)

resume_result = app.invoke(None, config)
print("Resumed. Final state:", resume_result)
log_run(resume_result)