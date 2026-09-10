import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from schemas import TriageInput, ReproductionInput

load_dotenv()
api_key = os.getenv("NVIDIA_API_KEY")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
)

def triage_agent(input: TriageInput) -> ReproductionInput:
    prompt = f"""
    A user reported this bug: {input.bug_description}
    
    Classify it as one word (e.g. "bug") and list clear reproduction steps.
    Respond ONLY in this exact JSON format, nothing else:
    {{"classification": "...", "reproduction_steps": ["step1", "step2", "step3"], "expected_result": "..."}}
    """
    
    response = client.chat.completions.create(
        model="nvidia/nemotron-3.5-lightning-30b-a3b",
        messages=[{"role": "user", "content": prompt}]
    )
    
    raw_text = response.choices[0].message.content
    parsed = json.loads(raw_text)
    
    return ReproductionInput(
        classification=parsed["classification"],
        reproduction_steps=parsed["reproduction_steps"],
        expected_result=parsed["expected_result"]
    )