#!/usr/bin/env python3
"""Test MCP server directly with stdio protocol"""

import json
import subprocess
import asyncio

async def test_mcp_call():
    # Start the MCP server
    proc = await asyncio.create_subprocess_exec(
        'mcp-server-conduit', '--transport', 'stdio',
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Send initialize request
    init_request = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0"}
        },
        "id": 1
    }
    
    proc.stdin.write((json.dumps(init_request) + '\n').encode())
    await proc.stdin.drain()
    
    # Read response
    response = await proc.stdout.readline()
    print("Initialize response:", response.decode())
    
    # Send initialized notification
    initialized = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    }
    proc.stdin.write((json.dumps(initialized) + '\n').encode())
    await proc.stdin.drain()
    
    # Call our tool with attachments
    tool_call = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "create_confluence_page_from_markdown",
            "arguments": {
                "space": "ASEP",
                "title": "Direct MCP Test",
                "content": "Test content",
                "site_alias": "saaga",
                "attachments": [
                    {
                        "local_path": "/tmp/test.txt",
                        "name_on_confluence": "test.txt"
                    }
                ]
            }
        },
        "id": 2
    }
    
    print("\nSending tool call:", json.dumps(tool_call, indent=2))
    proc.stdin.write((json.dumps(tool_call) + '\n').encode())
    await proc.stdin.drain()
    
    # Read response
    response = await proc.stdout.readline()
    print("\nTool response:", response.decode())
    
    # Read any stderr
    stderr = await proc.stderr.read()
    if stderr:
        print("\nServer stderr:", stderr.decode())
    
    proc.terminate()
    await proc.wait()

if __name__ == "__main__":
    asyncio.run(test_mcp_call())