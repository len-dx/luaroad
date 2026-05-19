import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
from pathlib import Path
import threading


class FixGameTab:
    def __init__(self, parent, app_ref):
        self.app = app_ref
        self.frame = ttk.Frame(parent)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(3, weight=1)
        self._build()

    def _build(self):
        header = ttk.Label(self.frame, text="Fix Game — Emulator Pipeline", font=("", 18, "bold"))
        header.grid(row=0, column=0, pady=(10, 2))
        ttk.Label(self.frame, text="Apply Steam emulators to make games playable without ownership check.", wraplength=700).grid(row=1, column=0, pady=(0, 6))

        main_pw = ttk.PanedWindow(self.frame, orient="horizontal")
        main_pw.grid(row=2, column=0, sticky="nsew", padx=6, pady=3)
        self.frame.rowconfigure(2, weight=1)

        left = ttk.Frame(main_pw)
        right = ttk.Frame(main_pw)
        main_pw.add(left, weight=2)
        main_pw.add(right, weight=1)

        self._scroll_canvas = tk.Canvas(left, highlightthickness=0)
        scrollbar = ttk.Scrollbar(left, orient="vertical", command=self._scroll_canvas.yview)
        self._scroll_canvas.configure(yscrollcommand=scrollbar.set)
        scroll_inner = ttk.Frame(self._scroll_canvas)
        scroll_inner.bind("<Configure>", lambda e: self._scroll_canvas.configure(scrollregion=self._scroll_canvas.bbox("all")))
        self._scroll_canvas.create_window((0, 0), window=scroll_inner, anchor="nw")
        self._scroll_canvas.bind("<Configure>", self._on_canvas_resize)
        self._scroll_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._build_target(scroll_inner)
        self._build_identity(scroll_inner)
        self._build_options(scroll_inner)

        act_frame = ttk.Frame(right)
        act_frame.pack(fill="x", pady=3)
        self._run_btn = ttk.Button(act_frame, text="Run Fix Game Pipeline", command=self._run_fix, width=30)
        self._run_btn.pack(pady=2)
        self._revert_btn = ttk.Button(act_frame, text="Revert Changes", command=self._run_revert, width=30)
        self._revert_btn.pack(pady=2)
        self._open_games_btn = ttk.Button(act_frame, text="Open in Games Tab", command=self._open_games_tab, width=30)
        self._open_games_btn.pack(pady=2)

        log_frame = ttk.LabelFrame(right, text="Status Output", padding=4)
        log_frame.pack(fill="both", expand=True, pady=3)
        self._log_area = scrolledtext.ScrolledText(log_frame, height=15, wrap="word", font=("Consolas", 9))
        self._log_area.pack(fill="both", expand=True)
        self._log_area.insert("end", "Ready.\n")

    def _log(self, msg):
        import datetime
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self._log_area.insert("end", f"[{ts}] {msg}\n")
        self._log_area.see("end")
        self.app.log(msg)

    def _on_canvas_resize(self, e):
        self._scroll_canvas.itemconfig(1, width=e.width)

    def _build_target(self, parent):
        grp = ttk.LabelFrame(parent, text="Target Game", padding=6)
        grp.pack(fill="x", padx=2, pady=2)

        row1 = ttk.Frame(grp)
        row1.pack(fill="x")
        ttk.Label(row1, text="Game Folder:").pack(side="left")
        self._path_var = tk.StringVar()
        self._path_entry = ttk.Entry(row1, textvariable=self._path_var)
        self._path_entry.pack(side="left", fill="x", expand=True, padx=4)
        ttk.Button(row1, text="Browse", command=self._browse).pack(side="left")

        row2 = ttk.Frame(grp)
        row2.pack(fill="x", pady=2)
        ttk.Label(row2, text="App ID:").pack(side="left")
        self._id_var = tk.StringVar()
        self._id_entry = ttk.Entry(row2, textvariable=self._id_var, width=15)
        self._id_entry.pack(side="left", padx=4)
        ttk.Button(row2, text="Auto-detect", command=self._auto_detect).pack(side="left", padx=4)

    def _build_identity(self, parent):
        grp = ttk.LabelFrame(parent, text="User Identity", padding=6)
        grp.pack(fill="x", padx=2, pady=2)

        row1 = ttk.Frame(grp)
        row1.pack(fill="x")
        ttk.Label(row1, text="Username:").pack(side="left")
        self._name_var = tk.StringVar(value="Player")
        ttk.Entry(row1, textvariable=self._name_var, width=20).pack(side="left", padx=4)

        row2 = ttk.Frame(grp)
        row2.pack(fill="x", pady=2)
        ttk.Label(row2, text="Steam64 ID:").pack(side="left")
        self._sid_var = tk.StringVar(value="76561198001737783")
        ttk.Entry(row2, textvariable=self._sid_var, width=25).pack(side="left", padx=4)
        ttk.Label(row2, text="Leave default unless you know what you're doing", font=("", 8)).pack(side="left", padx=4)

    def _build_options(self, parent):
        grp = ttk.LabelFrame(parent, text="Fix Options", padding=6)
        grp.pack(fill="x", padx=2, pady=2)

        row1 = ttk.Frame(grp)
        row1.pack(fill="x")
        ttk.Label(row1, text="Emulator Mode:").pack(side="left")
        self._mode_var = tk.StringVar(value="coldclient_simple")
        modes = [
            ("Regular — replace steam_api.dll", "regular"),
            ("ColdClient Simple (recommended)", "coldclient_simple"),
            ("ColdClient Advanced (GSE Fork)", "coldclient_advanced"),
            ("ColdLoader DLL", "coldloader_dll"),
        ]
        self._mode_combo = ttk.Combobox(row1, textvariable=self._mode_var, values=[m[0] for m in modes], width=40, state="readonly")
        self._mode_combo.pack(side="left", padx=4)

        self._chk_steamstub = tk.BooleanVar(value=True)
        ttk.Checkbutton(grp, text="Auto-unpack SteamStub DRM (Steamless)", variable=self._chk_steamstub).pack(anchor="w", pady=2)

        self._chk_launchbat = tk.BooleanVar(value=False)
        ttk.Checkbutton(grp, text="Create Launch.bat (for ColdClient)", variable=self._chk_launchbat).pack(anchor="w", pady=2)

        self._chk_goldberg_update = tk.BooleanVar(value=False)
        ttk.Checkbutton(grp, text="Check for Goldberg updates", variable=self._chk_goldberg_update).pack(anchor="w", pady=2)

    def _browse(self):
        p = filedialog.askdirectory(title="Select game folder")
        if p:
            self._path_var.set(p)
            if not self._id_var.get().strip():
                detected = self._detect_app_id(Path(p))
                if detected:
                    self._id_var.set(detected)

    def _auto_detect(self):
        p = self._path_var.get().strip()
        if p:
            detected = self._detect_app_id(Path(p))
            if detected:
                self._id_var.set(detected)
                self._log(f"Auto-detected App ID: {detected}")

    @staticmethod
    def _detect_app_id(game_path: Path) -> str:
        import re
        candidates = [
            game_path / "steam_appid.txt",
            game_path / "steam_settings" / "steam_appid.txt",
        ]
        for f in candidates:
            try:
                val = f.read_text(encoding="utf-8", errors="ignore").strip()
                if val.isdigit():
                    return val
            except Exception:
                pass
        ini = game_path / "ColdClientLoader.ini"
        try:
            for line in ini.read_text(encoding="utf-8", errors="ignore").splitlines():
                m = re.match(r"(?i)^AppId\s*=\s*(\d+)", line)
                if m:
                    return m.group(1)
        except Exception:
            pass
        try:
            steamapps = game_path.parent.parent
            game_name = game_path.name.lower()
            for acf in steamapps.glob("appmanifest_*.acf"):
                try:
                    text = acf.read_text(encoding="utf-8", errors="ignore")
                    dir_m = re.search(r'"installdir"\s*"([^"]+)"', text)
                    if dir_m and dir_m.group(1).lower() == game_name:
                        id_m = re.search(r'"appid"\s*"(\d+)"', text)
                        if id_m:
                            return id_m.group(1)
                except Exception:
                    pass
        except Exception:
            pass
        return ""

    def _run_fix(self):
        path = self._path_var.get().strip()
        if not path:
            self._log("Select a game folder first")
            return
        app_id = self._id_var.get().strip()
        if not app_id:
            detected = self._detect_app_id(Path(path))
            if detected:
                self._id_var.set(detected)
                app_id = detected
            else:
                self._log("Enter an App ID")
                return
        self._run_btn.config(state="disabled")
        self._revert_btn.config(state="disabled")
        self._log_area.delete("1.0", "end")
        self._log("Starting Fix Game pipeline...")
        threading.Thread(target=self._fix_thread, args=(path, app_id), daemon=True).start()

    def _fix_thread(self, game_dir, app_id_str):
        from luaroad_app.services.fix_game_service import FixGameService
        svc = FixGameService()
        mode_map = {
            "Regular — replace steam_api.dll": "regular",
            "ColdClient Simple (recommended)": "coldclient_simple",
            "ColdClient Advanced (GSE Fork)": "coldclient_advanced",
            "ColdLoader DLL": "coldloader_dll",
        }
        mode = mode_map.get(self._mode_combo.get(), "coldclient_simple")
        ok = svc.fix_game(
            app_id=int(app_id_str),
            game_dir=game_dir,
            emu_mode=mode,
            skip_steamstub=not self._chk_steamstub.get(),
            create_launch_bat=self._chk_launchbat.get(),
            skip_goldberg_update=not self._chk_goldberg_update.get(),
            player_name=self._name_var.get(),
            steam_id=self._sid_var.get(),
            log_func=lambda m: self.frame.after(0, self._log, m),
        )
        self.frame.after(0, lambda: [
            self._log("Pipeline " + ("completed!" if ok else "failed.")),
            self._run_btn.config(state="normal"),
            self._revert_btn.config(state="normal"),
        ])

    def _run_revert(self):
        path = self._path_var.get().strip()
        if not path:
            self._log("Select a game folder first")
            return
        from luaroad_app.ui.dialogs import ConfirmDialog
        dlg = ConfirmDialog(self.frame.winfo_toplevel(), "Confirm Revert", f"Revert all changes in\n{path}?")
        if not dlg.result:
            return
        self._log("Reverting changes...")
        threading.Thread(target=self._revert_thread, args=(path,), daemon=True).start()

    def _revert_thread(self, game_dir):
        from luaroad_app.services.fix_game_service import FixGameService
        svc = FixGameService()
        ok, msg = svc.restore_game(game_dir, log_func=lambda m: self.frame.after(0, self._log, m))
        self.frame.after(0, lambda: self._log(f"Revert: {msg}"))

    def prefill(self, game_path, app_id):
        self._path_var.set(game_path)
        if app_id:
            self._id_var.set(app_id)

    def _open_games_tab(self):
        games_tab = self.app.tabs.get("games")
        if games_tab:
            app_id = self._id_var.get().strip()
            if app_id and app_id.isdigit():
                self.app.add_game(int(app_id))
