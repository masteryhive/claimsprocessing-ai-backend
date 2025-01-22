from playwright.async_api import async_playwright, Page
from src.pipelines.local_markets._base import IBrowser
from src.error_trace.errorlogger import system_logger
import re
import asyncio
from playwright.async_api import expect

class PlaywrightBrowser(IBrowser):
    def __init__(self, email: str, password: str, timeout: int = 30):
        self.email = email
        self.password = password
        self.timeout = timeout
        self.playwright = None
        self.browser = None
        self.context = None

    async def initialize(self) -> None:
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=['--disable-dev-shm-usage', '--no-sandbox', '--disable-gpu']
            )
            self.context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
        except Exception as e:
            system_logger.error(f"Browser initialization failed: {e}")
            await self.cleanup()

    async def cleanup(self) -> None:
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            system_logger.error(f"Cleanup failed: {e}")
            
    #TODO: set notimplementedError
    async def login(self, page: Page) -> bool:
        try:
            await page.goto("https://www.jiji.ng/login.html", timeout=self.timeout * 1000)
            await expect(page.get_by_text("E-mail or phone", exact=True)).to_be_visible()
            
            await page.get_by_role("button", name=re.compile("E-mail or phone", re.IGNORECASE)).click()
            await asyncio.sleep(3)
            await page.fill(".qa-login-field", self.email)
            await page.fill(".qa-password-field", self.password)
            
            login_button = page.get_by_role("button", name=re.compile("SIGN IN", re.IGNORECASE))
            await expect(login_button).to_be_visible()
            await login_button.click()
            
            await page.wait_for_load_state("networkidle")
            return True
        except Exception as e:
            system_logger.error(f"Login failed: {e}")
            return False