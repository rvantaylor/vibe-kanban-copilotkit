from typing import Dict, Any, Optional, AsyncGenerator
from langgraph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel

class AgentState(BaseModel):
    messages: list = []
    context: Optional[Dict[str, Any]] = None
    current_step: str = "start"

class AgentGraph:
    def __init__(self):
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)
        
        workflow.add_node("start", self._start_node)
        workflow.add_node("process", self._process_node) 
        workflow.add_node("finish", self._finish_node)
        
        workflow.set_entry_point("start")
        
        workflow.add_edge("start", "process")
        workflow.add_edge("process", "finish")
        workflow.add_edge("finish", END)
        
        return workflow.compile()
    
    async def _start_node(self, state: AgentState) -> AgentState:
        state.current_step = "processing"
        return state
    
    async def _process_node(self, state: AgentState) -> AgentState:
        last_message = state.messages[-1] if state.messages else None
        
        if isinstance(last_message, HumanMessage):
            response = f"Processed: {last_message.content}"
            state.messages.append(AIMessage(content=response))
        
        state.current_step = "finishing"
        return state
    
    async def _finish_node(self, state: AgentState) -> AgentState:
        state.current_step = "completed"
        return state
    
    async def invoke(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        initial_state = AgentState(
            messages=[HumanMessage(content=message)],
            context=context or {}
        )
        
        result = await self.graph.ainvoke(initial_state)
        
        last_message = result.messages[-1] if result.messages else None
        response_content = last_message.content if last_message else "No response generated"
        
        return {
            "response": response_content,
            "metadata": {
                "step": result.current_step,
                "message_count": len(result.messages),
                "context": result.context
            }
        }
    
    async def stream(self, message: str, context: Optional[Dict[str, Any]] = None) -> AsyncGenerator[Dict[str, Any], None]:
        initial_state = AgentState(
            messages=[HumanMessage(content=message)],
            context=context or {}
        )
        
        async for chunk in self.graph.astream(initial_state):
            yield {
                "step": chunk.get("current_step", "unknown"),
                "data": chunk
            }