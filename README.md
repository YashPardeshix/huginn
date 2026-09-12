Triage Agent — reads the bug, classifies it, extracts reproduction steps
Reproduction Agent — recreates the bug inside the Docker sandbox
Diagnosis Agent — finds the root cause from what the sandbox showed
Fix Agent — proposes a fix
Test Agent — runs the existing test suite against the fix
Shadow Mode Evaluation Agent — later, compares the fix against a human's real resolution







