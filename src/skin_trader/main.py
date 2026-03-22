import asyncio
import logging
import uvloop
import coloredlogs
from playwright.async_api import async_playwright

from skin_trader.factory.settings import create_settings
from skin_trader.managers.browser import BrowserManager
from skin_trader.managers.purchase import PurchaseManager
from skin_trader.markets import CSFloat, CSMoney
from skin_trader.markets.haloskins import HaloSkins
from skin_trader.parsers.tradeon import TradeOn


logging.getLogger("skin_trader.managers.browser").disabled = True


async def start():
    coloredlogs.install(level=logging.INFO)  # pyright: ignore[reportUnknownMemberType]
    settings = create_settings()
    playwright = await async_playwright().start()
    browser_manager = BrowserManager(settings=settings, playwright=playwright)
    await browser_manager.start_with_persistent_context()
    purchase_manager = PurchaseManager(
        markets=[CSMoney(), CSFloat(), HaloSkins()],
        browser_manager=browser_manager,
        settings=settings,
    )
    try:
        async with browser_manager.page_context() as page:
            await TradeOn(page=page, purchase_manager=purchase_manager).start()
            while True:
                await asyncio.sleep(2000)
    finally:
        await browser_manager.close()


def main():
    uvloop.install()
    asyncio.run(start())


if __name__ == "__main__":
    main()
