import os
import docker
from dotenv import load_dotenv
from schemas import TestInput, ShadowEvalInput

load_dotenv()


def run_test_in_sandbox(code: str) -> tuple[bool, str]:
    docker_client = docker.from_env()
    container = docker_client.containers.create(
        image="python:3.11-slim",
        command=["python", "-c", code],
        mem_limit="256m",
        network_disabled=True,
    )
    container.start()
    
    try:
        result = container.wait(timeout=30)
        output = container.logs().decode("utf-8")
        if result.get("StatusCode") != 0:
            return False, output
        return True, output
    except Exception:
        try:
            container.kill()
        except Exception:
            pass
        return False, "ERROR: Test execution timed out (limit: 30s)"
    finally:
        container.remove(force=True)


def test_agent(input: TestInput) -> ShadowEvalInput:
    crashed_free, output = run_test_in_sandbox(input.proposed_fix)
    
    passed = crashed_free and (input.expected_result in output)
    
    return ShadowEvalInput(
    fix_passed=passed,
    test_output=output,
    expected_result=input.expected_result,
    human_fix="", 
    ai_fix=input.proposed_fix
)