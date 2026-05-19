import tkinter as tk
from tkinter import ttk


class DialogBase(tk.Toplevel):
    def __init__(self, parent, title: str, width: int = 400, height: int = 300):
        super().__init__(parent)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.result = None
        center_window(self, parent)


class InputDialog(DialogBase):
    def __init__(self, parent, title: str, label: str, default: str = "", width: int = 450):
        super().__init__(parent, title, width, 150)
        self._label_text = label
        self._default = default
        self._build()
        self.wait_window()

    def _build(self):
        ttk.Label(self, text=self._label_text).pack(pady=(20, 5), padx=20, anchor="w")
        self._entry = ttk.Entry(self, width=50)
        self._entry.insert(0, self._default)
        self._entry.pack(pady=5, padx=20, fill="x")
        self._entry.focus_set()

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="OK", command=self._ok).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self._cancel).pack(side="left", padx=5)

        self.bind("<Return>", lambda e: self._ok())
        self.bind("<Escape>", lambda e: self._cancel())

    def _ok(self):
        self.result = self._entry.get()
        self.destroy()

    def _cancel(self):
        self.destroy()


class ConfirmDialog(DialogBase):
    def __init__(self, parent, title: str, message: str, width: int = 400):
        super().__init__(parent, title, width, 150)
        self._message = message
        self._build()
        self.wait_window()

    def _build(self):
        ttk.Label(self, text=self._message, wraplength=350).pack(pady=(20, 10), padx=20)
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Yes", command=self._yes).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="No", command=self._no).pack(side="left", padx=5)
        self.bind("<Escape>", lambda e: self._no())

    def _yes(self):
        self.result = True
        self.destroy()

    def _no(self):
        self.result = False
        self.destroy()


class AboutDialog(DialogBase):
    def __init__(self, parent):
        super().__init__(parent, "About Luaroad", 400, 250)
        self._build()

    def _build(self):
        from luaroad_app.constants import APP_NAME, APP_VERSION
        ttk.Label(self, text=APP_NAME, font=("", 18, "bold")).pack(pady=(20, 5))
        ttk.Label(self, text=f"Version {APP_VERSION}").pack()
        ttk.Label(self, text="A modern Steam unlocker manager", wraplength=300).pack(pady=10)
        ttk.Label(self, text="Powered by OpenSteamTool & LumaCore", wraplength=300).pack()
        ttk.Label(self, text="Plugins via Lua scripting", wraplength=300).pack()
        ttk.Label(self, text="Supports Ryuu Manifest Hub", wraplength=300).pack()
        ttk.Button(self, text="Close", command=self.destroy).pack(pady=20)


def center_window(win, parent=None):
    win.update_idletasks()
    if parent:
        px = parent.winfo_x()
        py = parent.winfo_y()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
    else:
        px = py = 0
        pw = win.winfo_screenwidth()
        ph = win.winfo_screenheight()
    w = win.winfo_width()
    h = win.winfo_height()
    x = px + (pw - w) // 2
    y = py + (ph - h) // 2
    win.geometry(f"+{x}+{y}")
