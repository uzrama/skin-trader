import logging
import re
from typing import final, override

from patchright.async_api import Locator as PatchrightLocator
from playwright.async_api import Locator as PlaywrightLocator

from skin_trader.exceptions.market import MarketError
from skin_trader.managers.browser import Page
from skin_trader.markets.base import BaseMarket
from skin_trader.schemas.purchase import PurchaseRequest

logger = logging.getLogger(__name__)

Locator = PlaywrightLocator | PatchrightLocator


@final
class CSFloat(BaseMarket):
    NAME = "CsFloat"
    HOST = "csfloat.com"
    SEARCH_URL = "https://csfloat.com/search?sort_by=lowest_price&type=buy_now&market_hash_name="

    @override
    async def get_balance(self, page: Page) -> float:
        selector = ".balance-container"
        balance_text = await page.locator(selector).inner_text()
        balance = re.sub(r"[^\d.]", "", balance_text)
        return float(balance)

    async def _get_first_item_with_price(self, page: Page) -> tuple[Locator, float]:
        await page.wait_for_timeout(5000)
        first_item = page.locator("item-card").first
        price_text = await first_item.locator(".price").inner_text()
        price = re.sub(r"[^\d.]", "", price_text)
        return first_item, float(price)

    async def _wait_click_button(self, page: Page, selector: str):
        btn = page.locator(selector)
        await btn.wait_for(timeout=10000)
        await btn.click()

    @override
    async def purchase_item(self, page: Page, purchase_request: PurchaseRequest):
        try:
            await page.goto(f"{self.SEARCH_URL}{purchase_request.name}")
            first_item, price_market = await self._get_first_item_with_price(page)
            if price_market > purchase_request.price:
                logger.warning(f"Price changed: {price_market} on market, expected {purchase_request.price}.")
                raise MarketError("Price changed")
            await first_item.click()
            try:
                await self._wait_click_button(
                    page, 'xpath=//*[@id="mat-mdc-dialog-0"]/div/div/item-detail/div/div[2]/item-card/mat-card/div/div[3]/div[4]/div/div/div/button[2]'
                )
            except Exception:
                raise MarketError("Couldn't find the button: 'Buy now'")

            try:
                await self._wait_click_button(page, 'xpath=//*[@id="cdk-overlay-2"]/app-confirm-dialog/div/div[2]/button[1]')
            except Exception:
                raise MarketError("Couldn't find the button: 'Yes'")
            await page.wait_for_timeout(50000)
        except Exception:
            raise
