from typing import TypedDict

class PipelineState(TypedDict):
    bug_description: str
    classification: str
    reproduction_steps: list[str]
    expected_result: str
    actual_output: str
    error_output: str
    root_cause: str
    evidence: str
    proposed_fix: str
    explanation: str
    fix_passed: bool
    test_output: str
    human_fix: str
    ai_fix: str
    similarity_score: float
    reasoning: str
    verdict: str