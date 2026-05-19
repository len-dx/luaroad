import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

from luaroad_app.config import Config
from luaroad_app.constants import APP_NAME, APP_VERSION, PLUGINS_DIR, LUA_CONFIGS_DIR
from luaroad_app.engines.manager import EngineManager
from luaroad_app.plugins.api import PluginAPI
from luaroad_app.plugins.engine import LuaPluginEngine
from luaroad_app.plugins.registry import PluginRegistry
from luaroad_app.services.manifest import ManifestService
from luaroad_app.services.ryuu import RyuuService
from luaroad_app.services.steam import SteamService
from luaroad_app.utils.steam_path import find_steam_path
from luaroad_app.ui.theme import setup_theme


class LuaroadApp:
    def __init__(self):
        self.config = Config()

        self.engine_manager = EngineManager(self.config)
        self.manifest_service = ManifestService()
        self.ryuu_service = RyuuService(self.config.get("ryuu_api_key", ""))
        self.steam_service = SteamService(self.config.get_steam_path())
        self.plugin_registry = PluginRegistry()
        self.plugin_api = PluginAPI(self)
        self.plugin_engine = LuaPluginEngine(self.plugin_api)

        from luaroad_app.services.download_manager import DownloadManager
        self.download_manager = DownloadManager()

        self._log_buffer = []
        self.tabs = {}

        self._root = None

    def start(self):
        self._root = tk.Tk()
        self._root.title(f"{APP_NAME} v{APP_VERSION}")
        self._root.geometry(self.config.get("window_geometry", "1200x800"))
        self._root.minsize(900, 600)

        setup_theme(self._root, self.config.get("theme", "dark"))

        self._build_ui()

        self._auto_detect_steam()
        self._load_plugins()

        self._root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._root.mainloop()

    def _build_ui(self):
        notebook = ttk.Notebook(self._root)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)

        from luaroad_app.ui.home_tab import HomeTab
        from luaroad_app.ui.games_tab import GamesTab
        from luaroad_app.ui.manifests_tab import ManifestsTab
        from luaroad_app.ui.plugins_tab import PluginsTab
        from luaroad_app.ui.tools_tab import ToolsTab
        from luaroad_app.ui.settings_tab import SettingsTab
        from luaroad_app.ui.downloads_tab import DownloadsTab
        from luaroad_app.ui.fix_game_tab import FixGameTab
        from luaroad_app.ui.cloud_saves_tab import CloudSavesTab

        home = HomeTab(notebook, self)
        notebook.add(home.frame, text="Home")
        self.tabs["home"] = home

        games = GamesTab(notebook, self)
        notebook.add(games.frame, text="Games")
        self.tabs["games"] = games

        downloads = DownloadsTab(notebook, self)
        downloads.set_download_manager(self.download_manager)
        notebook.add(downloads.frame, text="Downloads")
        self.tabs["downloads"] = downloads

        manifests = ManifestsTab(notebook, self)
        notebook.add(manifests.frame, text="Manifests")
        self.tabs["manifests"] = manifests

        fix_game = FixGameTab(notebook, self)
        notebook.add(fix_game.frame, text="Fix Game")
        self.tabs["fix_game"] = fix_game

        cloud = CloudSavesTab(notebook, self)
        notebook.add(cloud.frame, text="Cloud Saves")
        self.tabs["cloud_saves"] = cloud

        plugins = PluginsTab(notebook, self)
        notebook.add(plugins.frame, text="Plugins")
        self.tabs["plugins"] = plugins

        tools = ToolsTab(notebook, self)
        notebook.add(tools.frame, text="Tools")
        self.tabs["tools"] = tools

        settings = SettingsTab(notebook, self)
        notebook.add(settings.frame, text="Settings")
        self.tabs["settings"] = settings

        status_frame = ttk.Frame(self._root)
        status_frame.pack(fill="x", padx=5, pady=(0, 5))

        self._status_label = ttk.Label(status_frame, text="Ready", anchor="w")
        self._status_label.pack(side="left", fill="x", expand=True)

        engine = self.engine_manager.get_current_engine()
        self._engine_label = ttk.Label(status_frame, text=f"Engine: {engine.get_name()} v{engine.get_version()}", anchor="e")
        self._engine_label.pack(side="right", padx=5)

    def _auto_detect_steam(self):
        if not self.config.get_steam_path():
            p = find_steam_path()
            if p:
                self.config.set_steam_path(str(p))
                self.steam_service = SteamService(p)
                self.log(f"Auto-detected Steam at: {p}", "info")

    def _load_plugins(self):
        if PLUGINS_DIR.exists():
            self.plugin_engine.load_directory(PLUGINS_DIR)
            plugins = self.plugin_engine.get_all_plugins()
            if plugins:
                self.log(f"Loaded {len(plugins)} plugin(s)", "info")
                for p in plugins:
                    p.call("on_load")

    def log(self, message: str, level: str = "info"):
        import datetime
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        formatted = f"[{ts}] [{level.upper()}] {message}"
        self._log_buffer.append(formatted)
        if hasattr(self, '_status_label'):
            self._status_label.config(text=message)
        print(formatted)

    def show_notification(self, title: str, message: str):
        try:
            from tkinter import messagebox
            self._root.after(0, messagebox.showinfo, title, message)
        except Exception:
            pass

    def open_folder(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)
        import os
        os.startfile(str(path))

    def open_steam_folder(self):
        sp = self.config.get_steam_path()
        if sp:
            self.open_folder(sp)
        else:
            self.log("Steam path not configured", "warning")

    def open_lua_folder(self):
        engine = self.engine_manager.get_current_engine()
        lua_dir = engine.get_lua_directory()
        if lua_dir:
            self.open_folder(lua_dir)
        else:
            self.log("No lua directory available", "warning")

    def open_plugins_folder(self):
        self.open_folder(PLUGINS_DIR)

    def get_configured_games(self) -> list:
        games_tab = self.tabs.get("games")
        if games_tab:
            return games_tab._games
        return []

    def add_game(self, appid: int, depot_key: str = ""):
        games_tab = self.tabs.get("games")
        if games_tab:
            if appid not in [g.get("appid") for g in games_tab._games]:
                games_tab._games.append({"appid": appid, "name": "", "depot_key": depot_key, "token": "", "manifest_gid": ""})
                games_tab._refresh_tree(select_appid=appid)

    def remove_game(self, appid: int):
        games_tab = self.tabs.get("games")
        if games_tab:
            games_tab._games = [g for g in games_tab._games if g.get("appid") != appid]
            games_tab._refresh_tree()

    def _menu_install_engine(self):
        engine = self.engine_manager.get_current_engine()
        if engine.install():
            self.log(f"Engine {engine.get_name()} installed to Steam", "info")
        else:
            self.log(f"Engine installation failed", "error")

    def _menu_uninstall_engine(self):
        engine = self.engine_manager.get_current_engine()
        if engine.uninstall():
            self.log(f"Engine {engine.get_name()} removed from Steam", "info")
        else:
            self.log(f"Engine removal failed", "error")

    def _refresh_all(self):
        home_tab = self.tabs.get("home")
        if home_tab:
            home_tab.refresh()
        engine = self.engine_manager.get_current_engine()
        self._engine_label.config(text=f"Engine: {engine.get_name()} v{engine.get_version()}")
        self.log("Status refreshed", "info")

    def _show_about(self):
        from luaroad_app.ui.dialogs import AboutDialog
        AboutDialog(self._root)

    def _on_close(self):
        geometry = self._root.geometry()
        self.config.set("window_geometry", geometry.split("+")[0])
        self._root.destroy()
