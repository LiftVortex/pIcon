import tkinter as tk
from tkinter import ttk
from ..components import Card
from ..theme import read_accent_color_hex

class SettingsPage(ttk.Frame):
    """Settings including theme and scaling."""
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app

        card = Card(self)
        card.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        ttk.Label(card, text="Appearance").pack(anchor="w", pady=(0,6))

        row = ttk.Frame(card); row.pack(fill=tk.X, pady=4)
        ttk.Label(row, text="Theme").pack(side=tk.LEFT)
        self.theme_var = tk.StringVar(value=self.app.appearance_mode.get())
        cb = ttk.Combobox(row, textvariable=self.theme_var, values=["System", "Light", "Dark"], state="readonly", width=12)
        cb.pack(side=tk.LEFT, padx=8)
        cb.bind("<<ComboboxSelected>>", lambda e: self.app.set_theme(self.theme_var.get()))

        # --- UI Scale
        # row = ttk.Frame(card)
        # row.pack(fill=tk.X, pady=(8, 0))
        # ttk.Label(row, text="UI Scale").pack(side=tk.LEFT, padx=(0, 8))

        # self.scale_var = tk.StringVar(value=f"{self.app.ui_scale:.2f}")
        # scale_box = ttk.Combobox(
            # row,
            # width=8,
            # textvariable=self.scale_var,
            # state="readonly",
            # values=["1.00", "1.10", "1.20", "1.25", "1.50", "1.75", "2.00"]
        # )
        # scale_box.pack(side=tk.LEFT)
        # scale_box.bind("<<ComboboxSelected>>", self._on_scale_apply)

        # ttk.Button(row, text="Apply", command=self._on_scale_apply).pack(side=tk.LEFT, padx=8)

        row3 = ttk.Frame(card); row3.pack(fill=tk.X, pady=(8,0))
        ttk.Label(row3, text=f"System accent color: {read_accent_color_hex() or 'Unknown'}").pack(anchor="w")

        # ttk.Label(card, text="Optional features").pack(anchor="w", pady=(16,6))
        # ttk.Label(card, text="- Drag & drop: tkinterdnd2\n- HEIC/HEIF: pi-heif").pack(anchor="w")

        ttk.Label(card, text="Keyboard shortcuts").pack(anchor="w", pady=(16,6))
        shortcuts = (
            "Ctrl+O Open   •  Ctrl+S Export  •  Ctrl+Shift+S Save As\n"
            "R Reset crop   •  + / - Zoom   •  Arrows Pan   •  F11 Maximize\n"
            "Ctrl+1/2/3 Pad/Crop/Stretch   •  Alt+Up/Down Navigate"
        )

        ttk.Label(card, text=shortcuts).pack(anchor="w")
        
    def _on_scale_apply(self, event=None):
        try:
            val = float(self.scale_var.get())
        except Exception:
            val = 1.0
        self.app.apply_scaling(val)
