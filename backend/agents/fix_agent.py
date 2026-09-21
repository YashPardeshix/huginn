import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI
from schemas import FixInput, TestInput

load_dotenv()
api_key = os.getenv("NVIDIA_API_KEY")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key,
    timeout=60.0,
)

def parse_json_safely(raw_text: str) -> dict:
    raw_text = raw_text.strip()
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON found in model output: {raw_text}")
    return json.loads(match.group(0))

def fix_agent(input: FixInput) -> TestInput:
    prompt = f"""
    Root cause: {input.root_cause}
    Evidence: {input.evidence}
    Expected result: {input.expected_result}

    Here is the ORIGINAL code that reproduces the bug — fix THIS exact code,
    keeping the same function name and signature:

    {input.original_code}

    Rules for your proposed fix:
    1. Write idiomatic, clean, complete Python code.
    2. Keep the original function name and parameters.
    3. At the bottom, include an `if __name__ == "__main__":` block that calls the function and explicitly PRINTS the returned result: `print(result)`.
    4. Do NOT wrap the call in unnecessary try/except blocks.

    Respond ONLY in this exact JSON format, nothing else:
    {{"proposed_fix": "<raw runnable python code as a single string, no markdown>", "explanation": "..."}}
    """
    
    response = client.chat.completions.create(
        model="nvidia/nemotron-3-super-120b-a12b",
        messages=[{"role": "user", "content": prompt}]
    )
    
    parsed = parse_json_safely(response.choices[0].message.content)
    fix_code = parsed["proposed_fix"].replace("\\n", "\n")
    
    return TestInput(
        proposed_fix=fix_code,
        explanation=parsed["explanation"],
        expected_result=input.expected_result
    )