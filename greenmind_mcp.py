# greenmind_mcp.py
import asyncio
import os
import sys
import socket
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.mcp.servers.greenmind_server import GreenMindMCPServer
from src.mcp.adapters.tool_adapters import create_adapters

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')
    
    def log_message(self, format, *args):
        pass

def run_health_server(port):
    try:
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        print(f"✅ Health check server running on 0.0.0.0:{port}")
        server.serve_forever()
    except Exception as e:
        print(f"❌ Health check server failed: {e}")

async def main():
    # Get port from environment variable (Render sets this) or default to 8765
    port = int(os.environ.get('PORT', 8765))
    # MUST bind to 0.0.0.0 for Render - this is non-negotiable
    host = "0.0.0.0"
    
    print(f"🔧 Configuring servers to bind to {host}:{port}")
    
    # Test if we can bind to this address/port
    test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        test_sock.bind((host, port))
        print(f"✅ Successfully bound test socket to {host}:{port}")
        test_sock.close()
    except Exception as e:
        print(f"❌ Cannot bind to {host}:{port}: {e}")
        return
    
    # Start health check server (explicitly on 0.0.0.0)
    health_thread = threading.Thread(target=run_health_server, args=(port,), daemon=True)
    health_thread.start()
    await asyncio.sleep(1)  # Give it a moment to start
    
    print("=" * 70)
    print("GREENMIND MCP SERVER - RUNNING")
    print("=" * 70)
    print(f"Main MCP server will bind to {host}:{port}")
    
    # Step 1: Create tool adapters
    print("\n1. Creating tool adapters...")
    adapters = create_adapters()
    print(f"   Created {len(adapters)} adapters")
    
    # Step 2: Create MCP server with EXPLICIT host and port
    print(f"\n2. Initializing MCP server with host='{host}', port={port}...")
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
    print("=" * 70)
    
    await server.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\nError: {str(e)}")