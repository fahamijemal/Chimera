import sys
from typing import Dict, Any, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack

class SkillExecutor:
    """
    Executes Agent Skills via Real MCP Tool calls.
    Manages the lifecycle of MCP connections.
    """
    
    def __init__(self, server_script_path: str = "./chimera/mcp/servers/news_server.py"):
        self.server_script_path = server_script_path
        self._exit_stack = AsyncExitStack()
        self._session: Optional[ClientSession] = None

    async def initialize(self):
        """
        Starts the MCP server subprocess and initializes the session.
        """
        # Define server parameters
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[self.server_script_path],
            env=None # Inherit env
        )
        
        # Connect via stdio
        read, write = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(read, write)
        )
        
        # Initialize the session
        await self._session.initialize()

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a real MCP tool.
        """
        # Validate against Skill Definitions (Contract)
        self._validate_tool_call(tool_name, arguments)

        if not self._session:
            await self.initialize()
            
        try:
            result = await self._session.call_tool(tool_name, arguments)
            return {
                "status": "success",
                "tool": tool_name,
                "result": result.content[0].text if result.content else "No output"
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }

    async def list_tools(self) -> list:
        """
        Lists available tools from the connected MCP server.
        """
        if not self._session:
            await self.initialize()
            
        try:
            # Note: The MCP SDK ClientSession typically exposes list_tools
            result = await self._session.list_tools()
            return result.tools
        except Exception:
            return []

    def _validate_tool_call(self, tool_name: str, arguments: Dict[str, Any]):
        """
        Validates arguments against known schemas (Skills Contract).
        This matches the logic defined in skills/README.md.
        """
        if tool_name == "generate_image":
            if "character_id" not in arguments:
                raise ValueError("character_id is required for generate_image")
            if "prompt" not in arguments:
                raise ValueError("prompt is required for generate_image")
        
        if tool_name == "post_tweet":
            if "content" not in arguments:
                raise ValueError("content is required for post_tweet")

    async def cleanup(self):
        """
        Closes connections.
        """
        await self._exit_stack.aclose()
