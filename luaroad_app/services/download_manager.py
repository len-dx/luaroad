import time
import logging
from dataclasses import dataclass, field
from enum import Enum
from threading import Lock
from typing import Optional

logger = logging.getLogger(__name__)


class DownloadStatus(Enum):
    QUEUED = "queued"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class DownloadItem:
    app_id: int
    game_name: str = ""
    mode: str = "full"
    status: DownloadStatus = DownloadStatus.QUEUED
    progress: int = 0
    downloaded_bytes: int = 0
    total_bytes: int = 0
    error: str = ""
    retry_count: int = 0
    max_retries: int = 3
    completed_at: float = 0.0
    started_at: float = 0.0


@dataclass
class HistoryEntry:
    app_id: int
    game_name: str
    status: str
    timestamp: float


class DownloadHistory:
    def __init__(self, max_entries: int = 200):
        self._entries: list[HistoryEntry] = []
        self._max = max_entries

    def add(self, app_id: int, game_name: str, status: str):
        self._entries.append(HistoryEntry(app_id, game_name, status, time.time()))
        if len(self._entries) > self._max:
            self._entries.pop(0)

    def get_all(self) -> list[HistoryEntry]:
        return list(self._entries)

    def clear(self):
        self._entries.clear()

    @property
    def count(self) -> int:
        return len(self._entries)


class DownloadManager:
    def __init__(self):
        self._lock = Lock()
        self._active: Optional[DownloadItem] = None
        self._queue: list[DownloadItem] = []
        self._completed: list[DownloadItem] = []
        self._failed: list[DownloadItem] = []
        self.history = DownloadHistory()

    def add_to_queue(self, item: DownloadItem):
        with self._lock:
            self._queue.append(item)

    def start_next(self) -> Optional[DownloadItem]:
        with self._lock:
            if self._active or not self._queue:
                return None
            self._active = self._queue.pop(0)
            self._active.status = DownloadStatus.ACTIVE
            self._active.started_at = time.time()
            return self._active

    def mark_completed(self, item: DownloadItem):
        with self._lock:
            item.status = DownloadStatus.COMPLETED
            item.completed_at = time.time()
            self._completed.append(item)
            self.history.add(item.app_id, item.game_name, "completed")
            if self._active and self._active.app_id == item.app_id:
                self._active = None

    def mark_failed(self, item: DownloadItem, error: str = ""):
        with self._lock:
            item.status = DownloadStatus.FAILED
            item.error = error
            item.retry_count += 1
            self._failed.append(item)
            self.history.add(item.app_id, item.game_name, f"failed: {error[:40]}")
            if self._active and self._active.app_id == item.app_id:
                self._active = None

    def retry_download(self, app_id: int):
        with self._lock:
            found = [f for f in self._failed if f.app_id == app_id]
            if not found:
                return
            item = found[0]
            if item.retry_count < item.max_retries:
                self._failed.remove(item)
                item.status = DownloadStatus.QUEUED
                item.error = ""
                self._queue.append(item)

    def get_active(self) -> Optional[DownloadItem]:
        return self._active

    def get_queue(self) -> list[DownloadItem]:
        return list(self._queue)

    def get_completed(self) -> list[DownloadItem]:
        return list(self._completed)

    def get_failed(self) -> list[DownloadItem]:
        return list(self._failed)

    def clear_completed(self):
        with self._lock:
            self._completed.clear()

    def clear_failed(self):
        with self._lock:
            self._failed.clear()
