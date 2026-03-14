import logging
from typing import override

from patchright.async_api import Locator as PatchrightLocator
from playwright.async_api import Locator as PlaywrightLocator

from skin_trader.exceptions.market import MarketError
from skin_trader.managers.browser import Page
from skin_trader.markets.base import BaseMarket
from skin_trader.schemas.purchase import PurchaseRequest

logger = logging.getLogger(__name__)

Locator = PlaywrightLocator | PatchrightLocator


class CSMoney(BaseMarket):
    NAME: str = "CsMoneyMarket"
    HOST: str = "cs.money"
    SEARCH_URL: str = "https://cs.money/market/buy/?sort=price&order=asc&search="

    @override
    async def get_balance(self, page: Page) -> float: ...

    async def _get_first_item_with_price(self, page: Page) -> tuple[Locator, float]:
        await page.wait_for_timeout(2000)
        first_item = page.locator("[data-card-item-id]").first
        price = await first_item.get_attribute("data-card-price")
        if price is None:
            raise MarketError("Price attribute not found")
        return first_item, float(price)

    @override
    async def purchase_item(self, page: Page, purchase_request: PurchaseRequest):
        try:
            await page.goto(f"{self.SEARCH_URL}{purchase_request.name}")
            first_item, price_market = await self._get_first_item_with_price(page)
            if price_market > purchase_request.price:
                logger.warning(f"Price changed: {price_market} on market, expected {purchase_request.price}.")
                raise MarketError("Price changed")
            # Click item
            await first_item.locator(".csm_8f18f147").click()
            # Wait 1 sec
            await page.wait_for_timeout(4000)
            # Click cart
            await page.locator(".csm_6c0017b4").click()
            # Click Buy
            await page.locator(".csm_4ca4f039").click()
            await page.wait_for_timeout(26000)
        except Exception as e:
            raise e
