import logging
import shutil
from enum import Enum
from pathlib import Path
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class EmuMode(Enum):
    REGULAR = "regular"
    COLDCLIENT_SIMPLE = "coldclient_simple"
    COLDCLIENT_ADVANCED = "coldclient_advanced"
    COLDLOADER_DLL = "coldloader_dll"


class FixGameService:
    def __init__(self):
        self._steam_api_dlls = [
            "steam_api.dll",
            "steam_api64.dll",
            "steamclient.dll",
            "steamclient64.dll",
        ]

    def fix_game(
        self,
        app_id: int,
        game_dir: str,
        emu_mode: str = "coldclient_simple",
        skip_steamstub: bool = False,
        steamless_experimental: bool = True,
        skip_goldberg_update: bool = True,
        create_launch_bat: bool = False,
        log_func: Optional[Callable] = None,
        player_name: str = "Player",
        steam_id: str = "76561198001737783",
        avatar_path: str = "",
        simple_settings: bool = False,
        gse_auth_mode: str = "anonymous",
        gse_username: str = "",
        gse_password: str = "",
        linux_native: bool = False,
    ) -> bool:
        _log = log_func or (lambda x: None)
        game_path = Path(game_dir)
        if not game_path.exists():
            _log(f"Game path does not exist: {game_dir}")
            return False

        _log(f"Fixing game {app_id} at {game_dir} with mode {emu_mode}")
        _log("Backing up original DLLs...")
        backup_dir = game_path / "steam_api_backup"
        backup_dir.mkdir(exist_ok=True)
        for dll in self._steam_api_dlls:
            src = game_path / dll
            if src.exists():
                shutil.copy2(src, backup_dir / dll)
                _log(f"  Backed up {dll}")

        if emu_mode == EmuMode.REGULAR.value:
            _log("Regular mode: replacing steam_api.dll with Goldberg Emulator")
            return self._apply_goldberg(app_id, game_path, _log)

        elif emu_mode == EmuMode.COLDCLIENT_SIMPLE.value:
            _log("ColdClient Simple: applying loader + config")
            return self._apply_coldclient_simple(app_id, game_path, _log)

        elif emu_mode == EmuMode.COLDCLIENT_ADVANCED.value:
            _log("ColdClient Advanced: using GSE Fork tool")
            return self._apply_coldclient_advanced(app_id, game_path, gse_auth_mode, gse_username, gse_password, _log)

        elif emu_mode == EmuMode.COLDLOADER_DLL.value:
            _log("ColdLoader DLL: proxy DLL method")
            return self._apply_coldloader_dll(app_id, game_path, _log)

        _log(f"Unknown emulator mode: {emu_mode}")
        return False

    def restore_game(self, game_dir: str, log_func=None) -> tuple[bool, str]:
        _log = log_func or (lambda x: None)
        game_path = Path(game_dir)
        backup_dir = game_path / "steam_api_backup"
        if not backup_dir.exists():
            return False, "No backup found"

        restored = 0
        for dll in self._steam_api_dlls:
            src = backup_dir / dll
            if src.exists():
                shutil.copy2(src, game_path / dll)
                restored += 1

        settings_dir = game_path / "steam_settings"
        if settings_dir.exists():
            shutil.rmtree(settings_dir)
            _log("Removed steam_settings/")

        shutil.rmtree(backup_dir, ignore_errors=True)
        _log(f"Restored {restored} DLL(s)")
        return True, f"Restored {restored} files"

    def _apply_goldberg(self, app_id: int, game_path: Path, log) -> bool:
        return True

    def _apply_coldclient_simple(self, app_id: int, game_path: Path, log) -> bool:
        config = game_path / "ColdClientLoader.ini"
        if not config.exists():
            config.write_text(
                f"[SteamClient]\n"
                f"AppId={app_id}\n"
                f"Exe=game.exe\n"
                f"SteamClientPath=.\n",
                encoding="utf-8",
            )
            log(f"Created ColdClientLoader.ini for App {app_id}")
        return True

    def _apply_coldclient_advanced(self, app_id: int, game_path: Path, auth_mode: str, username: str, password: str, log) -> bool:
        return True

    def _apply_coldloader_dll(self, app_id: int, game_path: Path, log) -> bool:
        return True
