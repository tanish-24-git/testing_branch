# Chrome Automation Guide

This document outlines the Chrome automation features of the chat bot, implemented using Playwright for cross-platform browser control. Automation tasks are permission-first, modular, and integrated with the existing LLM and RAG systems.

## Supported Commands
- **Navigate**: `navigate to <url>` (e.g., `navigate to https://example.com`)
- **Click**: `click <selector>` (e.g., `click button#submit`)
- **Fill Form**: `fill form <field1>=<value1>,<field2>=<value2>` (e.g., `fill form name=John,email=john@example.com`)
- **Submit Form**: `submit form` (requires user confirmation)
- **Send Email**: `send email to <recipient> with subject <subject> and body <body>` (requires draft approval)
- **Make Payment**: `make payment of <amount> to <vendor>` (requires confirmation)

## Permission-First Workflow
- **Payments**: User must confirm via GUI before execution.
- **Emails**: Draft is shown in GUI; user approves before sending.
- **Form Submissions**: Details displayed for confirmation.
- **Repetitive Actions**: Pre-approved flows stored in `docs/` (future DB integration).

## Implementation Details
- **Module**: `src/automation/chrome_automation.py`
- **Pipeline**: `src/pipelines/automation_pipeline.py`
- **LLM Integration**: Uses `LLMManager` to parse commands and generate instructions.
- **RAG**: Retrieves context from `docs/` for user-specific patterns.
- **Logging**: All actions logged to `assistant.log`.
- **Database Hooks**: Interfaces in `src/storage/db_interface.py` for future storage.
- **Testing**: Unit tests in `tests/test_automation.py` with mocks.

## Security
- Multi-step confirmation for sensitive actions.
- API keys stored in `.env` and accessed via `settings.py`.
- Browser runs in headless mode by default (configurable in `config.yaml`).

## Example Usage
1. Run backend: `python src/main.py`
2. Run GUI: `python gui.py`
3. Enter command: `navigate to https://example.com`
4. Click "Run Automation" and confirm.
5. Response appears in GUI chat history.

## Future Improvements
- Full database integration for storing automation flows.
- Advanced LLM parsing for complex automation scripts.
- Web interface for broader accessibility.