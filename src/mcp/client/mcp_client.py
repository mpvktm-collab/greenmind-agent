# src/mcp/client/mcp_client.py
import asyncio
import json
import logging
import ssl
from typing import Dict, Any, Optional, List

from ..protocol.messages import (
    MCPMessage, PingMessage, ListToolsMessage,
    CallToolMessage, create_message_from_dict
)

logger = logging.getLogger(__name__)

class MCPClient:
    """MCP Client for connecting to GreenMind MCP Server"""
    
    def __init__(self, host: str = "localhost", port: int = 8765, use_ssl: bool = False):
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.reader = None
        self.writer = None
        self.connected = False
    
    async def connect(self):
        """Connect to MCP server with optional SSL support"""
        try:
            print(f"Connecting to {self.host}:{self.port} (SSL: {self.use_ssl})")
            
            if self.use_ssl:
                # Create SSL context for secure connection
                ssl_context = ssl.create_default_context()
                # For self-signed certificates or testing, you might need:
                # ssl_context.check_hostname = False
                # ssl_context.verify_mode = ssl.CERT_NONE
                
                self.reader, self.writer = await asyncio.open_connection(
                    self.host, self.port, ssl=ssl_context
                )
            else:
                self.reader, self.writer = await asyncio.open_connection(
                    self.host, self.port
                )
            
            self.connected = True
            print(f"Successfully connected to {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Connection failed: {str(e)}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        if self.writer:
            self.writer.close()
            try:
                await self.writer.wait_closed()
            except:
                pass
        self.connected = False
        print("Disconnected from MCP server")
    
    async def send_message(self, message: MCPMessage) -> Dict[str, Any]:
        """Send a message to the server and wait for response"""
        if not self.connected:
            raise Exception("Not connected to server")
        
        # Send message (4-byte length prefix + data)
        message_json = message.to_json()
        message_bytes = message_json.encode()
        
        self.writer.write(len(message_bytes).to_bytes(4, byteorder='big'))
        self.writer.write(message_bytes)
        await self.writer.drain()
        
        # Read response (4-byte length prefix + data)
        data_length_bytes = await self.reader.read(4)
        if not data_length_bytes:
            raise Exception("Connection closed by server")
        
        data_length = int.from_bytes(data_length_bytes, byteorder='big')
        data = await self.reader.read(data_length)
        
        # Parse response
        response = json.loads(data.decode())
        return response
    
    async def ping(self) -> bool:
        """Send ping to server"""
        try:
            response = await self.send_message(PingMessage())
            return response.get("type") == "pong"
        except Exception as e:
            print(f"Ping failed: {str(e)}")
            return False
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools"""
        response = await self.send_message(ListToolsMessage())
        if response.get("type") == "tools_list":
            return response.get("tools", [])
        elif response.get("type") == "error":
            raise Exception(response.get("error", "Unknown error"))
        return []
    
    async def call_tool(self, tool_name: str, **params) -> Any:
        """Call a specific tool"""
        response = await self.send_message(CallToolMessage(tool_name, params))
        if response.get("type") == "tool_result":
            return response.get("result")
        elif response.get("type") == "error":
            raise Exception(response.get("error", "Unknown error"))
        else:
            raise Exception(f"Unexpected response type: {response.get('type')}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()