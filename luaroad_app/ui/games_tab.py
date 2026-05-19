import tkinter as tk
from tkinter import ttk, scrolledtext
from pathlib import Path
import webbrowser
import threading


_GAME_NAME_CACHE = {}


class GamesTab:
    def __init__(self, parent, app_ref):
        self.app = app_ref
        self.frame = ttk.Frame(parent)
        self._games = []
        self._all_apps = []
        self._search_after_id = None
        default_source = app_ref.config.get("default_lua_source", "auto")
        self._source_var = tk.StringVar(value=default_source)
        self._build()
        self.frame.after(100, self._load_games)

    def _build(self):
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(2, weight=1)

        ttk.Label(self.frame, text="Game Manager", font=("", 20, "bold")).grid(row=0, column=0, pady=(12, 0))
        ttk.Label(self.frame, text="Search games, add to config, download Lua + write to Steam.", font=("", 10)).grid(row=1, column=0, pady=(0, 6))

        main = ttk.Frame(self.frame)
        main.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 4))
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(0, weight=1)

        left = ttk.Frame(main)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)

        right = ttk.Frame(main)
        right.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        right.columnconfigure(0, weight=1)

        self._build_search(left)
        self._build_list(left)
        self._build_actions(right)
        self._build_quick_add(right)
        self._build_editor()

        status_frame = ttk.Frame(self.frame)
        status_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=2)
        status_frame.columnconfigure(0, weight=1)
        self._status = ttk.Label(status_frame, text="Ready", font=("", 9))
        self._status.grid(row=0, column=0, sticky="w")

    def _build_search(self, parent):
        search_frame = ttk.LabelFrame(parent, text="Search & Add Games", padding=6)
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        search_frame.columnconfigure(1, weight=1)

        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, sticky="w")
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", self._on_search_typed)
        self._search_entry = ttk.Entry(search_frame, textvariable=self._search_var)
        self._search_entry.grid(row=0, column=1, sticky="ew", padx=4)
        self._search_entry.bind("<Return>", lambda e: self._do_search())
        ttk.Button(search_frame, text="Search", command=self._do_search).grid(row=0, column=2, padx=2)
        ttk.Button(search_frame, text="Clear", command=self._clear_search).grid(row=0, column=3, padx=2)

        cols = ("AppID", "Name")
        self._search_tree = ttk.Treeview(search_frame, columns=cols, show="headings", height=5)
        self._search_tree.heading("AppID", text="AppID")
        self._search_tree.heading("Name", text="Game Name")
        self._search_tree.column("AppID", width=70)
        self._search_tree.column("Name", width=350)
        self._search_tree.grid(row=1, column=0, columnspan=4, sticky="ew", pady=4)
        self._search_tree.bind("<Double-1>", lambda e: self._add_selected_game())

        btn_row = ttk.Frame(search_frame)
        btn_row.grid(row=2, column=0, columnspan=4, sticky="ew")
        ttk.Button(btn_row, text="Add Selected to Config", command=self._add_selected_game).pack(side="left", padx=1)
        ttk.Button(btn_row, text="Open on SteamDB", command=self._open_steamdb).pack(side="left", padx=1)
        ttk.Button(btn_row, text="Scan My Library", command=self._scan_library).pack(side="left", padx=1)
        ttk.Label(btn_row, text="Double-click to add").pack(side="right")

    def _build_list(self, parent):
        list_frame = ttk.LabelFrame(parent, text="Configured Games", padding=4)
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        cols = ("AppID", "Name", "Depot Key", "Token", "Manifest GID")
        self._tree = ttk.Treeview(list_frame, columns=cols, show="headings")
        self._tree.heading("AppID", text="AppID")
        self._tree.heading("Name", text="Name")
        self._tree.heading("Depot Key", text="Depot Key")
        self._tree.heading("Token", text="Token")
        self._tree.heading("Manifest GID", text="Manifest GID")
        self._tree.column("AppID", width=60)
        self._tree.column("Name", width=140)
        self._tree.column("Depot Key", width=80)
        self._tree.column("Token", width=80)
        self._tree.column("Manifest GID", width=100)
        self._tree.grid(row=0, column=0, sticky="nsew")

        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self._tree.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self._tree.configure(yscrollcommand=scroll.set)

        btn_row = ttk.Frame(list_frame)
        btn_row.grid(row=1, column=0, columnspan=2, sticky="ew", pady=3)
        ttk.Button(btn_row, text="Remove Selected", command=self._remove_game).pack(side="left", padx=1)
        ttk.Button(btn_row, text="Clear All", command=self._clear_games).pack(side="left", padx=1)

    def _build_actions(self, parent):
        actions_frame = ttk.LabelFrame(parent, text="Actions", padding=8)
        actions_frame.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        actions_frame.columnconfigure(0, weight=1)

        source_row = ttk.Frame(actions_frame)
        source_row.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        ttk.Label(source_row, text="Lua source:").pack(side="left")
        source_combo = ttk.Combobox(
            source_row, textvariable=self._source_var,
            values=["auto", "revobd", "ryuu", "oureveryday", "hubcap"],
            width=12, state="readonly",
        )
        source_combo.pack(side="left", padx=4)

        self._dl_lua_btn = ttk.Button(
            actions_frame, text="Download Lua + Write to Steam",
            command=self._download_lua_write,
        )
        self._dl_lua_btn.grid(row=1, column=0, sticky="ew", pady=2, ipady=4)

        self._dl_manifest_btn = ttk.Button(
            actions_frame, text="Download Manifests",
            command=self._download_manifests,
        )
        self._dl_manifest_btn.grid(row=2, column=0, sticky="ew", pady=2, ipady=4)

        self._install_btn = ttk.Button(
            actions_frame, text="Open steam://install/",
            command=self._open_steam_install,
        )
        self._install_btn.grid(row=3, column=0, sticky="ew", pady=2, ipady=4)

    def _build_quick_add(self, parent):
        details_frame = ttk.LabelFrame(parent, text="Quick Add", padding=6)
        details_frame.grid(row=1, column=0, sticky="ew", pady=(0, 4))
        details_frame.columnconfigure(1, weight=1)

        ttk.Label(details_frame, text="AppID:").grid(row=0, column=0, sticky="w")
        self._appid_entry = ttk.Entry(details_frame)
        self._appid_entry.grid(row=0, column=1, sticky="ew", padx=4, pady=1)

        ttk.Label(details_frame, text="Depot Key:").grid(row=1, column=0, sticky="w")
        self._key_entry = ttk.Entry(details_frame)
        self._key_entry.grid(row=1, column=1, sticky="ew", padx=4, pady=1)

        ttk.Label(details_frame, text="Token:").grid(row=2, column=0, sticky="w")
        self._token_entry = ttk.Entry(details_frame)
        self._token_entry.grid(row=2, column=1, sticky="ew", padx=4, pady=1)

        ttk.Label(details_frame, text="Manifest GID:").grid(row=3, column=0, sticky="w")
        self._manifest_entry = ttk.Entry(details_frame)
        self._manifest_entry.grid(row=3, column=1, sticky="ew", padx=4, pady=1)

        ttk.Button(details_frame, text="Add Game", command=self._add_game_manual).grid(row=4, column=0, columnspan=2, sticky="ew", pady=4)

    def _build_editor(self):
        editor_frame = ttk.LabelFrame(self.frame, text="Lua Config Preview", padding=4)
        editor_frame.grid(row=4, column=0, sticky="ew", padx=8, pady=(0, 3))
        editor_frame.columnconfigure(0, weight=1)

        editor_top = ttk.Frame(editor_frame)
        editor_top.grid(row=0, column=0, sticky="ew")
        ttk.Button(editor_top, text="Generate from List", command=self._generate_config).pack(side="left", padx=1)
        ttk.Button(editor_top, text="Save to Steam", command=self._save_config).pack(side="left", padx=1)
        ttk.Button(editor_top, text="Load from Steam", command=self._load_config).pack(side="left", padx=1)
        ttk.Button(editor_top, text="Preview Selected Lua", command=self._preview_selected_lua).pack(side="left", padx=1)

        self._editor = scrolledtext.ScrolledText(editor_frame, height=4, wrap="none", font=("Consolas", 9))
        self._editor.grid(row=1, column=0, sticky="ew", pady=2)

    def _on_search_typed(self, *args):
        if self._search_after_id:
            self.frame.after_cancel(self._search_after_id)
        self._search_after_id = self.frame.after(400, self._do_search)

    def _do_search(self):
        query = self._search_var.get().strip()
        if len(query) < 2:
            return
        self._set_status(f"Searching '{query}'...")
        self._search_tree.delete(*self._search_tree.get_children())
        self._search_tree.insert("", "end", values=("…", "Loading…"))
        threading.Thread(target=self._search_thread, args=(query,), daemon=True).start()

    def _search_thread(self, query):
        try:
            from luaroad_app.services.manifest import ManifestService
            ms = ManifestService()
            results = ms.search_games(query)
            self.frame.after(0, self._display_results, results)
        except Exception as e:
            self.frame.after(0, self._display_error, str(e))

    def _display_results(self, results):
        self._search_tree.delete(*self._search_tree.get_children())
        if not results:
            self._search_tree.insert("", "end", values=("", "No results found."))
            self._set_status("No results")
            return
        for r in results:
            self._search_tree.insert("", "end", values=(r["appid"], r["name"]))
        self._set_status(f"Found {len(results)} games")

    def _display_error(self, msg):
        self._search_tree.delete(*self._search_tree.get_children())
        self._search_tree.insert("", "end", values=("", f"Error: {msg[:60]}"))
        self._set_status("Search failed")

    def _clear_search(self):
        self._search_var.set("")
        self._search_tree.delete(*self._search_tree.get_children())
        self._set_status("Ready")

    def _add_selected_game(self):
        sel = self._search_tree.selection()
        if not sel:
            return
        values = self._search_tree.item(sel[0], "values")
        if not values[0]:
            return
        try:
            appid = int(values[0])
        except ValueError:
            return
        name = values[1]
        if appid not in [g.get("appid") for g in self._games]:
            self._games.append({"appid": appid, "name": name, "depot_key": "", "token": "", "manifest_gid": ""})
            _GAME_NAME_CACHE[appid] = name
            self._refresh_tree(select_appid=appid)
            self.app.log(f"Added {name} ({appid})", "info")
            self._set_status(f"Added {name}")

    def _add_game_manual(self):
        text = self._appid_entry.get().strip()
        if not text.isdigit():
            return
        appid = int(text)
        if appid in [g.get("appid") for g in self._games]:
            self._set_status(f"App {appid} already in config")
            return
        self._games.append({
            "appid": appid,
            "name": _GAME_NAME_CACHE.get(appid, str(appid)),
            "depot_key": self._key_entry.get().strip(),
            "token": self._token_entry.get().strip(),
            "manifest_gid": self._manifest_entry.get().strip(),
        })
        self._refresh_tree(select_appid=appid)
        self._appid_entry.delete(0, "end")
        self._key_entry.delete(0, "end")
        self._token_entry.delete(0, "end")
        self._manifest_entry.delete(0, "end")
        self.app.log(f"Added app {appid}", "info")
        self._set_status(f"Added app {appid}")

    def _remove_game(self):
        sel = self._tree.selection()
        if not sel:
            return
        for item in sel:
            idx = self._tree.index(item)
            if idx < len(self._games):
                self._games.pop(idx)
        self._refresh_tree()

    def _clear_games(self):
        self._games.clear()
        self._refresh_tree()
        self._set_status("Cleared all")

    def _load_games(self):
        saved = self.app.config.get("configured_games", [])
        if saved:
            self._games.clear()
            for g in saved:
                self._games.append(dict(g))
                aid = g.get("appid")
                if aid and g.get("name"):
                    _GAME_NAME_CACHE[aid] = g["name"]
            self._refresh_tree()
            self._set_status(f"Loaded {len(self._games)} game(s)")

    def _save_games(self):
        self.app.config.set("configured_games", self._games)

    def _refresh_tree(self, select_appid=None):
        self._tree.delete(*self._tree.get_children())
        target = None
        for g in self._games:
            name = g.get("name", "")
            if not name or name == str(g.get("appid", "")):
                name = _GAME_NAME_CACHE.get(g.get("appid"), str(g.get("appid", "")))
            key = g.get("depot_key", "")
            if len(key) > 18:
                key = key[:18] + "…"
            token = g.get("token", "")
            if len(token) > 18:
                token = token[:18] + "…"
            item_id = self._tree.insert("", "end", values=(
                g.get("appid", ""), name, key, token, g.get("manifest_gid", ""),
            ))
            if select_appid is not None and g.get("appid") == select_appid:
                target = item_id
        if target:
            self._tree.selection_set(target)
            self._tree.focus(target)
            self._tree.see(target)
        self._save_games()

    def _get_selected_game(self) -> dict | None:
        sel = self._tree.selection()
        if not sel:
            return None
        idx = self._tree.index(sel[0])
        if idx >= len(self._games):
            return None
        return self._games[idx]

    def _download_lua_write(self):
        g = self._get_selected_game()
        if not g:
            self._set_status("Select a game from Configured Games first")
            return
        source = self._source_var.get()
        appid = g["appid"]
        self._set_status(f"Downloading Lua for {appid} from {source}...")
        self._dl_lua_btn.config(state="disabled")
        threading.Thread(target=self._dl_write_thread, args=(appid, source), daemon=True).start()

    def _dl_write_thread(self, appid: int, source: str):
        from luaroad_app.services.lua_downloader import LuaDownloaderService, LuaDownloadResult
        lds = LuaDownloaderService(self.app.ryuu_service)
        hubcap_key = self.app.config.get("hubcap_api_key", "")
        result = lds.download(appid, source, hubcap_key=hubcap_key)
        if not result:
            sources = {"auto": "revobd → ryuu → hubcap → oureveryday", "revobd": "revobd.club", "ryuu": "Ryuu", "oureveryday": "Steam DB + keys", "hubcap": "Hubcap Manifest"}.get(source, source)
            return self.frame.after(0, lambda: [
                self._set_status(f"No Lua found for {appid} (tried: {sources})"),
                self._dl_lua_btn.config(state="normal"),
            ])

        primary = result.get_primary_depot()
        manifest_gid = result.get_manifest_gid()

        idx = None
        for i, g in enumerate(self._games):
            if g["appid"] == appid:
                idx = i
                break
        if idx is not None:
            if primary:
                self._games[idx]["depot_key"] = primary.get("depot_key", "")
            if manifest_gid:
                self._games[idx]["manifest_gid"] = manifest_gid
            if primary and primary.get("token"):
                self._games[idx]["token"] = primary["token"]
            if result.tokens and not self._games[idx].get("token"):
                self._games[idx]["token"] = result.tokens.get(appid, "")

        engine = self.app.engine_manager.get_current_engine()
        lua_dir = engine.get_lua_directory()

        logs = [f"Downloaded Lua from {result.source}"]
        if lua_dir:
            lds.write_lua_to_steam(lua_dir, appid, result.content)
            logs.append(f"Wrote {appid}.lua")
            lds.write_lua_merged(lua_dir, self._games)
            logs.append("Updated luaroad_games.lua")

        if manifest_gid:
            code = LuaDownloaderService.download_manifest_for_game(manifest_gid)
            logs.append(f"Manifest: {'OK' if code else 'FAIL'}")

        self.app.log(" | ".join(logs), "info")

        def summary():
            depot_key = primary.get("depot_key", "(none)")[:24] if primary else "(none)"
            mgid = (manifest_gid[:24] + "…") if manifest_gid and len(manifest_gid) > 24 else (manifest_gid or "(none)")
            lines = [
                f"Source: {result.source}",
                f"Depot Key: {depot_key}",
                f"Manifest GID: {mgid}",
                f"Total configured: {len(self._games)}",
            ]
            from luaroad_app.ui.dialogs import ConfirmDialog
            ConfirmDialog(self.frame.winfo_toplevel(), f"Processed {appid}", "\n".join(lines))

        def select_and_summary():
            self._refresh_tree()
            self._generate_config()
            summary()
            self._set_status(f"Done: {appid} from {result.source}")
            self._dl_lua_btn.config(state="normal")

        self.frame.after(0, select_and_summary)

    def _generate_config(self):
        lines = []
        for g in self._games:
            appid = g.get("appid", 0)
            if g.get("depot_key"):
                lines.append(f'addappid({appid}, 0, "{g["depot_key"]}")')
            elif g.get("manifest_gid"):
                lines.append(f'addappid({appid})')
                lines.append(f'setManifestid({appid}, "{g["manifest_gid"]}")')
            else:
                lines.append(f"addappid({appid})")
            if g.get("token"):
                lines.append(f'addtoken({appid}, "{g["token"]}")')
        self._editor.delete("1.0", "end")
        self._editor.insert("1.0", "\n".join(lines) + "\n")
        self._set_status("Config generated")

    def _save_config(self):
        engine = self.app.engine_manager.get_current_engine()
        lua_dir = engine.get_lua_directory()
        if not lua_dir:
            self._set_status("Set Steam path in Settings first")
            return
        lua_dir.mkdir(parents=True, exist_ok=True)
        (lua_dir / "luaroad_games.lua").write_text(self._editor.get("1.0", "end-1c"), encoding="utf-8")
        self._set_status("Saved to Steam")

    def _load_config(self):
        engine = self.app.engine_manager.get_current_engine()
        lua_dir = engine.get_lua_directory()
        if not lua_dir:
            return
        path = lua_dir / "luaroad_games.lua"
        if path.exists():
            self._editor.delete("1.0", "end")
            self._editor.insert("1.0", path.read_text(encoding="utf-8"))
            self._set_status("Loaded from Steam")

    def _preview_selected_lua(self):
        g = self._get_selected_game()
        if not g:
            return
        engine = self.app.engine_manager.get_current_engine()
        lua_dir = engine.get_lua_directory()
        if not lua_dir:
            return
        path = lua_dir / f"{g['appid']}.lua"
        if path.exists():
            self._editor.delete("1.0", "end")
            self._editor.insert("1.0", path.read_text(encoding="utf-8"))
            self._set_status(f"Loaded {path.name}")
        else:
            self._set_status(f"No Lua file at {path}")

    def _download_manifests(self):
        g = self._get_selected_game()
        if not g:
            self._set_status("Select a game first")
            return
        manifest_gid = g.get("manifest_gid", "")
        if not manifest_gid:
            self._set_status(f"No manifest GID for {g['appid']}")
            return
        self._set_status("Downloading manifest...")
        self._dl_manifest_btn.config(state="disabled")
        threading.Thread(target=self._dl_manifest_thread, args=(g["appid"], manifest_gid), daemon=True).start()

    def _dl_manifest_thread(self, appid, gid):
        from luaroad_app.services.manifest import ManifestService
        code = ManifestService().fetch_manifest_code(gid)
        self.frame.after(0, lambda: [
            self._set_status(f"Manifest for {appid}: {'OK' if code else 'FAIL'}" + (f" ({code[:60]}...)" if code else "")),
            self._dl_manifest_btn.config(state="normal"),
        ])

    def _open_steam_install(self):
        g = self._get_selected_game()
        if not g:
            self._set_status("Select a game first")
            return
        url = f"steam://install/{g['appid']}"
        try:
            webbrowser.open(url)
            self._set_status(f"steam://install/{g['appid']} opened")
        except Exception as e:
            self._set_status(f"Failed: {e}")

    def _open_steamdb(self):
        sel = self._search_tree.selection()
        if not sel:
            return
        v = self._search_tree.item(sel[0], "values")
        if v[0]:
            webbrowser.open(f"https://steamdb.info/app/{v[0]}/")

    def _scan_library(self):
        sp = self.app.config.get_steam_path()
        if not sp:
            self._set_status("Set Steam path in Settings")
            return
        self._set_status("Scanning library...")
        threading.Thread(target=self._scan_thread, args=(sp,), daemon=True).start()

    def _scan_thread(self, sp):
        from luaroad_app.services.steam import SteamService
        games = SteamService(sp).get_installed_games()
        added = 0
        for g in games:
            if g["appid"] not in [x.get("appid") for x in self._games]:
                self._games.append({"appid": g["appid"], "name": g["name"], "depot_key": "", "token": "", "manifest_gid": ""})
                _GAME_NAME_CACHE[g["appid"]] = g["name"]
                added += 1
        self.frame.after(0, lambda: [
            self._refresh_tree(),
            self._set_status(f"Added {added} game(s) from library"),
        ])

    def _set_status(self, text):
        self._status.config(text=text)
