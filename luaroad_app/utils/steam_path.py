import subprocess
from pathlib import Path

from luaroad_app.constants import STEAM_PATHS_WIN, REGISTRY_STEAM_PATH, REGISTRY_STEAM_PATH_32


def find_steam_path_registry() -> Path | None:
    try:
        import winreg
        for reg_path in [REGISTRY_STEAM_PATH, REGISTRY_STEAM_PATH_32]:
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                    value, _ = winreg.QueryValueEx(key, "SteamPath")
                    p = Path(value)
                    if validate_steam_path(p):
                        return p
            except (OSError, FileNotFoundError):
                pass
    except ImportError:
        pass
    return None


def validate_steam_path(path: Path) -> bool:
    if not path.exists():
        return False
    steam_exe = path / "steam.exe"
    steamapps = path / "steamapps"
    return steam_exe.exists() and steamapps.exists()


def find_steam_path() -> Path | None:
    p = find_steam_path_registry()
    if p:
        return p
    for sp in STEAM_PATHS_WIN:
        if validate_steam_path(sp):
            return sp
    return None


def is_steam_running() -> bool:
    try:
        output = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq steam.exe"],
            capture_output=True, text=True, timeout=5
        )
        return "steam.exe" in output.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False
