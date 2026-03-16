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


class HaloSkins(BaseMarket):
    NAME: str = "Haloskins"
    HOST: str = "haloskins.io"
    SEARCH_URL: str = "https://www.haloskins.io/market?keyword="

    @override
    async def get_balance(self, page: Page) -> float: ...

    async def _get_first_item_with_price(self, page: Page) -> tuple[Locator, float]:
        await page.wait_for_timeout(2000)
        first_item = page.locator(".dynamic-grid > a.w-full.cursor-pointer").first
        price = await first_item.locator(".numFont.text-2xl.text-textPrimary").inner_text()
        try:
            return first_item, float(price)
        except ValueError as e:
            raise MarketError("Price is not float", e)

    @override
    async def purchase_item(self, page: Page, purchase_request: PurchaseRequest):
        try:
            await page.goto(f"{self.SEARCH_URL}{purchase_request.name}&sort=1")
            first_item, price_market = await self._get_first_item_with_price(page)
            if price_market > purchase_request.price:
                logger.warning(f"Price changed: {price_market} on market, expected {purchase_request.price}.")
                raise MarketError("Price changed")
            # # Click item
            await first_item.click()
            first_item = page.locator(".list_hover").first
            price_market = await first_item.locator(".numFont.text-xl.text-textPrimary").inner_text()
            if float(price_market) > purchase_request.price:
                logger.warning(f"Price changed: {price_market} on market, expected {purchase_request.price}.")
                raise MarketError("Price changed")
            await first_item.locator(".ant-btn.ant-btn-primary").click()
            await page.locator("#buyBtnSign").click()
            succesful = await page.locator(".ant-modal-confirm-title").inner_text()
            # if succesful != "Completed":
            #     print(succesful)
            #     raise MarketError("At the end of the purchase, problems arose.")
            await page.wait_for_timeout(30000)
        except Exception as e:
            raise e
