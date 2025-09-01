
# FILE: src/agents/browser/direct_handler.py
# Handles requests to open a website by searching for the official site and returning the top link.

import re
from typing import List, Dict

from duckduckgo_search import DDGS

async def handle_direct(query: str) -> Dict:
    """
    Searches for the official site of the requested entity and returns the URL.
    """
    site_name = re.sub(r"(open|go to)\s+", "", query, flags=re.I).strip()
    search_query = f"{site_name} official site"
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(search_query, max_results=1))
        if results:
            return {"url": results[0]["href"]}
        return {"error": "Site not found"}
    except Exception as e:
        return {"error": str(e)}