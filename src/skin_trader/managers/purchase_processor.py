import logging
from typing import final

from skin_trader.exceptions.purchase_manager import PurchaseManagerError
from skin_trader.managers.browser import BrowserManager
from skin_trader.markets.base import BaseMarket
from skin_trader.schemas.purchase import PurchaseRequest
from skin_trader.managers.purchase_history import PurchaseHistoryManager

logger = logging.getLogger(__name__)


@final
class PurchaseProcessor:
    """
    Processes purchase requests.

    This class is responsible for processing purchase requests by checking the purchase history,
    executing the purchase on the appropriate market, and updating the purchase history.

    Attributes:
        markets: A list of available markets to purchase from.
        browser_manager: The manager for the browser instance.
        history_manager: The manager for the purchase history.
    """

    def __init__(
        self,
        markets: list[BaseMarket] | BaseMarket,
        browser_manager: BrowserManager,
        history_manager: PurchaseHistoryManager,
    ):
        if isinstance(markets, BaseMarket):
            markets = [markets]
        self.markets = markets
        self.browser_manager = browser_manager
        self.history_manager = history_manager

    async def process_purchase(self, purchase_request: PurchaseRequest):
        """
        Processes a single purchase request.

        This method will first check if the purchase limit for the item has been reached.
        If not, it will execute the purchase and add it to the history.

        Args:
            purchase_request: The purchase request to process.
        """
        try:
            can_purchase = await self.history_manager.can_purchase(purchase_request)

            if not can_purchase:
                logger.warning(f"Reached the purchase limit: {purchase_request.name}")
                return

            await self.execute_purchase(purchase_request)
            await self.history_manager.add(purchase_request)

        except Exception as e:
            await self.history_manager.decrement_purchase_count(purchase_request)
            logger.error(e)

    async def execute_purchase(self, purchase_request: PurchaseRequest):
        """
        Executes a purchase on the available markets.

        It will try to purchase the item on each market in order until it succeeds.

        Args:
            purchase_request: The purchase request to execute.

        Raises:
            PurchaseManagerError: If the purchase fails on all markets.
        """
        async with self.browser_manager.page_context() as page:
            for market in self.markets:
                try:
                    if market.NAME == purchase_request.market:
                        await market.purchase_item(page, purchase_request)
                except Exception as e:
                    raise PurchaseManagerError(f"The purchase {purchase_request.name} failed on {market.NAME}. {e}")
