from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="AI Agent API")

class Query(BaseModel):
    query: str

@app.post("/research")
async def research(query: Query):
    answer = await run_deep_research_agent(query.query)
    return {"query": query.query, "answer": answer}