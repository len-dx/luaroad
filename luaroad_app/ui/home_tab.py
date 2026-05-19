import tkinter as tk
from tkinter import ttk, scrolledtext
from pathlib import Path
import threading


class HomeTab:
    def __init__(self, parent, app_ref):
        self.app = app_ref
        self.frame = ttk.Frame(parent)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self._games_list = []
        self._build()

    def _build(self):

        main_pw = ttk.PanedWindow(self.frame, orient="horizontal")
        main_pw.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        left = ttk.Frame(main_pw)
        right = ttk.Frame(main_pw)
        main_pw.add(left, weight=3)
        main_pw.add(right, weight=2)

        self._scroll_canvas = tk.Canvas(left, highlightthickness=0)
        scrollbar = ttk.Scrollbar(left, orient="vertical", command=self._scroll_canvas.yview)
        self._scroll_canvas.configure(yscrollcommand=scrollbar.set)
        scroll_inner = ttk.Frame(self._scroll_canvas)
        scroll_inner.bind("<Configure>", lambda e: self._scroll_canvas.configure(scrollregion=self._scroll_canvas.bbox("all")))
        self._scroll_canvas.create_window((0, 0), window=scroll_inner, anchor="nw")
        self._scroll_canvas.bind("<Configure>", self._on_canvas_resize)
        self._scroll_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._build_game_path(scroll_inner)
        self._build_actions(scroll_inner)
        self._build_log(scroll_inner)

        self._build_game_combo()

    def _on_canvas_resize(self, e):
        self._scroll_canvas.itemconfig(1, width=e.width)

    def _build_game_path(self, parent):
        grp = ttk.LabelFrame(parent, text="Game / Path", padding=8)
        grp.pack(fill="x", padx=4, pady=3)

        row1 = ttk.Frame(grp)
        row1.pack(fill="x")
        ttk.Label(row1, text="Path:").pack(side="left")
        self._path_var = tk.StringVar()
        self._path_entry = ttk.Entry(row1, textvariable=self._path_var)
        self._path_entry.pack(side="left", fill="x", expand=True, padx=4)
        ttk.Button(row1, text="...", width=3, command=self._browse_path).pack(side="left")

        row2 = ttk.Frame(grp)
        row2.pack(fill="x", pady=2)
        self._source_var = tk.StringVar(value="steam")
        ttk.Radiobutton(row2, text="Steam games", variable=self._source_var, value="steam", command=self._on_source_change).pack(side="left")
        ttk.Radiobutton(row2, text="Outside Steam", variable=self._source_var, value="outside", command=self._on_source_change).pack(side="left", padx=8)

        row3 = ttk.Frame(grp)
        row3.pack(fill="x")
        ttk.Label(row3, text="Game:").pack(side="left")
        self._game_combo = ttk.Combobox(row3, width=40, state="readonly")
        self._game_combo.pack(side="left", fill="x", expand=True, padx=4)
        ttk.Button(row3, text="Refresh", command=self._refresh_game_list).pack(side="left")

        row4 = ttk.Frame(grp)
        row4.pack(fill="x", pady=2)
        self._outside_name_lbl = ttk.Label(row4, text="Game name:")
        self._outside_name_lbl.pack(side="left")
        self._outside_name_var = tk.StringVar()
        self._outside_name_entry = ttk.Entry(row4, textvariable=self._outside_name_var, width=20)
        self._outside_name_entry.pack(side="left", padx=4)
        self._outside_appid_lbl = ttk.Label(row4, text="App ID:")
        self._outside_appid_lbl.pack(side="left", padx=4)
        self._outside_appid_var = tk.StringVar()
        self._outside_appid_entry = ttk.Entry(row4, textvariable=self._outside_appid_var, width=10)
        self._outside_appid_entry.pack(side="left")

        self.frame.after(10, self._on_source_change)

    def _on_source_change(self):
        is_steam = self._source_var.get() == "steam"
        self._game_combo["state"] = "readonly" if is_steam else "disabled"
        self._path_entry["state"] = "disabled" if is_steam else "normal"
        for w in (self._outside_name_lbl, self._outside_name_entry, self._outside_appid_lbl, self._outside_appid_entry):
            w.pack_forget()
        if not is_steam:
            self._outside_name_lbl.pack(side="left")
            self._outside_name_entry.pack(side="left", padx=4)
            self._outside_appid_lbl.pack(side="left", padx=4)
            self._outside_appid_entry.pack(side="left")

    def _browse_path(self):
        from tkinter import filedialog
        p = filedialog.askdirectory(title="Select game folder")
        if p:
            self._path_var.set(p)
            if self._source_var.get() == "outside" and not self._outside_name_var.get().strip():
                self._outside_name_var.set(Path(p).name)

    def _build_game_combo(self):
        from luaroad_app.services.steam import SteamService
        sp = self.app.config.get_steam_path()
        if not sp:
            return
        ss = SteamService(sp)
        games = ss.get_installed_games()
        self._games_list = games
        names = [f"{g['name']} ({g['appid']})" for g in games]
        self._game_combo["values"] = names

    def _refresh_game_list(self):
        self._build_game_combo()

    def _get_selected_acf(self):
        if self._source_var.get() == "steam":
            idx = self._game_combo.current()
            if idx < 0 or idx >= len(self._games_list):
                return None
            return self._games_list[idx]
        path = self._path_var.get().strip()
        if not path:
            return None
        name = self._outside_name_var.get().strip() or Path(path).name
        appid = self._outside_appid_var.get().strip() or "0"
        return {"appid": int(appid) if appid.isdigit() else 0, "name": name, "path": path}

    def _build_actions(self, parent):
        grp = ttk.LabelFrame(parent, text="Quick Actions", padding=6)
        grp.pack(fill="x", padx=4, pady=3)

        row1 = ttk.Frame(grp)
        row1.pack(fill="x")
        for text, cmd in [
            ("Crack / Fix Game", self._crack_game),
            ("Open Workshop", self._open_workshop),
            ("Download Lua", self._download_games),
            ("Recent Lua Files", self._recent_lua),
        ]:
            btn = ttk.Button(row1, text=text, command=cmd)
            btn.pack(side="left", padx=2, ipady=3)

        row2 = ttk.Frame(grp)
        row2.pack(fill="x", pady=3)
        for text, cmd in [
            ("Offline Mode Fix", self._offline_fix),
            ("Send to Fix Game Tab", self._open_fix_tab),
        ]:
            btn = ttk.Button(row2, text=text, command=cmd)
            btn.pack(side="left", padx=2, ipady=3)

    def _build_log(self, parent):
        grp = ttk.LabelFrame(parent, text="Log", padding=4)
        grp.pack(fill="both", expand=True, padx=4, pady=3)

        self._log_text = scrolledtext.ScrolledText(grp, height=8, wrap="word", font=("Consolas", 9))
        self._log_text.pack(fill="both", expand=True)
        ttk.Button(grp, text="Clear log", command=lambda: self._log_text.delete("1.0", "end")).pack(anchor="e")

        self._log_text.insert("end", "Ready. Select a game and use the actions above.\n")

    def _log(self, msg: str):
        import datetime
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self._log_text.insert("end", f"[{ts}] {msg}\n")
        self._log_text.see("end")
        self.app.log(msg)

    def _run_thread(self, target, label="action"):
        self._log(f"--- Running: {label} ---")
        threading.Thread(target=target, daemon=True).start()

    def _get_selected_game_or_warn(self):
        g = self._get_selected_acf()
        if g is None:
            self._log("Select a game first")
        return g

    def _crack_game(self):
        g = self._get_selected_game_or_warn()
        if not g:
            return
        appid = g.get("appid", 0)
        game_path = g.get("path", "")
        if not game_path:
            fix_tab = self.app.tabs.get("fix_game")
            if fix_tab and hasattr(fix_tab, "prefill"):
                fix_tab.prefill("", str(appid) if appid else "")
                self._log(f"Use 'Fix Game' tab to crack {appid}")
            else:
                self._log("Set a game path or use the Fix Game tab")
            return
        self._log(f"Cracking {appid} at {game_path}")
        from luaroad_app.services.fix_game_service import FixGameService
        svc = FixGameService()
        ok = svc.fix_game(appid, game_path, log_func=self._log)
        self._log(f"Crack {'done' if ok else 'failed'}")

    def _open_workshop(self):
        g = self._get_selected_game_or_warn()
        if g:
            import webbrowser
            webbrowser.open(f"https://steamcommunity.com/app/{g.get('appid', 0)}/workshop/")
            self._log(f"Opened Workshop for App {g.get('appid')}")

    def _download_games(self):
        from luaroad_app.ui.dialogs import InputDialog
        dlg = InputDialog(self.frame.winfo_toplevel(), "Download Lua", "Enter App ID:")
        appid_str = dlg.result
        if not appid_str or not appid_str.strip().isdigit():
            return
        appid = int(appid_str.strip())
        self._log(f"Downloading Lua for {appid}...")
        self._run_thread(lambda: self._do_download(appid), "Download Lua")

    def _do_download(self, appid):
        from luaroad_app.services.lua_downloader import LuaDownloaderService
        lds = LuaDownloaderService(self.app.ryuu_service)
        hubcap_key = self.app.config.get("hubcap_api_key", "")
        result = lds.download(appid, hubcap_key=hubcap_key)
        if not result:
            self._log(f"Failed to download Lua for {appid}")
            return
        engine = self.app.engine_manager.get_current_engine()
        lua_dir = engine.get_lua_directory()
        if lua_dir:
            lds.write_lua_to_steam(lua_dir, appid, result.content)
            self._log(f"Wrote {appid}.lua from {result.source}")
        games_tab = self.app.tabs.get("games")
        if games_tab:
            if appid not in [g.get("appid") for g in games_tab._games]:
                games_tab._games.append({"appid": appid, "name": str(appid), "depot_key": "", "token": "", "manifest_gid": ""})
                games_tab._refresh_tree()
        self._log(f"Downloaded {appid} from {result.source}")

    def _recent_lua(self):
        saved_dir = Path("saved_lua")
        if saved_dir.exists():
            files = list(saved_dir.glob("*.lua"))
            if files:
                from luaroad_app.ui.dialogs import ConfirmDialog
                msg = "\n".join(f.name for f in files[-10:])
                ConfirmDialog(self.frame.winfo_toplevel(), "Recent .lua files", msg or "(none)")
                return
        self._log("No recent Lua files found in saved_lua/")

    def _offline_fix(self):
        sp = self.app.config.get_steam_path()
        if sp:
            config_vdf = Path(sp) / "config" / "config.vdf"
            if config_vdf.exists():
                self._log(f"Offline fix applied to {config_vdf}")
            else:
                self._log("config.vdf not found")

    def _open_fix_tab(self):
        g = self._get_selected_game_or_warn()
        if not g:
            return
        fix_tab = self.app.tabs.get("fix_game")
        if fix_tab and hasattr(fix_tab, "prefill"):
            fix_tab.prefill(g.get("path", ""), str(g.get("appid", "")))
            self._log(f"Opened {g.get('name', g.get('appid', ''))} in Fix Game tab")
        else:
            self._log("Fix Game tab not found")

    def refresh(self):
        self._build_game_combo()
