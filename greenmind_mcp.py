# greenmind_mcp.py
import asyncio
import os
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.mcp.servers.greenmind_server import GreenMindMCPServer
from src.mcp.adapters.tool_adapters import create_adapters

class HealthCheckHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for Render health checks"""
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')
    
    def log_message(self, format, *args):
        # Suppress log messages to avoid clutter
        pass

def run_health_server(port):
    """Run a simple HTTP server for Render health checks"""
    try:
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        print(f"Health check server running on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Health check server error: {e}")

async def main():
    # Get port from environment variable (Render sets this) or default to 8765
    port = int(os.environ.get('PORT', 8765))
    # Bind to 0.0.0.0 to accept connections from anywhere (required for Render)
    host = "0.0.0.0"
    
    # Start a simple HTTP health check server on the same port in a background thread
    # This helps Render detect that the port is open
    health_thread = threading.Thread(target=run_health_server, args=(port,), daemon=True)
    health_thread.start()
    print(f"Health check server started on port {port}")
    
    print("=" * 70)
    print("GREENMIND MCP SERVER - RUNNING")
    print("=" * 70)
    print(f"Starting main MCP server on {host}:{port}")
    
    # Step 1: Create tool adapters
    print("\n1. Creating tool adapters...")
    adapters = create_adapters()
    print(f"   Created {len(adapters)} adapters")
    
    # Step 2: Create MCP server
    print("\n2. Initializing MCP server...")
    server = GreenMindMCPServer(host=host, port=port)
    
    # Step 3: Register all tools
    print("\n3. Registering tools with server...")
    for adapter in adapters:
        server.register_tool(
            adapter.name,
            adapter.handle,
            adapter.description
        )
        print(f"   Registered: {adapter.name}")
    
    # Step 4: Start server and keep it running
    print("\n4. Starting server...")
    print("   Press Ctrl+C to stop")
    print("=" * 70)
    
    await server.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\nError: {str(e)}")