# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Test/Lint Commands

- Install dev dependencies: `pip install -e ".[dev]"`
- Run all tests: `pytest`
- Run single test: `pytest tests/path/to/test_file.py::test_function_name`
- Run tests with coverage: `pytest --cov=conduit`
- Format code: `black .`
- Sort imports: `isort .`
- Type checking: `mypy .`
- Lint code: `ruff .`

## Code Style Guidelines

- **Imports**: Standard library first, third-party second, local imports last. Use `isort`.
- **Formatting**: Follow Black formatting standards.
- **Type Annotations**: Use type hints for all function parameters and return values.
- **Naming**: Classes use CamelCase, functions/variables use snake_case, constants use UPPER_SNAKE_CASE.
- **Documentation**: Google-style docstrings for classes and functions.
- **Error Handling**: Use custom exceptions from `conduit.core.exceptions`. Include informative error messages.
- **Logging**: Use the configured logger from `conduit.core.logger`.
- **Testing**: Write pytest tests for new functionality, including both happy paths and error cases.