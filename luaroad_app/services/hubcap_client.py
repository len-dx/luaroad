import httpx
from dataclasses import dataclass, field
from typing import Optional


BASE_URL = "https://hubcapmanifest.com/api/v1"


@dataclass
class GameInfo:
    app_id: int
    name: str
    last_updated: str = ""
    status: str = ""


@dataclass
class LibraryPage:
    games: list = field(default_factory=list)
    total: int = 0
    offset: int = 0
    limit: int = 100

    @property
    def total_pages(self):
        if self.limit <= 0:
            return 1
        return max(1, (self.total + self.limit - 1) // self.limit)


class HubcapClient:
    def __init__(self, api_key: str = "", timeout: float = 30.0):
        self.api_key = api_key
        self.timeout = timeout
        self._client: Optional[httpx.Client] = None

    def _get_client(self):
        if self._client is None or self._client.is_closed:
            self._client = httpx.Client(
                base_url=BASE_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "User-Agent": "Luaroad/1.0",
                },
                timeout=self.timeout,
            )
        return self._client

    def close(self):
        if self._client and not self._client.is_closed:
            self._client.close()

    @staticmethod
    def validate_api_key(key: str) -> bool:
        return bool(key and key.strip().startswith("smm") and len(key.strip()) > 10)

    def get_library(self, limit: int = 100, offset: int = 0, search: str = "") -> Optional[LibraryPage]:
        try:
            params = {"limit": limit, "offset": offset}
            if search:
                params["search"] = search
            resp = self._get_client().get("/library", params=params)
            if resp.status_code == 200:
                data = resp.json()
                games = [GameInfo(**g) for g in data.get("games", [])]
                return LibraryPage(
                    games=games,
                    total=data.get("total", 0),
                    offset=data.get("offset", 0),
                    limit=data.get("limit", limit),
                )
        except Exception:
            pass
        return None

    def get_game_depots(self, app_id: str) -> list:
        try:
            resp = self._get_client().get(f"/games/{app_id}/depots")
            if resp.status_code == 200:
                return resp.json().get("depots", [])
        except Exception:
            pass
        return []

    def get_game_status(self, app_id: str) -> Optional[dict]:
        try:
            resp = self._get_client().get(f"/games/{app_id}/status")
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None
