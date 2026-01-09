"""
Web-related tools for agents.
"""
from typing import Optional
from langchain.tools import BaseTool
from pydantic import Field
import json


class WebSearchTool(BaseTool):
    """
    Search the web for information.

    Uses DuckDuckGo for privacy-friendly web searches.
    """
    name: str = "web_search"
    description: str = """Search the web for information.

Use this tool when you need to find current information from the internet.

Input: A search query string (not JSON)

Examples:
- "Python asyncio best practices"
- "Frappe framework documentation"
- "Latest LangChain updates 2024"

Returns the top search results with titles, snippets, and URLs.
"""

    session_id: Optional[str] = Field(default=None, exclude=True)

    def _run(self, query: str) -> str:
        """Execute web search."""
        try:
            # Try to use DuckDuckGo search
            try:
                from duckduckgo_search import DDGS
            except ImportError:
                return "Error: Web search requires 'duckduckgo-search' package. Install with: pip install duckduckgo-search"

            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))

            if not results:
                return f"No results found for: {query}"

            output = f"Search results for: {query}\n\n"
            for i, result in enumerate(results, 1):
                output += f"{i}. **{result.get('title', 'No title')}**\n"
                output += f"   {result.get('body', 'No description')}\n"
                output += f"   URL: {result.get('href', 'No URL')}\n\n"

            return output

        except Exception as e:
            return f"Error searching web: {str(e)}"


class WebFetchTool(BaseTool):
    """
    Fetch content from a URL.
    """
    name: str = "web_fetch"
    description: str = """Fetch content from a web URL.

Use this tool to retrieve the content of a specific web page.

Input: A URL string (not JSON)

Examples:
- "https://docs.frappe.io/framework"
- "https://api.github.com/repos/frappe/frappe"

Returns the text content of the page (HTML stripped for readability).
"""

    session_id: Optional[str] = Field(default=None, exclude=True)

    def _run(self, url: str) -> str:
        """Fetch URL content."""
        try:
            import requests
            from html.parser import HTMLParser

            # Clean URL
            url = url.strip()
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            # Make request with timeout
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; FrappeDeepAgents/1.0)'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            content_type = response.headers.get('content-type', '')

            # If JSON, return formatted
            if 'application/json' in content_type:
                try:
                    data = response.json()
                    return json.dumps(data, indent=2)[:5000]
                except:
                    pass

            # For HTML, try to extract text
            if 'text/html' in content_type:
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Remove script and style elements
                    for script in soup(["script", "style", "nav", "footer", "header"]):
                        script.decompose()

                    text = soup.get_text(separator='\n', strip=True)
                    # Truncate if too long
                    if len(text) > 5000:
                        text = text[:5000] + "\n... (truncated)"
                    return text
                except ImportError:
                    # Fallback: basic HTML stripping
                    import re
                    text = re.sub(r'<[^>]+>', '', response.text)
                    text = re.sub(r'\s+', ' ', text)[:5000]
                    return text

            # For other content types
            return response.text[:5000]

        except requests.RequestException as e:
            return f"Error fetching URL: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
