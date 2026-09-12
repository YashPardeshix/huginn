# test_agent.py
import os
import docker
from dotenv import load_dotenv
from schemas import TestInput, ShadowEvalInput

load_dotenv()


def run_test_in_sandbox(code: str) -> tuple[bool, str]:
    docker_client = docker.from_env()
    
    try:
        output = docker_client.containers.run(
            image="python:3.11-slim",
            command=["python", "-c", code],
            mem_limit="256m",
            network_disabled=True,
            remove=True
        )
        return True, output.decode("utf-8")
    except docker.errors.ContainerError as e:
        return False, str(e)


def test_agent(input: TestInput) -> ShadowEvalInput:
    crashed_free, output = run_test_in_sandbox(input.proposed_fix)
    
    passed = crashed_free and (input.expected_result in output)
    
    return ShadowEvalInput(
        fix_passed=passed,
        test_output=output,
        expected_result=input.expected_result
    )