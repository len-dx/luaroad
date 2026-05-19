import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ManifestEntry:
    depot_id: str
    manifest_id: str
    date: str = ""
    branch: str = "public"
    source: str = ""


@dataclass
class VersionGroup:
    label: str
    date: str
    branch: str
    source: str
    entries: list[tuple[str, str]] = field(default_factory=list)
    entry_map: dict[str, ManifestEntry] = field(default_factory=dict)


def group_by_version(depot_history: dict[str, list[ManifestEntry]]) -> list[VersionGroup]:
    from collections import defaultdict
    groups: list[VersionGroup] = []
    seen = set()
    for depot_id, entries in depot_history.items():
        for entry in entries:
            key = (entry.date, entry.branch, entry.source)
            if key not in seen:
                seen.add(key)
                groups.append(VersionGroup(
                    label=f"{entry.source} — {entry.date} ({entry.branch})",
                    date=entry.date,
                    branch=entry.branch,
                    source=entry.source,
                ))
            for g in groups:
                if g.date == entry.date and g.branch == entry.branch and g.source == entry.source:
                    g.entries.append((depot_id, entry.manifest_id))
                    g.entry_map[depot_id] = entry
                    break
    groups.sort(key=lambda g: g.date, reverse=True)
    return groups


def has_depot_key(depot_id: str) -> bool:
    return False


def get_depots_for_app(app_id: str, progress_cb=None, force_refresh=False) -> dict[str, list[ManifestEntry]]:
    result: dict[str, list[ManifestEntry]] = {}
    try:
        import requests
        resp = requests.get(
            f"https://raw.githubusercontent.com/oureveryday/Steam-auto-crack/main/lua/{app_id}.lua",
            timeout=10,
        )
        if resp.status_code == 200:
            content = resp.text
            for m in re.finditer(r'addappid\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*"([^"]*)"\s*\)', content):
                depot_id = m.group(2)
                result[depot_id] = [
                    ManifestEntry(
                        depot_id=depot_id,
                        manifest_id="",
                        date="from Lua",
                        source="GitHub mirror",
                    )
                ]
        if progress_cb:
            progress_cb(f"Processed {app_id}")
    except Exception as e:
        logger.debug(f"get_depots_for_app: {e}")
    return result
