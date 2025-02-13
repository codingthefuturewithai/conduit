# Manual Testing Guide for Confluence Commands

This document provides a sequence of commands to manually test the Confluence integration functionality, particularly focusing on multi-site support. These tests verify that all Confluence operations work correctly across different site configurations.

## Prerequisites

1. Ensure you have conduit installed and configured
2. Configure at least one Confluence site in your `~/.config/conduit/config.yaml`
3. Have access to a Confluence space where you can view pages

## Test Commands

Replace the following placeholders in the commands:

- `<site-alias>`: Your configured site alias (e.g., "site1", "prod", etc.)
- `<space-key>`: Your Confluence space key (e.g., "DOCS", "TEAM", etc.)
- `<page-id>`: A valid page ID from your space
- `<page-title>`: The exact title of a page in your space

### 1. List Pages (Limited)

```bash
conduit confluence pages list <space-key> --limit 5 --site <site-alias>
```

### 2. List All Pages (With Pagination)

```bash
conduit confluence pages list-all <space-key> --batch-size 50 --site <site-alias>
```

### 3. Get Space Content (Clean Format)

```bash
conduit confluence pages content <space-key> --format clean --depth root --site <site-alias>
```

### 4. Get Space Content (Storage Format)

```bash
conduit confluence pages content <space-key> --format storage --depth all --site <site-alias>
```

### 5. Get Child Pages

```bash
conduit confluence pages children <page-id> --site <site-alias>
```

### 6. Get Page by Title (Clean Format)

```bash
conduit confluence pages get <space-key> "<page-title>" --format clean --site <site-alias>
```

### 7. Get Page by Title (Storage Format)

```bash
conduit confluence pages get <space-key> "<page-title>" --format storage --site <site-alias>
```

## Expected Results

1. **List Pages**: Should return a JSON array of up to 5 pages with basic metadata
2. **List All Pages**: Should show progress and return a complete list of pages in the space
3. **Space Content (Clean)**: Should return root-level content in clean text format
4. **Space Content (Storage)**: Should return all content in Confluence storage format
5. **Child Pages**: Should list all child pages of the specified parent
6. **Page by Title (Clean)**: Should return the page content in clean text format
7. **Page by Title (Storage)**: Should return the page content in Confluence storage format

## Troubleshooting

If any command fails:

1. Verify your site configuration in `~/.config/conduit/config.yaml`
2. Check that your API token has the necessary permissions
3. Ensure the space and pages exist and you have access to them
4. Verify that the page title exactly matches what's in Confluence
5. For storage format issues, ensure the content is properly formatted in Confluence

## Format Options

The `--format` option supports three values:

- `clean`: Formatted text suitable for AI/LLM consumption
- `storage`: Raw Confluence storage format with markup
- `raw`: Unprocessed API response with all metadata

## Depth Options

The `--depth` option for content retrieval supports:

- `root`: Only root-level pages
- `all`: All pages including children
- `children`: Direct child pages only
