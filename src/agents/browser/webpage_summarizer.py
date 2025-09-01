# FILE: src/agents/browser/webpage_summarizer.py
# Handles summarization of webpages with detailed content extraction (headings, paragraphs, lists, metadata).

import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, List

async def handle_webpage_summary(llm_manager, query: str) -> Dict:
    """
    Extracts detailed content from a webpage and generates a summary using LLM.
    """
    url_match = re.search(r"summarize\s+(.+)", query, re.I)
    if not url_match:
        return {"error": "No URL found in query"}
    url = url_match.group(1).strip()

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract metadata
        metadata = ""
        title = soup.find('title')
        if title:
            metadata += f"**Title**: {title.text}\n"
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            metadata += f"**Description**: {meta_desc['content']}\n"

        # Extract headings
        headings = ""
        for h in soup.find_all(['h1', 'h2', 'h3']):
            level = h.name
            text = h.text.strip()
            if text:
                headings += f"**{level.upper()}**: {text}\n"

        # Extract paragraphs
        paragraphs = " ".join([p.text.strip() for p in soup.find_all('p') if p.text.strip()])

        # Extract lists
        lists = ""
        for ul in soup.find_all(['ul', 'ol']):
            for li in ul.find_all('li'):
                text = li.text.strip()
                if text:
                    lists += f"- {text}\n"

        # Combine content
        content = f"{metadata}\n**Headings**:\n{headings}\n**Content**:\n{paragraphs}\n**Lists**:\n{lists}"

        # Safety: truncate overly long text
        if len(content) > 8000:
            content = content[:8000] + " ... [content truncated]"

        messages: List[Dict[str, str]] = [
            {"role": "system", "content": "Provide a detailed summary of the following webpage content, including key points, themes, and notable details from headings, paragraphs, lists, and metadata. Structure the summary with clear sections if applicable."},
            {"role": "user", "content": content}
        ]
        summary = await llm_manager.chat(messages)
        return {"summary": summary}
    except Exception as e:
        return {"error": str(e)}