#!/usr/bin/env python3
"""Test how Conduit MCP server exposes tool documentation"""

import asyncio
import json
import sys
from conduit.mcp.server import create_mcp_server

async def main():
    # Create the Conduit MCP server
    server = create_mcp_server()
    
    # List all tools
    tools = await server.list_tools()
    
    print("=== Conduit MCP Server Tool Documentation ===\n")
    print(f"Total tools available: {len(tools)}\n")
    
    # Group tools by category for better readability
    jira_tools = []
    confluence_tools = []
    other_tools = []
    
    for tool in tools:
        if 'jira' in tool.name.lower():
            jira_tools.append(tool)
        elif 'confluence' in tool.name.lower():
            confluence_tools.append(tool)
        else:
            other_tools.append(tool)
    
    # Display tools by category
    def print_tool_info(tool):
        print(f"**{tool.name}**")
        print(f"Description: {tool.description}")
        
        # Check if there are required vs optional parameters
        schema = tool.inputSchema
        required = schema.get('required', [])
        properties = schema.get('properties', {})
        
        print("Parameters:")
        for param_name, param_info in properties.items():
            is_required = param_name in required
            param_type = param_info.get('type', 'unknown')
            default = param_info.get('default', 'N/A')
            
            # Handle complex types
            if 'anyOf' in param_info:
                types = [t.get('type', 'unknown') for t in param_info['anyOf']]
                param_type = ' | '.join(types)
            
            status = "required" if is_required else f"optional (default: {default})"
            print(f"  - {param_name}: {param_type} [{status}]")
        
        print()
    
    print("## Other Tools\n")
    for tool in other_tools:
        print_tool_info(tool)
    
    print("## JIRA Tools\n")
    for tool in jira_tools:
        print_tool_info(tool)
    
    print("## Confluence Tools\n")
    for tool in confluence_tools:
        print_tool_info(tool)
    
    # Also show a sample of the raw schema for one complex tool
    print("\n## Raw Schema Example (create_confluence_page_from_markdown):\n")
    for tool in tools:
        if tool.name == "create_confluence_page_from_markdown":
            print(json.dumps(tool.inputSchema, indent=2))
            break

if __name__ == "__main__":
    asyncio.run(main())