#!/usr/bin/env python3
"""Test complete MCP server discovery including tools, resources, and prompts"""

import asyncio
import json
from mcp.server.fastmcp import FastMCP
import mcp.types as types
from typing import List, Optional

# Create a test server
mcp = FastMCP("TestFullServer")

# Add some tools
@mcp.tool(description="Add two numbers together")
async def add(a: int, b: int) -> list[types.TextContent]:
    """Adds two integers and returns the result."""
    return [types.TextContent(type="text", text=str(a + b))]

@mcp.tool()
async def complex_tool(
    required_str: str,
    optional_str: Optional[str] = None,
    number_list: List[int] = None,
    flag: bool = False
) -> list[types.TextContent]:
    """A complex tool demonstrating various parameter types.
    
    This shows how different parameter types are exposed in the schema.
    """
    result = f"Required: {required_str}\n"
    result += f"Optional: {optional_str}\n"
    result += f"Numbers: {number_list}\n"
    result += f"Flag: {flag}"
    return [types.TextContent(type="text", text=result)]

# Add a resource
@mcp.resource(uri="test://example", name="Example Resource")
async def example_resource() -> str:
    """An example resource for testing."""
    return "This is example resource content"

# Add a prompt
@mcp.prompt(name="greeting", description="Generate a greeting message")
async def greeting_prompt(name: str = "World") -> list[types.PromptMessage]:
    """Create a personalized greeting."""
    return [types.PromptMessage(
        role="user",
        content=types.TextContent(type="text", text=f"Hello, {name}!")
    )]

async def main():
    print("=== MCP Server Complete Discovery ===\n")
    
    # 1. Server Info
    print("SERVER INFO:")
    print(f"Name: {mcp.name}")
    print(f"Version: {mcp.version if hasattr(mcp, 'version') else 'N/A'}")
    print("\n" + "="*50 + "\n")
    
    # 2. List Tools
    tools = await mcp.list_tools()
    print(f"TOOLS ({len(tools)} available):\n")
    for tool in tools:
        print(f"Tool: {tool.name}")
        print(f"Description: {tool.description}")
        print(f"Schema: {json.dumps(tool.inputSchema, indent=2)}")
        print("-" * 30)
    print("\n" + "="*50 + "\n")
    
    # 3. List Resources
    resources = await mcp.list_resources()
    print(f"RESOURCES ({len(resources)} available):\n")
    for resource in resources:
        print(f"URI: {resource.uri}")
        print(f"Name: {resource.name}")
        print(f"Description: {resource.description}")
        print(f"MIME Type: {resource.mimeType}")
        print("-" * 30)
    print("\n" + "="*50 + "\n")
    
    # 4. List Prompts
    prompts = await mcp.list_prompts()
    print(f"PROMPTS ({len(prompts)} available):\n")
    for prompt in prompts:
        print(f"Name: {prompt.name}")
        print(f"Description: {prompt.description}")
        if hasattr(prompt, 'arguments'):
            print(f"Arguments: {prompt.arguments}")
        print("-" * 30)

if __name__ == "__main__":
    asyncio.run(main())