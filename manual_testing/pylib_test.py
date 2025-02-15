from conduit.platforms.jira import JiraClient
from conduit.platforms.confluence import ConfluenceClient
from conduit.core.exceptions import PlatformError

try:
    # Initialize Jira client with optional site alias
    jira = JiraClient(site_alias="ctf")  # or JiraClient() for default site
    jira.connect()

    # Get an issue
    try:
        issue = jira.get("ACT-50")  # Using a specific issue number
        print(f"Successfully retrieved issue ACT-50")
    except PlatformError as e:
        print(f"Failed to get issue: {e}")

    # Search issues
    try:
        issues = jira.search("project = ACT AND status = 'Done'")
        print(f"Found {len(issues) if issues else 0} issues matching search")
    except PlatformError as e:
        print(f"Failed to search issues: {e}")

except Exception as e:
    print(f"Failed to initialize Jira client: {e}")

try:
    # Initialize Confluence client with optional site alias
    confluence = ConfluenceClient(
        site_alias="ctf"
    )  # or ConfluenceClient() for default site
    confluence.connect()

    # Get pages from a space
    pages = confluence.get_pages_by_space("ACT", limit=10)

    # Get all pages with pagination
    all_pages = confluence.get_all_pages_by_space("ACT", batch_size=100)

    # Get the first page ID from all_pages (if any pages exist)
    if all_pages and len(all_pages) > 0:
        first_page_id = all_pages[0]["id"]
        print(f"Found page ID: {first_page_id}")

        # Get child pages using the real page ID
        try:
            child_pages = confluence.get_child_pages(first_page_id)
            print(f"Found {len(child_pages) if child_pages else 0} child pages")
        except PlatformError as e:
            print(f"Failed to get child pages: {e}")
    else:
        print("No pages found in space ACT")

    # Get a specific page by title
    try:
        page = confluence.get_page_by_title(
            "ACT", "Tech Stack", expand="version,body.storage"  # optional
        )
        print("Successfully retrieved Tech Stack page")
    except PlatformError as e:
        print(f"Failed to get Tech Stack page: {e}")

    # Get space content in raw format
    try:
        content = confluence.get_space_content(
            "ACT",
            depth="all",
            limit=500,
            expand="body.storage",
            format="storage",  # default
        )
        print("Successfully retrieved space content in raw format")
    except PlatformError as e:
        print(f"Failed to get space content in raw format: {e}")

    # Get space content in cleaned format (for AI/LLM)
    try:
        content = confluence.get_space_content(
            "ACT", depth="all", limit=500, expand="body.storage", format="clean"
        )
        print("Successfully retrieved space content in clean format")
    except PlatformError as e:
        print(f"Failed to get space content in clean format: {e}")

except Exception as e:
    print(f"Failed to initialize Confluence client: {e}")
