import os
from pathlib import Path

APP_NAME = "Luaroad"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Luaroad Team"

ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LUAROAD_APP_DIR = ROOT_DIR / "luaroad_app"

PLUGINS_DIR = ROOT_DIR / "plugins"
ENGINES_DIR = ROOT_DIR / "engines"
LUA_CONFIGS_DIR = ROOT_DIR / "lua_configs"

OPENSTEAMTOOL_SRC = ROOT_DIR / "OpenSteamTool"
OPENSTEAMTOOL_RELEASE = ROOT_DIR / "OpenSteamToolRelease"

MANIFEST_API_STEAMRUN = "https://manifest.steam.run/api/manifest/{gid}"
MANIFEST_API_RYUU = "https://api.ryuu.gg/manifest/{gid}"

STEAM_PATHS_WIN = [
    Path("C:/Program Files (x86)/Steam"),
    Path("C:/Program Files/Steam"),
]

REGISTRY_STEAM_PATH = r"SOFTWARE\Valve\Steam"
REGISTRY_STEAM_PATH_32 = r"SOFTWARE\WOW6432Node\Valve\Steam"

DEFAULT_THEME = "dark"
SUPPORTED_THEMES = ["dark", "light"]

ENGINE_OPENSTEAMTOOL = "opensteamtool"
ENGINE_LUMACORE = "lumacore"
SUPPORTED_ENGINES = [ENGINE_OPENSTEAMTOOL, ENGINE_LUMACORE]

LUA_DIR_OST = "config/lua"
LUA_DIR_LUMACORE = "config/stplug-in"

OPENSTEAMTOOL_DLL = "OpenSteamTool.dll"
OPENSTEAMTOOL_DWMAPI = "dwmapi.dll"
OPENSTEAMTOOL_XINPUT = "xinput1_4.dll"

LUMACORE_DLL = "LumaCore.dll"
LUMACORE_DWMAPI = "dwmapi.dll"
