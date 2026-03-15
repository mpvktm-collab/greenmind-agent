# src/mcp/protocol/messages.py
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import uuid

class MessageType(Enum):
    """MCP message types"""
    PING = "ping"
    PONG = "pong"
    LIST_TOOLS = "list_tools"
    TOOLS_LIST = "tools_list"
    CALL_TOOL = "call_tool"
    TOOL_RESULT = "tool_result"
    ERROR = "error"
    REGISTER_TOOL = "register_tool"
    TOOL_REGISTERED = "tool_registered"

class MCPMessage:
    """Base MCP message class"""
    
    def __init__(self, msg_type: MessageType, msg_id: Optional[str] = None):
        self.type = msg_type
        self.id = msg_id or str(uuid.uuid4())
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "type": self.type.value,
            "id": self.id,
            "timestamp": self.timestamp
        }
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPMessage':
        """Create message from dictionary"""
        return cls(MessageType(data["type"]), data.get("id"))

class PingMessage(MCPMessage):
    """Ping message for health checks"""
    def __init__(self, msg_id: Optional[str] = None):
        super().__init__(MessageType.PING, msg_id)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PingMessage':
        return cls(data.get("id"))

class PongMessage(MCPMessage):
    """Pong response message"""
    def __init__(self, ping_id: str, msg_id: Optional[str] = None):
        super().__init__(MessageType.PONG, msg_id)
        self.ping_id = ping_id
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["ping_id"] = self.ping_id
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PongMessage':
        return cls(data.get("ping_id"), data.get("id"))

class ListToolsMessage(MCPMessage):
    """Request list of available tools"""
    def __init__(self, msg_id: Optional[str] = None):
        super().__init__(MessageType.LIST_TOOLS, msg_id)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ListToolsMessage':
        return cls(data.get("id"))

class ToolsListMessage(MCPMessage):
    """Response with list of tools"""
    def __init__(self, tools: List[Dict[str, Any]], msg_id: Optional[str] = None):
        super().__init__(MessageType.TOOLS_LIST, msg_id)
        self.tools = tools
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["tools"] = self.tools
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolsListMessage':
        return cls(data.get("tools", []), data.get("id"))

class CallToolMessage(MCPMessage):
    """Request to call a specific tool"""
    def __init__(self, tool_name: str, params: Dict[str, Any], msg_id: Optional[str] = None):
        super().__init__(MessageType.CALL_TOOL, msg_id)
        self.tool_name = tool_name
        self.params = params
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["tool"] = self.tool_name
        data["params"] = self.params
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CallToolMessage':
        return cls(data.get("tool"), data.get("params", {}), data.get("id"))

class ToolResultMessage(MCPMessage):
    """Response from tool execution"""
    def __init__(self, call_id: str, result: Any, msg_id: Optional[str] = None):
        super().__init__(MessageType.TOOL_RESULT, msg_id)
        self.call_id = call_id
        self.result = result
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["call_id"] = self.call_id
        data["result"] = self.result
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolResultMessage':
        return cls(data.get("call_id"), data.get("result"), data.get("id"))

class ErrorMessage(MCPMessage):
    """Error response message"""
    def __init__(self, original_id: str, error: str, msg_id: Optional[str] = None):
        super().__init__(MessageType.ERROR, msg_id)
        self.original_id = original_id
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["original_id"] = self.original_id
        data["error"] = self.error
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ErrorMessage':
        return cls(data.get("original_id"), data.get("error"), data.get("id"))

class RegisterToolMessage(MCPMessage):
    """Register a tool with the server"""
    def __init__(self, tool_name: str, description: str = "", msg_id: Optional[str] = None):
        super().__init__(MessageType.REGISTER_TOOL, msg_id)
        self.tool_name = tool_name
        self.description = description
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["tool_name"] = self.tool_name
        data["description"] = self.description
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RegisterToolMessage':
        return cls(data.get("tool_name"), data.get("description", ""), data.get("id"))

class ToolRegisteredMessage(MCPMessage):
    """Confirmation that tool was registered"""
    def __init__(self, tool_name: str, status: str = "registered", msg_id: Optional[str] = None):
        super().__init__(MessageType.TOOL_REGISTERED, msg_id)
        self.tool_name = tool_name
        self.status = status
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["tool_name"] = self.tool_name
        data["status"] = self.status
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolRegisteredMessage':
        return cls(data.get("tool_name"), data.get("status", "registered"), data.get("id"))

# Message factory to create appropriate message from dict
def create_message_from_dict(data: Dict[str, Any]) -> MCPMessage:
    """Factory function to create the appropriate message type from a dictionary"""
    msg_type = MessageType(data["type"])
    
    if msg_type == MessageType.PING:
        return PingMessage.from_dict(data)
    elif msg_type == MessageType.PONG:
        return PongMessage.from_dict(data)
    elif msg_type == MessageType.LIST_TOOLS:
        return ListToolsMessage.from_dict(data)
    elif msg_type == MessageType.TOOLS_LIST:
        return ToolsListMessage.from_dict(data)
    elif msg_type == MessageType.CALL_TOOL:
        return CallToolMessage.from_dict(data)
    elif msg_type == MessageType.TOOL_RESULT:
        return ToolResultMessage.from_dict(data)
    elif msg_type == MessageType.ERROR:
        return ErrorMessage.from_dict(data)
    elif msg_type == MessageType.REGISTER_TOOL:
        return RegisterToolMessage.from_dict(data)
    elif msg_type == MessageType.TOOL_REGISTERED:
        return ToolRegisteredMessage.from_dict(data)
    else:
        raise ValueError(f"Unknown message type: {msg_type}")