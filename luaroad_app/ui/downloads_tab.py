import tkinter as tk
from tkinter import ttk
import time
import threading


class DownloadsTab:
    def __init__(self, parent, app_ref):
        self.app = app_ref
        self.frame = ttk.Frame(parent)
        self.frame.columnconfigure(0, weight=1)
        self._dm = None
        self._build()

    def _build(self):
        header = ttk.Label(self.frame, text="Download Tracking", font=("", 18, "bold"))
        header.pack(pady=(10, 2))
        ttk.Label(self.frame, text="Monitor active downloads, queue, and history.", wraplength=700).pack(pady=(0, 6))

        active_frame = ttk.LabelFrame(self.frame, text="Active Download", padding=6)
        active_frame.pack(fill="x", padx=10, pady=2)
        self._active_label = ttk.Label(active_frame, text="No active download")
        self._active_label.pack(anchor="w")
        self._progress = ttk.Progressbar(active_frame, length=400, mode="determinate")
        self._progress.pack(fill="x", pady=2)
        self._speed_label = ttk.Label(active_frame, text="")
        self._speed_label.pack(anchor="w")

        queue_frame = ttk.LabelFrame(self.frame, text="Queue", padding=4)
        queue_frame.pack(fill="x", padx=10, pady=2)
        cols = ("App ID", "Game", "Mode")
        self._queue_tree = ttk.Treeview(queue_frame, columns=cols, show="headings", height=4)
        for c in cols:
            self._queue_tree.heading(c, text=c)
        self._queue_tree.column("App ID", width=70)
        self._queue_tree.column("Game", width=200, stretch=True)
        self._queue_tree.column("Mode", width=80)
        self._queue_tree.pack(fill="both", expand=True)

        done_frame = ttk.LabelFrame(self.frame, text="Completed", padding=4)
        done_frame.pack(fill="x", padx=10, pady=2)
        cols = ("App ID", "Game", "Time")
        self._done_tree = ttk.Treeview(done_frame, columns=cols, show="headings", height=4)
        for c in cols:
            self._done_tree.heading(c, text=c)
        self._done_tree.column("App ID", width=70)
        self._done_tree.column("Game", width=200, stretch=True)
        self._done_tree.column("Time", width=100)
        self._done_tree.pack(fill="both", expand=True)
        ttk.Button(done_frame, text="Clear Completed", command=self._clear_completed).pack(anchor="e")

        fail_frame = ttk.LabelFrame(self.frame, text="Failed", padding=4)
        fail_frame.pack(fill="x", padx=10, pady=2)
        cols = ("App ID", "Game", "Error", "Retries")
        self._fail_tree = ttk.Treeview(fail_frame, columns=cols, show="headings", height=4)
        for c in cols:
            self._fail_tree.heading(c, text=c)
        self._fail_tree.column("App ID", width=70)
        self._fail_tree.column("Game", width=150, stretch=True)
        self._fail_tree.column("Error", width=200, stretch=True)
        self._fail_tree.column("Retries", width=60)
        self._fail_tree.pack(fill="both", expand=True)
        btn_row = ttk.Frame(fail_frame)
        btn_row.pack(anchor="e")
        ttk.Button(btn_row, text="Retry Selected", command=self._retry_selected).pack(side="left", padx=2)
        ttk.Button(btn_row, text="Clear Failed", command=self._clear_failed).pack(side="left", padx=2)

        self._status_label = ttk.Label(self.frame, text="Download manager ready.")
        self._status_label.pack(anchor="w", padx=10, pady=2)

        self.frame.after(1000, self._refresh_loop)

    def set_download_manager(self, dm):
        self._dm = dm

    def _refresh_loop(self):
        self._refresh()
        self.frame.after(2000, self._refresh_loop)

    def _refresh(self):
        if not self._dm:
            return
        active = self._dm.get_active()
        if active:
            self._active_label.config(text=f"{active.game_name} ({active.app_id}) — {active.progress}%")
            self._progress["value"] = active.progress
        else:
            self._active_label.config(text="No active download")
            self._progress["value"] = 0

        self._queue_tree.delete(*self._queue_tree.get_children())
        for item in self._dm.get_queue():
            self._queue_tree.insert("", "end", values=(item.app_id, item.game_name, item.mode))

        self._done_tree.delete(*self._done_tree.get_children())
        for item in self._dm.get_completed():
            t = time.strftime("%H:%M:%S", time.localtime(item.completed_at)) if item.completed_at else ""
            self._done_tree.insert("", "end", values=(item.app_id, item.game_name, t))

        self._fail_tree.delete(*self._fail_tree.get_children())
        for item in self._dm.get_failed():
            self._fail_tree.insert("", "end", values=(item.app_id, item.game_name, item.error[:60], f"{item.retry_count}/{item.max_retries}"))

    def _clear_completed(self):
        if self._dm:
            self._dm.clear_completed()

    def _clear_failed(self):
        if self._dm:
            self._dm.clear_failed()

    def _retry_selected(self):
        if not self._dm:
            return
        sel = self._fail_tree.selection()
        if not sel:
            return
        values = self._fail_tree.item(sel[0], "values")
        if values:
            try:
                self._dm.retry_download(int(values[0]))
            except ValueError:
                pass
