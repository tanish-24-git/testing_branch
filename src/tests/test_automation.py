import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from automation.browser_automation import ChromeAutomation
from src.llm_manager import LLMManager
from src.rag import RAG

@pytest.mark.asyncio
async def test_navigate():
    automation = ChromeAutomation()
    automation.start_browser = AsyncMock()
    automation.page = MagicMock()
    automation.page.goto = AsyncMock(return_value=None)
    result = await automation.navigate("https://example.com")
    assert result == "Navigated to https://example.com"
    automation.page.goto.assert_called_with("https://example.com", wait_until="domcontentloaded")

@pytest.mark.asyncio
async def test_click_element():
    automation = ChromeAutomation()
    automation.start_browser = AsyncMock()
    automation.page = MagicMock()
    automation.page.click = AsyncMock(return_value=None)
    result = await automation.click_element("button#submit")
    assert result == "Clicked button#submit"
    automation.page.click.assert_called_with("button#submit")

@pytest.mark.asyncio
async def test_fill_form():
    automation = ChromeAutomation()
    automation.start_browser = AsyncMock()
    automation.page = MagicMock()
    automation.page.fill = AsyncMock(return_value=None)
    fields = {"name": "John", "email": "john@example.com"}
    result = await automation.fill_form(fields)
    assert result == f"Filled form with {fields}"
    automation.page.fill.assert_any_call("name", "John")
    automation.page.fill.assert_any_call("email", "john@example.com")

@pytest.mark.asyncio
async def test_submit_form():
    automation = ChromeAutomation()
    automation.start_browser = AsyncMock()
    automation.page = MagicMock()
    automation.page.evaluate = AsyncMock(return_value=None)
    result = await automation.submit_form()
    assert result == "Form submitted"
    automation.page.evaluate.assert_called_with("document.querySelector('form').submit()")

@pytest.mark.asyncio
async def test_execute_command():
    automation = ChromeAutomation()
    automation.start_browser = AsyncMock()
    automation.navigate = AsyncMock(return_value="Navigated to https://example.com")
    llm_manager = MagicMock()
    llm_manager.process = AsyncMock(return_value="navigate")
    rag = MagicMock()
    rag.retrieve = MagicMock(return_value=["context"])
    result = await automation.execute_command("navigate to https://example.com", llm_manager, rag)
    assert result == "Navigated to https://example.com"