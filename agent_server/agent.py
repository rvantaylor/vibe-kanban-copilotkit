from langgraph.graph import StateGraph, END
from typing import Dict, Any
from typing_extensions import TypedDict

class AgentState(TypedDict):
    input: str
    output: str

def process_input(state: AgentState) -> AgentState:
    user_input = state["input"]
    processed_output = f"Processed: {user_input}"
    return {"input": user_input, "output": processed_output}

def create_agent_graph() -> StateGraph:
    workflow = StateGraph(AgentState)
    
    workflow.add_node("process", process_input)
    
    workflow.set_entry_point("process")
    workflow.add_edge("process", END)
    
    return workflow.compile()