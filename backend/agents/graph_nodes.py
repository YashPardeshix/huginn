from state import PipelineState
from schemas import TriageInput, ReproductionInput, DiagnosisInput, FixInput, TestInput, ShadowEvalInput
from triage_agent import triage_agent
from reproduction_agent import reproduction_agent
from diagnosis_agent import diagnosis_agent
from fix_agent import fix_agent
from test_agent import test_agent
from shadow_eval_agent import shadow_eval_agent
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3




def triage_node(state: PipelineState) -> dict:
    result = triage_agent(TriageInput(bug_description=state["bug_description"]))
    return {
        "classification": result.classification,
        "reproduction_steps": result.reproduction_steps,
        "expected_result": result.expected_result
    }

def reproduction_node(state: PipelineState) -> dict:
    result = reproduction_agent(ReproductionInput(
        classification=state["classification"],
        reproduction_steps=state["reproduction_steps"],
        expected_result=state["expected_result"]
    ))
    return {
        "actual_output": result.actual_output,
        "error_output": result.error_output
    }

def diagnosis_node(state: PipelineState) -> dict:
    result = diagnosis_agent(DiagnosisInput(
        expected_result=state["expected_result"],
        actual_output=state["actual_output"],
        error_output=state["error_output"]
    ))
    return {
        "root_cause": result.root_cause,
        "evidence": result.evidence
    }

def fix_node(state: PipelineState) -> dict:
    result = fix_agent(FixInput(
        root_cause=state["root_cause"],
        evidence=state["evidence"],
        expected_result=state["expected_result"]
    ))
    return {
        "proposed_fix": result.proposed_fix,
        "explanation": result.explanation
    }

def test_node(state: PipelineState) -> dict:
    result = test_agent(TestInput(
        proposed_fix=state["proposed_fix"],
        explanation=state["explanation"],
        expected_result=state["expected_result"]
    ))
    return {
        "fix_passed": result.fix_passed,
        "test_output": result.test_output,
        "ai_fix": result.ai_fix
    }

def shadow_eval_node(state: PipelineState) -> dict:
    result = shadow_eval_agent(ShadowEvalInput(
        fix_passed=state["fix_passed"],
        test_output=state["test_output"],
        expected_result=state["expected_result"],
        human_fix=state["human_fix"],
        ai_fix=state["ai_fix"]
    ))
    return {
        "similarity_score": result.similarity_score,
        "reasoning": result.reasoning,
        "verdict": result.verdict
    }

def human_approval_node(state: PipelineState) -> dict:
    print("Human approved. Proceeding with final action.")
    return {}



def build_graph():
    graph = StateGraph(PipelineState)
    
    graph.add_node("triage", triage_node)
    graph.add_node("reproduction", reproduction_node)
    graph.add_node("diagnosis", diagnosis_node)
    graph.add_node("fix", fix_node)
    graph.add_node("test", test_node)
    graph.add_node("shadow_eval", shadow_eval_node)
    graph.add_node("human_approval", human_approval_node)
    
    graph.set_entry_point("triage")
    graph.add_edge("triage", "reproduction")
    graph.add_edge("reproduction", "diagnosis")
    graph.add_edge("diagnosis", "fix")
    graph.add_edge("fix", "test")
    graph.add_edge("test", "shadow_eval")
    graph.add_edge("shadow_eval","human_approval")
    graph.add_edge("human_approval", END)
    
    conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    
    return graph.compile(checkpointer=checkpointer, interrupt_before=["human_approval"])

 