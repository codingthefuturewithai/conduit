#!/usr/bin/env python3
"""Test how MCP servers expose tool documentation to clients"""

import asyncio
import json
from mcp.server.fastmcp import FastMCP
import mcp.types as types

# Create a test server
mcp = FastMCP("TestDocServer")

@mcp.tool(
    name="example_tool",
    description="This is the decorator description that shows in tool listing"
)
async def example_tool(param1: str, param2: int = 42) -> list[types.TextContent]:
    """This is the function docstring - does it get exposed?
    
    Args:
        param1: First parameter description
        param2: Second parameter with default
        
    Returns:
        A text response
    """
    return [types.TextContent(type="text", text=f"Got {param1} and {param2}")]

@mcp.tool()  # No explicit description
async def tool_with_only_docstring(value: str) -> list[types.TextContent]:
    """This tool only has a docstring, no decorator description.
    
    It should be interesting to see what clients receive.
    """
    return [types.TextContent(type="text", text=f"Value: {value}")]

async def main():
    # List all tools to see what documentation is exposed
    tools = await mcp.list_tools()
    
    print("=== MCP Tool Documentation Discovery ===\n")
    
    for tool in tools:
        print(f"Tool: {tool.name}")
        print(f"Description: {tool.description}")
        print(f"Input Schema:")
        print(json.dumps(tool.inputSchema, indent=2))
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(main())