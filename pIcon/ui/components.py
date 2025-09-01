import tkinter as tk
from tkinter import ttk, colorchooser
from typing import Callable, List, Optional

from . import tokens
from .assets import get_icon

class Card(ttk.Frame):
    """A padded container that simulates rounded corners via internal padding and outline."""
    def __init__(self, master, **kwargs):
        # allow callers to override the style; default to Card.TFrame
        style = kwargs.pop("style", "Card.TFrame")
        super().__init__(master, padding=12, style=style, **kwargs)

class Banner(Card):
    """
    Inline banner styled as a Card so its corners match other cards.
    kind: "info" | "warn" | "error"
    """
    def __init__(self, parent, kind: str, text: str, on_close=None):
        kind_cap = (kind or "info").title()  # Info/Warn/Error
        style_name = f"Banner{kind_cap}Card.TFrame"
        super().__init__(parent, style=style_name)
        self._on_close = on_close

        # Layout: message left (expands), actions right
        self.columnconfigure(0, weight=1)

        lbl_style = f"Banner{kind_cap}.TLabel"
        self.lbl = ttk.Label(self, text=text, style=lbl_style, wraplength=800)
        self.lbl.grid(row=0, column=0, sticky="w", padx=4, pady=2)

        self.actions_frame = ttk.Frame(self, style=style_name)
        self.actions_frame.grid(row=0, column=1, sticky="e")

        # Dismiss (rightmost)
        self.btn_dismiss = ttk.Button(self.actions_frame, text="Dismiss", command=self._close)
        self.btn_dismiss.pack(side=tk.RIGHT)

    def set_text(self, s: str):
        self.lbl.configure(text=s)

    def add_action(self, text: str, command):
        """Add a button to the right-side actions, to the left of Dismiss."""
        btn = ttk.Button(self.actions_frame, text=text, command=command)
        btn.pack(side=tk.RIGHT, padx=(0, 8))
        return btn

    def _close(self):
        if callable(self._on_close):
            try:
                self._on_close()
            except Exception:
                pass
        self.destroy()

class ToastManager:
    """Top-right ephemeral messages."""
    def __init__(self, root: tk.Tk):
        self.root = root
        self.container = tk.Toplevel(root)
        self.container.overrideredirect(True)
        self.container.attributes("-topmost", True)
        self.container.withdraw()
        self.items: List[ttk.Label] = []
        root.bind("<Configure>", self._reposition, add="+")
        self.spacing = 6

    def _reposition(self, _evt=None):
        if not self.items:
            self.container.withdraw()
            return
        self.container.deiconify()
        self.container.lift()
        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()
        w = self.root.winfo_width()
        x = root_x + w - self.container.winfo_width() - 24
        y = root_y + 24
        self.container.geometry(f"+{x}+{y}")

    def show(self, text: str, duration_ms: int = 3000):
        lbl = ttk.Label(self.container, text=text, padding=8, style="Toast.TLabel")
        lbl.pack(anchor="e", pady=(self.spacing if self.items else 0, 0))
        self.items.append(lbl)
        self._reposition()
        self.container.after(duration_ms, lambda: self._dismiss(lbl))

    def _dismiss(self, lbl: ttk.Label):
        try:
            lbl.destroy()
        except Exception:
            pass
        if lbl in self.items:
            self.items.remove(lbl)
        self._reposition()

class SegmentedControl(ttk.Frame):
    """Three-state segmented control using Radiobuttons."""
    def __init__(self, master, variable: tk.StringVar, items: list, command=None):
        super().__init__(master)
        self.configure(style="Segmented.TFrame")
        for i, (text, value) in enumerate(items):
            rb = ttk.Radiobutton(
                self,
                text=text,
                value=value,
                variable=variable,
                command=command,
                style="Segmented.TRadiobutton"
            )
            # no negative padding (Tk requires positive distance)
            rb.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 1, 0))
            self.columnconfigure(i, weight=1)

class Chip(ttk.Checkbutton):
    """Checkable size chip."""
    def __init__(self, master, text: str, variable: tk.IntVar):
        super().__init__(master, text=text, variable=variable, style="Chip.TCheckbutton", padding=6)

class CommandBar(ttk.Frame):
    """Sticky top/bottom command bar."""
    def __init__(self, master):
        super().__init__(master, padding=(8,6))
        self.configure(style="CommandBar.TFrame")

class Nav(ttk.Frame):
    """Left navigation with icons + text."""
    def __init__(self, master, items: list, on_select):
        super().__init__(master, padding=8, style="Nav.TFrame")
        self.on_select = on_select
        self.buttons = []
        self.active = None

        for key, label, icon_name in items:
            img = get_icon(icon_name, master=self)
            b = ttk.Button(
                self,
                text=label,
                image=img,
                compound=tk.LEFT,
                style="Nav.TButton",
                command=lambda k=key: self.select(k, notify=True)  # notify on user click
            )
            b.image = img
            b.pack(fill=tk.X, pady=2)
            self.buttons.append((key, b))

    def select(self, key: str, notify: bool = True):
        """Update visual selection; optionally notify the app."""
        if key == self.active and notify is False:
            # already synced; no-op
            pass
        self.active = key
        for k, b in self.buttons:
            if k == key:
                b.state(["pressed"])
            else:
                b.state(["!pressed"])
        if notify and self.on_select:
            self.on_select(key)

def install_styles(root: tk.Tk, is_light: bool, scale: float = 1.0):
    """Set ttk styles using tokens, with paddings that scale by 'scale'."""
    s = ttk.Style(root)
    colors = tokens.get_colors(is_light)

    # Scaled spacings
    pad  = max(2, int(round(8 * scale)))   # outer paddings
    ip   = max(2, int(round(6 * scale)))   # inner paddings (buttons, etc.)
    chip = max(2, int(round(4 * scale)))   # small chips

    # Base window bg
    root.configure(background=colors["bg"])

    # Cards / containers
    s.configure("Card.TFrame", background=colors["card"], padding=pad)

    # Banners as Cards (so corners match Card rounding)
    s.configure("BannerInfoCard.TFrame",  background=colors["banner_info"],  padding=pad)
    s.configure("BannerWarnCard.TFrame",  background=colors["banner_warn"],  padding=pad)
    s.configure("BannerErrorCard.TFrame", background=colors["banner_error"], padding=pad)

    # Labels per banner kind (so bg matches the card color)
    s.configure("BannerInfo.TLabel",  background=colors["banner_info"],  foreground=colors["text"])
    s.configure("BannerWarn.TLabel",  background=colors["banner_warn"],  foreground=colors["text"])
    s.configure("BannerError.TLabel", background=colors["banner_error"], foreground=colors["text"])

    s.configure("Toast.TLabel",
               background=colors["card"],
               foreground=colors["text"],
               borderwidth=1, relief="solid",
               padding=(ip, max(2, int(ip * 0.6))))

    # Segmented control
    s.configure("Segmented.TFrame", background=colors["card"])
    s.configure("Segmented.TRadiobutton", padding=(ip, max(2, int(ip * 0.6))))

    # Chips
    s.configure("Chip.TCheckbutton", padding=(chip, chip))

    # Command bar
    s.configure("CommandBar.TFrame", background=colors["card"], padding=(pad, max(2, int(pad / 2))))

    # Navigation
    s.configure("Nav.TFrame", background=colors["bg"])
    s.configure("Nav.TButton", anchor="w", padding=(pad, pad))

