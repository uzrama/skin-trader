from skin_trader.configs.base import EnvSettings


class PurchaseManagerSetting(EnvSettings, env_prefix="PURCHASE_MANAGER_"):
    max_concurrent: int = 3
    max_queue: int = 200
    history_file_path: str = "purchases.csv"
