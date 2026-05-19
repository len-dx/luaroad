import io
import zipfile
import requests


RYUU_BASE = "https://generator.ryuu.lol"


def _read_lua_from_zip(data: bytes) -> str | None:
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            for info in zf.filelist:
                if info.filename.endswith(".lua"):
                    return zf.read(info).decode("utf-8", errors="replace")
    except zipfile.BadZipFile:
        pass
    return None


class RyuuService:
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "Luaroad/1.0",
        })

    def set_api_key(self, key: str):
        self.api_key = key

    def _params(self) -> dict:
        return {"auth_code": self.api_key} if self.api_key else {}

    def download_lua(self, appid: int) -> str | None:
        if not self.api_key:
            return None
        urls = [
            f"{RYUU_BASE}/secure_download?appid={appid}&auth_code={self.api_key}",
            f"{RYUU_BASE}/resellerlua?appid={appid}&auth_code={self.api_key}",
        ]
        for url in urls:
            try:
                resp = self._session.get(url, timeout=60)
                if resp.status_code == 200 and resp.content:
                    text = _read_lua_from_zip(resp.content)
                    if text:
                        return text
                    if resp.text and "addappid" in resp.text:
                        return resp.text
                elif resp.status_code == 404:
                    continue
            except Exception:
                pass
        return None

    def fetch_manifest_code(self, gid: str) -> str | None:
        try:
            url = f"{RYUU_BASE}/manifest/{gid}"
            resp = self._session.get(url, params=self._params(), timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                return str(data.get("content", data.get("code", "")))
        except Exception:
            pass
        return None

    def fetch_fixes(self) -> list[dict]:
        try:
            resp = self._session.get(
                f"{RYUU_BASE}/fixes",
                params=self._params(),
                timeout=15,
            )
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return []

    def fetch_fix_details(self, fix_id: str) -> dict | None:
        try:
            resp = self._session.get(
                f"{RYUU_BASE}/fixes/{fix_id}",
                params=self._params(),
                timeout=15,
            )
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def search(self, query: str) -> list[dict]:
        try:
            resp = self._session.get(
                f"{RYUU_BASE}/search",
                params={**self._params(), "q": query},
                timeout=15,
            )
            if resp.status_code == 200:
                return resp.json().get("results", [])
        except Exception:
            pass
        return []
