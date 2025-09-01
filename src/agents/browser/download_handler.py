
# FILE: src/agents/browser/download_handler.py
# Handles download requests by searching for official download link.
# Uses LLM to generate installation steps (not hardcoded).

import re
from typing import List, Dict
from duckduckgo_search import DDGS

async def handle_download(llm_manager, query: str) -> Dict:
    """
    Finds the official download link for the software.
    Uses LLM to generate installation steps.
    """
    software = re.sub(r"download\s+", "", query, flags=re.I).strip()
    search_query = f"download {software} official"
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(search_query, max_results=1))
        if not results:
            return {"error": "Download not found"}
        url = results[0]["href"]

        # LLM for steps (general, since client PC info not available)
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": "Provide step-by-step installation guide for the software on common OS (Windows/Mac/Linux). Assume typical PC config."},
            {"role": "user", "content": f"Installation steps for {software}"}
        ]
        steps = await llm_manager.chat(messages)
        return {"download_url": url, "steps": steps}
    except Exception as e:
        return {"error": str(e)}