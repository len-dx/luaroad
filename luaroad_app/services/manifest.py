import requests
from luaroad_app.constants import MANIFEST_API_STEAMRUN


class ManifestService:
    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": "Luaroad/1.0"})

    def fetch_manifest_code_steamrun(self, gid: str) -> str | None:
        try:
            url = MANIFEST_API_STEAMRUN.format(gid=gid)
            resp = self._session.get(url, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                return str(data.get("content", ""))
        except Exception:
            pass
        return None

    def fetch_manifest_code(self, gid: str, api: str = "steamrun") -> str | None:
        return self.fetch_manifest_code_steamrun(gid)

    def fetch_depot_keys(self, appid: int) -> list[dict]:
        results = []
        try:
            resp = self._session.get(
                f"https://steamdb.info/api/patchnotes/?appid={appid}",
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("data", [])
        except Exception:
            pass
        return results

    def search_games(self, query: str) -> list[dict]:
        results = []
        try:
            resp = self._session.get(
                f"https://steamcommunity.com/actions/SearchApps/{query}",
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                timeout=10,
            )
            if resp.status_code == 200:
                results = [
                    {"appid": int(r["appid"]), "name": r["name"]}
                    for r in resp.json()
                ][:50]
        except Exception:
            pass
        return results

    def get_app_details(self, appid: int) -> dict | None:
        try:
            resp = self._session.get(
                f"https://store.steampowered.com/api/appdetails?appids={appid}",
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json().get(str(appid), {})
                if data.get("success"):
                    return data.get("data")
        except Exception:
            pass
        return None

    def get_app_depots(self, appid: int) -> dict | None:
        details = self.get_app_details(appid)
        if details:
            return details.get("dlc", [])
        return None
