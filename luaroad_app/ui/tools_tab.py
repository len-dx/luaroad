import tkinter as tk
from tkinter import ttk, scrolledtext
from pathlib import Path


class ToolsTab:
    def __init__(self, parent, app_ref):
        self.app = app_ref
        self.frame = ttk.Frame(parent)
        self._build()

    def _build(self):
        notebook = ttk.Notebook(self.frame)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self._build_engine_tab(notebook)
        self._build_library_tab(notebook)
        self._build_updater_tab(notebook)
        self._build_dlc_tab(notebook)
        self._build_gbe_tab(notebook)
        self._build_vdf_tab(notebook)
        self._build_applist_tab(notebook)
        self._build_logs_tab(notebook)

    def _build_engine_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Engine")

        ttk.Label(tab, text="Engine Management", font=("", 16, "bold")).pack(pady=(15, 10))

        info_frame = ttk.LabelFrame(tab, text="Current Engine", padding=10)
        info_frame.pack(fill="x", padx=15, pady=5)

        engine = self.app.engine_manager.get_current_engine()
        self._engine_status = tk.StringVar(value=f"Engine: {engine.get_name()} | Version: {engine.get_version()} | Installed: {engine.is_installed()}")
        ttk.Label(info_frame, textvariable=self._engine_status).pack(anchor="w")

        btn_frame = ttk.Frame(info_frame)
        btn_frame.pack(fill="x", pady=5)

        ttk.Button(btn_frame, text="Install Engine", command=self._install_engine).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Uninstall Engine", command=self._uninstall_engine).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Refresh Status", command=self._refresh_engine_status).pack(side="left", padx=2)

        switch_frame = ttk.LabelFrame(tab, text="Switch Engine", padding=10)
        switch_frame.pack(fill="x", padx=15, pady=5)

        self._engine_var = tk.StringVar(value=self.app.config.get_engine())
        for e in self.app.engine_manager.list_engines():
            rb = ttk.Radiobutton(
                switch_frame, text=f"{e['name']} - {e['description']}",
                variable=self._engine_var, value=e["id"],
            )
            rb.pack(anchor="w", pady=2)

        ttk.Button(switch_frame, text="Apply Engine Switch", command=self._switch_engine).pack(pady=5)

    def _build_library_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Library Scanner")

        ttk.Label(tab, text="Installed Steam Games", font=("", 16, "bold")).pack(pady=(15, 10))

        scan_frame = ttk.Frame(tab)
        scan_frame.pack(fill="x", padx=15, pady=5)

        ttk.Button(scan_frame, text="Scan Library", command=self._scan_library).pack(side="left", padx=5)
        ttk.Button(scan_frame, text="Add Selected to Games List", command=self._add_selected_to_games).pack(side="left", padx=5)

        list_frame = ttk.Frame(tab)
        list_frame.pack(fill="both", expand=True, padx=15, pady=5)

        cols = ("AppID", "Name", "Size")
        self._lib_tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=12)
        self._lib_tree.heading("AppID", text="AppID")
        self._lib_tree.heading("Name", text="Name")
        self._lib_tree.heading("Size", text="Size on Disk")
        self._lib_tree.column("AppID", width=80)
        self._lib_tree.column("Name", width=300)
        self._lib_tree.column("Size", width=100)
        self._lib_tree.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self._lib_tree.yview)
        scroll.pack(side="right", fill="y")
        self._lib_tree.configure(yscrollcommand=scroll.set)

    def _build_updater_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Updater")

        ttk.Label(tab, text="OpenSteamTool Local Update", font=("", 16, "bold")).pack(pady=(15, 10))

        info_frame = ttk.LabelFrame(tab, text="Version Info", padding=10)
        info_frame.pack(fill="x", padx=15, pady=5)

        from luaroad_app.services.updater import UpdaterService
        updater = UpdaterService()

        self._updater_info = tk.StringVar(
            value=f"Available: {updater.get_available_version()} | Installed: {updater.get_installed_version()}"
        )
        ttk.Label(info_frame, textvariable=self._updater_info).pack(anchor="w")

        btn_frame = ttk.Frame(info_frame)
        btn_frame.pack(fill="x", pady=5)

        ttk.Button(btn_frame, text="Update from Local Release", command=self._do_update).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Check for Updates", command=self._check_updates).pack(side="left", padx=2)

        ttk.Label(tab, text="How to update: Build OpenSteamTool from source, then copy the\nRelease DLLs to the OpenSteamToolRelease folder, or click below\nto re-install from the local release folder.", wraplength=500, justify="left").pack(pady=10, padx=15)

        local_frame = ttk.LabelFrame(tab, text="Local Update Source", padding=10)
        local_frame.pack(fill="x", padx=15, pady=5)

        from luaroad_app.constants import OPENSTEAMTOOL_RELEASE
        ttk.Label(local_frame, text=f"Source folder: {OPENSTEAMTOOL_RELEASE}").pack(anchor="w")
        ttk.Label(local_frame, text="Place updated .dll files there manually, then click Update.").pack(anchor="w", pady=5)

    def _build_dlc_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="DLC Tools")

        ttk.Label(tab, text="DLC Unlocker Tools", font=("", 16, "bold")).pack(pady=(15, 10))

        ttk.Label(tab, text="DLC unlockers help you access DLC content for games you own.\nPlace unlocker DLLs in your game folders as needed.", wraplength=500, justify="left").pack(pady=5, padx=15)

        dlc_frame = ttk.LabelFrame(tab, text="DLC Unlockers (CreamAPI / SmokeAPI style)", padding=10)
        dlc_frame.pack(fill="x", padx=15, pady=5)

        from luaroad_app.constants import ENGINES_DIR
        unlockers_dir = ENGINES_DIR.parent / "dlc_unlockers"
        ttk.Label(dlc_frame, text=f"Unlockers directory: {unlockers_dir}").pack(anchor="w")
        ttk.Button(dlc_frame, text="Open DLC Unlockers Folder", command=lambda: self._open_folder(unlockers_dir)).pack(pady=5)

        ttk.Label(tab, text="Bundled unlockers:\n• CreamAPI - Generic DLC unlocker\n• SmokeAPI - Alternative DLC unlocker\n• Koaloader - Modern DLC unlocker\n• Uplay - Uplay DLC unlocker", wraplength=500, justify="left").pack(pady=10, padx=15)

    def _build_gbe_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="GBE Token")

        ttk.Label(tab, text="GBE Token Generator", font=("", 16, "bold")).pack(pady=(15, 10))
        ttk.Label(tab, text="Generate Goldberg Emulator configuration files for games you own.", wraplength=500).pack(pady=5, padx=15)

        key_frame = ttk.LabelFrame(tab, text="Steam Web API Key", padding=8)
        key_frame.pack(fill="x", padx=15, pady=5)

        key_row = ttk.Frame(key_frame)
        key_row.pack(fill="x")
        ttk.Label(key_row, text="API Key:").pack(side="left")
        self._gbe_key_var = tk.StringVar(value=self.app.config.get("steam_web_api_key", ""))
        self._gbe_key_entry = ttk.Entry(key_row, textvariable=self._gbe_key_var, width=50, show="*")
        self._gbe_key_entry.pack(side="left", padx=4, fill="x", expand=True)
        ttk.Button(key_row, text="Show", command=self._toggle_gbe_key).pack(side="left")
        ttk.Label(tab, text="Get your key at: https://steamcommunity.com/dev/apikey", font=("", 9)).pack(anchor="w", padx=15)

        appid_frame = ttk.LabelFrame(tab, text="App & Output", padding=8)
        appid_frame.pack(fill="x", padx=15, pady=5)

        row1 = ttk.Frame(appid_frame)
        row1.pack(fill="x")
        ttk.Label(row1, text="App ID:").pack(side="left")
        self._gbe_appid_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self._gbe_appid_var, width=15).pack(side="left", padx=4)
        ttk.Label(row1, text="Output:").pack(side="left", padx=4)
        self._gbe_out_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self._gbe_out_var, width=40).pack(side="left", padx=4, fill="x", expand=True)
        ttk.Button(row1, text="Browse", command=self._browse_gbe_out).pack(side="left")

        ttk.Button(tab, text="Generate Token", command=self._gen_gbe_token).pack(pady=5)

        self._gbe_log = scrolledtext.ScrolledText(tab, height=6, wrap="word", font=("Consolas", 9))
        self._gbe_log.pack(fill="x", padx=15, pady=5)
        self._gbe_log.insert("end", "Ready. Make sure Steam is running and you own the game.\n")

    def _build_vdf_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="VDF Keys")

        ttk.Label(tab, text="VDF Depot Key Extractor", font=("", 16, "bold")).pack(pady=(15, 10))
        ttk.Label(tab, text="Extract decryption keys from Steam config.vdf.", wraplength=500).pack(pady=5, padx=15)

        vdf_frame = ttk.LabelFrame(tab, text="config.vdf", padding=8)
        vdf_frame.pack(fill="x", padx=15, pady=5)

        vdf_row = ttk.Frame(vdf_frame)
        vdf_row.pack(fill="x")
        ttk.Label(vdf_row, text="Path:").pack(side="left")
        self._vdf_path_var = tk.StringVar()
        sp = self.app.config.get_steam_path()
        if sp:
            default = Path(sp) / "config" / "config.vdf"
            if default.exists():
                self._vdf_path_var.set(str(default))
        ttk.Entry(vdf_row, textvariable=self._vdf_path_var, width=60).pack(side="left", padx=4, fill="x", expand=True)
        ttk.Button(vdf_row, text="Browse", command=self._browse_vdf).pack(side="left")

        ttk.Button(tab, text="Extract Keys", command=self._extract_vdf_keys).pack(pady=5)

        cols = ("App ID", "Depot ID", "Decryption Key")
        self._vdf_tree = ttk.Treeview(tab, columns=cols, show="headings", height=8)
        for c in cols:
            self._vdf_tree.heading(c, text=c)
        self._vdf_tree.column("App ID", width=70)
        self._vdf_tree.column("Depot ID", width=70)
        self._vdf_tree.column("Decryption Key", width=300)
        self._vdf_tree.pack(fill="both", expand=True, padx=15, pady=5)

    def _build_applist_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="AppList")

        ttk.Label(tab, text="AppList Profile Management", font=("", 16, "bold")).pack(pady=(15, 10))
        ttk.Label(tab, text="Manage GreenLuma AppList profiles. Create, switch, and manage game lists.", wraplength=500).pack(pady=5, padx=15)

        btn_row = ttk.Frame(tab)
        btn_row.pack(fill="x", padx=15, pady=5)
        ttk.Button(btn_row, text="Create Profile", command=self._create_applist_profile).pack(side="left", padx=2)
        ttk.Button(btn_row, text="Switch Profile", command=self._switch_applist_profile).pack(side="left", padx=2)
        ttk.Button(btn_row, text="Refresh", command=self._refresh_applist).pack(side="left", padx=2)

        cols = ("Profile", "App Count", "Apps")
        self._applist_tree = ttk.Treeview(tab, columns=cols, show="headings", height=8)
        self._applist_tree.heading("Profile", text="Profile")
        self._applist_tree.heading("App Count", text="App Count")
        self._applist_tree.heading("Apps", text="Apps")
        self._applist_tree.column("Profile", width=150)
        self._applist_tree.column("App Count", width=80)
        self._applist_tree.column("Apps", width=300)
        self._applist_tree.pack(fill="both", expand=True, padx=15, pady=5)

    def _build_logs_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Logs")

        ttk.Label(tab, text="Application Logs", font=("", 16, "bold")).pack(pady=(15, 10))

        self._log_text = scrolledtext.ScrolledText(tab, height=20, wrap="word")
        self._log_text.pack(fill="both", expand=True, padx=15, pady=5)

        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill="x", padx=15, pady=5)

        ttk.Button(btn_frame, text="Refresh", command=self._refresh_logs).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Clear", command=self._clear_logs).pack(side="left", padx=2)

        self._refresh_logs()

    def _install_engine(self):
        engine = self.app.engine_manager.get_current_engine()
        if engine.install():
            self.app.log(f"Engine {engine.get_name()} installed successfully", "info")
        else:
            self.app.log(f"Failed to install {engine.get_name()}", "error")
        self._refresh_engine_status()

    def _uninstall_engine(self):
        engine = self.app.engine_manager.get_current_engine()
        if engine.uninstall():
            self.app.log(f"Engine {engine.get_name()} uninstalled", "info")
        else:
            self.app.log(f"Failed to uninstall {engine.get_name()}", "error")
        self._refresh_engine_status()

    def _refresh_engine_status(self):
        engine = self.app.engine_manager.get_current_engine()
        self._engine_status.set(f"Engine: {engine.get_name()} | Version: {engine.get_version()} | Installed: {engine.is_installed()}")

    def _switch_engine(self):
        name = self._engine_var.get()
        if self.app.engine_manager.switch_engine(name):
            self.app.log(f"Switched to {name} engine", "info")
            self._refresh_engine_status()
        else:
            self.app.log(f"Failed to switch engine", "error")

    def _scan_library(self):
        steam_path = self.app.config.get_steam_path()
        if not steam_path:
            self.app.log("Steam path not configured", "error")
            return
        from luaroad_app.services.steam import SteamService
        ss = SteamService(steam_path)
        games = ss.get_installed_games()
        for item in self._lib_tree.get_children():
            self._lib_tree.delete(item)
        for g in games:
            size_mb = g.get("size", 0) // (1024 * 1024)
            self._lib_tree.insert("", "end", values=(g["appid"], g["name"], f"{size_mb} MB"))
        self.app.log(f"Found {len(games)} installed games", "info")

    def _add_selected_to_games(self):
        sel = self._lib_tree.selection()
        if not sel:
            return
        count = 0
        for item in sel:
            values = self._lib_tree.item(item, "values")
            appid = int(values[0])
            self.app.add_game(appid)
            count += 1
        self.app.log(f"Added {count} game(s) to config", "info")

    def _do_update(self):
        from luaroad_app.services.updater import UpdaterService
        updater = UpdaterService()
        if updater.update_from_local():
            self._updater_info.set(f"Available: {updater.get_available_version()} | Installed: {updater.get_available_version()}")
            self.app.log("Engine DLLs updated from local release", "info")
        else:
            self.app.log("Update failed", "error")

    def _check_updates(self):
        from luaroad_app.services.updater import UpdaterService
        updater = UpdaterService()
        self._updater_info.set(f"Available: {updater.get_available_version()} | Installed: {updater.get_installed_version()}")
        if updater.has_updates():
            self.app.log("Updates available!", "info")
        else:
            self.app.log("No updates available", "info")

    def _open_folder(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)
        import os
        os.startfile(str(path))

    def _toggle_gbe_key(self):
        if self._gbe_key_entry.cget("show") == "*":
            self._gbe_key_entry.config(show="")
        else:
            self._gbe_key_entry.config(show="*")

    def _browse_gbe_out(self):
        from tkinter import filedialog
        p = filedialog.askdirectory(title="Output Directory")
        if p:
            self._gbe_out_var.set(p)

    def _gen_gbe_token(self):
        api_key = self._gbe_key_var.get().strip()
        if not api_key:
            self._gbe_log.insert("end", "Enter a Steam Web API key first.\n")
            return
        appid_str = self._gbe_appid_var.get().strip()
        if not appid_str.isdigit():
            self._gbe_log.insert("end", "Enter a valid App ID.\n")
            return
        out_dir = self._gbe_out_var.get().strip()
        if not out_dir:
            self._gbe_log.insert("end", "Select an output directory.\n")
            return
        self._gbe_log.delete("1.0", "end")
        self._gbe_log.insert("end", "Generating GBE token... (requires Steam running)\n")
        self.app.config.set("steam_web_api_key", api_key)
        from luaroad_app.services.manifest import ManifestService
        ms = ManifestService()
        code = ms.fetch_manifest_code(appid_str)
        if code:
            self._gbe_log.insert("end", f"Got manifest code: {code[:80]}...\n")
        else:
            self._gbe_log.insert("end", "Could not generate token. Make sure Steam is running.\n")

    def _browse_vdf(self):
        from tkinter import filedialog
        p = filedialog.askopenfilename(title="Select config.vdf", filetypes=[("VDF files", "*.vdf"), ("All files", "*.*")])
        if p:
            self._vdf_path_var.set(p)

    def _extract_vdf_keys(self):
        vdf_path = Path(self._vdf_path_var.get().strip())
        if not vdf_path.exists():
            self.app.log("config.vdf not found", "error")
            return
        import re
        try:
            text = vdf_path.read_text(encoding="utf-8", errors="ignore")
            self._vdf_tree.delete(*self._vdf_tree.get_children())
            count = 0
            for m in re.finditer(r'"(\d+)"\s*\n\s*{\s*\n\s*"DepotID"\s*"(\d+)"\s*\n\s*"DecryptionKey"\s*"([^"]+)"', text):
                self._vdf_tree.insert("", "end", values=(m.group(1), m.group(2), m.group(3)))
                count += 1
            self.app.log(f"Extracted {count} keys from config.vdf", "info")
        except Exception as e:
            self.app.log(f"Failed to extract keys: {e}", "error")

    def _create_applist_profile(self):
        from luaroad_app.ui.dialogs import InputDialog
        dlg = InputDialog(self.frame.winfo_toplevel(), "Create Profile", "Profile name:")
        if dlg.result:
            self.app.log(f"Created AppList profile: {dlg.result}", "info")

    def _switch_applist_profile(self):
        self.app.log("AppList profile switching requires GreenLuma", "info")

    def _refresh_applist(self):
        self.app.log("AppList profiles refreshed", "info")
        self._applist_tree.delete(*self._applist_tree.get_children())
        self._applist_tree.insert("", "end", values=("Default", "0", "(no apps yet — use Games tab)"))

    def _refresh_logs(self):
        self._log_text.delete("1.0", "end")
        for msg in self.app._log_buffer:
            self._log_text.insert("end", msg + "\n")
        self._log_text.see("end")

    def _clear_logs(self):
        self._log_text.delete("1.0", "end")
        self.app._log_buffer.clear()
