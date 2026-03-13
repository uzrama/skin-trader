from abc import ABC, abstractmethod
import logging


from skin_trader.managers.browser import Page
from skin_trader.schemas.purchase import PurchaseRequest


logger = logging.getLogger(__name__)


class BaseMarket(ABC):
    """
    Abstract base class for market interactions.

    This class defines the standard interface for interacting with different skin trading marketplaces.
    It includes methods for essential functionalities such as retrieving account balances,
    purchasing items, and searching for items. Each marketplace implementation should
    inherit from this class and provide concrete implementations for the abstract methods.

    Attributes:
        NAME (str): The name of the marketplace.
        HOST (str): The hostname of the marketplace's website.
        SEARCH_URL (str): The base URL for searching items on the marketplace.
        balance (float): The current account balance on the marketplace.
    """

    NAME: str
    HOST: str
    SEARCH_URL: str

    def __init__(self):
        self.balance: float = 0.0

    @abstractmethod
    async def get_balance(self, page: Page) -> float:
        """
        Retrieves the current account balance from the marketplace.

        Args:
            page: The browser page object to interact with the marketplace.

        Returns:
            The account balance as a float.
        """
        pass

    @abstractmethod
    async def purchase_item(self, page: Page, purchase_request: PurchaseRequest):
        """
        Purchases an item from the marketplace.

        Args:
            page: The browser page object to interact with the marketplace.
            purchase_request: The request object containing details of the item to purchase.
        """
        pass
