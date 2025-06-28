# Confluence Image Embed Instructions

This guide shows your AI coding assistant how to embed an image when creating or updating Confluence pages.

## Prerequisites
- `confluence` client is initialized and authenticated.
- Existing code supports `create_page()` and `update_page()`.

## Steps

1. **Create or retrieve the page**  
   ```python
   page = confluence.create_page(
       space="YOUR_SPACE",
       title="Page Title",
       body="",  # start empty
       representation="storage"
   )
   page_id = page["id"]
   ```

2. **Attach the image**  
   ```python
   confluence.attach_file(
       filename="/path/to/image.png",
       page_id=page_id
   )
   ```

3. **Update the page body to embed the image**  
   ```python
   body = """<p>Your intro text</p>
   <ac:image>
     <ri:attachment ri:filename="image.png"/>
   </ac:image>
   <p>Your follow-up text</p>"""
   confluence.update_page(
       page_id=page_id,
       title="Page Title",  # must match
       body=body,
       representation="storage"
   )
   ```

**Notes**  
- Ensure `ri:filename` matches the uploaded file name.  
- Use Confluence Storage Format (`representation="storage"`) for embedding macros.
