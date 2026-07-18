from langchain.tools import tool
from tavily import TavilyClient
from bs4 import BeautifulSoup
from rich import print
from dotenv import load_dotenv
import requests
import os

load_dotenv()

client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))

@tool
def search_tool(query: str) -> str:
    """Search the information about the query and provid Topic, URL and Content."""
    result = client.search(query=query, max_results=5)
    out = []
    for r in result['results']:
        out.append(f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content'][:300]}")

    return "\n-----\n".join(out)


@tool
def scrape_tool(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:3000]
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"
