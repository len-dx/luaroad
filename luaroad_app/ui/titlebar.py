import tkinter as tk
from tkinter import ttk


def install_custom_titlebar(root):
    root.overrideredirect(True)

    bar = ttk.Frame(root, height=32)
    bar.pack(fill="x", before=root.winfo_children()[0] if root.winfo_children() else None)

    bar.columnconfigure(1, weight=1)

    icon = ttk.Label(bar, text="\u2699", font=("Segoe UI", 12))
    icon.grid(row=0, column=0, padx=(10, 4), pady=4)

    title = root.title()
    title_lbl = ttk.Label(bar, text=title, font=("Segoe UI", 10))
    title_lbl.grid(row=0, column=1, sticky="w", pady=4)

    btn_frame = ttk.Frame(bar)
    btn_frame.grid(row=0, column=2, sticky="e")

    def minimize():
        root.wm_attributes("-alpha", 0)
        root.iconify()
        root.wm_attributes("-alpha", 1)

    def maximize():
        if root.wm_state() == "zoomed":
            root.wm_state("normal")
        else:
            root.wm_state("zoomed")

    def close():
        root.destroy()

    min_btn = ttk.Button(btn_frame, text="\u2014", width=3, command=minimize)
    min_btn.pack(side="left", padx=0)

    max_btn = ttk.Button(btn_frame, text="\u25a1", width=3, command=maximize)
    max_btn.pack(side="left", padx=0)

    close_btn = ttk.Button(btn_frame, text="\u2715", width=3, command=close)
    close_btn.pack(side="left", padx=0)

    drag_data = {"x": 0, "y": 0, "max": False}

    def on_drag_start(e):
        drag_data["x"] = e.x_root - root.winfo_x()
        drag_data["y"] = e.y_root - root.winfo_y()
        drag_data["max"] = root.wm_state() == "zoomed"

    def on_drag(e):
        if drag_data["max"]:
            drag_data["max"] = False
            root.wm_state("normal")
            root.update_idletasks()
            drag_data["x"] = e.x_root - root.winfo_x()
            drag_data["y"] = e.y_root - root.winfo_y()
        x = e.x_root - drag_data["x"]
        y = e.y_root - drag_data["y"]
        root.geometry(f"+{x}+{y}")

    def on_double_click(e):
        maximize()

    for w in (bar, icon, title_lbl):
        w.bind("<Button-1>", on_drag_start)
        w.bind("<B1-Motion>", on_drag)
        w.bind("<Double-Button-1>", on_double_click)

    def update_title():
        title_lbl.config(text=root.title())
        root.after(200, update_title)

    update_title()

    return bar
