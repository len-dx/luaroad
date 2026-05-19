import json
import os
from pathlib import Path

from luaroad_app.constants import ROOT_DIR, ENGINE_OPENSTEAMTOOL, DEFAULT_THEME


CONFIG_FILE = ROOT_DIR / "config.json"


class Settings:
    THEME = "theme"
    ENGINE = "engine"
    STEAM_PATH = "steam_path"
    RYUU_API_KEY = "ryuu_api_key"
    MANIFEST_API = "manifest_api"
    LUA_DIRS = "lua_dirs"
    WINDOW_GEOMETRY = "window_geometry"
    AUTO_RELOAD = "auto_reload"
    CHECK_UPDATES = "check_updates"
    LOG_LEVEL = "log_level"
    LANGUAGE = "language"
    CONFIGURED_GAMES = "configured_games"


DEFAULT_CONFIG = {
    Settings.THEME: DEFAULT_THEME,
    Settings.ENGINE: ENGINE_OPENSTEAMTOOL,
    Settings.STEAM_PATH: "",
    Settings.RYUU_API_KEY: "",
    Settings.MANIFEST_API: "steamrun",
    Settings.LUA_DIRS: [],
    Settings.WINDOW_GEOMETRY: "1200x800",
    Settings.AUTO_RELOAD: True,
    Settings.CHECK_UPDATES: True,
    Settings.LOG_LEVEL: "info",
    Settings.LANGUAGE: "en",
    Settings.CONFIGURED_GAMES: [],
}


class Config:
    def __init__(self):
        self._data = dict(DEFAULT_CONFIG)
        self._load()

    def _load(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r") as f:
                    loaded = json.load(f)
                    if "ryuub_api_key" in loaded and "ryuu_api_key" not in loaded:
                        loaded["ryuu_api_key"] = loaded.pop("ryuub_api_key")
                    self._data.update(loaded)
            except (json.JSONDecodeError, OSError):
                pass

    def save(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self._data, f, indent=2)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value
        self.save()

    def get_steam_path(self) -> Path | None:
        path = self.get(Settings.STEAM_PATH)
        if path:
            p = Path(path)
            if p.exists():
                return p
        return None

    def set_steam_path(self, path: str | Path):
        self.set(Settings.STEAM_PATH, str(path))

    def get_engine(self) -> str:
        return self.get(Settings.ENGINE, ENGINE_OPENSTEAMTOOL)

    def get_lua_dir(self, steam_path: Path) -> Path:
        from luaroad_app.constants import LUA_DIR_OST, LUA_DIR_LUMACORE
        engine = self.get_engine()
        subdir = LUA_DIR_OST if engine == "opensteamtool" else LUA_DIR_LUMACORE
        return steam_path / subdir

    def get_engine_dlls_dir(self) -> Path:
        from luaroad_app.constants import ENGINES_DIR
        return ENGINES_DIR / self.get_engine()
