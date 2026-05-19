import tkinter as tk
from tkinter import ttk, scrolledtext
from pathlib import Path


class ManifestsTab:
    def __init__(self, parent, app_ref):
        self.app = app_ref
        self.frame = ttk.Frame(parent)
        self._build()

    def _build(self):
        header = ttk.Label(self.frame, text="Manifest Manager", font=("", 18, "bold"))
        header.pack(pady=(15, 5))

        ttk.Label(self.frame, text="Download manifest codes to pin specific game versions or unlock protected content.", wraplength=700).pack(pady=(0, 10))

        top_frame = ttk.LabelFrame(self.frame, text="Fetch Manifest Code", padding=10)
        top_frame.pack(fill="x", padx=15, pady=5)

        row1 = ttk.Frame(top_frame)
        row1.pack(fill="x")
        ttk.Label(row1, text="Manifest GID:").pack(side="left")
        self._gid_entry = ttk.Entry(row1, width=35)
        self._gid_entry.pack(side="left", padx=5)
        ttk.Label(row1, text="Source:").pack(side="left", padx=(10, 5))
        self._api_var = tk.StringVar(value="steamrun")
        self._api_combo = ttk.Combobox(row1, textvariable=self._api_var, values=["steamrun", "Ryuu"], width=10, state="readonly")
        self._api_combo.pack(side="left", padx=5)
        ttk.Button(row1, text="Fetch Code", command=self._fetch_code).pack(side="left", padx=10)

        row2 = ttk.Frame(top_frame)
        row2.pack(fill="x", pady=5)
        ttk.Label(row2, text="AppID:").pack(side="left")
        self._appid_entry = ttk.Entry(row2, width=12)
        self._appid_entry.pack(side="left", padx=5)
        ttk.Label(row2, text="DepotID:").pack(side="left", padx=(10, 5))
        self._depotid_entry = ttk.Entry(row2, width=12)
        self._depotid_entry.pack(side="left", padx=5)
        ttk.Button(row2, text="Fetch Extended", command=self._fetch_code_ex).pack(side="left", padx=5)
        ttk.Button(row2, text="Add to Games List", command=self._add_to_games).pack(side="left", padx=5)

        result_frame = ttk.LabelFrame(self.frame, text="Result", padding=5)
        result_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self._result_text = scrolledtext.ScrolledText(result_frame, height=6, wrap="word")
        self._result_text.pack(fill="both", expand=True)

        ryuu_frame = ttk.LabelFrame(self.frame, text="Ryuu Manifest Hub", padding=10)
        ryuu_frame.pack(fill="x", padx=15, pady=5)

        rf1 = ttk.Frame(ryuu_frame)
        rf1.pack(fill="x")
        ttk.Label(rf1, text="API Key:").pack(side="left")
        self._ryuu_key_entry = ttk.Entry(rf1, width=50, show="*")
        self._ryuu_key_entry.pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(rf1, text="Save Key", command=self._save_ryuu_key).pack(side="left", padx=5)
        ttk.Button(rf1, text="Show", command=self._toggle_ryuu_key_show).pack(side="left")

        rf2 = ttk.Frame(ryuu_frame)
        rf2.pack(fill="x", pady=5)
        ttk.Label(rf2, text="Search Fixes:").pack(side="left")
        self._ryuu_search_entry = ttk.Entry(rf2, width=40)
        self._ryuu_search_entry.pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(rf2, text="Search", command=self._search_ryuu_fixes).pack(side="left", padx=5)

        self._ryuu_key_shown = False
        saved_key = self.app.config.get("ryuu_api_key", "")
        if saved_key:
            self._ryuu_key_entry.insert(0, saved_key)

    def _fetch_code(self):
        gid = self._gid_entry.get().strip()
        if not gid:
            return
        api = self._api_var.get()
        self._result_text.delete("1.0", "end")
        self._result_text.insert("1.0", f"Fetching from {api}...\n")
        code = None
        if api == "Ryuu":
            code = self.app.ryuu_service.fetch_manifest_code(gid)
        else:
            from luaroad_app.services.manifest import ManifestService
            ms = ManifestService()
            code = ms.fetch_manifest_code(gid)
        if code:
            self._result_text.insert("end", f"Manifest Code: {code}\n")
        else:
            self._result_text.insert("end", "Failed to fetch manifest code.\n")

    def _fetch_code_ex(self):
        gid = self._gid_entry.get().strip()
        appid = self._appid_entry.get().strip()
        depotid = self._depotid_entry.get().strip()
        if not gid or not appid:
            return
        result = f"Extended fetch for appid={appid}, depotid={depotid or 'N/A'}, gid={gid}\n"
        self._result_text.delete("1.0", "end")
        self._result_text.insert("1.0", result)
        hook_results = self.app.plugin_engine.call_hook("fetch_manifest_code_ex", int(appid), int(depotid or appid), gid)
        if hook_results:
            self._result_text.insert("end", f"Plugin returned: {hook_results[0]}\n")
        else:
            self._result_text.insert("end", "No plugin handled this. Use a Lua plugin with fetch_manifest_code_ex.\n")

    def _add_to_games(self):
        gid = self._gid_entry.get().strip()
        appid_text = self._appid_entry.get().strip()
        depotid_text = self._depotid_entry.get().strip()
        if not gid or not appid_text:
            return
        games_tab = self.app.tabs.get("games")
        if games_tab:
            appid = int(appid_text)
            depotid = int(depotid_text) if depotid_text else appid
            existing = [g for g in games_tab._games if g.get("appid") == appid]
            if existing:
                existing[0]["manifest_gid"] = gid
                existing[0]["depotid"] = depotid
            else:
                games_tab._games.append({
                    "appid": appid, "depotid": depotid,
                    "manifest_gid": gid, "depot_key": "",
                })
            games_tab._refresh_tree()
            self.app.log(f"Added manifest {gid} to game {appid}", "info")

    def _save_ryuu_key(self):
        key = self._ryuu_key_entry.get().strip()
        if key:
            self.app.config.set("ryuu_api_key", key)
            self.app.ryuu_service.set_api_key(key)
            self.app.log("Ryuu API key saved", "info")

    def _toggle_ryuu_key_show(self):
        if self._ryuu_key_shown:
            self._ryuu_key_entry.config(show="*")
            self._ryuu_key_shown = False
        else:
            self._ryuu_key_entry.config(show="")
            self._ryuu_key_shown = True

    def _search_ryuu_fixes(self):
        query = self._ryuu_search_entry.get().strip()
        if not query:
            return
        self._result_text.delete("1.0", "end")
        self._result_text.insert("1.0", "Searching Ryuu fixes...\n")
        results = self.app.ryuu_service.search(query)
        self._result_text.delete("1.0", "end")
        if results:
            for r in results[:20]:
                self._result_text.insert("end", f"  {r.get('name', 'Unknown')} [ID: {r.get('id', '?')}]\n")
        else:
            self._result_text.insert("1.0", "No Ryuu fixes found.\n")

    def refresh(self):
        saved_key = self.app.config.get("ryuu_api_key", "")
        self._ryuu_key_entry.delete(0, "end")
        if saved_key:
            self._ryuu_key_entry.insert(0, saved_key)
