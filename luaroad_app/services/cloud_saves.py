import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class SaveBackup:
    app_id: str
    game_name: str
    timestamp: float
    path: str


class CloudSaves:
    @staticmethod
    def list_steam_games(steam_path: str, steam32_id: str) -> list[tuple[int, str]]:
        results = []
        userdata = Path(steam_path) / "userdata" / str(steam32_id)
        if not userdata.exists():
            return results
        from luaroad_app.services.steam import SteamService
        ss = SteamService(steam_path)
        games = {g["appid"]: g["name"] for g in ss.get_installed_games()}
        for app_dir in userdata.iterdir():
            if not app_dir.is_dir():
                continue
            remote_dir = app_dir / "remote"
            if not remote_dir.exists():
                continue
            app_id_str = app_dir.name
            try:
                app_id = int(app_id_str)
            except ValueError:
                continue
            name = games.get(app_id, f"App {app_id}")
            results.append((app_id, name))
        results.sort(key=lambda x: x[1].lower())
        return results

    @staticmethod
    def backup_steam_save(
        steam_path: str,
        steam32_id: str,
        app_id: int,
        game_name: str,
        dest_folder: str,
        log_func=None,
    ) -> Optional[str]:
        src = Path(steam_path) / "userdata" / str(steam32_id) / str(app_id) / "remote"
        if not src.exists():
            if log_func:
                log_func(f"Source not found: {src}")
            return None
        import shutil
        import datetime
        safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in game_name).strip()
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = Path(dest_folder) / f"{safe_name} [{app_id}]" / "remote"
        dest.mkdir(parents=True, exist_ok=True)
        count = 0
        for f in src.rglob("*"):
            if f.is_file():
                rel = f.relative_to(src)
                target = dest / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, target)
                count += 1
        if log_func:
            log_func(f"Backed up {count} files to {dest}")
        return str(dest.parent)

    @staticmethod
    def restore_steam_save(
        backup_folder: str,
        steam_path: str,
        steam32_id: str,
        app_id: int,
        log_func=None,
    ) -> bool:
        src = Path(backup_folder) / "remote"
        if not src.exists():
            if log_func:
                log_func(f"Backup remote/ not found in {backup_folder}")
            return False
        dest = Path(steam_path) / "userdata" / str(steam32_id) / str(app_id) / "remote"
        import shutil
        if dest.exists():
            safety = dest.parent / "remote_backup_before_restore"
            if not safety.exists():
                shutil.copytree(dest, safety)
                if log_func:
                    log_func(f"Safety backup created at {safety}")
        dest.mkdir(parents=True, exist_ok=True)
        count = 0
        for f in src.rglob("*"):
            if f.is_file():
                rel = f.relative_to(src)
                target = dest / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, target)
                count += 1
        if log_func:
            log_func(f"Restored {count} files to {dest}")
        return True

    def get_backups(self, app_id_str: str) -> list:
        return []

    def backup(self, app_id_str: str, remote_dir: str):
        pass
