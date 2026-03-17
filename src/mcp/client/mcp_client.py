# src/mcp/client/mcp_client.py
import requests
import logging

logger = logging.getLogger(__name__)


class MCPClient:
    """
    HTTP-based MCP Client for GreenMind
    Communicates with the MCP server deployed on Render using REST APIs.
    """

    def __init__(self, host: str):
        """
        Initialize client with server host.

        Example:
        host = "greenmind-mcp.onrender.com"
        """
        self.host = host
        self.base_url = f"https://{host}"
        self.connected = False

    async def connect(self) -> bool:
        """
        Test connection to MCP server.
        """
        try:
            response = requests.get(self.base_url, timeout=10)

            if response.status_code == 200:
                self.connected = True
                logger.info("Connected to MCP server")
                return True
            else:
                logger.error("Server returned non-200 response")
                return False

        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            self.connected = False
            return False

    async def disconnect(self):
        """
        Disconnect client (no persistent socket so just reset state).
        """
        self.connected = False
        logger.info("Disconnected from MCP server")

    async def call_tool(self, tool_name: str, **params):
        """
        Call a tool on the MCP server.

        Example request:
        POST /call_tool
        {
            "tool": "Carbon_Footprint_Calculator",
            "input": "delhi"
        }
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
                raise Exception(
                    f"Server error: HTTP {response.status_code}"
                )

            data = response.json()

            if "error" in data:
                raise Exception(data["error"])

            return data.get("result")

        except Exception as e:
            logger.error(f"Tool call failed: {str(e)}")
            raise

    async def list_tools(self):
        """
        Optional method to fetch available tools from server.
        Requires /tools endpoint on server.
        """

        try:

            response = requests.get(
                f"{self.base_url}/tools",
                timeout=10
            )

            if response.status_code == 200:
                return response.json()

            return []

        except Exception:
            return []