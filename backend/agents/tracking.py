import mlflow
from datetime import datetime, timezone

mlflow.set_tracking_uri("sqlite:///mlflow.db")

def log_run(thread_id: str, state: dict):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H:%M:%S")
    run_name = f"eval_{timestamp}_{thread_id[:8]}"
    with mlflow.start_run(run_name=run_name) as run:
        mlflow.set_tag("thread_id", thread_id)
        mlflow.log_metric("similarity_score", state.get("similarity_score", 0.0))
        mlflow.log_param("verdict", state.get("verdict", "unknown"))
        mlflow.log_param("fix_passed", state.get("fix_passed", "unknown"))
        mlflow.log_param("ai_fix", state.get("ai_fix", ""))
        mlflow.log_param("human_fix", state.get("human_fix", ""))
        mlflow.log_param("reasoning", state.get("reasoning", ""))
        mlflow.log_param("github_owner", state.get("github_owner", ""))
        mlflow.log_param("github_repo", state.get("github_repo", ""))
        mlflow.log_param("github_issue_number", state.get("github_issue_number", ""))
    return run.info.run_id