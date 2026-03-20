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

# Register tools with debug output
print("=" * 50)
print("REGISTERING TOOLS")
print("=" * 50)

try:
    adapters = create_adapters()
    print(f"create_adapters() returned {len(adapters) if adapters else 0} adapters")
    
    if adapters:
        for adapter in adapters:
            print(f"Attempting to register: {adapter.name}")
            mcp_server.register_tool(
                adapter.name,
                adapter.handle,
                adapter.description
            )
            print(f"Registered: {adapter.name}")
    else:
        print("No adapters returned from create_adapters()")
        
except Exception as e:
    print(f"Error creating adapters: {str(e)}")
    import traceback
    traceback.print_exc()

print(f"Total tools registered: {len(mcp_server.tools)}")
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