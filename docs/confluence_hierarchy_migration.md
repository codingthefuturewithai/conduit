# Confluence Hierarchy Migration Guide

## Overview

As of version X.X.X, Conduit has replaced the flat `list_all_confluence_pages` endpoint with a more powerful `retrieve_confluence_hierarchy` endpoint that provides hierarchical page retrieval capabilities.

## Migration Summary

- **Deprecated**: `list_all_confluence_pages`
- **New**: `retrieve_confluence_hierarchy`

## Key Improvements

The new endpoint provides several advantages:

1. **Hierarchical Structure**: Returns pages in a tree structure preserving parent-child relationships
2. **Flexible Starting Points**: Can start from space root or any specific page
3. **Depth Control**: Optional `max_depth` parameter to limit traversal depth
4. **Batch Processing**: Respects `batch_size` across the entire hierarchy

## API Changes

### Old Endpoint (Deprecated)

```python
# MCP Tool: list_all_confluence_pages
Parameters:
- space_key: str (required)
- batch_size: int = 100
- site_alias: str = None

Returns: Flat table of pages
```

### New Endpoint

```python
# MCP Tool: retrieve_confluence_hierarchy
Parameters:
- space_key: str (required)
- parent_page_id: str = None  # NEW: Start from specific page
- batch_size: int = 100
- max_depth: int = None      # NEW: Limit traversal depth
- site_alias: str = None

Returns: Hierarchical tree structure
```

## Migration Steps

### 1. Update Tool Calls

**Before:**
```python
# Old flat listing
await mcp.list_all_confluence_pages(
    space_key="MYSPACE",
    batch_size=50
)
```

**After:**
```python
# New hierarchical retrieval
await mcp.retrieve_confluence_hierarchy(
    space_key="MYSPACE",
    batch_size=50
)
```

### 2. Handle Response Format Changes

**Old Response Format:**
```
# Pages in MYSPACE space

| Title | ID | URL |
|-------|----|---------
| Page A | 123 | /pages/123 |
| Page B | 124 | /pages/124 |
```

**New Response Format:**
```
# Confluence Page Hierarchy

**Space**: MYSPACE
**Starting from**: Space root
**Total pages retrieved**: 2

## Page Tree

- **Page A**
  - ID: 123
  - Version: 1
  - Last Updated: 2024-01-01
  - URL: /pages/123
  - **Page B**
    - ID: 124
    - Version: 1
    - Last Updated: 2024-01-02
    - URL: /pages/124
```

### 3. Leverage New Features

#### Retrieve Subtree from Specific Page
```python
# Get only children of a specific page
await mcp.retrieve_confluence_hierarchy(
    space_key="MYSPACE",
    parent_page_id="123",  # Start from this page
    batch_size=50
)
```

#### Limit Traversal Depth
```python
# Get only 2 levels deep
await mcp.retrieve_confluence_hierarchy(
    space_key="MYSPACE",
    max_depth=2,
    batch_size=50
)
```

## Code Examples

### Processing Hierarchical Results

```python
def process_hierarchy(hierarchy_response):
    """Process the hierarchical response from retrieve_confluence_hierarchy."""
    
    def traverse_node(node, level=0):
        indent = "  " * level
        print(f"{indent}{node['title']} (ID: {node['id']})")
        
        # Process children recursively
        for child in node.get('children', []):
            traverse_node(child, level + 1)
    
    # Process each root node
    for root in hierarchy_response['hierarchy']:
        traverse_node(root)
```

### Finding a Specific Page in Hierarchy

```python
def find_page_in_hierarchy(hierarchy_response, target_title):
    """Find a page by title in the hierarchical structure."""
    
    def search_node(node):
        if node['title'] == target_title:
            return node
        
        for child in node.get('children', []):
            result = search_node(child)
            if result:
                return result
        return None
    
    for root in hierarchy_response['hierarchy']:
        result = search_node(root)
        if result:
            return result
    return None
```

## Benefits of Migration

1. **Preserve Structure**: Maintain parent-child relationships between pages
2. **Efficient Navigation**: Navigate page trees without multiple API calls
3. **Targeted Retrieval**: Get only the subtree you need
4. **Better Performance**: Batch processing with depth control
5. **Richer Metadata**: Each page includes version and update information

## Troubleshooting

### Q: I need a flat list like before
A: You can flatten the hierarchy in your code:

```python
def flatten_hierarchy(hierarchy_response):
    """Convert hierarchical response to flat list."""
    pages = []
    
    def collect_pages(node):
        pages.append({
            'id': node['id'],
            'title': node['title'],
            'url': node['url']
        })
        for child in node.get('children', []):
            collect_pages(child)
    
    for root in hierarchy_response['hierarchy']:
        collect_pages(root)
    
    return pages
```

### Q: The response is too large
A: Use the `batch_size` and `max_depth` parameters to limit the response:

```python
# Limit to 20 pages, max 2 levels deep
await mcp.retrieve_confluence_hierarchy(
    space_key="MYSPACE",
    batch_size=20,
    max_depth=2
)
```

## Support

For questions or issues with the migration, please:
1. Check the [Conduit documentation](https://github.com/your-org/conduit)
2. Open an issue on GitHub
3. Contact the Conduit team