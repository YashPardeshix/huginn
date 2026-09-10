from schemas import TriageInput
from triage_agent import triage_agent
from reproduction_agent import reproduction_agent

bug = TriageInput(bug_description="When I add -5 and -3, I get 8 instead of -8.")

step1 = triage_agent(bug)
print("Agent 1 output:", step1)

step2 = reproduction_agent(step1)
print("Agent 2 output:", step2)