# greenmind_mcp.py
import asyncio
import os
import sys
import socket
import subprocess
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.mcp.servers.greenmind_server import GreenMindMCPServer
from src.mcp.adapters.tool_adapters import create_adapters

def kill_process_on_port(port):
    """Kill any process using the specified port"""
    try:
        print(f"Checking for process using port {port}...")
        # Find and kill process using the port
        result = subprocess.run(
            f"lsof -ti:{port} | xargs kill -9",
            shell=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(f"Killed process: {result.stdout}")
        else:
            print(f"No process found on port {port}")
    except Exception as e:
        print(f"Error killing process: {e}")

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
        print(f"Health check server running on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Health check server error: {e}")

async def main():
    # Get port from environment variable (Render sets this) or default to 10000
    port = int(os.environ.get('PORT', 10000))
    host = "0.0.0.0"
    
    # Kill any existing process on the port
    kill_process_on_port(port)
    
    # Small delay to ensure port is released
    await asyncio.sleep(2)
    
    print(f"Starting services on {host}:{port}")
    
    # Test if port is available
    test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        test_sock.bind((host, port))
        print(f"Port {port} is available")
        test_sock.close()
    except Exception as e:
        print(f"Port {port} is still in use: {e}")
        # Try one more kill
        kill_process_on_port(port)
        await asyncio.sleep(2)
        try:
            test_sock.bind((host, port))
            print(f"Port {port} now available after second kill")
            test_sock.close()
        except Exception as e2:
            print(f"Port {port} still unavailable: {e2}")
            return
    
    # Start health check server
    health_thread = threading.Thread(target=run_health_server, args=(port,), daemon=True)
    health_thread.start()
    
    print("=" * 70)
    print("GREENMIND MCP SERVER - RUNNING")
    print("=" * 70)
    
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
    print("=" * 70)
    
    await server.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\nError: {str(e)}")