#!/usr/bin/env python3
"""Standalone MCP server script for Conduit"""

import asyncio
import logging
import sys
from mcp.server.fastmcp import FastMCP
from mcp.server.stdio import stdio_server
from .server import main

# Configure logging
logging.basicConfig(
    stream=sys.stderr,
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("conduit.mcp")

# Create server instance
mcp = FastMCP(
    "Conduit",
    host="localhost",  # Not used in stdio mode but required
    port=8000,  # Not used in stdio mode but required
    debug=True,
    log_level="DEBUG",
)


async def main():
    """Run the MCP server in stdio mode"""
    try:
        options = mcp.create_initialization_options()
        async with stdio_server() as (read_stream, write_stream):
            await mcp.run(read_stream, write_stream, options, raise_exceptions=True)
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
