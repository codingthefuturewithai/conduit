#!/usr/bin/env python3
"""Test what parameters are actually received by MCP server"""

import asyncio
import json
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
from typing import List
import mcp.types as types

class TestAttachment(BaseModel):
    path: str
    name: str

mcp = FastMCP("TestServer")

@mcp.tool(name="test_params")
async def test_params(
    simple: str,
    number: int,
    attachments: List[TestAttachment] = None
) -> list[types.TextContent]:
    """Test parameter passing"""
    result = "Received parameters:\n"
    result += f"- simple: {simple} (type: {type(simple).__name__})\n"
    result += f"- number: {number} (type: {type(number).__name__})\n"
    result += f"- attachments: {attachments} (type: {type(attachments).__name__})\n"
    
    if attachments:
        result += "\nAttachments detail:\n"
        for i, att in enumerate(attachments):
            result += f"  {i}: {att} (type: {type(att).__name__})\n"
            result += f"     path={att.path}, name={att.name}\n"
    
    return [types.TextContent(type="text", text=result)]

async def main():
    # Get the schema
    tools = await mcp.list_tools()
    for tool in tools:
        if tool.name == "test_params":
            print("Tool schema:")
            print(json.dumps(tool.model_dump()['inputSchema'], indent=2))
            
    # Test direct call
    print("\nDirect call test:")
    result = await test_params(
        simple="hello",
        number=42,
        attachments=[TestAttachment(path="/tmp/file.txt", name="test.txt")]
    )
    print(result[0].text)

if __name__ == "__main__":
    asyncio.run(main())