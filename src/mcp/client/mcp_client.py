# src/mcp/client/mcp_client.py
import requests
import logging

logger = logging.getLogger(__name__)

class MCPClient:
    def __init__(self, host: str = "localhost", port: int = 8000):
        self.host = host
        self.port = port
        self.base_url = f"https://{host}"
        self.connected = False

    async def connect(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/tools", timeout=30)
            if response.status_code == 200:
                self.connected = True
                logger.info(f"Connected to {self.base_url}")
                return True
            return False
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    async def disconnect(self):
        self.connected = False

    async def call_tool(self, tool_name: str, **params):
        if not self.connected:
            await self.connect()
        try:
            payload = {"tool": tool_name, "input": params.get("input", "")}
            response = requests.post(
                f"{self.base_url}/call_tool",
                json=payload,
                timeout=60
            )
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}")
            data = response.json()
            if "error" in data:
                raise Exception(data["error"])
            return data.get("result")
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            raise

    async def list_tools(self):
        try:
            response = requests.get(f"{self.base_url}/tools", timeout=10)
            if response.status_code == 200:
                return response.json()
            return {"tools": []}
        except Exception:
            return {"tools": []}