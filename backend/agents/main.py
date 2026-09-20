import sqlite3
import uuid
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mlflow

from github_client import parse_github_url, fetch_github_issue
from graph_nodes import build_graph
from tracking import log_run
from shadow_eval_agent import shadow_eval_agent
from schemas import ShadowEvalInput

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

mlflow.set_tracking_uri("sqlite:///mlflow.db")

graph_app = build_graph()

run_status = {}


class IssueUrlRequest(BaseModel):
    github_issue_url: str


class HumanFixRequest(BaseModel):
    human_fix: str


def run_pipeline_background(thread_id: str, bug_description: str):
    config = {"configurable": {"thread_id": thread_id}}
    initial_state = {"bug_description": bug_description, "human_fix": ""}
    try:
        for step in graph_app.stream(initial_state, config):
            node_name = list(step.keys())[0]
            run_status[thread_id] = {"current_node": node_name, "done": False, "error": None}
        run_status[thread_id] = {"current_node": "awaiting_approval", "done": True, "error": None}

        final_state = graph_app.get_state(config).values
        log_run(thread_id, final_state)
    except Exception as e:
        run_status[thread_id] = {"current_node": "error", "done": True, "error": str(e)}


@app.get("/runs")
def list_runs():
    client = mlflow.tracking.MlflowClient()
    experiment = client.get_experiment_by_name("Default")
    if experiment is None:
        return []

    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["start_time DESC"],
    )
    seen = set()
    result = []
    for run in runs:
        thread_id = run.data.tags.get("thread_id", run.info.run_id)
        if thread_id in seen:
            continue
        seen.add(thread_id)
        result.append({
            "run_id": thread_id,
            "run_name": run.info.run_name,
            "verdict": run.data.params.get("verdict"),
            "created_at": run.info.start_time,
        })
    return result


@app.get("/runs/{run_id}")
def get_run(run_id: str):
    client = mlflow.tracking.MlflowClient()
    experiment = client.get_experiment_by_name("Default")
    if experiment is None:
        raise HTTPException(status_code=404, detail="Run not found")

    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        filter_string=f"tags.thread_id = '{run_id}'",
    )
    if not runs:
        raise HTTPException(status_code=404, detail="Run not found")

    run = runs[0]
    return {
        "run_id": run_id,
        "similarity_score": run.data.metrics.get("similarity_score", 0.0),
        "verdict": run.data.params.get("verdict", "unknown"),
        "fix_passed": run.data.params.get("fix_passed", "unknown"),
        "ai_fix": run.data.params.get("ai_fix", ""),
        "human_fix": run.data.params.get("human_fix", ""),
        "reasoning": run.data.params.get("reasoning", ""),
        "pending_approval": True,
    }


@app.delete("/runs/{run_id}")
def delete_run(run_id: str):
    client = mlflow.tracking.MlflowClient()
    experiment = client.get_experiment_by_name("Default")
    if experiment is None:
        raise HTTPException(status_code=404, detail="Run not found")

    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        filter_string=f"tags.thread_id = '{run_id}'",
    )

    if runs:
        for run in runs:
            client.delete_run(run.info.run_id)
    else:
        try:
            client.get_run(run_id)
        except Exception:
            raise HTTPException(status_code=404, detail="Run not found")
        client.delete_run(run_id)

    run_status.pop(run_id, None)

    return {"run_id": run_id, "status": "deleted"}


@app.get("/runs/{run_id}/status")
def get_run_status(run_id: str):
    if run_id in run_status:
        return run_status[run_id]

    # Not in memory (likely a uvicorn --reload restart wiped it) —
    # fall back to the persisted LangGraph checkpoint, which survives restarts.
    config = {"configurable": {"thread_id": run_id}}
    try:
        state_snapshot = graph_app.get_state(config)
    except Exception:
        raise HTTPException(status_code=404, detail="Run not found")

    if not state_snapshot or not state_snapshot.values:
        raise HTTPException(status_code=404, detail="Run not found")
    is_fully_finished = len(state_snapshot.next) == 0
    return {
        "current_node": "completed" if is_fully_finished else "awaiting_approval",
        "done": True,
        "error": None,
    }


@app.get("/metrics/trend")
def metrics_trend():
    client = mlflow.tracking.MlflowClient()
    experiment = client.get_experiment_by_name("Default")
    if experiment is None:
        return []

    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["start_time DESC"],
    )

    seen = set()
    deduped = []
    for run in runs:
        thread_id = run.data.tags.get("thread_id", run.info.run_id)
        if thread_id in seen:
            continue
        seen.add(thread_id)
        deduped.append(run)

    deduped.reverse()

    return [
        {
            "timestamp": run.info.start_time,
            "similarity_score": run.data.metrics.get("similarity_score", 0.0),
            "verdict": run.data.params.get("verdict"),
        }
        for run in deduped
    ]


import hmac
import hashlib
import os
from fastapi import Request

GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")


def verify_github_signature(payload_body: bytes, signature_header: str) -> bool:
    if not GITHUB_WEBHOOK_SECRET:
        return False
    if not signature_header:
        return False
    hash_object = hmac.new(
        GITHUB_WEBHOOK_SECRET.encode("utf-8"),
        msg=payload_body,
        digestmod=hashlib.sha256,
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)


@app.post("/webhook/github")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    payload_body = await request.body()
    signature_header = request.headers.get("X-Hub-Signature-256", "")

    if not verify_github_signature(payload_body, signature_header):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    payload = await request.json()

    event_type = request.headers.get("X-GitHub-Event", "")
    if event_type != "issues":
        return {"status": "ignored", "reason": f"not an issues event ({event_type})"}

    if payload.get("action") != "opened":
        return {"status": "ignored", "reason": f"action was '{payload.get('action')}', not 'opened'"}

    issue = payload.get("issue", {})
    title = issue.get("title", "")
    body = issue.get("body", "") or ""
    bug_description = f"Title: {title}\n\n{body}"

    thread_id = str(uuid.uuid4())
    run_status[thread_id] = {"current_node": "starting", "done": False, "error": None}
    background_tasks.add_task(run_pipeline_background, thread_id, bug_description)

    return {"status": "accepted", "thread_id": thread_id}
def run_from_url(request: IssueUrlRequest, background_tasks: BackgroundTasks):
    try:
        owner, repo, issue_number = parse_github_url(request.github_issue_url)
        bug_description = fetch_github_issue(owner, repo, issue_number)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    thread_id = str(uuid.uuid4())
    run_status[thread_id] = {"current_node": "starting", "done": False, "error": None}
    background_tasks.add_task(run_pipeline_background, thread_id, bug_description)

    return {"run_id": thread_id, "thread_id": thread_id, "status": "started"}


@app.post("/runs/{run_id}/approve")
def approve_run(run_id: str):
    client = mlflow.tracking.MlflowClient()
    experiment = client.get_experiment_by_name("Default")
    preserved = {}
    if experiment is not None:
        existing_runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            filter_string=f"tags.thread_id = '{run_id}'",
            order_by=["start_time DESC"],
        )
        if existing_runs:
            latest = existing_runs[0]
            preserved = {
                "similarity_score": latest.data.metrics.get("similarity_score", 0.0),
                "verdict": latest.data.params.get("verdict", "unknown"),
                "reasoning": latest.data.params.get("reasoning", ""),
                "human_fix": latest.data.params.get("human_fix", ""),
            }

    config = {"configurable": {"thread_id": run_id}}
    result = graph_app.invoke(None, config)

    merged_state = {**result, **preserved}
    log_run(run_id, merged_state)

    return {
        "run_id": run_id,
        "thread_id": run_id,
        "status": "completed",
        "state": merged_state
    }


@app.post("/runs/{run_id}/human-fix")
def submit_human_fix(run_id: str, request: HumanFixRequest):
    """
    Accepts a real human fix for an already-completed run and re-runs
    just the Shadow Mode Evaluation agent against it, then re-logs the run
    so the dashboard shows the updated, genuine comparison.
    """
    config = {"configurable": {"thread_id": run_id}}
    try:
        state = graph_app.get_state(config).values
    except Exception:
        raise HTTPException(status_code=404, detail="Run not found")

    if not state:
        raise HTTPException(status_code=404, detail="Run not found")

    shadow_input = ShadowEvalInput(
        fix_passed=state.get("fix_passed", False),
        test_output=state.get("test_output", ""),
        expected_result=state.get("expected_result", ""),
        human_fix=request.human_fix,
        ai_fix=state.get("ai_fix", ""),
    )
    result = shadow_eval_agent(shadow_input)

    updated_state = {
        **state,
        "human_fix": request.human_fix,
        "similarity_score": result.similarity_score,
        "reasoning": result.reasoning,
        "verdict": result.verdict,
    }

    log_run(run_id, updated_state)

    return {
        "run_id": run_id,
        "similarity_score": result.similarity_score,
        "reasoning": result.reasoning,
        "verdict": result.verdict,
    }