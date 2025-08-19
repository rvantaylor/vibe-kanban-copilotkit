from fastapi import FastAPI
from pydantic import BaseModel
from agent import create_agent_graph

app = FastAPI(title="Agent Backend Server")

class QueryRequest(BaseModel):
    message: str

class QueryResponse(BaseModel):
    response: str

@app.get("/")
async def root():
    return {"message": "Agent Backend Server is running"}

@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    graph = create_agent_graph()
    result = await graph.ainvoke({"input": request.message})
    return QueryResponse(response=result.get("output", "No response"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)