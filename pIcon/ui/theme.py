import platform
import sys
import tkinter as tk
from tkinter import ttk
from typing import Optional
from tkinter import font as tkfont
from . import tokens

# Optional deps
try:
    import sv_ttk  # Sun Valley theme
except Exception:
    sv_ttk = None  # type: ignore

if sys.platform == "win32":
    try:
        import winreg
        import pywinstyles
    except Exception:
        winreg = None  # type: ignore
        pywinstyles = None  # type: ignore
else:
    winreg = None  # type: ignore
    pywinstyles = None  # type: ignore

# Use "mica" or "acrylic" for Tk apps; "transparent" breaks Tk child rendering.
BACKDROP_MODE = "mica"  # options: "mica" | "acrylic" | "dark" | "normal"

def system_is_light() -> bool:
    """Read Windows 'AppsUseLightTheme'. Defaults to True elsewhere."""
    if sys.platform != "win32" or winreg is None:
        return True
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        ) as key:
            val, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return bool(val)
    except Exception:
        return True

def read_accent_color_hex() -> Optional[str]:
    """
    Read Windows accent color (ColorizationColor) and return as #RRGGBB.
    """
    if sys.platform != "win32" or winreg is None:
        return None
    keys = [
        (r"Software\Microsoft\Windows\DWM", "ColorizationColor"),
        (r"Software\Microsoft\Windows\CurrentVersion\Explorer\Accent", "AccentColorMenu"),
        (r"Software\Microsoft\Windows\DWM", "AccentColor"),
    ]
    for path, name in keys:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path) as k:
                dword, _ = winreg.QueryValueEx(k, name)
                # DWM stores as BBGGRR (little endian ARGB sometimes). Convert to RGB.
                # dword is 0xAABBGGRR; we want RRGGBB.
                r = dword & 0xFF
                g = (dword >> 8) & 0xFF
                b = (dword >> 16) & 0xFF
                return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            continue
    return None

def apply_theme(root: tk.Tk, mode: str = "System") -> bool:
    """
    Apply ttk theme and window titlebar styles. Returns True on success.
    mode: "Light" | "Dark" | "System"
    """
    is_light = system_is_light() if mode == "System" else (mode == "Light")

    # Apply ttk theme
    try:
        if sv_ttk:
            sv_ttk.set_theme("light" if is_light else "dark")
        else:
            ttk.Style(root).theme_use("vista" if platform.system() == "Windows" else "clam")
    except Exception:
        pass

    default = tkfont.nametofont("TkDefaultFont")
    try:
        default.configure(family="Segoe UI Variable", size=10)
    except Exception:
        default.configure(family="Segoe UI", size=10)

    # Keep other standard fonts in sync (ttk uses these)
    for name in ("TkTextFont", "TkHeadingFont", "TkMenuFont"):
        try:
            tkfont.nametofont(name).configure(
                family=default.cget("family"),
                size=default.cget("size")
            )
        except Exception:
            pass

    # Title bar / header color (Windows)
    # Title bar / backdrop (Windows)
    if sys.platform == "win32":
        try:
            apply_backdrop(root, BACKDROP_MODE if BACKDROP_MODE else ("dark" if not is_light else "normal"))
        except Exception:
            # Fallback: simple header colors if pywinstyles/backdrop fails
            try:
                import pywinstyles as _pws  # may already be imported above
                if not is_light:
                    _pws.change_header_color(root, "#1c1c1c")
                    _pws.change_title_color(root, "white")
                else:
                    _pws.change_header_color(root, "#fafafa")
                    _pws.change_title_color(root, "black")
            except Exception:
                pass


    return True

def set_font_scale(root, scale: float):
    """
    Set sizes of Tk named fonts so ttk text scales immediately.
    Base size = 10pt at 1.0×; scale multiplies that.
    """
    from tkinter import font as tkfont
    size = max(8, int(round(10 * float(scale))))
    for name in ("TkDefaultFont", "TkTextFont", "TkHeadingFont", "TkMenuFont"):
        try:
            tkfont.nametofont(name).configure(size=size)
        except Exception:
            pass

def set_window_icon(root: tk.Tk, ico_path: str | None = None):
    """
    Set the app/window icon.
    - Uses .ico on Windows if found (best for title bar + taskbar).
    - Falls back to an embedded PNG via assets.get_icon(...).
    """
    import os, sys, pathlib
    try:
        from .assets import get_icon  # PNG fallback from your base64 assets
    except Exception:
        get_icon = None

    # Build candidate paths for an .ico file
    candidates = []
    if ico_path:
        candidates.append(ico_path)

    try:
        # Directory of this module (package)
        candidates.append(str(pathlib.Path(__file__).resolve().parent / "app.ico"))
    except Exception:
        pass
    try:
        # Executable folder (useful under PyInstaller)
        candidates.append(os.path.join(os.path.dirname(sys.executable), "app.ico"))
    except Exception:
        pass
    try:
        # Current working dir (dev runs)
        candidates.append(str(pathlib.Path.cwd() / "app.ico"))
    except Exception:
        pass

    ico_used = False
    for p in candidates:
        if p and os.path.isfile(p):
            try:
                root.iconbitmap(default=p)
                ico_used = True
                break
            except Exception:
                pass

    if not ico_used and get_icon:
        # Fallback to embedded PNG
        try:
            img = get_icon("icon", master=root)  # change key if you have a different 'app' icon in assets
            root.iconphoto(True, img)
        except Exception:
            pass


def apply_backdrop(root, mode: str):
    """
    mode: "normal" | "dark" | "mica" | "acrylic" | "transparent"
    Note: Tk widgets do not render reliably on a fully transparent DWM surface.
          We map "transparent" -> "acrylic" for stability.
    """
    try:
        import pywinstyles
    except Exception:
        return  # silently skip on non-Windows or missing package

    m = (mode or "").lower()
    if m == "transparent":
        # Fallback to acrylic to keep child controls visible
        m = "acrylic"

    try:
        if m in ("mica", "acrylic", "optimised", "aero", "inverse", "win7", "popup"):
            pywinstyles.apply_style(root, m)
        elif m == "dark":
            pywinstyles.apply_style(root, "dark")
        else:
            pywinstyles.apply_style(root, "normal")
    except Exception:
        pass

    # Title color for contrast
    try:
        if m in ("acrylic", "mica", "dark"):
            pywinstyles.change_title_color(root, "white")
        else:
            pywinstyles.change_title_color(root, "black")
    except Exception:
        pass

    # Nudge: force a repaint on some builds so the frame re-renders
    try:
        root.wm_attributes("-alpha", 0.99); root.wm_attributes("-alpha", 1.0)
    except Exception:
        pass

class ThemeWatcher:
    """Polls the system theme when mode == System and re-applies."""
    def __init__(self, root: tk.Tk, getter, applier):
        self.root = root
        self.getter = getter
        self.applier = applier
        self.last = None
        self._tick()

    def _tick(self):
        try:
            cur = system_is_light()
            if self.last is None or cur != self.last:
                self.applier()
                self.last = cur
        except Exception:
            pass
        self.root.after(2000, self._tick)
