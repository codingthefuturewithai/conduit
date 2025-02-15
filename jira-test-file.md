# Description

Create a Python script that fetches a set of web pages periodically and stores them into a local SQLite3 database. The script should utilize the requests library to retrieve the web pages without any authentication.

# Acceptance Criteria

1. The script successfully fetches the specified web pages at defined intervals.
2. The fetched content is stored in a local SQLite3 database.

# Technical Guidance

- Use the `requests` library for making HTTP requests.
- Use `sqlite3` for database operations.
- Ensure that the script handles potential errors in fetching pages gracefully.
