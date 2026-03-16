import logging
from typing import cast, final

from playwright.async_api import ConsoleMessage as PlaywrightConsoleMessage
from patchright.async_api import ConsoleMessage as PatchrightConsoleMessage
from skin_trader.factory.purchase import PurchaseFactory
from skin_trader.managers.browser import Page
from skin_trader.managers.purchase import PurchaseManager

logger = logging.getLogger(__name__)

ConsoleMessage = PlaywrightConsoleMessage | PatchrightConsoleMessage


@final
class TradeOn:
    """
    Manages interactions with the TradeOn.space website to capture item data.

    This class utilizes a browser automation page to listen for specific console
    messages on the TradeOn.space live page. When a message containing item data
    is detected, it parses the data, creates a purchase request using the
    PurchaseFactory, and forwards it to the provided purchase manager.

    Args:
        purchase_manager: An instance of a BasePurchaseManager to which new
            purchase requests will be added.
        page: The browser page object used to interact with the website.

    Attributes:
        BASE_URL (str): The base URL for the TradeOn.space website.
        LOGIN_PAGE (str): The URL for the login page.
        APP_LIVE_PAGE (str): The URL for the live application page.
    """

    BASE_URL: str = "https://pulse.tradeon.space"
    LOGIN_PAGE: str = f"{BASE_URL}/app/login"
    APP_LIVE_PAGE: str = f"{BASE_URL}/app/live"

    def __init__(self, purchase_manager: PurchaseManager, page: Page) -> None:
        self.purchase_manager = purchase_manager
        self._page = page

    async def start(self):
        """
        Starts the TradeOn parser.

        This method registers a console message handler, starts the purchase
        manager, and navigates the browser page to the TradeOn live application
        page to begin monitoring for item data.
        """
        self._page.on("console", self._handle_console)
        await self.purchase_manager.start()
        await self._page.goto(self.APP_LIVE_PAGE)

    async def _validate_data(self, msg: ConsoleMessage) -> dict[str, dict[str, str]] | None:
        """
        Validates that the console message contains item data.

        Args:
            msg: The console message to validate.

        Returns:
            The item data if it exists, otherwise None.
        """
        if msg.type == "info" and msg.args:
            event = cast(str, await msg.args[0].json_value())
            if event == "[event] messageReceived":
                data = cast(dict[str, dict[str, str]], await msg.args[1].json_value())
                return data

    async def _handle_console(self, msg: ConsoleMessage):
        """
        Handles console messages from the page.

        Args:
            msg: The console message to handle.
        """
        data = await self._validate_data(msg)
        if data:
            purchase_request = PurchaseFactory.create_purchase(data)
            await self.purchase_manager.add_purchase(purchase_request)
