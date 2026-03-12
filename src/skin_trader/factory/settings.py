from skin_trader.configs.account import AccountSetting
from skin_trader.configs.browser import BrowserSetting
from skin_trader.configs.purchase_manager import PurchaseManagerSetting
from skin_trader.configs.general import Settings


def create_settings() -> Settings:
    account = AccountSetting()
    user_data_dir = f"./browser_data/profiles/{account.username}"
    return Settings(
        account=account,
        browser=BrowserSetting(user_data_dir=user_data_dir),
        purchase_manager=PurchaseManagerSetting(),
    )
