import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
from pathlib import Path
import threading


class CloudSavesTab:
    def __init__(self, parent, app_ref):
        self.app = app_ref
        self.frame = ttk.Frame(parent)
        self.frame.columnconfigure(0, weight=1)
        self._games = []
        self._build()

    def _build(self):
        header = ttk.Label(self.frame, text="Cloud Saves — Backup & Restore", font=("", 18, "bold"))
        header.pack(pady=(10, 2))
        ttk.Label(self.frame, text="Backup and restore Steam cloud save files.", wraplength=700).pack(pady=(0, 6))

        setup_frame = ttk.LabelFrame(self.frame, text="Steam Setup", padding=6)
        setup_frame.pack(fill="x", padx=10, pady=2)

        sp_row = ttk.Frame(setup_frame)
        sp_row.pack(fill="x")
        ttk.Label(sp_row, text="Steam Path:").pack(side="left")
        self._sp_var = tk.StringVar(value=str(self.app.config.get_steam_path() or ""))
        ttk.Entry(sp_row, textvariable=self._sp_var, width=50).pack(side="left", padx=4, fill="x", expand=True)
        ttk.Button(sp_row, text="Browse", command=self._browse_sp).pack(side="left")

        id_row = ttk.Frame(setup_frame)
        id_row.pack(fill="x", pady=2)
        ttk.Label(id_row, text="Steam32 ID:").pack(side="left")
        self._sid_var = tk.StringVar(value=self.app.config.get("steam32_id", ""))
        self._sid_entry = ttk.Entry(id_row, textvariable=self._sid_var, width=25)
        self._sid_entry.pack(side="left", padx=4)
        ttk.Button(id_row, text="Save ID", command=self._save_id).pack(side="left", padx=2)
        ttk.Label(id_row, text="Find at steamid.xyz", font=("", 8)).pack(side="left", padx=4)

        ttk.Button(setup_frame, text="Scan Games", command=self._scan_games).pack(anchor="w", pady=2)

        games_frame = ttk.LabelFrame(self.frame, text="Games with Cloud Saves (remote/ folder)", padding=4)
        games_frame.pack(fill="x", padx=10, pady=2)

        cols = ("App ID", "Game Name")
        self._games_tree = ttk.Treeview(games_frame, columns=cols, show="headings", height=6)
        self._games_tree.heading("App ID", text="App ID")
        self._games_tree.heading("Game Name", text="Game Name")
        self._games_tree.column("App ID", width=70)
        self._games_tree.column("Game Name", width=300, stretch=True)
        self._games_tree.pack(fill="both", expand=True)

        ttk.Separator(self.frame, orient="horizontal").pack(fill="x", padx=10, pady=5)

        backup_frame = ttk.LabelFrame(self.frame, text="Backup Saves", padding=6)
        backup_frame.pack(fill="x", padx=10, pady=2)
        ttk.Label(backup_frame, text="Select a game above, then choose backup destination.").pack(anchor="w")

        dest_row = ttk.Frame(backup_frame)
        dest_row.pack(fill="x")
        ttk.Label(dest_row, text="Destination:").pack(side="left")
        self._dest_var = tk.StringVar()
        ttk.Entry(dest_row, textvariable=self._dest_var).pack(side="left", padx=4, fill="x", expand=True)
        ttk.Button(dest_row, text="Browse", command=self._browse_dest).pack(side="left")
        ttk.Button(backup_frame, text="Backup Selected Game", command=self._do_backup).pack(anchor="w", pady=2)

        ttk.Separator(self.frame, orient="horizontal").pack(fill="x", padx=10, pady=5)

        restore_frame = ttk.LabelFrame(self.frame, text="Import (Restore) Saves", padding=6)
        restore_frame.pack(fill="x", padx=10, pady=2)
        ttk.Label(restore_frame, text="Browse to a backup folder to restore.").pack(anchor="w")

        imp_row = ttk.Frame(restore_frame)
        imp_row.pack(fill="x")
        ttk.Label(imp_row, text="Backup Folder:").pack(side="left")
        self._import_var = tk.StringVar()
        ttk.Entry(imp_row, textvariable=self._import_var).pack(side="left", padx=4, fill="x", expand=True)
        ttk.Button(imp_row, text="Browse", command=self._browse_import).pack(side="left")
        ttk.Button(restore_frame, text="Import Saves → Steam", command=self._do_restore).pack(anchor="w", pady=2)

        log_frame = ttk.LabelFrame(self.frame, text="Output", padding=4)
        log_frame.pack(fill="both", expand=True, padx=10, pady=2)
        self._log = scrolledtext.ScrolledText(log_frame, height=6, wrap="word", font=("Consolas", 9))
        self._log.pack(fill="both", expand=True)

    def _log_msg(self, msg):
        import datetime
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self._log.insert("end", f"[{ts}] {msg}\n")
        self._log.see("end")

    def _browse_sp(self):
        p = filedialog.askdirectory(title="Select Steam Folder")
        if p:
            self._sp_var.set(p)

    def _save_id(self):
        val = self._sid_var.get().strip()
        if val.isdigit():
            self.app.config.set("steam32_id", val)
            self._log_msg(f"Steam32 ID saved: {val}")
        else:
            self._log_msg("Invalid Steam32 ID (must be digits)")

    def _browse_dest(self):
        p = filedialog.askdirectory(title="Select Backup Destination")
        if p:
            self._dest_var.set(p)

    def _browse_import(self):
        p = filedialog.askdirectory(title="Select Backup Folder")
        if p:
            self._import_var.set(p)

    def _scan_games(self):
        sp = self._sp_var.get().strip()
        sid = self._sid_var.get().strip()
        if not sp or not sid:
            self._log_msg("Set Steam path and Steam32 ID first")
            return
        self._log_msg("Scanning...")
        threading.Thread(target=self._scan_thread, args=(sp, sid), daemon=True).start()

    def _scan_thread(self, sp, sid):
        from luaroad_app.services.cloud_saves import CloudSaves
        games = CloudSaves.list_steam_games(sp, sid)
        self._games = games
        self.frame.after(0, lambda: [
            self._games_tree.delete(*self._games_tree.get_children()),
            [self._games_tree.insert("", "end", values=(a, n)) for a, n in games],
            self._log_msg(f"Found {len(games)} game(s) with save data"),
        ])

    def _get_selected_game(self):
        sel = self._games_tree.selection()
        if not sel:
            return None
        values = self._games_tree.item(sel[0], "values")
        if values:
            try:
                return int(values[0]), values[1]
            except (ValueError, IndexError):
                pass
        return None

    def _do_backup(self):
        game = self._get_selected_game()
        if not game:
            self._log_msg("Select a game first")
            return
        dest = self._dest_var.get().strip()
        if not dest:
            self._log_msg("Select a destination folder")
            return
        sp = self._sp_var.get().strip()
        sid = self._sid_var.get().strip()
        app_id, name = game
        self._log_msg(f"Backing up {name} ({app_id})...")
        threading.Thread(target=self._backup_thread, args=(sp, sid, app_id, name, dest), daemon=True).start()

    def _backup_thread(self, sp, sid, app_id, name, dest):
        from luaroad_app.services.cloud_saves import CloudSaves
        result = CloudSaves.backup_steam_save(
            sp, sid, app_id, name, dest,
            log_func=lambda m: self.frame.after(0, self._log_msg, m),
        )
        self.frame.after(0, lambda: self._log_msg(f"Backup {'done' if result else 'failed'}"))

    def _do_restore(self):
        game = self._get_selected_game()
        if not game:
            self._log_msg("Select a game first")
            return
        backup = self._import_var.get().strip()
        if not backup:
            self._log_msg("Select a backup folder")
            return
        sp = self._sp_var.get().strip()
        sid = self._sid_var.get().strip()
        app_id, name = game
        self._log_msg(f"Restoring {name} ({app_id})...")
        threading.Thread(target=self._restore_thread, args=(sp, sid, app_id, backup), daemon=True).start()

    def _restore_thread(self, sp, sid, app_id, backup):
        from luaroad_app.services.cloud_saves import CloudSaves
        ok = CloudSaves.restore_steam_save(
            backup, sp, sid, app_id,
            log_func=lambda m: self.frame.after(0, self._log_msg, m),
        )
        self.frame.after(0, lambda: self._log_msg(f"Restore {'done' if ok else 'failed'}"))
