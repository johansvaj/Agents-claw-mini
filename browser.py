"""Browser automation for Agents Claw Mini."""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from .config import BrowserConfig
from .exceptions import BrowserException

logger = logging.getLogger("AgentsClawMini.Browser")

@dataclass
class PageInfo:
    """Information about a web page."""
    url: str
    title: str
    html: str
    text: str
    links: List[str]
    images: List[str]
    status_code: int = 200

class Browser:
    """
    Browser automation untuk web scraping dan automation.

    Supports:
    - Selenium WebDriver
    - Playwright (coming soon)
    - Stealth mode (anti-detection)
    - Proxy support
    - Headless/headed mode
    """

    def __init__(self, config: Optional[BrowserConfig] = None):
        self.config = config or BrowserConfig()
        self._driver = None
        self._playwright = None
        self._context = None
        self._page = None

    async def start(self):
        """Start browser instance."""
        if self.config.driver == "selenium":
            await self._start_selenium()
        elif self.config.driver == "playwright":
            await self._start_playwright()
        else:
            raise BrowserException(f"Driver '{self.config.driver}' tidak didukung")

        logger.info("🌐 Browser started (%s mode)", 
                   "headless" if self.config.headless else "headed")

    async def _start_selenium(self):
        """Start Selenium WebDriver."""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service

            options = Options()
            if self.config.headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument(f"--window-size={self.config.window_width},{self.config.window_height}")

            if self.config.user_agent:
                options.add_argument(f"--user-agent={self.config.user_agent}")

            if self.config.disable_images:
                prefs = {"profile.managed_default_content_settings.images": 2}
                options.add_experimental_option("prefs", prefs)

            if self.config.proxy:
                options.add_argument(f"--proxy-server={self.config.proxy}")

            if self.config.stealth_mode:
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)

            self._driver = webdriver.Chrome(options=options)

            if self.config.stealth_mode:
                self._driver.execute_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                )

        except ImportError:
            raise BrowserException("Selenium tidak terinstall. Run: pip install selenium")

    async def _start_playwright(self):
        """Start Playwright browser."""
        try:
            from playwright.async_api import async_playwright

            self._playwright = await async_playwright().start()
            browser = await self._playwright.chromium.launch(
                headless=self.config.headless,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )

            context_options = {
                "viewport": {"width": self.config.window_width, "height": self.config.window_height}
            }
            if self.config.user_agent:
                context_options["user_agent"] = self.config.user_agent

            self._context = await browser.new_context(**context_options)
            self._page = await self._context.new_page()

            if self.config.stealth_mode:
                await self._page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    window.chrome = { runtime: {} };
                """)

        except ImportError:
            raise BrowserException("Playwright tidak terinstall. Run: pip install playwright")

    async def goto(self, url: str, wait_for: Optional[str] = None) -> PageInfo:
        """Navigate to URL."""
        if not self._driver and not self._page:
            await self.start()

        try:
            if self.config.driver == "selenium" and self._driver:
                self._driver.get(url)
                if wait_for:
                    from selenium.webdriver.support.ui import WebDriverWait
                    from selenium.webdriver.support import expected_conditions as EC
                    from selenium.webdriver.common.by import By
                    WebDriverWait(self._driver, self.config.timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, wait_for))
                    )

                return self._get_page_info_selenium()

            elif self.config.driver == "playwright" and self._page:
                await self._page.goto(url, wait_until="networkidle")
                if wait_for:
                    await self._page.wait_for_selector(wait_for, timeout=self.config.timeout * 1000)

                return await self._get_page_info_playwright()

        except Exception as e:
            raise BrowserException(f"Gagal membuka {url}: {e}")

    def _get_page_info_selenium(self) -> PageInfo:
        """Get page info from Selenium."""
        from bs4 import BeautifulSoup

        html = self._driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text(separator='\n', strip=True)
        links = [a.get('href') for a in soup.find_all('a', href=True)]
        images = [img.get('src') for img in soup.find_all('img', src=True)]

        return PageInfo(
            url=self._driver.current_url,
            title=self._driver.title,
            html=html,
            text=text,
            links=links,
            images=images,
        )

    async def _get_page_info_playwright(self) -> PageInfo:
        """Get page info from Playwright."""
        html = await self._page.content()
        title = await self._page.title()
        url = self._page.url

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text(separator='\n', strip=True)
        links = await self._page.eval_on_selector_all('a[href]', 'elements => elements.map(e => e.href)')
        images = await self._page.eval_on_selector_all('img[src]', 'elements => elements.map(e => e.src)')

        return PageInfo(
            url=url,
            title=title,
            html=html,
            text=text,
            links=links,
            images=images,
        )

    async def click(self, selector: str):
        """Click element."""
        if self.config.driver == "selenium":
            from selenium.webdriver.common.by import By
            element = self._driver.find_element(By.CSS_SELECTOR, selector)
            element.click()
        elif self.config.driver == "playwright":
            await self._page.click(selector)

    async def type(self, selector: str, text: str):
        """Type text into element."""
        if self.config.driver == "selenium":
            from selenium.webdriver.common.by import By
            element = self._driver.find_element(By.CSS_SELECTOR, selector)
            element.clear()
            element.send_keys(text)
        elif self.config.driver == "playwright":
            await self._page.fill(selector, text)

    async def screenshot(self, path: str):
        """Take screenshot."""
        if self.config.driver == "selenium":
            self._driver.save_screenshot(path)
        elif self.config.driver == "playwright":
            await self._page.screenshot(path=path)
        logger.info("📸 Screenshot saved: %s", path)

    async def scroll(self, amount: int = 500):
        """Scroll page."""
        if self.config.driver == "selenium":
            self._driver.execute_script(f"window.scrollBy(0, {amount});")
        elif self.config.driver == "playwright":
            await self._page.evaluate(f"window.scrollBy(0, {amount})")

    async def close(self):
        """Close browser."""
        if self._driver:
            self._driver.quit()
            self._driver = None
        if self._context:
            await self._context.close()
            self._context = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
        logger.info("🌐 Browser closed")

    def __repr__(self):
        return f"Browser(driver={self.config.driver}, headless={self.config.headless})"
