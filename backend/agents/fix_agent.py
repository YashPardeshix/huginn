import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from schemas import FixInput, TestInput
 
load_dotenv()
api_key = os.getenv("NVIDIA_API_KEY")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
)

def fix_agent(input: FixInput) -> TestInput:
    prompt = f"""
    Root cause: {input.root_cause}
    Evidence: {input.evidence}
    Expected result: {input.expected_result}

    Here is the ORIGINAL code that reproduces the bug — fix THIS exact code,
    keeping the same function name and signature. Do not invent a different
    function or change what the function is called:

    {input.original_code}

    Write the complete, corrected, runnable Python code that fixes this bug,
    using the SAME function name as above.

    Respond ONLY in this exact JSON format, nothing else:
    {{"proposed_fix": "<raw runnable python code as a single string, no markdown>", "explanation": "..."}}
    """
    
    response = client.chat.completions.create(
        model="nvidia/nemotron-3-super-120b-a12b",
        messages=[{"role": "user", "content": prompt}]
    )
    
    parsed = json.loads(response.choices[0].message.content)
    
    return TestInput(
        proposed_fix=parsed["proposed_fix"],
        explanation=parsed["explanation"],
        expected_result=input.expected_result
    )