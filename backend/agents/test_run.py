from schemas import TriageInput
from triage_agent import triage_agent
from reproduction_agent import reproduction_agent
from diagnosis_agent import diagnosis_agent
from fix_agent import fix_agent
from test_agent import test_agent

bug = TriageInput(bug_description="""
I have this function:

def add(a, b):
    return abs(a) + abs(b)

When I call add(-5, -3), I expect -8, but I get 8 instead.
""")

step1 = triage_agent(bug)
print("Agent 1 output:", step1)

step2 = reproduction_agent(step1)
print("Agent 2 output:", step2)

step3 = diagnosis_agent(step2)
print("Agent 3 output:", step3)

step4 = fix_agent(step3)
print("Agent 4 output:", step4)

step5 = test_agent(step4)
print("Agent 5 output:", step5)