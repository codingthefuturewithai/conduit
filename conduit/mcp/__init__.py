# __init__.py
from .server import mcp


def main():
    """Entry point for MCP server"""
    try:
        mcp.run()
    except Exception as e:
        import sys
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Failed to start MCP server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
