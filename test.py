from playwright.async_api import async_playwright
import asyncio

async def test_browser():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://google.com")
        title = await page.title()
        print(f"Page title: {title}")
        await browser.close()

asyncio.run(test_browser())