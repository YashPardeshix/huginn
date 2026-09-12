# shadow_eval_agent.py
def shadow_eval_agent(input):
    if input.fix_passed:
        return f"Fix PASSED. Output: {input.test_output}"
    else:
        return f"Fix FAILED. Output: {input.test_output}"