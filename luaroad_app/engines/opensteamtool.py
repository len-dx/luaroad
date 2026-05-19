import shutil
from pathlib import Path

from luaroad_app.engines.base import EngineBase
from luaroad_app.constants import (
    ENGINES_DIR, OPENSTEAMTOOL_RELEASE,
    OPENSTEAMTOOL_DLL, OPENSTEAMTOOL_DWMAPI, OPENSTEAMTOOL_XINPUT,
    LUA_DIR_OST,
)
from luaroad_app.utils.helpers import copy_dlls


class OpenSteamToolEngine(EngineBase):
    name = "opensteamtool"
    display_name = "OpenSteamTool"
    description = "Open-source Steam unlocker with Lua config, hot reload, and manifest support"

    def __init__(self, steam_path: Path | None):
        super().__init__(steam_path)
        self._engine_dir = ENGINES_DIR / self.name
        self._version = self._detect_version()

    def _detect_version(self) -> str:
        dll_path = self._engine_dir / OPENSTEAMTOOL_DLL
        if not dll_path.exists():
            dll_path = OPENSTEAMTOOL_RELEASE / OPENSTEAMTOOL_DLL
        if dll_path.exists():
            try:
                import struct
                with open(dll_path, "rb") as f:
                    data = f.read()
                import re
                match = re.search(rb'v?(\d+\.\d+\.\d+)', data)
                if match:
                    return match.group(1).decode()
            except Exception:
                pass
        return "unknown"

    def get_dlls_to_copy(self) -> list[str]:
        return [OPENSTEAMTOOL_DLL, OPENSTEAMTOOL_DWMAPI, OPENSTEAMTOOL_XINPUT]

    def install(self) -> bool:
        if not self.steam_path:
            return False
        if not self._engine_dir.exists():
            self._engine_dir.mkdir(parents=True, exist_ok=True)
        src_dlls = [OPENSTEAMTOOL_DLL, OPENSTEAMTOOL_DWMAPI, OPENSTEAMTOOL_XINPUT]
        src_dir = OPENSTEAMTOOL_RELEASE
        copied = copy_dlls(src_dir, self._engine_dir, src_dlls)
        if len(copied) < 2:
            copied = copy_dlls(src_dir, self._engine_dir, src_dlls)
        copied_to_steam = copy_dlls(self._engine_dir, self.steam_path, src_dlls)
        lua_dir = self.steam_path / LUA_DIR_OST
        if not lua_dir.exists():
            lua_dir.mkdir(parents=True, exist_ok=True)
        return len(copied_to_steam) >= 2

    def uninstall(self) -> bool:
        if not self.steam_path:
            return False
        for dll in self.get_dlls_to_copy():
            f = self.steam_path / dll
            if f.exists():
                f.unlink()
        return True

    def is_installed(self) -> bool:
        if not self.steam_path:
            return False
        for dll in self.get_dlls_to_copy():
            if (self.steam_path / dll).exists():
                return True
        return False

    def get_version(self) -> str:
        return self._version

    def get_lua_directory(self) -> Path | None:
        if self.steam_path:
            return self.steam_path / LUA_DIR_OST
        return None
