import re
import shutil
from pathlib import Path


def parse_appid(text: str) -> list[int]:
    ids = re.findall(r'\b(\d{6,10})\b', text)
    return [int(x) for x in ids]


def parse_lua_config(text: str) -> list[dict]:
    games = []
    for match in re.finditer(r'addappid\s*\(\s*(\d+)\s*(?:,\s*(\d+))?\s*(?:,\s*"([^"]*)")?\s*\)', text):
        games.append({
            "appid": int(match.group(1)),
            "depot_key": match.group(3) or "",
        })
    for match in re.finditer(r'setManifestid\s*\(\s*(\d+)\s*,\s*"(\d+)"\s*(?:,\s*(\d+))?\s*\)', text):
        existing = [g for g in games if g.get("depotid") == int(match.group(1))]
        if existing:
            existing[0]["manifest_gid"] = match.group(2)
            existing[0]["manifest_size"] = int(match.group(3)) if match.group(3) else 0
        else:
            games.append({
                "depotid": int(match.group(1)),
                "manifest_gid": match.group(2),
                "manifest_size": int(match.group(3)) if match.group(3) else 0,
            })
    return games


def generate_lua_config(games: list[dict]) -> str:
    lines = []
    for g in games:
        appid = g.get("appid") or g.get("depotid", 0)
        if g.get("depot_key"):
            lines.append(f'addappid({appid}, 0, "{g["depot_key"]}")')
        elif g.get("manifest_gid"):
            size = g.get("manifest_size", 0)
            if size:
                lines.append(f'setManifestid({appid}, "{g["manifest_gid"]}", {size})')
            else:
                lines.append(f'setManifestid({appid}, "{g["manifest_gid"]}")')
        else:
            lines.append(f"addappid({appid})")
        if g.get("token"):
            lines.append(f'addtoken({appid}, "{g["token"]}")')
    return "\n".join(lines)


def copy_dlls(src_dir: Path, dst_dir: Path, dlls: list[str]) -> list[str]:
    copied = []
    for dll in dlls:
        src = src_dir / dll
        dst = dst_dir / dll
        if src.exists():
            shutil.copy2(str(src), str(dst))
            copied.append(dll)
    return copied
