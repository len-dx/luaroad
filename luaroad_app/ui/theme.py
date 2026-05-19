import sys
import ctypes
from ctypes import wintypes
import sv_ttk


DWMWA_USE_IMMERSIVE_DARK_MODE = 20

_dwm_set = None
try:
    _dwm_set = ctypes.windll.dwmapi.DwmSetWindowAttribute
    _dwm_set.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_void_p, ctypes.c_int]
    _dwm_set.restype = ctypes.c_long
except Exception:
    pass


def _apply_dark_titlebar(root, dark: bool):
    hwnd = root.winfo_id()
    value = ctypes.c_int(1 if dark else 0)

    try:
        import pywinstyles
        version = sys.getwindowsversion()
        if version.major == 10 and version.build >= 22000:
            bg = "#1c1c1c" if dark else "#fafafa"
            pywinstyles.change_header_color(root, bg)
            return
        elif version.major == 10:
            style = "dark" if dark else "normal"
            pywinstyles.apply_style(root, style)
            return
    except ImportError:
        pass

    if _dwm_set:
        _dwm_set(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value))


def setup_theme(root, theme: str = "dark"):
    try:
        sv_ttk.set_theme(theme)
    except Exception:
        pass

    if sys.platform == "win32":
        _apply_dark_titlebar(root, theme == "dark")


def toggle_theme(root, current_theme: str) -> str:
    new_theme = "light" if current_theme == "dark" else "dark"
    setup_theme(root, new_theme)
    return new_theme
