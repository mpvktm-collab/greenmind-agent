# -*- coding: utf-8 -*-
import requests
import logging

logger = logging.getLogger(__name__)


class MCPClient:
    """
    HTTP-based MCP Client for GreenMind
    Communicates with the MCP server using REST APIs.
    """

    def __init__(self, host: str = "localhost", port: int = 8000):
        """
        Initialize client with server host and port.
        """
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.connected = False

    async def connect(self) -> bool:
        """
        Test connection to MCP server.
        """
        try:
            response = requests.get(f"{self.base_url}/tools", timeout=10)

            if response.status_code == 200:
                self.connected = True
                logger.info(f"Connected to MCP server at {self.base_url}")
                return True
            else:
                logger.error(f"Server returned non-200 response: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            self.connected = False
            return False

    async def disconnect(self):
        """
        Disconnect client.
        """
        self.connected = False
        logger.info("Disconnected from MCP server")

    async def call_tool(self, tool_name: str, **params):
        """
        Call a tool on the MCP server.
        """
        if not self.connected:
            raise Exception("Client is not connected to MCP server")

        try:
            payload = {
                "tool": tool_name,
                "input": params.get("input", "")
            }

            response = requests.post(
                f"{self.base_url}/call_tool",
                json=payload,
                timeout=60
            )

            if response.status_code != 200:
                raise Exception(f"Server error: HTTP {response.status_code}")

            data = response.json()

            if "error" in data:
                raise Exception(data["error"])

            return data.get("result")

        except Exception as e:
            logger.error(f"Tool call failed: {str(e)}")
            raise

    async def list_tools(self):
        """
        Fetch available tools from server.
        """
        try:
            response = requests.get(f"{self.base_url}/tools", timeout=10)
            if response.status_code == 200:
                return response.json()
            return {"tools": []}
        except Exception:
            return {"tools": []}