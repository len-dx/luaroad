from pathlib import Path

from luaroad_app.constants import PLUGINS_DIR


class PluginRegistry:
    def __init__(self):
        self._hooks: dict[str, list[callable]] = {}

    def register_hook(self, hook_name: str, callback: callable):
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []
        self._hooks[hook_name].append(callback)

    def unregister_hook(self, hook_name: str, callback: callable):
        if hook_name in self._hooks:
            self._hooks[hook_name] = [h for h in self._hooks[hook_name] if h != callback]

    def run_hook(self, hook_name: str, *args, **kwargs):
        results = []
        for cb in self._hooks.get(hook_name, []):
            try:
                r = cb(*args, **kwargs)
                if r is not None:
                    results.append(r)
            except Exception as e:
                pass
        return results

    def scan_plugins(self) -> list[dict]:
        plugins = []
        if PLUGINS_DIR.exists():
            for f in PLUGINS_DIR.glob("*.lua"):
                plugins.append({
                    "name": f.stem,
                    "path": str(f),
                    "size": f.stat().st_size,
                    "modified": f.stat().st_mtime,
                })
        return plugins
