# greenmind_mcp.py
import os
import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

from src.mcp.servers.greenmind_server import GreenMindMCPServer
from src.mcp.adapters.tool_adapters import create_adapters

# ------------------------------------------------
# FastAPI App
# ------------------------------------------------

app = FastAPI(title="GreenMind MCP Server")

# Initialize MCP server
mcp_server = GreenMindMCPServer()

# Register tools
adapters = create_adapters()

for adapter in adapters:
    mcp_server.register_tool(
        adapter.name,
        adapter.handle,
        adapter.description
    )


# ------------------------------------------------
# Request Schema
# ------------------------------------------------

class ToolRequest(BaseModel):
    tool: str
    input: str


# ------------------------------------------------
# Health Endpoint
# ------------------------------------------------

@app.get("/")
def health():
    return {
        "status": "running",
        "service": "GreenMind MCP"
    }


# ------------------------------------------------
# Tool Call Endpoint
# ------------------------------------------------

@app.post("/call_tool")
async def call_tool(req: ToolRequest):

    if req.tool not in mcp_server.tools:
        return {"error": f"Tool '{req.tool}' not found"}

    tool = mcp_server.tools[req.tool]

    try:

        if asyncio.iscoroutinefunction(tool.handler):
            result = await tool.handler(input=req.input)
        else:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: tool.handler(input=req.input)
            )

        return {"result": result}

    except Exception as e:
        return {"error": str(e)}


# ------------------------------------------------
# Server Start
# ------------------------------------------------

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    uvicorn.run(
        "greenmind_mcp:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )