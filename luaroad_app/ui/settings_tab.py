import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path


class SettingsTab:
    def __init__(self, parent, app_ref):
        self.app = app_ref
        self.frame = ttk.Frame(parent)
        self._build()

    def _build(self):
        notebook = ttk.Notebook(self.frame)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self._build_general(notebook)
        self._build_api_keys(notebook)
        self._build_steam(notebook)
        self._build_about(notebook)

    # ── General ────────────────────────────────────────────────────────

    def _build_general(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="General")

        ttk.Label(tab, text="General Settings", font=("", 16, "bold")).pack(pady=(15, 10))

        # Appearance
        frame = ttk.LabelFrame(tab, text="Appearance", padding=10)
        frame.pack(fill="x", padx=15, pady=4)
        r = ttk.Frame(frame)
        r.pack(fill="x")
        ttk.Label(r, text="Theme:").pack(side="left")
        self._theme_var = tk.StringVar(value=self.app.config.get("theme", "dark"))
        ttk.Combobox(r, textvariable=self._theme_var, values=["dark", "light"], width=10, state="readonly").pack(side="left", padx=5)
        ttk.Button(r, text="Apply", command=self._apply_theme).pack(side="left")

        # Default Lua Source
        frame = ttk.LabelFrame(tab, text="Lua Downloads", padding=10)
        frame.pack(fill="x", padx=15, pady=4)
        r = ttk.Frame(frame)
        r.pack(fill="x")
        ttk.Label(r, text="Default source:").pack(side="left")
        self._lua_source_var = tk.StringVar(value=self.app.config.get("default_lua_source", "auto"))
        ttk.Combobox(r, textvariable=self._lua_source_var, values=["auto", "revobd", "ryuu", "oureveryday", "hubcap"], width=12, state="readonly").pack(side="left", padx=5)
        ttk.Button(r, text="Save", command=self._save_lua_source).pack(side="left")
        ttk.Label(frame, text="Auto tries: revobd → Ryuu → Hubcap → oureveryday", font=("", 8)).pack(anchor="w", pady=(4, 0))

        # Default Engine
        frame = ttk.LabelFrame(tab, text="Engine", padding=10)
        frame.pack(fill="x", padx=15, pady=4)
        self._engine_var = tk.StringVar(value=self.app.config.get_engine())
        for e in self.app.engine_manager.list_engines():
            ttk.Radiobutton(frame, text=e["name"], variable=self._engine_var, value=e["id"]).pack(anchor="w", pady=1)
        ttk.Button(frame, text="Set Default", command=self._set_default_engine).pack(pady=4)

        # Misc
        frame = ttk.LabelFrame(tab, text="Other", padding=10)
        frame.pack(fill="x", padx=15, pady=4)
        self._auto_reload_var = tk.BooleanVar(value=self.app.config.get("auto_reload", True))
        ttk.Checkbutton(frame, text="Auto-reload Lua configs", variable=self._auto_reload_var, command=self._save_auto_reload).pack(anchor="w")
        self._check_updates_var = tk.BooleanVar(value=self.app.config.get("check_updates", True))
        ttk.Checkbutton(frame, text="Check for updates on startup", variable=self._check_updates_var, command=self._save_check_updates).pack(anchor="w")

    # ── API Keys ───────────────────────────────────────────────────────

    def _build_api_keys(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="API Keys")

        ttk.Label(tab, text="API Keys & Authentication", font=("", 16, "bold")).pack(pady=(15, 10))
        ttk.Label(tab, text="Configure API keys for various services.", font=("", 10)).pack(pady=(0, 6))

        # Ryuu
        frame = ttk.LabelFrame(tab, text="Ryuu", padding=10)
        frame.pack(fill="x", padx=15, pady=4)
        ttk.Label(frame, text="Required for Ryuu Lua downloads & manifest hub.").pack(anchor="w")
        r = ttk.Frame(frame)
        r.pack(fill="x", pady=3)
        ttk.Label(r, text="API Key:").pack(side="left")
        self._ryuu_key_var = tk.StringVar(value=self.app.config.get("ryuu_api_key", ""))
        self._ryuu_key_entry = ttk.Entry(r, textvariable=self._ryuu_key_var, width=50, show="*")
        self._ryuu_key_entry.pack(side="left", fill="x", expand=True, padx=4)
        self._ryuu_key_shown = False
        ttk.Button(r, text="Show", command=self._toggle_ryuu_key).pack(side="left", padx=1)
        ttk.Button(r, text="Save", command=self._save_ryuu_key).pack(side="left", padx=1)
        ttk.Label(frame, text="Get a key at: https://generator.ryuu.lol/", font=("", 9)).pack(anchor="w")

        # Hubcap
        frame = ttk.LabelFrame(tab, text="Hubcap Manifest", padding=10)
        frame.pack(fill="x", padx=15, pady=4)
        ttk.Label(frame, text="Used as a Lua download source and manifest library.").pack(anchor="w")
        r = ttk.Frame(frame)
        r.pack(fill="x", pady=3)
        ttk.Label(r, text="API Key:").pack(side="left")
        self._hubcap_key_var = tk.StringVar(value=self.app.config.get("hubcap_api_key", ""))
        self._hubcap_key_entry = ttk.Entry(r, textvariable=self._hubcap_key_var, width=50, show="*")
        self._hubcap_key_entry.pack(side="left", fill="x", expand=True, padx=4)
        ttk.Button(r, text="Show", command=self._toggle_hubcap_key).pack(side="left", padx=1)
        ttk.Button(r, text="Save", command=self._save_hubcap_key).pack(side="left", padx=1)
        ttk.Label(frame, text="Get a key at: https://hubcapmanifest.com (free, starts with smm_)", font=("", 9)).pack(anchor="w")

        # Steam Web API
        frame = ttk.LabelFrame(tab, text="Steam Web API", padding=10)
        frame.pack(fill="x", padx=15, pady=4)
        ttk.Label(frame, text="Used by the GBE Token Generator (Tools tab).").pack(anchor="w")
        r = ttk.Frame(frame)
        r.pack(fill="x", pady=3)
        ttk.Label(r, text="API Key:").pack(side="left")
        self._steamweb_key_var = tk.StringVar(value=self.app.config.get("steam_web_api_key", ""))
        self._steamweb_key_entry = ttk.Entry(r, textvariable=self._steamweb_key_var, width=50, show="*")
        self._steamweb_key_entry.pack(side="left", fill="x", expand=True, padx=4)
        ttk.Button(r, text="Show", command=self._toggle_steamweb_key).pack(side="left", padx=1)
        ttk.Button(r, text="Save", command=self._save_steamweb_key).pack(side="left", padx=1)
        ttk.Label(frame, text="Get a key at: https://steamcommunity.com/dev/apikey", font=("", 9)).pack(anchor="w")

        # Manifest API
        frame = ttk.LabelFrame(tab, text="Manifest API (default)", padding=10)
        frame.pack(fill="x", padx=15, pady=4)
        ttk.Label(frame, text="Which backend to use when fetching manifest codes.").pack(anchor="w")
        r = ttk.Frame(frame)
        r.pack(fill="x", pady=3)
        self._manifest_api_var = tk.StringVar(value=self.app.config.get("manifest_api", "steamrun"))
        ttk.Combobox(r, textvariable=self._manifest_api_var, values=["steamrun", "Ryuu"], width=12, state="readonly").pack(side="left")
        ttk.Button(r, text="Save", command=self._save_manifest_api).pack(side="left", padx=5)

    # ── Steam ──────────────────────────────────────────────────────────

    def _build_steam(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Steam")

        ttk.Label(tab, text="Steam Configuration", font=("", 16, "bold")).pack(pady=(15, 10))

        # Steam Path
        frame = ttk.LabelFrame(tab, text="Steam Path", padding=10)
        frame.pack(fill="x", padx=15, pady=4)
        ttk.Label(frame, text="Location of your Steam installation.").pack(anchor="w")
        self._steam_path_var = tk.StringVar(value=str(self.app.config.get_steam_path() or ""))
        ttk.Entry(frame, textvariable=self._steam_path_var, width=60).pack(fill="x", pady=3)
        r = ttk.Frame(frame)
        r.pack(fill="x")
        ttk.Button(r, text="Browse...", command=self._browse_steam_path).pack(side="left", padx=1)
        ttk.Button(r, text="Auto-Detect", command=self._auto_detect).pack(side="left", padx=1)
        ttk.Button(r, text="Save", command=self._save_steam_path).pack(side="left", padx=1)
        engine = self.app.engine_manager.get_current_engine()
        lua_dir = engine.get_lua_directory()
        if lua_dir:
            ttk.Button(r, text="Open Lua Dir", command=lambda: self._open_folder(lua_dir)).pack(side="left", padx=1)

        # Steam32 ID
        frame = ttk.LabelFrame(tab, text="Steam32 ID", padding=10)
        frame.pack(fill="x", padx=15, pady=4)
        ttk.Label(frame, text="Required by the Cloud Saves tab to locate save folders.").pack(anchor="w")
        r = ttk.Frame(frame)
        r.pack(fill="x", pady=3)
        ttk.Label(r, text="ID:").pack(side="left")
        self._steam32_var = tk.StringVar(value=self.app.config.get("steam32_id", ""))
        ttk.Entry(r, textvariable=self._steam32_var, width=25).pack(side="left", padx=4)
        ttk.Button(r, text="Save", command=self._save_steam32_id).pack(side="left")
        ttk.Label(frame, text="Find yours at: https://steamid.xyz", font=("", 9)).pack(anchor="w")

    # ── About ──────────────────────────────────────────────────────────

    def _build_about(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="About")

        from luaroad_app.constants import APP_NAME, APP_VERSION

        ttk.Label(tab, text=APP_NAME, font=("", 24, "bold")).pack(pady=(30, 5))
        ttk.Label(tab, text=f"Version {APP_VERSION}", font=("", 14)).pack()
        ttk.Label(tab, text="A modern Steam unlocker manager with Lua plugin support", wraplength=500).pack(pady=10)

        info = """Features:
• OpenSteamTool & LumaCore engine support (swappable)
• Lua-based plugin/add-on system
• Ryuu Manifest Hub integration
• Steam game library scanner
• DLC unlocker tools
• Local engine update system
• Modern Sun Valley UI theme

Powered by:
• OpenSteamTool (github.com/OpenSteam001/OpenSteamTool)
• LumaCore (github.com/Midrags/SFF)
• Sun-Valley-ttk-theme (github.com/rdbende/Sun-Valley-ttk-theme)

For educational purposes only."""
        ttk.Label(tab, text=info, wraplength=500, justify="left").pack(pady=10, padx=20)

    # ── Handlers ───────────────────────────────────────────────────────

    def _apply_theme(self):
        theme = self._theme_var.get()
        from luaroad_app.ui.theme import setup_theme
        setup_theme(self.frame.winfo_toplevel(), theme)
        self.app.config.set("theme", theme)
        self.app.log(f"Theme changed to {theme}", "info")

    def _save_lua_source(self):
        self.app.config.set("default_lua_source", self._lua_source_var.get())

    def _set_default_engine(self):
        name = self._engine_var.get()
        self.app.config.set("engine", name)
        self.app.log(f"Default engine set to {name}", "info")

    def _save_auto_reload(self):
        self.app.config.set("auto_reload", self._auto_reload_var.get())

    def _save_check_updates(self):
        self.app.config.set("check_updates", self._check_updates_var.get())

    def _save_manifest_api(self):
        self.app.config.set("manifest_api", self._manifest_api_var.get())
        self.app.log(f"Manifest API set to {self._manifest_api_var.get()}", "info")

    def _save_ryuu_key(self):
        key = self._ryuu_key_var.get().strip()
        if key:
            self.app.config.set("ryuu_api_key", key)
            self.app.ryuu_service.set_api_key(key)
            self.app.log("Ryuu API key saved", "info")

    def _toggle_ryuu_key(self):
        if self._ryuu_key_shown:
            self._ryuu_key_entry.config(show="*")
            self._ryuu_key_shown = False
        else:
            self._ryuu_key_entry.config(show="")
            self._ryuu_key_shown = True

    def _toggle_hubcap_key(self):
        if self._hubcap_key_entry.cget("show") == "*":
            self._hubcap_key_entry.config(show="")
        else:
            self._hubcap_key_entry.config(show="*")

    def _save_hubcap_key(self):
        key = self._hubcap_key_var.get().strip()
        if key:
            self.app.config.set("hubcap_api_key", key)
            self.app.log("Hubcap API key saved", "info")

    def _toggle_steamweb_key(self):
        if self._steamweb_key_entry.cget("show") == "*":
            self._steamweb_key_entry.config(show="")
        else:
            self._steamweb_key_entry.config(show="*")

    def _save_steamweb_key(self):
        key = self._steamweb_key_var.get().strip()
        if key:
            self.app.config.set("steam_web_api_key", key)
            self.app.log("Steam Web API key saved", "info")

    def _save_steam32_id(self):
        val = self._steam32_var.get().strip()
        if val.isdigit():
            self.app.config.set("steam32_id", val)
            self.app.log(f"Steam32 ID saved: {val}", "info")
        else:
            self.app.log("Invalid Steam32 ID (must be digits)", "warning")

    def _browse_steam_path(self):
        p = filedialog.askdirectory(title="Select Steam Folder")
        if p:
            self._steam_path_var.set(p)

    def _auto_detect(self):
        from luaroad_app.utils.steam_path import find_steam_path
        p = find_steam_path()
        if p:
            self._steam_path_var.set(str(p))
            self.app.log(f"Steam found at: {p}", "info")
        else:
            self.app.log("Steam not found automatically", "warning")

    def _save_steam_path(self):
        path = self._steam_path_var.get().strip()
        if not path:
            self.app.log("No path entered", "warning")
            return
        from luaroad_app.utils.steam_path import validate_steam_path
        p = Path(path)
        if validate_steam_path(p):
            self.app.config.set_steam_path(path)
            self.app.log(f"Steam path saved: {path}", "info")
        else:
            self.app.log("Invalid Steam path (no steam.exe or steamapps folder)", "error")

    @staticmethod
    def _open_folder(path: Path):
        path.mkdir(parents=True, exist_ok=True)
        import os
        os.startfile(str(path))
