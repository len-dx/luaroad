import tkinter as tk
from tkinter import ttk, scrolledtext
from pathlib import Path
import threading


class StoreTab:
    def __init__(self, parent, app_ref):
        self.app = app_ref
        self.frame = ttk.Frame(parent)
        self._client = None
        self._current_page = 1
        self._total_pages = 1
        self._games_data = []
        self._build()

    def _build(self):
        header = ttk.Label(self.frame, text="Store — Hubcap Manifest Library", font=("", 18, "bold"))
        header.pack(pady=(10, 2))
        ttk.Label(self.frame, text="Browse and download game versions from the Hubcap Manifest library.", wraplength=700).pack(pady=(0, 6))

        key_frame = ttk.LabelFrame(self.frame, text="API Configuration", padding=6)
        key_frame.pack(fill="x", padx=10, pady=2)
        kr = ttk.Frame(key_frame)
        kr.pack(fill="x")
        ttk.Label(kr, text="Hubcap API Key:").pack(side="left")
        self._key_var = tk.StringVar()
        self._key_entry = ttk.Entry(kr, textvariable=self._key_var, width=50, show="*")
        self._key_entry.pack(side="left", padx=4, fill="x", expand=True)
        ttk.Button(kr, text="Connect", command=self._connect).pack(side="left", padx=2)
        ttk.Button(kr, text="Show", command=self._toggle_key).pack(side="left")
        saved = self.app.config.get("hubcap_api_key", "")
        if saved:
            self._key_entry.insert(0, saved)

        search_frame = ttk.Frame(self.frame)
        search_frame.pack(fill="x", padx=10, pady=3)
        ttk.Label(search_frame, text="Search:").pack(side="left")
        self._search_var = tk.StringVar()
        self._search_entry = ttk.Entry(search_frame, textvariable=self._search_var, width=40)
        self._search_entry.pack(side="left", padx=4, fill="x", expand=True)
        self._search_entry.bind("<Return>", lambda e: self._search())
        ttk.Button(search_frame, text="Search", command=self._search).pack(side="left", padx=2)
        ttk.Button(search_frame, text="Browse All", command=self._browse_all).pack(side="left", padx=2)

        cols = ("App ID", "Name", "Status", "Last Updated")
        self._table = ttk.Treeview(self.frame, columns=cols, show="headings", height=12)
        for c in cols:
            self._table.heading(c, text=c)
        self._table.column("App ID", width=70)
        self._table.column("Name", width=300)
        self._table.column("Status", width=100)
        self._table.column("Last Updated", width=120)
        self._table.pack(fill="both", expand=True, padx=10, pady=3)

        scroll = ttk.Scrollbar(self.frame, orient="vertical", command=self._table.yview)
        scroll.place(relx=1, rely=0, relheight=1, anchor="ne")
        self._table.configure(yscrollcommand=scroll.set)

        page_frame = ttk.Frame(self.frame)
        page_frame.pack(fill="x", padx=10, pady=2)
        self._prev_btn = ttk.Button(page_frame, text="← Previous", command=self._prev_page, state="disabled")
        self._prev_btn.pack(side="left")
        self._page_label = ttk.Label(page_frame, text="Page 1 of 1")
        self._page_label.pack(side="left", padx=10)
        self._next_btn = ttk.Button(page_frame, text="Next →", command=self._next_page, state="disabled")
        self._next_btn.pack(side="left")

        dl_frame = ttk.Frame(self.frame)
        dl_frame.pack(fill="x", padx=10, pady=3)
        self._dl_btn = ttk.Button(dl_frame, text="Download (choose version)...", command=self._open_version_picker)
        self._dl_btn.pack(side="left", padx=2)
        self._force_btn = ttk.Button(dl_frame, text="Force Refresh", command=self._force_refresh)
        self._force_btn.pack(side="left", padx=2)
        self._appid_direct_var = tk.StringVar()
        appid_direct_entry = ttk.Entry(dl_frame, textvariable=self._appid_direct_var, width=12)
        appid_direct_entry.pack(side="left", padx=4)
        appid_direct_entry.insert(0, "")
        ttk.Label(dl_frame, text="(or enter App ID directly)").pack(side="left")

        self._status_label = ttk.Label(self.frame, text="Connect with your Hubcap API key to browse.")
        self._status_label.pack(anchor="w", padx=10, pady=2)

    def _toggle_key(self):
        if self._key_entry.cget("show") == "*":
            self._key_entry.config(show="")
        else:
            self._key_entry.config(show="*")

    def _connect(self):
        key = self._key_var.get().strip()
        if not key:
            self._set_status("Enter an API key (get one at hubcapmanifest.com)")
            return
        from luaroad_app.services.hubcap_client import HubcapClient
        if not HubcapClient.validate_api_key(key):
            self._set_status("Invalid key format. Should start with 'smm_'")
            return
        self._client = HubcapClient(key)
        self.app.config.set("hubcap_api_key", key)
        self._set_status("Connected! Search or browse the library.")

    def _set_status(self, text):
        self._status_label.config(text=text)

    def _search(self):
        if not self._client:
            self._set_status("Connect with your API key first")
            return
        self._current_page = 1
        self._fetch(self._search_var.get().strip())

    def _browse_all(self):
        if not self._client:
            self._set_status("Connect with your API key first")
            return
        self._current_page = 1
        self._search_var.set("")
        self._fetch("")

    def _prev_page(self):
        if self._current_page > 1 and self._client:
            self._current_page -= 1
            self._fetch(self._search_var.get().strip())

    def _next_page(self):
        if self._current_page < self._total_pages and self._client:
            self._current_page += 1
            self._fetch(self._search_var.get().strip())

    def _fetch(self, query):
        self._set_status("Loading...")
        self._table.delete(*self._table.get_children())
        threading.Thread(target=self._fetch_thread, args=(query,), daemon=True).start()

    def _fetch_thread(self, query):
        try:
            page = self._client.get_library(limit=100, offset=(self._current_page - 1) * 100, search=query)
            self.frame.after(0, self._display_results, page)
        except Exception as e:
            self.frame.after(0, self._set_status, f"Error: {e}")

    def _display_results(self, page):
        if page is None:
            self._set_status("No results or connection error.")
            return
        self._games_data = page.games
        self._total_pages = page.total_pages
        self._table.delete(*self._table.get_children())
        for g in page.games:
            self._table.insert("", "end", values=(g.app_id, g.name, g.status, g.last_updated))
        self._page_label.config(text=f"Page {self._current_page} of {self._total_pages}")
        self._prev_btn.config(state="normal" if self._current_page > 1 else "disabled")
        self._next_btn.config(state="normal" if self._current_page < self._total_pages else "disabled")
        self._set_status(f"Showing {len(page.games)} results (page {self._current_page}/{self._total_pages})")

    def _resolve_app_id(self):
        direct = self._appid_direct_var.get().strip()
        if direct.isdigit():
            return int(direct), f"App {direct}"
        sel = self._table.selection()
        if not sel:
            return None, None
        values = self._table.item(sel[0], "values")
        if values and values[0]:
            return int(values[0]), values[1]
        return None, None

    def _open_version_picker(self):
        app_id, name = self._resolve_app_id()
        if app_id is None:
            self._set_status("Select a game in the table or enter an App ID")
            return
        self._set_status(f"Fetching depot history for {name}...")
        threading.Thread(target=self._fetch_history, args=(app_id, name, False), daemon=True).start()

    def _force_refresh(self):
        app_id, name = self._resolve_app_id()
        if app_id is None:
            self._set_status("Select a game in the table or enter an App ID")
            return
        self._set_status(f"Forcing refresh for {name}...")
        threading.Thread(target=self._fetch_history, args=(app_id, name, True), daemon=True).start()

    def _fetch_history(self, app_id, name, force):
        from luaroad_app.services.depot_history import get_depots_for_app
        hist = get_depots_for_app(str(app_id), progress_cb=lambda m: self.frame.after(0, self._set_status, m), force_refresh=force)
        self.frame.after(0, self._show_version_picker, app_id, name, hist)

    def _show_version_picker(self, app_id, name, hist):
        if not hist:
            self._set_status(f"No manifest history for {name}")
            return
        from luaroad_app.ui.dialogs import ConfirmDialog
        lines = [f"App {app_id} — {name}", f"Depots found: {len(hist)}"]
        for depot_id, entries in hist.items():
            lines.append(f"  Depot {depot_id}: {len(entries)} entries")
        ConfirmDialog(self.frame.winfo_toplevel(), "Version History", "\n".join(lines))
        self._set_status("Version picker shown (check Games tab for selected version)")
