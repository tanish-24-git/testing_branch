
# FILE: src/agents/browser/direct_handler.py
# Handles requests to open a website by searching for the official site and returning the top link.
# Updated search_query to f"{site_name}" to fix "Site not found" for common sites like github.

import re
from typing import Dict
from duckduckgo_search import DDGS

async def handle_direct(query: str) -> Dict:
    """
    Searches for the site and returns the URL.
    """
    site_name = re.sub(r"(open|go to)\s+", "", query, flags=re.I).strip()
    search_query = site_name  # Simplified to fix "Site not found"
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(search_query, max_results=1))
        if results:
            return {"url": results[0]["href"]}
        return {"error": "Site not found"}
    except Exception as e:
        return {"error": str(e)}