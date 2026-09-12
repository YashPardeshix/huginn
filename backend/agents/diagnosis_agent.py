import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from schemas import DiagnosisInput, FixInput

load_dotenv()
api_key = os.getenv("NVIDIA_API_KEY")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
)

def diagnosis_agent(input: DiagnosisInput) -> FixInput:
    prompt = f"""
    The bug was reproduced. Here's what happened:
    Expected output: {input.expected_result}
    Actual output: {input.actual_output}
    Error output: {input.error_output}
    
    Find the root cause and provide evidence.
    Respond ONLY in this exact JSON format, nothing else:
    {{"root_cause": "...", "evidence": "..."}}
    """
    
    response = client.chat.completions.create(
        model="nvidia/nemotron-3-super-120b-a12b",
        messages=[{"role": "user", "content": prompt}]
    )
    
    raw_text = response.choices[0].message.content
    parsed = json.loads(raw_text)
    
    return FixInput(
        root_cause=parsed["root_cause"],
        evidence=parsed["evidence"],
        expected_result=input.expected_result
    )