# FastMCP/Uvicorn Logging Implementation Instructions

## Overview

These instructions are based on a working implementation that successfully handles logging in a FastAPI/Uvicorn application, ensuring visibility of logs from all components including Uvicorn middleware and application endpoints.

## Key Implementation Details

The solution is based on the following principles:

1. Early logging configuration (before any other imports)
2. Proper handling of Uvicorn loggers
3. Consistent use of stdout for log output
4. Proper logger hierarchy and propagation

## Implementation Steps

### 1. Create Logging Configuration Module

Create a new file at `conduit/mcp/logging_config.py`:

```python
"""Logging configuration for the MCP server"""
import logging
import sys

def configure_logging(log_level: str = "INFO") -> None:
    """Configure logging for the MCP server

    Args:
        log_level: Log level to use (default: INFO)
    """
    # Get log level from string
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure basic logging to stdout
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],  # Critical: Use stdout
    )

    # Configure standard formatter with source context
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.getLogger().handlers[0].setFormatter(formatter)

    # Get our application logger
    logger = logging.getLogger("conduit.mcp")
    logger.handlers = []  # Remove any handlers to ensure inheritance
    logger.propagate = True  # Make sure it inherits from root

    # Critical: Configure Uvicorn loggers to ensure their logs are visible
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers = []  # Remove any existing handlers
        uvicorn_logger.propagate = True  # Ensure logs propagate to root
```

### 2. Update Server Module

Modify your server initialization code to configure logging early. In `conduit/mcp/server.py`:

```python
from .logging_config import configure_logging

def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server instance"""
    # Configure logging first, before any other operations
    configure_logging("DEBUG")  # Or get from environment

    logger = logging.getLogger("conduit.mcp")
    logger.info("Creating FastMCP server")

    server = FastMCP(
        "Conduit",
        host="localhost",
        port=8000,
        debug=True,
        log_level="DEBUG",
    )

    return server
```

### 3. Update Module Initialization

In your module's `__init__.py`, ensure logging is configured before any other operations:

```python
"""MCP server package"""
import asyncio
import logging
import sys
from .logging_config import configure_logging
from .server import server, create_mcp_server

__all__ = ["server", "create_mcp_server"]

def main(transport: str = "stdio"):
    """Entry point for MCP server"""
    try:
        # Configure logging first
        configure_logging()
        logger = logging.getLogger(__name__)

        if transport == "stdio":
            asyncio.run(server.run_stdio_async())
        else:
            asyncio.run(server.run_sse_async())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}", exc_info=True)
        sys.exit(1)
```

## Key Points to Remember

1. **Use stdout, not stderr**

   - The implementation specifically uses `sys.stdout` for logging
   - This is critical for proper log visibility with Uvicorn

2. **Logger Hierarchy**

   - Application loggers should have no handlers of their own
   - Set `propagate=True` to ensure logs flow up to the root logger
   - This ensures consistent formatting and output

3. **Uvicorn Logger Configuration**

   - Configure Uvicorn loggers before Uvicorn starts
   - Remove their handlers and set `propagate=True`
   - This ensures Uvicorn logs are visible and properly formatted

4. **Early Configuration**
   - Configure logging before any other imports or operations
   - This ensures all logs are captured from the start

## Testing the Implementation

1. Start your server and verify you see startup logs
2. Make a request to an endpoint and verify you see:
   - Uvicorn access logs
   - Your application logs
   - Any middleware logs

## Troubleshooting

If logs are not visible:

1. Verify logging is configured before Uvicorn starts
2. Check that you're using `sys.stdout` not `sys.stderr`
3. Ensure all loggers have `propagate=True`
4. Verify no handlers are attached to individual loggers

## Example Log Output

When properly configured, you should see logs like this:

```
2024-03-26 16:45:23 - server.py:45 - INFO - Creating FastMCP server
2024-03-26 16:45:23 - uvicorn.error:45 - INFO - Started server process
2024-03-26 16:45:23 - uvicorn.error:45 - INFO - Waiting for application startup
2024-03-26 16:45:23 - middleware.py:45 - DEBUG - Request started path=/api/health
```
