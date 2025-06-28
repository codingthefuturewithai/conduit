# FastAPI/Uvicorn Logging Implementation Guide

## Background and Problem Statement

### Current MCP Server Logging Issues

The MCP (Machine Control Protocol) server currently has a critical logging visibility problem:

1. **Limited Log Visibility**
   - Only the initial MCP server startup logs are visible
   - Logs from MCP server endpoint functions (tool handlers) are not showing up
   - Logs from backend code called by these endpoints are not visible
   - This severely impacts our ability to debug and monitor the server's operation

The root cause appears to be:

- Logger configuration is not properly propagating to child loggers
- Logging setup may be happening too late in the startup process
- Logger hierarchy is not properly established between the MCP server and its endpoint functions

This is particularly problematic because:

- We cannot see what's happening inside our tool handler functions
- Debug logs from backend service calls are invisible
- Error tracking and debugging becomes extremely difficult
- No visibility into the execution flow of requests

## Key Implementation Details

The solution is based on the following principles:

1. Early logging configuration (before any other imports)
2. Proper handling of all loggers in the hierarchy
3. Consistent use of stdout for log output
4. Proper logger inheritance and propagation

## Solution Overview

The solution focuses on ensuring all logs are visible throughout the MCP server's operation:

1. **Early Configuration**

   - Configure logging before any module imports
   - Ensure configuration happens before FastAPI/MCP server initialization
   - Set up proper logger hierarchy from the start

2. **Logger Hierarchy**

   - Configure root logger as the primary handler
   - Ensure all child loggers inherit from root
   - Remove any direct handlers from child loggers
   - Enable propagation for all loggers

3. **Unified Output**
   - Direct all logs to stdout for consistency
   - Use a single formatter for all logs
   - Include source context in log messages

## Core Principles

Based on the proven implementation in the backend project, the following principles must be followed:

1. **Single Source of Truth**

   - Use Python's `logging.basicConfig()` for configuration
   - No JSON configuration files
   - No multiple configuration approaches

2. **Stream Output**

   - Use `sys.stdout` explicitly, not stderr
   - All logs should flow through a single stream
   - Consistent visibility in container environments

3. **Root Logger Configuration**

   - Configure the root logger as the primary logging source
   - Single handler attached to root logger only
   - All other loggers inherit from root

4. **Logger Inheritance**
   - Enable propagation (`propagate=True`) for all loggers
   - Remove any direct handlers from child loggers
   - Ensure consistent formatting across all logs

## Implementation Details

### 1. Core Configuration

```python
import logging
import sys

def configure_logging():
    """Configure root logger with stdout handler and source context formatter."""
    # Create formatter with source context
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Configure root logger with stdout
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,  # Base level, can be overridden
        format=formatter._fmt,
        datefmt=formatter.datefmt
    )
```

### 2. Logger Setup

```python
def setup_loggers():
    """Configure specific loggers to inherit from root."""
    # Get the root logger's handler and formatter
    root = logging.getLogger()

    # Configure API logger
    api_logger = logging.getLogger("api")
    # Remove any existing handlers
    api_logger.handlers.clear()
    # Ensure propagation to root
    api_logger.propagate = True

    # Configure Uvicorn loggers
    for name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        logger = logging.getLogger(name)
        # Remove any existing handlers
        logger.handlers.clear()
        # Ensure propagation to root
        logger.propagate = True
```

## Usage Guidelines

1. **Initialization Order**

   - Configure logging before any other application setup
   - Call `configure_logging()` first
   - Then call `setup_loggers()`

2. **Logger Acquisition**

   ```python
   logger = logging.getLogger(__name__)
   # No additional configuration needed - inherits from root
   ```

3. **Log Levels**
   - Default to INFO for production
   - Allow override via environment variables
   - Maintain consistent levels across related loggers

## Common Pitfalls to Avoid

1. **❌ DO NOT:**

   - Use JSON configuration files
   - Configure multiple handlers
   - Disable propagation
   - Mix different logging approaches
   - Write to stderr (use stdout)
   - Add handlers to individual loggers

2. **✅ DO:**
   - Use single root logger configuration
   - Enable propagation everywhere
   - Use consistent formatting
   - Include source context in logs
   - Write all logs to stdout
   - Remove handlers from child loggers

## Testing and Verification

1. **Verify Configuration**

   ```python
   def verify_logging_setup():
       """Verify logging configuration is correct."""
       root = logging.getLogger()
       assert len(root.handlers) == 1, "Root should have exactly one handler"
       assert isinstance(root.handlers[0], logging.StreamHandler), "Handler should be StreamHandler"
       assert root.handlers[0].stream == sys.stdout, "Handler should write to stdout"

       # Verify child logger setup
       api_logger = logging.getLogger("api")
       assert len(api_logger.handlers) == 0, "Child loggers should have no handlers"
       assert api_logger.propagate, "Child loggers should propagate to root"
   ```

2. **Test Log Output**
   - Ensure logs appear in stdout
   - Verify source context is present
   - Check log format consistency
   - Confirm proper logger inheritance

## Maintenance

1. **Regular Checks**

   - Monitor for handler proliferation
   - Verify propagation settings
   - Ensure consistent formatting
   - Check for stdout usage

2. **Updates**
   - Maintain single configuration approach
   - Document any level changes
   - Keep formatter consistent
   - Preserve inheritance model

## Implementation Strategy

### Phase 1: Preparation

1. **Backup Current State**

   - Document existing logger configurations
   - Map out current logger hierarchy
   - Identify all log output points

2. **Clean Slate**

   - Remove all existing logging configuration
   - Delete any JSON config files
   - Clear custom handlers from all loggers

3. **Dependencies**
   - Ensure all logging is configured before FastAPI/Uvicorn startup
   - Review FastAPI and Uvicorn logging documentation
   - Understand logger naming conventions

### Phase 2: Implementation

1. **Root Logger Setup**

   - Configure basic logging first
   - Verify stdout stream configuration
   - Test basic log output

2. **Component Integration**

   - Configure Uvicorn loggers
   - Set up FastAPI logging
   - Integrate MCP server logging

3. **Verification**
   - Check for duplicate logs
   - Verify log format consistency
   - Ensure proper logger inheritance

### Phase 3: Migration

1. **Gradual Rollout**

   - Start with development environment
   - Monitor for any log loss
   - Verify all components are logging

2. **Validation**

   - Check container log collection
   - Verify log levels are appropriate
   - Ensure no logging gaps

3. **Rollback Plan**
   - Keep old configuration backed up
   - Document reversion steps
   - Test rollback procedure

## Common Implementation Mistakes

1. **Configuration Timing**

   - ❌ Configuring logging after FastAPI setup
   - ❌ Mixing configuration approaches
   - ✅ Configure all logging before any imports

2. **Handler Management**

   - ❌ Adding handlers to individual loggers
   - ❌ Forgetting to clear existing handlers
   - ✅ Use only root logger handlers

3. **Stream Selection**

   - ❌ Using stderr for some loggers
   - ❌ Mixed stream usage
   - ✅ Consistent stdout usage

4. **Logger Hierarchy**
   - ❌ Disabling propagation
   - ❌ Duplicate handlers
   - ✅ Proper inheritance chain

## Troubleshooting Guide

### Duplicate Logs

1. **Check for:**

   - Multiple handlers on loggers
   - Propagation settings
   - Handler inheritance

2. **Solution:**
   ```python
   # Remove all handlers from child loggers
   for name in logging.root.manager.loggerDict:
       logger = logging.getLogger(name)
       logger.handlers.clear()
       logger.propagate = True
   ```

### Missing Logs

1. **Verify:**

   - Logger hierarchy
   - Log levels
   - Handler configuration

2. **Debug:**
   ```python
   # Add temporary debug logging
   root = logging.getLogger()
   print(f"Root logger level: {root.level}")
   print(f"Root handlers: {root.handlers}")
   ```

### Format Inconsistency

1. **Check:**

   - Formatter configuration
   - Handler formatting
   - Logger inheritance

2. **Fix:**
   ```python
   # Ensure consistent formatting
   formatter = logging.Formatter(
       fmt="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
       datefmt="%Y-%m-%d %H:%M:%S"
   )
   root = logging.getLogger()
   for handler in root.handlers:
       handler.setFormatter(formatter)
   ```

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

    # Configure root logger with stdout handler
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

    # Configure all relevant loggers to inherit from root
    loggers_to_configure = [
        "conduit.mcp",           # MCP server logger
        "conduit.core",          # Core backend logger
        "conduit.platforms",     # Platform integration logger
        "uvicorn",              # Uvicorn server logger
        "uvicorn.error",        # Uvicorn error logger
        "uvicorn.access",       # Uvicorn access logger
        "fastapi"               # FastAPI logger
    ]

    # Remove any existing handlers and ensure propagation
    for name in loggers_to_configure:
        logger = logging.getLogger(name)
        logger.handlers = []     # Remove any existing handlers
        logger.propagate = True  # Critical: Ensure logs propagate to root
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

# Configure logging before importing server
configure_logging()

from .server import server, create_mcp_server
__all__ = ["server", "create_mcp_server"]

def main(transport: str = "stdio"):
    """Entry point for MCP server"""
    try:
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

## Testing the Implementation

1. Start your server and verify you see:

   - Initial MCP server startup logs
   - Logs from tool handler functions when endpoints are called
   - Logs from backend services called by the endpoints

2. Test endpoint logging by calling a tool:

   ```python
   logger.debug("Starting tool execution")
   # Your tool logic here
   logger.info("Tool execution completed")
   ```

3. Verify backend service logs:
   ```python
   # In a backend service
   logger = logging.getLogger("conduit.core")
   logger.debug("Backend service called")
   ```

## Example Log Output

When properly configured, you should see logs like this:

```
2024-03-26 16:45:23 - server.py:45 - INFO - Creating FastMCP server
2024-03-26 16:45:23 - tool_handler.py:23 - DEBUG - Starting tool execution
2024-03-26 16:45:23 - backend_service.py:12 - DEBUG - Backend service called
2024-03-26 16:45:23 - tool_handler.py:45 - INFO - Tool execution completed
```
