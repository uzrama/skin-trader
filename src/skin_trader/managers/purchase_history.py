import asyncio
import logging
from typing import final
from collections import Counter

from skin_trader.schemas.purchase import PurchaseRequest
from skin_trader.services.purchase import PurchaseCSVService

logger = logging.getLogger(__name__)


@final
class PurchaseHistoryManager:
    """
    Manages the purchase history of items.

    This class is responsible for loading the purchase history, adding new purchases,
    and checking if a purchase can be made based on the purchase limit.

    Attributes:
        purchase_service: The service for interacting with the purchase history data.
        purchase_counter: A counter for the number of times each item has been purchased.
    """

    def __init__(self, file_path: str):
        self.purchase_service = PurchaseCSVService(file_path=file_path)
        self._purchase_counter: Counter[str] = Counter()
        self._lock = asyncio.Lock()

    async def load(self):
        """
        Loads the purchase history from the purchase service.
        """
        purchases = await self.purchase_service.get_all()
        name_purchases = [purchase.name for purchase in purchases]
        self._purchase_counter = Counter(name_purchases)
        logger.info(f"Loaded {len(self._purchase_counter)} items from purchase history")

    async def add(self, created_purchase: PurchaseRequest) -> None:
        """
        Adds a purchase to the history.

        Args:
            created_purchase: The purchase to add to the history.
        """
        created_purchase = await self.purchase_service.create(created_purchase)
        logger.info(f"Added or updated purchase in history: {created_purchase.name}")

    async def can_purchase(self, purchase_request: PurchaseRequest) -> bool:
        """
        Checks if the purchase can be made.

        Args:
            purchase_request: The purchase request to check.

        Returns:
            True if the purchase can be made, False otherwise.
        """
        async with self._lock:
            current_count = self._purchase_counter[purchase_request.name]
            can_purchase = False

            if not current_count >= purchase_request.purchase_limit:
                self._purchase_counter.update([purchase_request.name])
                can_purchase = True

            return can_purchase

    async def decrement_purchase_count(self, purchase_request: PurchaseRequest):
        """
        Decrements the purchase count for an item.

        Args:
            purchase_request: The purchase request to decrement the count for.
        """
        async with self._lock:
            self._purchase_counter.subtract([purchase_request.name])

    @property
    def purchase_counter(self) -> Counter[str]:
        return self._purchase_counter
