```
cleaned_ai_agent_project/
├── README.md                  # Updated with Gmail setup
├── requirements.txt           # Cleaned, added Google libs
├── setup.py                   # Packaging
├── .env.template              # LLM keys only (Gmail uses credentials.json)
├── config.yaml                # Simplified (no RAG/browser)
├── credentials.json           # Place your Google OAuth JSON here (not in Git)
└── src/
    ├── __init__.py
    ├── main.py                # FastAPI server
    ├── config.py              # Config loader
    ├── settings.py            # Env settings
    ├── llm_manager.py         # Only Gemini/Groq
    ├── agents/                # Agents
    │   ├── __init__.py
    │   ├── agent_manager.py   # Manages agents
    │   ├── base_agent.py      # Base class
    │   └── email_agent.py     # Modular Gmail API integration
    └── llms/                  # LLMs
        ├── __init__.py
        ├── llm_base.py
        ├── llm_gemini.py
        └── llm_groq.py
```