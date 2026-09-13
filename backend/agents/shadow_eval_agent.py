import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from schemas import ShadowEvalInput, EvaluationResult

load_dotenv()
api_key = os.getenv("NVIDIA_API_KEY")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
)

def shadow_eval_agent(input: ShadowEvalInput) -> EvaluationResult:
    prompt = f"""
    Fix passed: {input.fix_passed}
    Test output: {input.test_output}
    Expected result: {input.expected_result}
    Human fix: {input.human_fix}
    AI fix: {input.ai_fix}

    Evaluate how similar the AI's fix is to the human's fix.
    Give a similarity score between 0 and 1 (e.g. 0.85), a short reasoning, and a verdict of either "trustworthy" or "needs_human_rework".

    Respond ONLY in this exact JSON format, nothing else:
    {{"similarity_score": <float>, "reasoning": "<short explanation>", "verdict": "<trustworthy or needs_human_rework>"}}
    """ 
    response = client.chat.completions.create(
        model="nvidia/nemotron-3-super-120b-a12b",
        messages=[{"role": "user", "content": prompt}]
    )
    
    parsed = json.loads(response.choices[0].message.content)
    
    return EvaluationResult(
        similarity_score=parsed["similarity_score"],
        reasoning=parsed["reasoning"],
        verdict=parsed["verdict"]
    )