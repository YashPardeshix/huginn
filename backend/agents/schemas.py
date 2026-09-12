from pydantic import BaseModel

class TriageInput(BaseModel):
    bug_description: str
    

class ReproductionInput(BaseModel):
    classification: str
    reproduction_steps: list[str]
    expected_result: str

class DiagnosisInput(BaseModel):
    expected_result: str
    actual_output: str
    error_output: str = ""


class FixInput(BaseModel):
    root_cause: str
    evidence:str
    expected_result: str

class TestInput(BaseModel):
    proposed_fix: str
    explanation: str
    expected_result: str

class ShadowEvalInput(BaseModel):
    fix_passed: bool
    test_output: str

