from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
import httpx

mcp_app = FastMCP(name="AgentTools")

# Define tools via decorators
@mcp_app.tool(name="search_web", description="Searches the web for a query")
async def search_web(query: str) -> str:
    params = {"q": query, "format": "json"}
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.duckduckgo.com/", params=params)
    data = resp.json()
    return data.get("Answer", "")

app = FastAPI(lifespan=mcp_app.lifespan)
app.mount("/mcp", mcp_app)