import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
from typing import Optional, Tuple

from . import tokens

class PreviewCanvas(tk.Canvas):
    """
    Square preview canvas with checkerboard and interactive crop (pan/zoom).
    """
    def __init__(self, master, get_image_callable, is_light_callable):
        super().__init__(master, highlightthickness=0, background="#000000")
        self._get_image = get_image_callable
        self._is_light = is_light_callable
        self._preview_side = 256
        self._preview_w = 256
        self._preview_h = 256

        self._checker_imgtk = None
        self._checker_imgtk_size = None
        self._checker_is_light = None

        self.preview_imgtk = None

        # Crop interaction state (owned by host; mirrored here for keys)
        self.on_wheel_cb = None
        self.on_drag_start_cb = None
        self.on_drag_move_cb = None
        self.on_drag_end_cb = None

        self.bind("<Configure>", self._on_resize)

    # Checkerboard drawing (adapted to tokens)
    def _draw_checkerboard(self):
        w = int(self._preview_w)
        h = int(self._preview_h)
        side = int(self._preview_side)

        colors = tokens.get_colors(self._is_light())
        c1, c2 = colors["checker_dark"], colors["checker_light"]

        need_new = (
            self._checker_imgtk is None
            or self._checker_imgtk_size != side
            or self._checker_is_light != self._is_light()
        )
        if need_new:
            tile = 12
            cols = side // tile + 2
            rows = side // tile + 2

            img = Image.new("RGB", (cols * tile, rows * tile), c1)
            draw = ImageDraw.Draw(img)
            for y in range(rows):
                yy0, yy1 = y * tile, (y + 1) * tile
                start = (y % 2)
                for x in range(start, cols, 2):
                    xx0, xx1 = x * tile, (x + 1) * tile
                    draw.rectangle([xx0, yy0, xx1, yy1], fill=c2)

            img = img.crop((0, 0, side, side))
            self._checker_imgtk = ImageTk.PhotoImage(img)
            self._checker_imgtk_size = side
            self._checker_is_light = self._is_light()

        try:
            self.configure(background=c1)
        except Exception:
            pass

        x0 = (w - side) // 2
        y0 = (h - side) // 2

        self.delete("checker")
        self.create_image(x0 + side // 2, y0 + side // 2, image=self._checker_imgtk, tags="checker")

    def refresh(self):
        self._draw_checkerboard()
        img = self._get_image()
        if img is None:
            self.delete("preview")
            return
        side = int(self._preview_side)
        disp = img.resize((side, side))
        self.preview_imgtk = ImageTk.PhotoImage(disp)
        self.delete("preview")
        self.create_image(self._preview_w // 2, self._preview_h // 2, image=self.preview_imgtk, tags="preview")

    def _on_resize(self, event):
        self._preview_w = max(1, int(event.width))
        self._preview_h = max(1, int(event.height))
        side = max(64, min(self._preview_w, self._preview_h))
        self._preview_side = side
        self.after(50, self.refresh)
