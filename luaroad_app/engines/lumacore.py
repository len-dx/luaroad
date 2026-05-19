import shutil
from pathlib import Path

from luaroad_app.engines.base import EngineBase
from luaroad_app.constants import (
    ENGINES_DIR, LUA_DIR_LUMACORE,
    LUMACORE_DLL, LUMACORE_DWMAPI,
)


class LumaCoreEngine(EngineBase):
    name = "lumacore"
    display_name = "LumaCore"
    description = "LumaCore DLL injector for Steam - reads Lua from stplug-in"

    def __init__(self, steam_path: Path | None):
        super().__init__(steam_path)
        self._engine_dir = ENGINES_DIR / self.name
        self._version = self._detect_version()

    def _detect_version(self) -> str:
        dll_path = self._engine_dir / LUMACORE_DLL
        if dll_path.exists():
            try:
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
        return [LUMACORE_DLL, LUMACORE_DWMAPI]

    def install(self) -> bool:
        if not self.steam_path:
            return False
        if not self._engine_dir.exists():
            return False
        dlls = self.get_dlls_to_copy()
        copied = []
        for dll in dlls:
            src = self._engine_dir / dll
            dst = self.steam_path / dll
            if src.exists():
                shutil.copy2(str(src), str(dst))
                copied.append(dll)
        lua_dir = self.steam_path / LUA_DIR_LUMACORE
        if not lua_dir.exists():
            lua_dir.mkdir(parents=True, exist_ok=True)
        return len(copied) >= 2

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
            return self.steam_path / LUA_DIR_LUMACORE
        return None
