"""
Web Search and Webpage Reader Tool for Project Jarvis.
Provides internet search via DuckDuckGo and web page content reading.
"""

import re
import requests
from typing import Optional
from tools.registry import tool

@tool(description="Search the web for real-time information, current events, weather, docs, or facts using DuckDuckGo.")
def search_web(query: str, max_results: int = 5) -> str:
    """
    Search the web for information.
    query: The search query string
    max_results: Maximum number of search results to return (default 5)
    """
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            
        if not results:
            return f"No search results found for query: '{query}'"

        formatted = []
        for idx, res in enumerate(results, start=1):
            title = res.get("title", "No Title")
            snippet = res.get("body", "")
            href = res.get("href", "")
            formatted.append(f"{idx}. **{title}**\n   {snippet}\n   URL: {href}")
            
        return "\n\n".join(formatted)
    except Exception as e:
        return f"Web search failed: {str(e)}"

@tool(description="Fetch and extract readable text content from a given web URL.")
def fetch_webpage_content(url: str) -> str:
    """
    Fetch webpage readable text.
    url: The web URL to fetch and read
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=12)
        resp.raise_for_status()
        
        # Simple HTML to text extraction
        html = resp.text
        # Strip script and style blocks
        html = re.sub(r'<script[\s\S]*?</script>', '', html, flags=re.IGNORECASE)
        html = re.sub(r'<style[\s\S]*?</style>', '', html, flags=re.IGNORECASE)
        # Replace tags with space
        text = re.sub(r'<[^>]+>', ' ', html)
        # Collapse whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Cap at 2500 characters
        if len(text) > 2500:
            text = text[:2500] + "\n... [Content truncated]"
            
        return f"Content of {url}:\n{text}"
    except Exception as e:
        return f"Failed to fetch webpage at '{url}': {str(e)}"
