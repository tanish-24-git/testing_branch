
# FILE: src/agents/browser/search_handler.py
# Handles search queries by using DuckDuckGo to fetch results.
# Appends location-based info to query using ipinfo.

import requests
from typing import List, Dict

from duckduckgo_search import DDGS

def get_location() -> str:
    """
    Gets country from IP using ipinfo.
    Returns empty if fails.
    """
    try:
        ipinfo = requests.get("https://ipinfo.io/json").json()
        return ipinfo.get("country", "")
    except:
        return ""

async def handle_search(query: str) -> Dict:
    """
    Performs a search using DuckDuckGo, appending location if available.
    Returns top 5 results.
    """
    country = get_location()
    if country:
        query += f" in {country}"
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        return {"results": [{"title": r["title"], "body": r["body"], "href": r["href"]} for r in results]}
    except Exception as e:
        return {"error": str(e)}