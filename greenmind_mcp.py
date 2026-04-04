#greenmind_mcp.py
import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from src.mcp.servers.greenmind_server import GreenMindMCPServer
from src.mcp.adapters.tool_adapters import create_adapters

# ------------------------------------------------
# FastAPI App
# ------------------------------------------------

app = FastAPI(title="GreenMind MCP Server")

# Add CORS middleware to allow requests from Streamlit Cloud
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MCP server
mcp_server = GreenMindMCPServer()

# Register tools
print("=" * 50)
print("CREATING ADAPTERS")
print("=" * 50)

adapters = create_adapters()

print(f"\nGot {len(adapters)} adapters from create_adapters()")
print("=" * 50)
print("REGISTERING TOOLS")
print("=" * 50)

for adapter in adapters:
    try:
        print(f"Registering: {adapter.name}")
        mcp_server.register_tool(
            adapter.name,
            adapter.handle,
            adapter.description
        )
        print(f"Successfully registered: {adapter.name}")
    except Exception as e:
        print(f"Failed to register {adapter.name}: {str(e)}")

print(f"\nTotal tools registered: {len(mcp_server.tools)}")
print("=" * 50)


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
        "service": "GreenMind MCP",
        "tools": list(mcp_server.tools.keys())
    }


# ------------------------------------------------
# Tool Call Endpoint
# ------------------------------------------------

@app.post("/call_tool")
async def call_tool(req: ToolRequest):
    print(f"Calling tool: {req.tool}")
    
    if req.tool not in mcp_server.tools:
        error_msg = f"Tool '{req.tool}' not found. Available tools: {list(mcp_server.tools.keys())}"
        print(error_msg)
        return {"error": error_msg}
    
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
        print(f"Error executing tool: {str(e)}")
        return {"error": str(e)}


# ------------------------------------------------
# Tools List Endpoint
# ------------------------------------------------

@app.get("/tools")
def list_tools():
    """Return list of all registered tools"""
    return {"tools": list(mcp_server.tools.keys())}


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