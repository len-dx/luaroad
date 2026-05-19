import os
from pathlib import Path

from luaroad_app.plugins.api import PluginAPI


class LuaPlugin:
    def __init__(self, name: str, filepath: Path, api: PluginAPI, lua_runtime):
        self.name = name
        self.filepath = filepath
        self._api = api
        self._lua = lua_runtime
        self.enabled = True
        self._functions = {}

    def load(self) -> bool:
        try:
            if not self.filepath.exists():
                return False
            with open(self.filepath, "r", encoding="utf-8") as f:
                source = f.read()

            g = self._lua.globals()
            g.luaroad = self._api
            g.plugin_name = self.name

            exec_globs = {"__builtins__": {}}
            exec_globs["luaroad"] = self._api
            exec_globs["plugin_name"] = self.name

            self._lua.execute(source)
            return True
        except Exception as e:
            self._api.log(f"Failed to load plugin {self.name}: {e}", "error")
            return False

    def has_function(self, name: str) -> bool:
        return name in self._lua.globals()

    def call(self, name: str, *args):
        try:
            fn = self._lua.globals()[name]
            if fn:
                return fn(*args)
        except Exception as e:
            self._api.log(f"Plugin {self.name} error in {name}: {e}", "error")
        return None


class LuaPluginEngine:
    def __init__(self, api: PluginAPI):
        self._api = api
        self._plugins: dict[str, LuaPlugin] = {}
        self._lua = None
        self._init_lua()

    def _init_lua(self):
        try:
            from lupa import LuaRuntime
            self._lua = LuaRuntime(unpack_returned_tuples=True)

            lua_globals = self._lua.globals()
            lua_globals.print = lambda msg: self._api.log(str(msg), "plugin")

            def lua_http_get(url, headers=None):
                body, code = self._api.http_get(url, headers or {})
                return body, code

            def lua_http_post(url, body, headers=None):
                resp_body, code = self._api.http_post(url, body, headers or {})
                return resp_body, code

            lua_globals.http_get = lua_http_get
            lua_globals.http_post = lua_http_post
            lua_globals.log = lambda msg: self._api.log(str(msg), "plugin")
        except ImportError:
            self._api.log("lupa not installed - Lua plugins disabled", "warning")

    def load_plugin(self, filepath: Path) -> LuaPlugin | None:
        if self._lua is None:
            return None
        name = filepath.stem
        plugin = LuaPlugin(name, filepath, self._api, self._lua)
        if plugin.load():
            self._plugins[name] = plugin
            return plugin
        return None

    def load_directory(self, directory: Path):
        if not directory.exists():
            return
        for f in sorted(directory.glob("*.lua")):
            self.load_plugin(f)

    def get_plugin(self, name: str) -> LuaPlugin | None:
        return self._plugins.get(name)

    def get_all_plugins(self) -> list[LuaPlugin]:
        return list(self._plugins.values())

    def unload_plugin(self, name: str):
        if name in self._plugins:
            del self._plugins[name]

    def reload_all(self):
        paths = [(p.name, p.filepath) for p in self._plugins.values()]
        self._plugins.clear()
        for name, fp in paths:
            self.load_plugin(fp)

    def call_hook(self, hook_name: str, *args):
        results = []
        for plugin in self._plugins.values():
            if plugin.enabled and plugin.has_function(hook_name):
                result = plugin.call(hook_name, *args)
                if result is not None:
                    results.append(result)
        return results
