"""Content processing utilities for Confluence."""

import re
import warnings

from bs4 import BeautifulSoup, NavigableString

# Suppress parser warnings
warnings.filterwarnings("ignore", category=UserWarning, module="bs4")


class ConfluenceContentCleaner:
    """Clean and process Confluence storage format content."""

    def clean_element(self, element: BeautifulSoup | NavigableString) -> str:
        """Recursively clean and extract text from Confluence storage elements."""
        if isinstance(element, NavigableString):
            return element.strip()

        # Handle Confluence-specific elements
        if element.name and element.name.startswith("ac:"):
            # Handle task lists
            if element.name == "ac:task-list":
                tasks = []
                for task in element.find_all("ac:task"):
                    status = task.find("ac:task-status")
                    body = task.find("ac:task-body")
                    status_mark = "☐" if status and status.text == "incomplete" else "☑"
                    if body:
                        tasks.append(f"{status_mark} {self.clean_element(body)}")
                return "\n".join(tasks) + "\n"

            # Handle Confluence links
            if element.name == "ac:link":
                text = element.find("ac:plain-text-link-body")
                link_text = text.get_text() if text else element.get_text()
                # Try to get the linked page title
                page = element.find("ri:page")
                if page and page.get("ri:content-title"):
                    return f"[{link_text}] (-> {page['ri:content-title']})"
                return f"[{link_text}]"

            # Handle other ac: elements by getting their text
            return " ".join(self.clean_element(child) for child in element.children)

        # Handle resource identifiers
        if element.name and element.name.startswith("ri:"):
            # For now, just return any text content
            return element.get_text()

        # Handle standard HTML elements
        if element.name == "p":
            text = " ".join(
                self.clean_element(child) for child in element.children
            ).strip()
            return f"{text}\n" if text else "\n"

        if element.name == "strong" or element.name == "b":
            return f"**{' '.join(self.clean_element(child) for child in element.children)}**"

        if element.name == "em" or element.name == "i":
            return (
                f"_{' '.join(self.clean_element(child) for child in element.children)}_"
            )

        if element.name in ["div", "td", "li"]:
            return " ".join(
                self.clean_element(child) for child in element.children
            ).strip()

        if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            level = int(element.name[1])
            text = " ".join(
                self.clean_element(child) for child in element.children
            ).strip()
            return f"\n{'#' * level} {text}\n"

        if element.name == "br":
            return "\n"

        if element.name == "table":
            rows = []
            headers = []
            # Process headers first
            header_row = element.find("tr")
            if header_row:
                for th in header_row.find_all(["th", "td"]):
                    headers.append(self.clean_element(th).strip())
                if headers:
                    rows.append(" | ".join(headers))
                    rows.append("-" * (len(" | ".join(headers))))

            # Process data rows
            for row in (
                element.find_all("tr")[1:] if headers else element.find_all("tr")
            ):
                cells = []
                for cell in row.find_all(["td", "th"]):
                    cells.append(self.clean_element(cell).strip())
                if cells:
                    rows.append(" | ".join(cells))
            return "\n" + "\n".join(rows) + "\n"

        if element.name in ["ul", "ol"]:
            items = []
            for i, li in enumerate(element.find_all("li", recursive=False)):
                prefix = "* " if element.name == "ul" else f"{i+1}. "
                items.append(f"{prefix}{self.clean_element(li).strip()}")
            return "\n" + "\n".join(items) + "\n"

        if element.name == "code":
            return f"`{element.get_text()}`"

        if element.name == "pre":
            return f"\n```\n{element.get_text()}\n```\n"

        # Recursively process other elements
        return " ".join(self.clean_element(child) for child in element.children).strip()

    def clean(self, content: str) -> str:
        """Clean Confluence storage format content."""
        if not content:
            return ""

        # Parse content with HTML parser instead of XML
        # Use 'html.parser' instead of 'xml' to better handle XHTML-like content
        soup = BeautifulSoup(content, "html.parser")

        # Get cleaned text from all top-level elements
        cleaned_parts = []
        for element in soup.children:
            if not isinstance(element, NavigableString) or element.strip():
                cleaned_parts.append(self.clean_element(element))

        text = "\n".join(part for part in cleaned_parts if part.strip())

        # Post-process
        text = self._post_process(text)

        return text.strip()

    def _post_process(self, text: str) -> str:
        """Post-process cleaned text."""
        # Replace multiple newlines with double newline
        text = re.sub(r"\n\s*\n+", "\n\n", text)

        # Replace multiple spaces with single space
        text = re.sub(r" +", " ", text)

        # Ensure sections are well separated
        text = re.sub(r"([^\n])\n#", r"\1\n\n#", text)

        return text
