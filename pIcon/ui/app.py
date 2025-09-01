import os
import sys
import json
import pathlib
import threading
import tkinter as tk
from dataclasses import dataclass, field
from tkinter import ttk, filedialog, messagebox

from PIL import Image

from .components import Nav
from .theme import apply_theme, system_is_light
from .components import install_styles
from .pages.page_icon_export import IconExportPage
from .pages.page_recent import RecentPage
from .pages.page_settings import SettingsPage

# Optional DnD
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except Exception:
    DND_FILES = None
    TkinterDnD = None


@dataclass
class Model:
    input_path: tk.StringVar = field(default_factory=lambda: tk.StringVar())
    output_path: tk.StringVar = field(default_factory=lambda: tk.StringVar())
    fit_mode: tk.StringVar = field(default_factory=lambda: tk.StringVar(value="crop"))
    pad_color: tuple = (0, 0, 0, 0)  # RGBA
    loaded_img: Image.Image | None = None
    crop_zoom: float = 1.0
    crop_cx: float | None = None
    crop_cy: float | None = None
    _drag_last: tuple | None = None


class AppRoot:
    """Holds Tk or TkinterDnD root to simplify type usage."""
    def __init__(self):
        if TkinterDnD:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()


class IconMakerApp:
    def __init__(self):
        self._root_wrapper = AppRoot()
        self.root: tk.Tk = self._root_wrapper.root
        try:
            self.root.call("tk", "scaling", 1.2)
        except Exception:
            pass

        self.root.title("pIcon")

        # Set the title bar / taskbar icon (.ico preferred, PNG fallback)
        from .theme import set_window_icon
        set_window_icon(self.root)  # or: set_window_icon(self.root, ico_path="D:/path/to/app.ico")

        self.root.minsize(980, 640)

        # Settings (recents + last-used dirs)
        self.settings = {}
        self.recent_files: list[str] = []
        self._load_settings()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.model = Model()

        # Theme state
        self.appearance_mode = tk.StringVar(value="System")
        self.ui_scale = 1.2

        apply_theme(self.root, self.appearance_mode.get())
        install_styles(self.root, self.is_light_ui(), scale=self.ui_scale)

        # Toast manager
        from .components import ToastManager
        self.toast_mgr = ToastManager(self.root)

        # Layout + shortcuts
        self._build_layout()
        self._bind_shortcuts()

        # DnD
        if DND_FILES is not None:
            try:
                self.root.drop_target_register(DND_FILES)
                self.root.dnd_bind("<<Drop>>", self._on_drop)
            except Exception:
                pass

        # Watch system theme
        from .theme import ThemeWatcher
        self.theme_watcher = ThemeWatcher(self.root, system_is_light, lambda: self.set_theme(self.appearance_mode.get()))

    # ---- Settings persistence (recents + last-used directories) ----
    def _settings_path(self) -> str:
        # Windows-friendly location; fallback to home on other platforms
        if sys.platform == "win32":
            appdata = os.environ.get("APPDATA") or str(pathlib.Path.home())
            base = os.path.join(appdata, "IconMakerWin11")
        else:
            base = os.path.join(str(pathlib.Path.home()), ".pIcon_win11")
        os.makedirs(base, exist_ok=True)
        return os.path.join(base, "settings.json")

    def _load_settings(self):
        self._settings_file = self._settings_path()
        defaults = {
            "recent_files": [],
            "last_dirs": {
                "open_image": None,
                "save_ico": None,
            }
        }
        try:
            with open(self._settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
        # merge with defaults
        self.settings = defaults
        for k, v in data.items():
            if k == "recent_files" and isinstance(v, list):
                self.settings["recent_files"] = v
            elif k == "last_dirs" and isinstance(v, dict):
                self.settings["last_dirs"].update(v)
        # hydrate in-memory lists
        self.recent_files = list(self.settings.get("recent_files") or [])

    def _save_settings(self):
        try:
            self.settings["recent_files"] = list(self.recent_files)
            with open(self._settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            pass

    def get_last_dir(self, key: str) -> str | None:
        try:
            d = self.settings.get("last_dirs", {}).get(key)
            return d if d and os.path.isdir(d) else None
        except Exception:
            return None

    def set_last_dir(self, key: str, path: str):
        try:
            if not path:
                return
            self.settings.setdefault("last_dirs", {})
            self.settings["last_dirs"][key] = path
            self._save_settings()
        except Exception:
            pass

    def _on_close(self):
        self._save_settings()
        try:
            self.root.destroy()
        except Exception:
            pass

    # ---- UI helpers
    def is_light_ui(self) -> bool:
        mode = self.appearance_mode.get()
        return system_is_light() if mode == "System" else (mode == "Light")

    def set_theme(self, mode: str):
        self.appearance_mode.set(mode)
        apply_theme(self.root, mode)
        install_styles(self.root, self.is_light_ui(), scale=self.ui_scale)

        try:
            self.pages["icon"].preview.refresh()
        except Exception:
            pass

    def apply_scaling(self, scale: float):
        """Apply UI scale to Tk's dpi scaling, default fonts, and ttk paddings."""
        try:
            scale = float(scale)
        except Exception:
            scale = 1.0

        # 1) Tk DPI scaling (affects point-based sizes & geometry units)
        try:
            self.root.call("tk", "scaling", scale)
        except Exception:
            pass

        # 2) Default font sizes (so ttk text actually grows/shrinks)
        try:
            from .theme import set_font_scale
            set_font_scale(self.root, scale)
        except Exception:
            pass

        # 3) Reinstall styles with scaled paddings/margins
        self.ui_scale = scale
        install_styles(self.root, self.is_light_ui(), scale=scale)

        # 4) Nudge layout & preview
        try:
            self.pages["icon"].preview.refresh()
        except Exception:
            pass

        # 5) Friendly toast
        try:
            self.toast(f"UI scale set to {scale:.2f}×")
        except Exception:
            pass

    def _build_layout(self):
        container = ttk.Frame(self.root, padding=8)
        container.pack(fill=tk.BOTH, expand=True)

        # Left nav
        nav_items = [
            ("icon", "Icon Maker", "icon"),
            ("recent", "Recent", "recent"),
            ("settings", "Settings", "theme"),
        ]

        self.nav = Nav(container, nav_items, on_select=self.navigate)
        self.nav.pack(side=tk.LEFT, fill=tk.Y)

        # Main content
        self.content = ttk.Frame(container)
        self.content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))

        self.pages: dict[str, tk.Frame] = {}
        self.pages["icon"] = IconExportPage(self.content, self)
        self.pages["recent"] = RecentPage(self.content, self)
        self.pages["settings"] = SettingsPage(self.content, self)

        for p in self.pages.values():
            p.place(relx=0, rely=0, relwidth=1, relheight=1)
            p.lower()

        self.navigate("icon")

    def navigate(self, key: str):
        for k, p in self.pages.items():
            if k == key:
                p.lift()
            else:
                p.lower()
        # Update nav selection without re-triggering navigate (avoid recursion)
        self.nav.select(key, notify=False)

        if key == "recent":
            try:
                self.pages["recent"].refresh()
            except Exception:
                pass

    # ---- Shortcuts
    def _bind_shortcuts(self):
        r = self.root
        r.bind("<Control-o>", lambda e: self.action_open())
        r.bind("<Control-s>", lambda e: self.pages["icon"].__dict__.get("_export")())
        r.bind("<Control-S>", lambda e: self.pages["icon"].__dict__.get("_export")())
        r.bind("<Control-Shift-S>", lambda e: self.pages["icon"]._choose_output())

        # Fit modes
        r.bind("<Control-Key-1>", lambda e: self._set_fit("pad"))
        r.bind("<Control-Key-2>", lambda e: self._set_fit("crop"))
        r.bind("<Control-Key-3>", lambda e: self._set_fit("stretch"))

        # Crop interactions
        r.bind("<r>", lambda e: self._reset_crop())
        r.bind("<plus>", lambda e: self._zoom(1))
        r.bind("<KP_Add>", lambda e: self._zoom(1))
        r.bind("<minus>", lambda e: self._zoom(-1))
        r.bind("<KP_Subtract>", lambda e: self._zoom(-1))
        r.bind("<Up>", lambda e: self._pan(0, -20))
        r.bind("<Down>", lambda e: self._pan(0, 20))
        r.bind("<Left>", lambda e: self._pan(-20, 0))
        r.bind("<Right>", lambda e: self._pan(20, 0))

        # Maximize
        r.bind("<F11>", lambda e: self._toggle_maximize())

        # Nav
        r.bind("<Alt-Up>", lambda e: self._nav_step(-1))
        r.bind("<Alt-Down>", lambda e: self._nav_step(1))

    def _toggle_maximize(self):
        try:
            state = self.root.state()
            self.root.state("normal" if state == "zoomed" else "zoomed")
        except Exception:
            pass

    def _nav_step(self, delta: int):
        # Move selection up/down in the left nav
        idx_cur = 0
        for i, (k, b) in enumerate(self.nav.buttons):
            st = b.state()
            if "pressed" in st:
                idx_cur = i
                break
        idx = (idx_cur + delta) % len(self.nav.buttons)
        self.navigate(self.nav.buttons[idx][0])

    def _set_fit(self, mode: str):
        self.model.fit_mode.set(mode)
        try:
            self.pages["icon"]._on_fit_changed()
        except Exception:
            pass

    def _reset_crop(self):
        if self.model.loaded_img is None:
            return
        w, h = self.model.loaded_img.size
        self.model.crop_zoom = 1.0
        self.model.crop_cx = w / 2
        self.model.crop_cy = h / 2
        self.pages["icon"].preview.refresh()

    def _zoom(self, direction: int):
        if self.model.loaded_img is None or self.model.fit_mode.get() != "crop":
            return
        factor = 1.1 if direction > 0 else (1/1.1)
        self.model.crop_zoom = max(1.0, min(20.0, self.model.crop_zoom * factor))
        self.pages["icon"].preview.refresh()

    def _pan(self, dx: int, dy: int):
        if self.model.loaded_img is None or self.model.fit_mode.get() != "crop":
            return
        w, h = self.model.loaded_img.size
        base = min(w, h)
        side = max(1, int(round(base / max(1.0, self.model.crop_zoom))))
        px_to_img = side / float(self.pages["icon"].preview._preview_side)
        self.model.crop_cx -= dx * px_to_img
        self.model.crop_cy -= dy * px_to_img
        # clamp
        half = side / 2
        self.model.crop_cx = min(max(self.model.crop_cx, half), w - half)
        self.model.crop_cy = min(max(self.model.crop_cy, half), h - half)
        self.pages["icon"].preview.refresh()

    # ---- Actions
    def action_open(self):
        initdir = self.get_last_dir("open_image")
        path = filedialog.askopenfilename(
            title="Select image",
            initialdir=initdir,
            filetypes=[
                ("Images", "*.png;*.jpg;*.jpeg;*.webp;*.gif;*.bmp;*.tif;*.tiff;*.ico;*.heic;*.heif"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg;*.jpeg"),
                ("WEBP", "*.webp"),
                ("GIF", "*.gif"),
                ("BMP", "*.bmp"),
                ("TIFF", "*.tif;*.tiff"),
                ("ICO", "*.ico"),
                ("HEIC/HEIF", "*.heic;*.heif"),
                ("All files", "*.*"),
            ]
        )
        if not path:
            return
        self.pages["icon"].open_path(path)
        self._add_recent(path)
        # remember this folder for open-image
        try:
            self.set_last_dir("open_image", os.path.dirname(path))
        except Exception:
            pass

    def _add_recent(self, path: str):
        try:
            if path in self.recent_files:
                self.recent_files.remove(path)
            self.recent_files.append(path)
            if len(self.recent_files) > 100:
                self.recent_files = self.recent_files[-100:]
            self._save_settings()
        except Exception:
            pass

    def _on_drop(self, event):
        # Receive paths like {C:\path with space\img.png}
        raw = event.data
        if not raw:
            return
        paths = []
        buf = ""
        in_brace = False
        for ch in raw:
            if ch == "{":
                in_brace = True; buf = ""
            elif ch == "}":
                in_brace = False; paths.append(buf)
            elif ch == " " and not in_brace:
                if buf:
                    paths.append(buf)
                    buf = ""
            else:
                buf += ch
        if buf:
            paths.append(buf)
        if paths:
            self.navigate("icon")
            self.pages["icon"].open_path(paths[0])
            self._add_recent(paths[0])

    # ---- Toasts
    def toast(self, text: str, duration_ms: int = 3000):
        self.toast_mgr.show(text, duration_ms)


def main():
    app = IconMakerApp()
    app.root.mainloop()


if __name__ == "__main__":
    main()
