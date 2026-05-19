import os
from pathlib import Path

import vdf


class SteamService:
    def __init__(self, steam_path: Path | None):
        self.steam_path = steam_path

    def get_library_folders(self) -> list[Path]:
        if not self.steam_path:
            return []
        folders = [self.steam_path / "steamapps"]
        vdf_path = self.steam_path / "steamapps" / "libraryfolders.vdf"
        if vdf_path.exists():
            try:
                data = vdf.load(open(vdf_path, encoding="utf-8"))
                lib = data.get("libraryfolders", {})
                for key in lib:
                    if isinstance(lib[key], dict) and "path" in lib[key]:
                        p = Path(lib[key]["path"]) / "steamapps"
                        if p.exists() and p not in folders:
                            folders.append(p)
            except Exception:
                pass
        return folders

    def get_installed_games(self) -> list[dict]:
        games = []
        for folder in self.get_library_folders():
            for acf in folder.glob("*.acf"):
                try:
                    data = vdf.load(open(acf, encoding="utf-8"))
                    app_state = data.get("AppState", {})
                    appid = app_state.get("appid")
                    name = app_state.get("name", "Unknown")
                    if appid:
                        games.append({
                            "appid": int(appid),
                            "name": name,
                            "installdir": app_state.get("installdir", ""),
                            "size": app_state.get("SizeOnDisk", 0),
                        })
                except Exception:
                    pass
        return games

    def read_config_vdf(self) -> dict | None:
        if not self.steam_path:
            return None
        config_path = self.steam_path / "config" / "config.vdf"
        if config_path.exists():
            try:
                return vdf.load(open(config_path, encoding="utf-8"))
            except Exception:
                pass
        return None

    def get_lua_files(self, lua_dir: Path) -> list[dict]:
        if not lua_dir.exists():
            return []
        files = []
        for f in sorted(lua_dir.glob("*.lua")):
            files.append({
                "name": f.name,
                "path": str(f),
                "size": f.stat().st_size,
                "modified": f.stat().st_mtime,
            })
        return files

    def read_lua_file(self, path: Path) -> str:
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def write_lua_file(self, path: Path, content: str):
        path.write_text(content, encoding="utf-8")

    def delete_lua_file(self, path: Path):
        if path.exists():
            path.unlink()
