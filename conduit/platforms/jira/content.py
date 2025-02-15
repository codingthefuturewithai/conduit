"""Content conversion utilities for Jira."""


def markdown_to_jira(content: str) -> str:
    """Convert markdown content to Jira markup format.

    Handles common markdown elements and converts them to Jira's expected format:
    - Headers (# -> h1. ## -> h2. etc)
    - Lists (- or * -> -)
    - Code blocks (``` -> {code})
    - Inline code (` -> {{)
    """
    lines = content.split("\n")
    converted_lines = []

    for line in lines:
        # Convert headers
        if line.startswith("# "):
            line = "h1. " + line[2:]
        elif line.startswith("## "):
            line = "h2. " + line[3:]
        elif line.startswith("### "):
            line = "h3. " + line[4:]

        # Convert list items (preserve existing list numbers if present)
        elif line.strip().startswith("- "):
            line = "* " + line[2:]
        elif line.strip().startswith("* "):
            line = "* " + line[2:]

        # Convert inline code
        if "`" in line:
            # Handle inline code (single backticks)
            while "`" in line:
                if line.count("`") >= 2:
                    line = line.replace("`", "{{", 1).replace("`", "}}", 1)
                else:
                    # If there's an unpaired backtick, just replace it
                    line = line.replace("`", "{{")

        converted_lines.append(line)

    return "\n".join(converted_lines)
