# __init__.py
"""MCP server package"""
import asyncio
from .server import mcp


def main():
    """Entry point for MCP server"""
    try:
        # Use SSE transport explicitly like the working CLI version
        mcp.run(transport="sse")
    except KeyboardInterrupt:
        import logging

        logger = logging.getLogger(__name__)
        logger.info("Server stopped by user")
    except Exception as e:
        import sys
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Failed to start MCP server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
