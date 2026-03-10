from pydantic import BaseModel

from skin_trader.configs.account import AccountSetting
from skin_trader.configs.browser import BrowserSetting
from skin_trader.configs.purchase_manager import PurchaseManagerSetting


class Settings(BaseModel):
    browser: BrowserSetting
    account: AccountSetting
    purchase_manager: PurchaseManagerSetting
