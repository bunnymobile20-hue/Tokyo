import asyncio
from playwright.async_api import async_playwright

async def open_url(url: str, headless: bool = False) -> str:
    """Opens a URL and returns the page title."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        page = await browser.new_page()
        await page.goto(url, wait_until="domcontentloaded")
        title = await page.title()
        # Sleep for a bit so the user can see it if it's not headless
        if not headless:
            await asyncio.sleep(2)
        await browser.close()
        return title

async def extract_text(url: str, headless: bool = True) -> dict:
    """Extracts text from a URL."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        page = await browser.new_page()
        await page.goto(url, wait_until="domcontentloaded")
        title = await page.title()
        # get all visible text
        text = await page.evaluate("document.body.innerText")
        await browser.close()
        return {
            "title": title,
            "text": text[:1000] + "..." if len(text) > 1000 else text # truncate for safety
        }
