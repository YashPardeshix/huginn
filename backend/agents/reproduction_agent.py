import os
import json
import docker
from dotenv import load_dotenv
from openai import OpenAI
from schemas import ReproductionInput, DiagnosisInput

load_dotenv()
api_key = os.getenv("NVIDIA_API_KEY")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
)

def run_in_sandbox(code: str) -> str:
    docker_client = docker.from_env()
    
    try:
        output = docker_client.containers.run(
            image="python:3.11-slim",
            command=["python", "-c", code],
            mem_limit="256m",
            network_disabled=True,
            remove=True
        )
        return output.decode("utf-8")
    except docker.errors.ContainerError as e:
        return f"ERROR: {e}"

def reproduction_agent(input: ReproductionInput) -> DiagnosisInput:
    steps_text = "\n".join(input.reproduction_steps)
    
    prompt = f"""
    Write Python code that performs these steps to reproduce a bug:
    {steps_text}
    
    The code should print what actually happens.
    Respond with ONLY the raw Python code, nothing else — no explanation, no markdown.
    """
    
    response = client.chat.completions.create(
        model="nvidia/nemotron-3-super-120b-a12b",
        messages=[{"role": "user", "content": prompt}]
    )
    
    generated_code = response.choices[0].message.content
    actual_result = run_in_sandbox(generated_code)
    
    return DiagnosisInput(
        expected_output=input.expected_result,
        actual_output=actual_result,
        error_output=actual_result if actual_result.startswith("ERROR:") else ""
    )

