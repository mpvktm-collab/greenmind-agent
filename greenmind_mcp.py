# greenmind_mcp.py
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.mcp.servers.greenmind_server import GreenMindMCPServer
from src.mcp.adapters.tool_adapters import create_adapters

async def main():
    print("=" * 70)
    print("GREENMIND MCP SERVER - RUNNING")
    print("=" * 70)
    
    # Step 1: Create tool adapters
    print("\n1. Creating tool adapters...")
    adapters = create_adapters()
    print(f"   Created {len(adapters)} adapters")
    
    # Step 2: Create MCP server
    print("\n2. Initializing MCP server...")
    server = GreenMindMCPServer()
    
    # Step 3: Register all tools
    print("\n3. Registering tools with server...")
    for adapter in adapters:
        server.register_tool(
            adapter.name,
            adapter.handle,
            adapter.description
        )
        print(f"   ✓ Registered: {adapter.name}")
    
    # Step 4: Start server and keep it running
    print("\n4. Starting server...")
    print("   Press Ctrl+C to stop")
    print("=" * 70)
    
    # This line keeps the server running
    await server.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\nError: {str(e)}")
   