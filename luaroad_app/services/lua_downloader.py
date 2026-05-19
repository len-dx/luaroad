import io
import json
import re
import zipfile
import requests
from pathlib import Path

FALLBACK_DB = Path(__file__).parent / "fallback_depotkeys.json"
REVO_PATTERN = re.compile(
    r'addappid\(\s*(\d+)\s*,\s*[01]\s*,\s*["\']([0-9a-fA-F]{64})["\']\s*\)'
)


def _read_lua_from_zip(data: bytes) -> str | None:
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            for info in zf.filelist:
                if info.filename.endswith(".lua"):
                    return zf.read(info).decode("utf-8", errors="replace")
    except zipfile.BadZipFile:
        pass
    return None


def _load_fallback_keys() -> dict:
    if FALLBACK_DB.exists():
        try:
            return json.loads(FALLBACK_DB.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


class LuaDownloadResult:
    def __init__(self, appid: int, content: str, source: str):
        self.appid = appid
        self.content = content
        self.source = source
        self.depots: list[dict] = []
        self.manifest_overrides: dict[str, str] = {}
        self.tokens: dict[int, str] = {}
        self._parse()

    def _strip_comments(self, line: str) -> str:
        idx = line.find("--")
        return line[:idx] if idx >= 0 else line

    def _parse(self):
        for line in self.content.splitlines():
            stripped = self._strip_comments(line).strip()
            if not stripped:
                continue

            m = re.match(r'addappid\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*"([^"]*)"\s*\)', stripped)
            if m:
                self.depots.append({
                    "appid": int(m.group(1)),
                    "depotid": int(m.group(2)),
                    "depot_key": m.group(3),
                })
                continue

            m = re.match(r'addappid\s*\(\s*(\d+)\s*,\s*"([^"]*)"\s*\)', stripped)
            if m:
                self.depots.append({
                    "appid": int(m.group(1)),
                    "depotid": int(m.group(1)),
                    "depot_key": m.group(2),
                })
                continue

            m = re.match(r'addappid\s*\(\s*(\d+)\s*\)', stripped)
            if m:
                self.depots.append({
                    "appid": int(m.group(1)),
                    "depotid": int(m.group(1)),
                    "depot_key": "",
                })
                continue

            m = re.match(r'setManifestid\s*\(\s*(\d+)\s*,\s*"(\d+)"\s*\)', stripped)
            if m:
                self.manifest_overrides[m.group(1)] = m.group(2)
                continue

            m = re.match(r'addtoken\s*\(\s*(\d+)\s*,\s*"([^"]*)"\s*\)', stripped)
            if m:
                aid = int(m.group(1))
                self.tokens[aid] = m.group(2)
                existing = [d for d in self.depots if d["appid"] == aid]
                if existing:
                    existing[0]["token"] = m.group(2)

    def get_primary_depot(self) -> dict | None:
        if not self.depots:
            return None
        for d in self.depots:
            if d["appid"] == self.appid:
                return d
        return self.depots[0]

    def get_manifest_gid(self) -> str:
        return self.manifest_overrides.get(str(self.appid), "")


class LuaDownloaderService:
    def __init__(self, ryuu_service=None):
        self._ryuu = ryuu_service
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": "Luaroad/1.0"})

    # ── revobd.club (free, no auth, ZIP with .lua inside) ──────────────

    def download_from_revobd(self, appid: int) -> LuaDownloadResult | None:
        url = f"https://api.luagen.revobd.club/{appid}.zip"
        try:
            resp = self._session.get(url, timeout=20)
            if resp.status_code == 200 and resp.content:
                lua_text = _read_lua_from_zip(resp.content)
                if lua_text:
                    return LuaDownloadResult(appid, lua_text, "revobd")
        except Exception:
            pass
        return None

    # ── Ryuu (needs API key) ───────────────────────────────────────────

    def download_from_ryuu(self, appid: int) -> LuaDownloadResult | None:
        if not self._ryuu or not self._ryuu.api_key:
            return None
        try:
            lua_content = self._ryuu.download_lua(appid)
            if lua_content:
                return LuaDownloadResult(appid, lua_content, "Ryuu")
        except Exception:
            pass
        return None

    # ── Hubcap (needs API key) ─────────────────────────────────────────

    def download_from_hubcap(self, appid: int, api_key: str = "") -> LuaDownloadResult | None:
        if not api_key:
            return None
        url = f"https://hubcapmanifest.com/api/v1/manifest/{appid}"
        headers = {"Authorization": f"Bearer {api_key}"}
        try:
            resp = self._session.get(url, headers=headers, timeout=20)
            if resp.status_code == 200 and resp.content:
                lua_text = _read_lua_from_zip(resp.content)
                if lua_text:
                    return LuaDownloadResult(appid, lua_text, "hubcap")
        except Exception:
            pass
        return None

    # ── Oureveryday (Steam query + bundled keys + revobd fallback) ─────

    def download_from_oureveryday(self, appid: int) -> LuaDownloadResult | None:
        keys_dict = _load_fallback_keys()
        if keys_dict:
            lines = [f"addappid({appid})"]
            found = 0
            depots = self._get_steam_depots(appid)
            if depots:
                for d in depots:
                    key = keys_dict.get(d, "")
                    if key:
                        lines.append(f'addappid({d}, 1, "{key}")')
                        found += 1
            if found > 0:
                lua_text = "\n".join(lines) + "\n"
                return LuaDownloadResult(appid, lua_text, "oureveryday")

        result = self.download_from_revobd(appid)
        if result:
            result.source = "oureveryday"
            return result

        return None

    @staticmethod
    def _get_steam_depots(appid: int) -> list[str]:
        try:
            resp = requests.get(
                f"https://store.steampowered.com/api/appdetails?appids={appid}",
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json()
                app_data = data.get(str(appid), {}).get("data", {})
                depots_raw = app_data.get("depots", {})
                return [d for d in depots_raw.keys() if d.isdigit()]
        except Exception:
            pass
        return []

    # ── Main entry ─────────────────────────────────────────────────────

    def download(self, appid: int, source: str = "auto", hubcap_key: str = "") -> LuaDownloadResult | None:
        if source == "ryuu":
            return self.download_from_ryuu(appid)
        if source == "oureveryday":
            return self.download_from_oureveryday(appid)
        if source == "revobd":
            return self.download_from_revobd(appid)
        if source == "hubcap":
            return self.download_from_hubcap(appid, hubcap_key)

        if source == "auto":
            result = self.download_from_revobd(appid)
            if result:
                return result
            result = self.download_from_ryuu(appid)
            if result:
                return result
            result = self.download_from_hubcap(appid, hubcap_key)
            if result:
                return result
            return self.download_from_oureveryday(appid)

        return None

    # ── Write helpers ──────────────────────────────────────────────────

    def write_lua_to_steam(self, lua_dir: Path, appid: int, content: str) -> bool:
        try:
            lua_dir.mkdir(parents=True, exist_ok=True)
            (lua_dir / f"{appid}.lua").write_text(content, encoding="utf-8")
            return True
        except Exception:
            return False

    def write_lua_merged(self, lua_dir: Path, games: list[dict]) -> str:
        lines = []
        for g in games:
            appid = g.get("appid", 0)
            if g.get("depot_key"):
                depotid = g.get("depotid", g.get("appid", 0))
                lines.append(f'addappid({appid}, {depotid}, "{g["depot_key"]}")')
            else:
                lines.append(f"addappid({appid})")
            if g.get("manifest_gid"):
                lines.append(f'setManifestid({appid}, "{g["manifest_gid"]}")')
            if g.get("token"):
                lines.append(f'addtoken({appid}, "{g["token"]}")')
        content = "\n".join(lines) + "\n"
        try:
            lua_dir.mkdir(parents=True, exist_ok=True)
            (lua_dir / "luaroad_games.lua").write_text(content, encoding="utf-8")
        except Exception:
            pass
        return content

    @staticmethod
    def download_manifest_for_game(manifest_gid: str) -> str | None:
        from luaroad_app.services.manifest import ManifestService
        ms = ManifestService()
        return ms.fetch_manifest_code(manifest_gid)
