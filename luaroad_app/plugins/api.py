import requests


class PluginAPI:
    def __init__(self, app_ref):
        self._app = app_ref

    def log(self, message: str, level: str = "info"):
        self._app.log(message, level)

    def http_get(self, url: str, headers: dict | None = None) -> tuple:
        try:
            hdrs = headers or {}
            resp = requests.get(url, headers=hdrs, timeout=15)
            return resp.text, resp.status_code
        except Exception as e:
            return None, str(e)

    def http_post(self, url: str, body: str, headers: dict | None = None) -> tuple:
        try:
            hdrs = headers or {}
            resp = requests.post(url, data=body, headers=hdrs, timeout=15)
            return resp.text, resp.status_code
        except Exception as e:
            return None, str(e)

    def get_setting(self, key: str, default=None):
        return self._app.config.get(key, default)

    def set_setting(self, key: str, value):
        self._app.config.set(key, value)

    def get_steam_path(self) -> str | None:
        sp = self._app.config.get_steam_path()
        return str(sp) if sp else None

    def get_games(self) -> list:
        return self._app.get_configured_games()

    def add_game(self, appid: int, depot_key: str = ""):
        self._app.add_game(appid, depot_key)

    def remove_game(self, appid: int):
        self._app.remove_game(appid)

    def notify(self, title: str, message: str):
        self._app.show_notification(title, message)

    def get_app_version(self) -> str:
        from luaroad_app.constants import APP_VERSION
        return APP_VERSION
