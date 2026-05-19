import shutil
from pathlib import Path

from luaroad_app.constants import OPENSTEAMTOOL_RELEASE, ENGINES_DIR, OPENSTEAMTOOL_DLL, OPENSTEAMTOOL_DWMAPI, OPENSTEAMTOOL_XINPUT


class UpdaterService:
    def __init__(self):
        self._source_dir = OPENSTEAMTOOL_RELEASE

    def get_available_version(self) -> str:
        dll_path = self._source_dir / OPENSTEAMTOOL_DLL
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

    def get_installed_version(self) -> str:
        engine_dir = ENGINES_DIR / "opensteamtool"
        dll_path = engine_dir / OPENSTEAMTOOL_DLL
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
        return "not installed"

    def update_from_local(self) -> bool:
        engine_dir = ENGINES_DIR / "opensteamtool"
        if not engine_dir.exists():
            engine_dir.mkdir(parents=True, exist_ok=True)
        dlls = [OPENSTEAMTOOL_DLL, OPENSTEAMTOOL_DWMAPI, OPENSTEAMTOOL_XINPUT]
        success = True
        for dll in dlls:
            src = self._source_dir / dll
            dst = engine_dir / dll
            if src.exists():
                try:
                    shutil.copy2(str(src), str(dst))
                except OSError:
                    success = False
        return success

    def has_updates(self) -> bool:
        available = self.get_available_version()
        installed = self.get_installed_version()
        if available == "unknown" or installed == "not installed":
            return available != "unknown"
        try:
            avail_parts = [int(x) for x in available.split(".")]
            inst_parts = [int(x) for x in installed.split(".")]
            return avail_parts > inst_parts
        except (ValueError, IndexError):
            return available != installed

    def set_source_directory(self, path: Path):
        self._source_dir = path
