import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
from pathlib import Path


class PluginsTab:
    def __init__(self, parent, app_ref):
        self.app = app_ref
        self.frame = ttk.Frame(parent)
        self._build()

    def _build(self):
        header = ttk.Label(self.frame, text="Lua Plugins & Add-ons", font=("", 18, "bold"))
        header.pack(pady=(15, 5))

        ttk.Label(self.frame, text="Extend Luaroad with custom Lua scripts.", wraplength=600).pack(pady=(0, 10))

        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill="both", expand=True, padx=15, pady=5)

        left_frame = ttk.LabelFrame(main_frame, text="Installed Plugins", padding=5)
        left_frame.pack(side="left", fill="both", expand=True)

        cols = ("Name", "Status", "Size")
        self._tree = ttk.Treeview(left_frame, columns=cols, show="headings", height=14)
        self._tree.heading("Name", text="Name")
        self._tree.heading("Status", text="Status")
        self._tree.heading("Size", text="Size")
        self._tree.column("Name", width=180)
        self._tree.column("Status", width=80)
        self._tree.column("Size", width=70)
        self._tree.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(left_frame, orient="vertical", command=self._tree.yview)
        scroll.pack(side="right", fill="y")
        self._tree.configure(yscrollcommand=scroll.set)

        self._tree.bind("<<TreeviewSelect>>", self._on_select)

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="right", fill="y", padx=(10, 0))

        ttk.Button(right_frame, text="Load Plugin", command=self._load_plugin).pack(fill="x", pady=2)
        ttk.Button(right_frame, text="Reload All", command=self._reload_all).pack(fill="x", pady=2)
        ttk.Button(right_frame, text="Unload Plugin", command=self._unload_plugin).pack(fill="x", pady=2)
        ttk.Button(right_frame, text="Open Plugins Folder", command=self.app.open_plugins_folder).pack(fill="x", pady=2)
        ttk.Button(right_frame, text="New Plugin...", command=self._new_plugin).pack(fill="x", pady=2)
        ttk.Button(right_frame, text="Refresh", command=self._refresh_list).pack(fill="x", pady=2)

        preview_frame = ttk.LabelFrame(self.frame, text="Plugin Preview", padding=5)
        preview_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self._preview = scrolledtext.ScrolledText(preview_frame, height=8, wrap="none")
        self._preview.pack(fill="both", expand=True)

        self._refresh_list()

    def _refresh_list(self):
        for item in self._tree.get_children():
            self._tree.delete(item)
        from luaroad_app.constants import PLUGINS_DIR
        if PLUGINS_DIR.exists():
            for f in sorted(PLUGINS_DIR.glob("*.lua")):
                plugin = self.app.plugin_engine.get_plugin(f.stem)
                status = "Loaded" if plugin else "Unloaded"
                size = f.stat().st_size
                self._tree.insert("", "end", values=(f.stem, status, f"{size} B"))

    def _on_select(self, event):
        sel = self._tree.selection()
        if not sel:
            return
        name = self._tree.item(sel[0], "values")[0]
        from luaroad_app.constants import PLUGINS_DIR
        f = PLUGINS_DIR / f"{name}.lua"
        if f.exists():
            content = f.read_text(encoding="utf-8")
            self._preview.delete("1.0", "end")
            self._preview.insert("1.0", content)

    def _load_plugin(self):
        sel = self._tree.selection()
        if not sel:
            return
        name = self._tree.item(sel[0], "values")[0]
        from luaroad_app.constants import PLUGINS_DIR
        f = PLUGINS_DIR / f"{name}.lua"
        if f.exists():
            plugin = self.app.plugin_engine.load_plugin(f)
            if plugin:
                self.app.log(f"Loaded plugin: {name}", "info")
                self._refresh_list()

    def _reload_all(self):
        self.app.plugin_engine.reload_all()
        self._refresh_list()
        self.app.log("All plugins reloaded", "info")

    def _unload_plugin(self):
        sel = self._tree.selection()
        if not sel:
            return
        name = self._tree.item(sel[0], "values")[0]
        self.app.plugin_engine.unload_plugin(name)
        self._refresh_list()
        self.app.log(f"Unloaded plugin: {name}", "info")

    def _new_plugin(self):
        from luaroad_app.ui.dialogs import InputDialog
        dialog = InputDialog(self.frame.winfo_toplevel(), "New Plugin", "Plugin name:")
        name = dialog.result
        if not name:
            return
        from luaroad_app.constants import PLUGINS_DIR
        PLUGINS_DIR.mkdir(parents=True, exist_ok=True)
        f = PLUGINS_DIR / f"{name}.lua"
        if f.exists():
            self.app.log(f"Plugin {name}.lua already exists", "warning")
            return
        template = f"""-- {name}.lua
-- Luaroad Plugin

function on_load()
    luaroad:log("{name} loaded!")
end

function on_unload()
    luaroad:log("{name} unloaded!")
end

-- Hook into events:
-- function on_game_added(appid, depot_key)
--     luaroad:log("Game added: " .. appid)
-- end

-- function fetch_manifest_code_ex(app_id, depot_id, gid)
--     -- Custom manifest code fetching
--     return nil
-- end
"""
        f.write_text(template, encoding="utf-8")
        self._refresh_list()
        self.app.log(f"Created plugin: {name}.lua", "info")
