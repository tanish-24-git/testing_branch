```
# Updated project structure with BrowserAgent implementation
cleaned_ai_agent_project/
├── README.md                  # Updated with Gmail setup and BrowserAgent info
├── requirements.txt           # Cleaned, added Google libs, added browser deps: duckduckgo-search, beautifulsoup4, lxml, youtube-transcript-api, openai-whisper, pytube, requests
├── setup.py                   # Packaging
├── .env.template              # LLM keys only (Gmail uses credentials.json), added YOUTUBE_API_KEY
├── config.yaml                # Simplified (no RAG/browser)
├── credentials.json           # Place your Google OAuth JSON here (not in Git)
└── src/
    ├── __init__.py
    ├── main.py                # FastAPI server, updated /chat to route commands
    ├── config.py              # Config loader
    ├── settings.py            # Env settings, added youtube_api_key
    ├── llm_manager.py         # Only Gemini/Groq, with chat method
    ├── agents/                # Agents
    │   ├── __init__.py
    │   ├── agent_manager.py   # Manages agents, added BrowserAgent registration
    │   ├── base_agent.py      # Base class
    │   ├── email_agent.py     # Modular Gmail API integration
    │   └── browser/           # New folder for BrowserAgent
    │       ├── __init__.py
    │       ├── browser_agent.py  # Orchestrates browser tasks, routes based on intent, returns markdown
    │       ├── intent_classifier.py  # Classifies query intent using LLM
    │       ├── search_handler.py     # Handles search queries using DuckDuckGo, appends location from ipinfo
    │       ├── direct_handler.py     # Handles direct site opening by searching official link, updated query to f"{site_name}"
    │       ├── download_handler.py   # Handles software downloads, uses LLM for install steps
    │       └── summarizer_handler.py # Handles content summarization (web/YouTube), with Whisper fallback, optional YouTube API enrich, changed parser to 'html.parser'
    └── llms/                  # LLMs
        ├── __init__.py
        ├── llm_base.py
        ├── llm_gemini.py
        └── llm_groq.py
└── frontend/                  # Flutter frontend, removed BrowserPage, integrated into ChatPage
    ├── README.md
    ├── analysis_options.yaml
    ├── pubspec.lock           # Updated with new deps like url_launcher
    ├── pubspec.yaml           # Added url_launcher
    ├── .metadata
    ├── android/               # (unchanged)
    ├── ios/                   # (unchanged)
    ├── lib/
    │   ├── main.dart          # Entry point
    │   ├── theme.dart         # Theme
    │   ├── pages/
    │   │   ├── chat_page.dart # Chat page, updated to handle markdown links with url_launcher
    │   │   ├── email_page.dart# Email page
    │   │   └── home_page.dart # Home, removed Browser button
    ├── linux/                 # (unchanged)
    ├── macos/                 # (unchanged)
    ├── test/                  # (unchanged)
    ├── web/                   # (unchanged)
    └── windows/               # (unchanged)
```