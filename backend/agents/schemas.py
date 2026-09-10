from pydantic import BaseModel

class TriageInput(BaseModel):
    bug_description: str
    

class ReproductionInput(BaseModel):
    classification: str
    reproduction_steps: list[str]
    expected_result: str

class DiagnosisInput(BaseModel):
    expected_output: str
    actual_output: str
    error_output: str = ""