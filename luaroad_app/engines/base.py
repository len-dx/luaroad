from abc import ABC, abstractmethod
from pathlib import Path


class EngineBase(ABC):
    name: str = ""
    display_name: str = ""
    description: str = ""

    def __init__(self, steam_path: Path | None):
        self.steam_path = steam_path

    @abstractmethod
    def install(self) -> bool:
        pass

    @abstractmethod
    def uninstall(self) -> bool:
        pass

    @abstractmethod
    def is_installed(self) -> bool:
        pass

    @abstractmethod
    def get_version(self) -> str:
        return "unknown"

    @abstractmethod
    def get_dlls_to_copy(self) -> list[str]:
        return []

    @abstractmethod
    def get_lua_directory(self) -> Path | None:
        if self.steam_path:
            return self.steam_path / "config" / "lua"
        return None

    def get_name(self) -> str:
        return self.display_name or self.name
