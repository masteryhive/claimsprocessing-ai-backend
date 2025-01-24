from playwright.async_api import async_playwright, Page
from src.pipelines.local_markets._base import IBrowser
from src.pipelines.local_markets.jiji.config import BrowserConfig
from src.error_trace.errorlogger import system_logger
import re
import asyncio
from playwright.async_api import expect

class PlaywrightBrowser(IBrowser):
    def __init__(self, email: str, password: str, timeout: int = BrowserConfig.LOGIN_TIMEOUT):
        self.email = email
        self.password = password
        self.timeout = timeout
        self.playwright = None
        self.browser = None
        self.storage_state = None

    async def initialize(self) -> None:
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=['--disable-dev-shm-usage', '--no-sandbox']
            )
            # Initial login and storage state capture
            context = await self.browser.new_context()
            page = await context.new_page()
            await self._perform_login(page)
            self.storage_state = await context.storage_state()
            await context.close()
        except Exception as e:
            await self.cleanup()
            raise RuntimeError(f"Browser initialization failed: {e}") from e


    async def create_authenticated_page(self) -> Page:
        if not self.storage_state:
            raise RuntimeError("Browser not initialized")
        context = await self.browser.new_context(storage_state=self.storage_state)
        return await context.new_page()

    # async def cleanup(self) -> None:
    #     try:
    #         if self.context:
    #             await self.context.close()
    #         if self.browser:
    #             await self.browser.close()
    #         if self.browsers:
    #             await asyncio.gather(*[browser.close() for browser in self.browsers])
    #         if self.playwright:
    #             await self.playwright.stop()
    #     except Exception as e:
    #         system_logger.error(f"Cleanup failed: {e}")
            
    # In playwright_browser.py
    async def cleanup(self) -> None:
        cleanup_tasks = []
        if hasattr(self, 'context'):
            cleanup_tasks.append(self.context.close())
        if hasattr(self, 'browser'):
            cleanup_tasks.append(self.browser.close())
        if hasattr(self, 'playwright'):
            cleanup_tasks.append(self.playwright.stop())
        
        await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        # Reset state
        self.playwright = None
        self.browser = None
        self.context = None

    async def _perform_login(self, page: Page) -> bool:
        try:
            await page.goto("https://www.jiji.ng/login.html", timeout=self.timeout * 1000)
            await page.wait_for_load_state('load')
            await expect(page.get_by_text("E-mail or phone", exact=True)).to_be_visible()
            
            await page.get_by_role("button", name=re.compile("E-mail or phone", re.IGNORECASE)).click()
            await asyncio.sleep(3)
            await page.fill(".qa-login-field", self.email)
            await page.fill(".qa-password-field", self.password)
            
            login_button = page.get_by_role("button", name=re.compile("SIGN IN", re.IGNORECASE))
            await expect(login_button).to_be_visible()
            await login_button.click()
            await asyncio.sleep(3)
            return True
        except Exception as e:
            system_logger.error(f"Login failed: {e}")
            return False