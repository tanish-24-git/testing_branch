# FILE: src/agents/browser/intent_classifier.py
# Uses LLM to classify the user query into one of the supported intents: search, open_site, download, summarize_youtube, summarize_webpage.

from typing import List, Dict

async def classify_intent(llm_manager, command: str) -> str:
    """
    Classifies the intent of the command using LLM.
    Returns the intent as a lowercase string.
    """
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": "Classify the query into one category: search, open_site, download, summarize_youtube, summarize_webpage. Respond with only the category name."},
        {"role": "user", "content": command}
    ]
    response = await llm_manager.chat(messages)
    return response.strip().lower()