# __init__.py
"""MCP server package"""
from .server import mcp

__all__ = ["mcp"]


def main(transport: str = "sse"):
    """Entry point for MCP server

    Args:
        transport: Transport mode to use ("sse" or "stdio")
    """
    try:
        if transport == "stdio":
            asyncio.run(mcp.run_stdio_async())
        else:
            asyncio.run(mcp.run_sse_async())
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
