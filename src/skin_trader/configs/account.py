from skin_trader.configs.base import EnvSettings


class AccountSetting(EnvSettings, env_prefix="ACCOUNT_"):
    username: str = "defualt"
