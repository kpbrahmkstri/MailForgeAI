from src.mcp.registry import call_tool

# Import tools so they register
from src.mcp.tools import template_tool
from src.mcp.tools import contacts_tool
from src.mcp.tools import policy_tool


class MCPServer:

    def call(self, tool_name: str, payload: dict):
        return call_tool(tool_name, payload)


mcp = MCPServer()