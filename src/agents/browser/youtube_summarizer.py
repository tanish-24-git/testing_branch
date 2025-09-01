# FILE: src/agents/browser/youtube_summarizer.py
# Handles summarization of YouTube videos with detailed metadata extraction.
# Uses YouTube Transcript API first, falls back to Whisper for transcription.
# Optionally enriches with YouTube Data API if key present.

import re
import os
import requests
import tempfile
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
    Enriches with YouTube Data API if key present: title, description, views, duration, channel, publish date, etc.
    Returns formatted string or empty.
    """
    if not settings.youtube_api_key:
        return ""
    try:
        youtube = build("youtube", "v3", developerKey=settings.youtube_api_key)
        response = youtube.videos().list(part="snippet,statistics,contentDetails", id=video_id).execute()
        if 'items' in response and response['items']:
            item = response['items'][0]
            snippet = item['snippet']
            stats = item['statistics']
            details = item['contentDetails']
            title = snippet['title']
            desc = snippet['description']
            channel = snippet['channelTitle']
            publish_date = snippet['publishedAt']
            views = stats.get('viewCount', 'N/A')
            likes = stats.get('likeCount', 'N/A')
            duration = details['duration']  # ISO 8601 format
            return f"**Video Details**:\n- **Title**: {title}\n- **Channel**: {channel}\n- **Published**: {publish_date}\n- **Views**: {views}\n- **Likes**: {likes}\n- **Duration**: {duration}\n- **Description**: {desc[:500]}\n\n"
        return ""
    except Exception as e:
        return ""

async def handle_youtube_summary(llm_manager, query: str) -> Dict:
    """
    Extracts content from YouTube video and generates a detailed summary using LLM.
    """
    url_match = re.search(r"summarize\s+(.+)", query, re.I)
    if not url_match:
        return {"error": "No URL found in query"}
    url = url_match.group(1).strip()

    try:
        if not ("youtube.com" in url or "youtu.be" in url):
            return {"error": "Not a YouTube URL"}
        video_id = re.search(r"v=([^&]+)", url).group(1) if "v=" in url else url.split("/")[-1]
        enrich = await get_youtube_details(video_id)
        text = ""
        
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

        # Safety: truncate overly long text
        if len(text) > 8000:
            text = text[:8000] + " ... [content truncated]"

        messages: List[Dict[str, str]] = [
            {"role": "system", "content": "Provide a detailed summary of the following YouTube video content, including key points, themes, and any notable details. Structure the summary with clear sections if applicable."},
            {"role": "user", "content": enrich + text}
        ]
        summary = await llm_manager.chat(messages)
        return {"summary": summary}
    except Exception as e:
        return {"error": str(e)}