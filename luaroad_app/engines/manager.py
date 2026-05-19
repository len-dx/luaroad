from pathlib import Path

from luaroad_app.config import Config
from luaroad_app.constants import SUPPORTED_ENGINES, ENGINE_OPENSTEAMTOOL, ENGINE_LUMACORE
from luaroad_app.engines.base import EngineBase
from luaroad_app.engines.opensteamtool import OpenSteamToolEngine
from luaroad_app.engines.lumacore import LumaCoreEngine


class EngineManager:
    def __init__(self, config: Config):
        self.config = config
        self._engines: dict[str, EngineBase] = {
            ENGINE_OPENSTEAMTOOL: OpenSteamToolEngine,
            ENGINE_LUMACORE: LumaCoreEngine,
        }

    def get_engine(self, name: str | None = None) -> EngineBase:
        name = name or self.config.get_engine()
        steam_path = self.config.get_steam_path()
        cls = self._engines.get(name)
        if not cls:
            cls = self._engines[ENGINE_OPENSTEAMTOOL]
        return cls(steam_path)

    def get_current_engine(self) -> EngineBase:
        return self.get_engine()

    def switch_engine(self, name: str) -> bool:
        if name not in self._engines:
            return False
        self.config.set("engine", name)
        return True

    def list_engines(self) -> list[dict]:
        return [
            {
                "id": eid,
                "name": cls.display_name,
                "description": cls.description,
            }
            for eid, cls in self._engines.items()
        ]
