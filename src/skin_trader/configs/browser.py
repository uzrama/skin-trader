from patchright.async_api import ViewportSize
from skin_trader.configs.base import EnvSettings


class BrowserSetting(EnvSettings, env_prefix="BROWSER_"):
    headless: bool = False
    extension_path: str | None = None
    user_data_dir: str
    viewport: ViewportSize = {"width": 1920, "height": 1200}
