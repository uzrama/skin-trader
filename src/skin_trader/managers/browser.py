import logging
from contextlib import asynccontextmanager
from typing import final
import shutil
from patchright.async_api import Browser as PatchrightBrowser
from patchright.async_api import BrowserContext as PatchrightBrowserContext
from patchright.async_api import Page as PatchrightPage
from patchright.async_api import Playwright as Patchright
from playwright.async_api import Browser as PlaywrightBrowser
from playwright.async_api import BrowserContext as PlaywrightBrowserContext
from playwright.async_api import Page as PlaywrightPage
from playwright.async_api import Playwright

from skin_trader.configs.general import Settings
from skin_trader.exceptions.browser_manager import BrowserManagerError

Browser = PatchrightBrowser | PlaywrightBrowser
BrowserContext = PatchrightBrowserContext | PlaywrightBrowserContext
Page = PatchrightPage | PlaywrightPage


logger = logging.getLogger(__name__)


@final
class BrowserManager:
    """
    Manages the browser instance, including starting, stopping, and creating new pages.

    This class is a wrapper around Playwright's browser management capabilities.
    It can be used to manage both persistent and non-persistent browser contexts.
    """

    def __init__(self, settings: Settings, playwright: Playwright | Patchright) -> None:
        """
        Initializes the BrowserManager.

        Args:
            settings: The application settings.
            playwright: The Playwright or Patchright instance to use.
        """
        self.settings = settings
        self.playwright = playwright
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._is_persistent_context: bool = False

    async def _copy_extension_dirs(self):
        shutil.copytree(f"{self.settings.browser.extension_path}", f"{self.settings.browser.user_data_dir}/extensions", dirs_exist_ok=True)

    def _get_browser_args(self) -> list[str]:
        """
        Gets the browser arguments.

        Returns:
            A list of browser arguments.
        """
        args = ["--disable-blink-features=AutomationControlled"]

        if self.settings.browser.extension_path:
            extension_path = f"{self.settings.browser.user_data_dir}/extensions/proxy"
            args.extend(
                [
                    f"--disable-extensions-except={extension_path}",
                    f"--load-extension={extension_path}",
                ]
            )
        return args

    async def start_browser(self) -> Browser:
        """
        Starts a new browser instance.

        Raises:
            BrowserManagerError: If a browser instance already exists.

        Returns:
            The new browser instance.
        """
        if self._browser is not None:
            raise BrowserManagerError("Browser already exists")

        self._browser = await self.playwright.chromium.launch(
            headless=self.settings.browser.headless,
            args=self._get_browser_args(),
        )
        return self._browser

    async def start_with_persistent_context(self) -> BrowserContext:
        """
        Starts a new browser instance with a persistent context.

        Raises:
            BrowserManagerError: If a browser context already exists.

        Returns:
            The new browser context.
        """
        if self._context is not None:
            raise BrowserManagerError("Browser context already exists")
        await self._copy_extension_dirs()
        self._context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.settings.browser.user_data_dir,
            headless=self.settings.browser.headless,
            viewport=self.settings.browser.viewport,
            args=self._get_browser_args(),
        )
        self._is_persistent_context = True
        return self._context

    async def create_context(self) -> BrowserContext:
        """
        Creates a new browser context.

        Raises:
            BrowserManagerError: If the browser is not started or if the context is persistent.

        Returns:
            The new browser context.
        """
        if self._browser is None:
            raise BrowserManagerError("Browser not started. Call start_browser() first")

        if self._is_persistent_context:
            raise BrowserManagerError("Cannot create context for persistent browser")

        self._context = await self._browser.new_context()
        return self._context

    async def new_page(self) -> Page:
        """
        Creates a new page in the current browser context.

        Raises:
            BrowserManagerError: If no browser or context is available.

        Returns:
            The new page.
        """
        if self._context:
            return await self._context.new_page()
        elif self._browser:
            return await self._browser.new_page()
        else:
            raise BrowserManagerError("No browser or context available")

    @asynccontextmanager
    async def page_context(self):
        """
        A context manager that provides a new page and closes it automatically.

        Yields:
            The new page.
        """
        page = None
        try:
            page = await self.new_page()
            yield page
        except Exception as e:
            logger.error(f"Error in page context: {e}")
            raise
        finally:
            if page:
                try:
                    await page.close()
                    logger.debug("Page closed successfully")
                except Exception as e:
                    logger.warning(f"Failed to close browser page: {e}")

    async def close(self) -> None:
        """Closes the browser and/or context."""
        try:
            if self._context and not self._is_persistent_context:
                await self._context.close()

            if self._browser:
                await self._browser.close()
        finally:
            self._browser = None
            self._context = None
            self._is_persistent_context = False
