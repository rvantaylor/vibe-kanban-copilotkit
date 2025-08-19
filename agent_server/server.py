from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
from agent import AgentGraph

app = FastAPI(title="Agent Server", version="0.1.0")

agent_graph = AgentGraph()

class AgentRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    response: str
    metadata: Optional[Dict[str, Any]] = None

@app.get("/")
async def root():
    return {"message": "Agent Server is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/agent/invoke", response_model=AgentResponse)
async def invoke_agent(request: AgentRequest):
    try:
        result = await agent_graph.invoke(request.message, request.context)
        return AgentResponse(
            response=result.get("response", ""),
            metadata=result.get("metadata", {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/stream")
async def stream_agent(request: AgentRequest):
    try:
        async for chunk in agent_graph.stream(request.message, request.context):
            yield chunk
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )