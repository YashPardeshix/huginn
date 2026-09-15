import mlflow

mlflow.set_tracking_uri("sqlite:///mlflow.db")

def log_run(state: dict):
    with mlflow.start_run():
        mlflow.log_metric("similarity_score", state["similarity_score"])
        mlflow.log_param("verdict", state["verdict"])
        mlflow.log_param("fix_passed", state["fix_passed"])