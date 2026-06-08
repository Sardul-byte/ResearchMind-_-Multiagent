import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from pathlib import Path
from dotenv import load_dotenv
from rich import print

_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path, override=True)


def get_tavily_client() -> TavilyClient:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "Missing TAVILY_API_KEY. Set it in .env or the environment before running."
        )
    return TavilyClient(api_key=api_key)


def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic. Returns titles, URLs and snippets."""
    try:
        client = get_tavily_client()
        results = client.search(query=query, max_results=5)
        out = []
        for r in results.get("results", []):
            out.append(
                f"Title: {r.get('title', 'N/A')}\n"
                f"URL: {r.get('url', 'N/A')}\n"
                f"Snippet: {r.get('content', '')[:300]}\n"
            )
        return "\n----\n".join(out) if out else "No search results found."
    except Exception as e:
        return f"Web search failed: {str(e)}"


def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:3000]
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"

