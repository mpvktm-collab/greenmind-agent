# src/mcp/servers/greenmind_server.py
import asyncio
import json
import logging
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime

from ..protocol.messages import (
    MCPMessage, MessageType, PingMessage, PongMessage,
    ListToolsMessage, ToolsListMessage, CallToolMessage,
    ToolResultMessage, ErrorMessage, RegisterToolMessage,
    ToolRegisteredMessage, create_message_from_dict
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ToolRegistration:
    """Registration info for a tool"""
    def __init__(self, name: str, handler: Callable, description: str = ""):
        self.name = name
        self.handler = handler
        self.description = description
        self.registered_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for listing"""
        return {
            "name": self.name,
            "description": self.description,
            "registered_at": self.registered_at
        }

class GreenMindMCPServer:
    """MCP Server for GreenMind Agent"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.server_id = f"greenmind_mcp_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.tools: Dict[str, ToolRegistration] = {}
        self.clients = {}
        self.is_running = False
        self.server = None
        logger.info(f"GreenMind MCP Server initialized with ID: {self.server_id}")
    
    def register_tool(self, name: str, handler: Callable, description: str = "") -> Dict[str, Any]:
        """Register a tool with the server"""
        self.tools[name] = ToolRegistration(name, handler, description)
        logger.info(f"Tool registered: {name}")
        return {"status": "registered", "tool": name, "description": description}
    
    async def handle_ping(self, message: PingMessage) -> PongMessage:
        """Handle ping message"""
        logger.debug(f"Handling ping from {message.id}")
        return PongMessage(message.id)
    
    async def handle_list_tools(self, message: ListToolsMessage) -> ToolsListMessage:
        """Handle list tools request"""
        logger.debug(f"Handling list tools request from {message.id}")
        tool_list = [reg.to_dict() for reg in self.tools.values()]
        return ToolsListMessage(tool_list)
    
    async def handle_call_tool(self, message: CallToolMessage) -> Any:
        """Handle tool call request"""
        logger.info(f"Calling tool: {message.tool_name} (ID: {message.id})")
        
        if message.tool_name not in self.tools:
            error_msg = f"Tool '{message.tool_name}' not found"
            logger.error(error_msg)
            return ErrorMessage(message.id, error_msg)
        
        try:
            tool = self.tools[message.tool_name]
            
            # Execute the tool handler
            if asyncio.iscoroutinefunction(tool.handler):
                result = await tool.handler(**message.params)
            else:
                # Run sync function in thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, 
                    lambda: tool.handler(**message.params)
                )
            
            logger.info(f"Tool {message.tool_name} executed successfully")
            return ToolResultMessage(message.id, result)
            
        except Exception as e:
            logger.error(f"Error executing tool {message.tool_name}: {str(e)}")
            return ErrorMessage(message.id, str(e))
    
    async def handle_register_tool(self, message: RegisterToolMessage) -> ToolRegisteredMessage:
        """Handle tool registration request from client"""
        logger.info(f"Registering tool from client: {message.tool_name}")
        
        # This would need a client-to-server tool registration mechanism
        # For now, tools are registered directly on server startup
        
        return ToolRegisteredMessage(message.tool_name, "registered")
    
    async def handle_message(self, data: str) -> str:
        """Handle incoming message"""
        try:
            print(f"RAW RECEIVED: {repr(data)}")  # Important debug line using repr to show special chars
            msg_dict = json.loads(data)
            print(f"PARSED: {msg_dict}")  # Important debug line
            message = create_message_from_dict(msg_dict)
            
            logger.debug(f"Received message: {message.type.value} (ID: {message.id})")
            
            # Route to appropriate handler
            if message.type == MessageType.PING:
                response = await self.handle_ping(message)
            elif message.type == MessageType.LIST_TOOLS:
                response = await self.handle_list_tools(message)
            elif message.type == MessageType.CALL_TOOL:
                response = await self.handle_call_tool(message)
            elif message.type == MessageType.REGISTER_TOOL:
                response = await self.handle_register_tool(message)
            else:
                error_msg = f"Unsupported message type: {message.type.value}"
                logger.warning(error_msg)
                response = ErrorMessage(message.id, error_msg)
            
            return response.to_json()
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {str(e)}")
            print(f"JSON DECODE ERROR: {str(e)}")  # Important debug line
            print(f"RAW DATA THAT FAILED: {repr(data)}")  # Show the raw data that failed
            error_msg = ErrorMessage("unknown", f"Invalid JSON: {str(e)}")
            return error_msg.to_json()
            
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            print(f"ERROR HANDLING MESSAGE: {str(e)}")  # Important debug line
            import traceback
            traceback.print_exc()  # Print full stack trace
            error_msg = ErrorMessage("unknown", f"Server error: {str(e)}")
            return error_msg.to_json()
    
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle client connection"""
        client_address = writer.get_extra_info('peername')
        logger.info(f"Client connected: {client_address}")
        print(f"CLIENT CONNECTED: {client_address}")  # Debug line
        
        try:
            while self.is_running:
                # Read message (4-byte length prefix + data)
                data_length_bytes = await reader.read(4)
                if not data_length_bytes:
                    break
                
                data_length = int.from_bytes(data_length_bytes, byteorder='big')
                print(f"Received message length: {data_length}")  # Debug line
                data = await reader.read(data_length)
                
                if not data:
                    break
                
                # Process message
                response = await self.handle_message(data.decode('utf-8'))
                
                # Send response (4-byte length prefix + data)
                response_bytes = response.encode('utf-8')
                writer.write(len(response_bytes).to_bytes(4, byteorder='big'))
                writer.write(response_bytes)
                await writer.drain()
                
        except asyncio.CancelledError:
            logger.info(f"Client handler cancelled for {client_address}")
            print(f"CLIENT HANDLER CANCELLED: {client_address}")  # Debug line
            
        except Exception as e:
            logger.error(f"Error handling client {client_address}: {str(e)}")
            print(f"CLIENT HANDLER ERROR: {str(e)}")  # Debug line
            import traceback
            traceback.print_exc()
            
        finally:
            writer.close()
            await writer.wait_closed()
            logger.info(f"Client disconnected: {client_address}")
            print(f"CLIENT DISCONNECTED: {client_address}")  # Debug line
    
    async def start(self):
        """Start the MCP server"""
        self.is_running = True
        logger.info(f"Starting GreenMind MCP Server on {self.host}:{self.port}")
        print(f"STARTING SERVER ON {self.host}:{self.port}")  # Debug line
        
        # Create server
        self.server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )
        
        logger.info(f"GreenMind MCP Server started on {self.host}:{self.port}")
        print(f"SERVER STARTED ON {self.host}:{self.port}")  # Debug line
        return {
            "status": "running",
            "server_id": self.server_id,
            "address": f"{self.host}:{self.port}",
            "tools_registered": len(self.tools)
        }
    
    async def stop(self):
        """Stop the MCP server"""
        self.is_running = False
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        logger.info("GreenMind MCP Server stopped")
        print("SERVER STOPPED")  # Debug line
        return {"status": "stopped"}
    
    async def run(self):
        """Run the server"""
        await self.start()
        try:
            async with self.server:
                await self.server.serve_forever()
        except KeyboardInterrupt:
            logger.info("Server stopped by keyboard interrupt")
            print("SERVER STOPPED BY KEYBOARD INTERRUPT")  # Debug line
            await self.stop()
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
            print(f"SERVER ERROR: {str(e)}")  # Debug line
            await self.stop()

# For running directly
async def main():
    server = GreenMindMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())