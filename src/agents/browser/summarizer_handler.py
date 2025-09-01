
# FILE: src/agents/browser/summarizer_handler.py
# Handles summarization of web content or YouTube videos by extracting text.
# Falls back to Whisper local transcription if YouTube has no subtitles.
# Optionally enriches with YouTube Data API if key present.

import re
import os
import requests
import tempfile
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from pytube import YouTube
from typing import Dict, List
import whisper
from googleapiclient.discovery import build
from src.settings import settings

# Load whisper model once (base = smaller/faster, medium/large = better quality)
whisper_model = whisper.load_model("base")

async def transcribe_audio_local(audio_path: str) -> str:
    """
    Transcribes audio locally using Whisper (no API key required).
    """
    result = whisper_model.transcribe(audio_path, language="en")
    return result["text"]

async def get_youtube_details(video_id: str) -> str:
    """
    Enriches with YouTube Data API if key present: title, description, views.
    Returns formatted string or empty.
    """
    if not settings.youtube_api_key:
        return ""
    try:
        youtube = build("youtube", "v3", developerKey=settings.youtube_api_key)
        response = youtube.videos().list(part="snippet,statistics", id=video_id).execute()
        if 'items' in response and response['items']:
            item = response['items'][0]
            title = item['snippet']['title']
            desc = item['snippet']['description'][:500]  # Truncate
            views = item['statistics'].get('viewCount', 'N/A')
            return f"Title: {title}\nDescription: {desc}\nViews: {views}\n\n"
        return ""
    except Exception as e:
        return ""

async def handle_summarize(llm_manager, query: str) -> Dict:
    """
    Extracts content from URL (web page or YouTube) and generates a summary using LLM.
    """
    url_match = re.search(r"summarize\s+(.+)", query, re.I)
    if not url_match:
        return {"error": "No URL found in query"}
    url = url_match.group(1).strip()

    try:
        text = ""
        enrich = ""

        if "youtube.com" in url or "youtu.be" in url:
            video_id = re.search(r"v=([^&]+)", url).group(1) if "v=" in url else url.split("/")[-1]
            enrich = await get_youtube_details(video_id)
            # Try YouTube transcript first
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                text = " ".join([t["text"] for t in transcript])
            except (TranscriptsDisabled, NoTranscriptFound):
                # Fallback to audio download + Whisper
                yt = YouTube(url)
                audio_stream = yt.streams.filter(only_audio=True).first()
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
                    audio_stream.download(filename=temp_file.name)
                    text = await transcribe_audio_local(temp_file.name)
                os.unlink(temp_file.name)  # Clean up
        else:
            # Summarize webpage
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            text = " ".join([p.text for p in soup.find_all('p')])

        # Safety: truncate overly long text
        if len(text) > 8000:
            text = text[:8000] + " ... [content truncated]"

        messages: List[Dict[str, str]] = [
            {"role": "system", "content": "Summarize the following content concisely with key points."},
            {"role": "user", "content": enrich + text}
        ]
        summary = await llm_manager.chat(messages)
        return {"summary": summary}
    except Exception as e:
        return {"error": str(e)}