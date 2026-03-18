import logging
from typing import final

from skin_trader.configs.general import Settings
from skin_trader.managers.browser import BrowserManager
from skin_trader.markets.base import BaseMarket
from skin_trader.schemas.purchase import PurchaseRequest
from skin_trader.managers.purchase_history import PurchaseHistoryManager
from skin_trader.managers.purchase_processor import PurchaseProcessor
from skin_trader.managers.purchase_worker import PurchaseWorker


logger = logging.getLogger(__name__)


@final
class PurchaseManager:
    """
    Manages the purchase of items from different markets.

    This class acts as a facade, coordinating the purchase queue,
    history, and processing.
    """

    def __init__(
        self,
        markets: list[BaseMarket] | BaseMarket,
        browser_manager: BrowserManager,
        settings: Settings,
    ):
        """
        Initializes the PurchaseManager.

        Args:
            markets: A list of markets or a single market to purchase from.
            browser_manager: The browser manager to use for web scraping.
            purchase_service: The service to use for recording purchase history.
            settings: The application settings.
        """
        self.history_manager = PurchaseHistoryManager(settings.purchase_manager.history_file_path)
        self.processor = PurchaseProcessor(
            markets=markets,
            browser_manager=browser_manager,
            history_manager=self.history_manager,
        )
        self.purchase_worker = PurchaseWorker(settings=settings, purchase_processor=self.processor)

    async def add_purchase(self, purchase_request: PurchaseRequest):
        """
        Adds a purchase request to the queue.

        Args:
            purchase_request: The purchase request to add to the queue.
        """
        await self.purchase_worker.add_purchase(purchase_request)

    async def start(self):
        """Starts the purchase manager."""
        await self.history_manager.load()
        await self.purchase_worker.start()

    async def stop(self):
        """Stops the purchase manager."""
        await self.purchase_worker.stop()
