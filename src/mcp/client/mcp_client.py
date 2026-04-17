# -*- coding: utf-8 -*-
import requests
import logging
import asyncio

logger = logging.getLogger(__name__)

class MCPClient:
    def __init__(self, host: str = "localhost", port: int = 8000, timeout: int = 60):
        self.host = host
        self.port = port
        self.timeout = timeout
        # Use HTTPS for remote hosts, HTTP for localhost
        if host != "localhost":
            self.base_url = f"https://{host}"
        else:
            self.base_url = f"http://{host}:{port}"
        self.connected = False

    async def connect(self, retries: int = 2) -> bool:
        """Attempt to connect to the MCP server with retries."""
        for attempt in range(retries):
            try:
                response = requests.get(
                    f"{self.base_url}/tools",
                    timeout=self.timeout
                )
                if response.status_code == 200:
                    self.connected = True
                    logger.info(f"Connected to MCP server at {self.base_url}")
                    return True
                else:
                    logger.warning(f"Attempt {attempt+1}: Server returned {response.status_code}")
            except requests.exceptions.Timeout:
                logger.warning(f"Attempt {attempt+1}: Connection timeout after {self.timeout}s")
            except Exception as e:
                logger.warning(f"Attempt {attempt+1}: {str(e)}")
            if attempt < retries - 1:
                await asyncio.sleep(2)
        self.connected = False
        logger.error(f"Failed to connect to {self.base_url} after {retries} attempts")
        return False

    async def disconnect(self):
        self.connected = False
        logger.info("Disconnected from MCP server")

    async def call_tool(self, tool_name: str, **params):
        if not self.connected:
            # Try to reconnect once
            if not await self.connect(retries=1):
                raise Exception("Client is not connected to MCP server")
        try:
            payload = {"tool": tool_name, "input": params.get("input", "")}
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
            # Mark as disconnected so next call will retry connection
            self.connected = False
            raise

    async def list_tools(self):
        try:
            response = requests.get(f"{self.base_url}/tools", timeout=10)
            if response.status_code == 200:
                return response.json()
            return {"tools": []}
        except Exception:
            return {"tools": []}