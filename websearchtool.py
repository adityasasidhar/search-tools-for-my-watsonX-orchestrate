from ddgs import DDGS
import requests
import time
import random
from bs4 import BeautifulSoup
from ibm_watsonx_orchestrate.agent_builder.tools import tool


@tool
def search_internet(query: str, max_results: int = 10) -> str:
    """
    Searches DuckDuckGo and returns search results with titles, URLs, and snippets.

    Args:
        query (str): The search terms to look up.
        max_results (int): Maximum number of results to return (default 10).

    Returns:
        str: Formatted search results with titles, URLs, and snippets.
    """
    try:
        ddgs = DDGS()
        search_results = ddgs.text(query, max_results=max_results)

        if not search_results:
            return "No search results found."

        results_list = list(search_results)
        formatted_results = []

        for i, result in enumerate(results_list):
            title = result.get('title', 'No title')
            url = result.get('href', 'No URL')
            snippet = result.get('body', 'No description')

            formatted_results.append(
                f"### Result {i + 1}: {title}\n"
                f"**URL:** {url}\n"
                f"**Snippet:** {snippet}\n"
            )
        return f"Found {len(results_list)} results for '{query}':\n\n" + "\n".join(formatted_results)

    except Exception as e:
        return f"Search Error: {str(e)}"


@tool
def fetch_url(url: str, max_length: int = 5000) -> str:
    """
    Fetches and extracts readable content from a specific URL.

    Args:
        url (str): The URL to fetch and scrape.
        max_length (int): Maximum length of content to return (default 5000 characters).

    Returns:
        str: Extracted and cleaned text content from the URL.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove non-content elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
            element.decompose()

        # Try to get main content
        main_content = (
                soup.find('main') or
                soup.find('article') or
                soup.find('div', class_='content') or
                soup.body
        )

        if main_content:
            text = main_content.get_text(separator=" ", strip=True)
        else:
            text = soup.get_text(separator=" ", strip=True)

        # Clean up whitespace
        clean_text = " ".join(text.split())

        # Truncate to max_length
        if len(clean_text) > max_length:
            clean_text = clean_text[:max_length] + "..."

        if not clean_text:
            return f"No readable content found at {url}"

        return f"Content from {url}:\n\n{clean_text}"

    except requests.exceptions.HTTPError as e:
        return f"HTTP Error {e.response.status_code} when accessing {url}"

    except requests.exceptions.Timeout:
        return f"Request timed out when accessing {url}"

    except Exception as e:
        return f"Error fetching {url}: {str(e)}"
