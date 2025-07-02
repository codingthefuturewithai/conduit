#!/usr/bin/env python3
"""Test MCP client to verify parameter passing"""

import asyncio
import json
import subprocess

async def test_mcp_protocol():
    # Start the test server
    proc = await asyncio.create_subprocess_exec(
        'python', 'test_mcp_server.py', '--stdio',
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
    print("Initialize response:", json.loads(response))
    
    # Send initialized notification
    initialized = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    }
    proc.stdin.write((json.dumps(initialized) + '\n').encode())
    await proc.stdin.drain()
    
    # Call tool with attachments
    tool_call = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "test_attachments",
            "arguments": {
                "title": "Test Title",
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
    print("\nTool response:", json.loads(response))
    
    # Read stderr
    stderr = await proc.stderr.read()
    if stderr:
        print("\nServer stderr:")
        print(stderr.decode())
    
    proc.terminate()
    await proc.wait()

if __name__ == "__main__":
    asyncio.run(test_mcp_protocol())