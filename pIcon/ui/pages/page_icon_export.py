import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image

from ...core.images import load_image_as_rgba, make_square, create_multi_resolution_ico
from ...core.sizes import DEFAULT_SIZES, parse_custom_sizes
from ..components import Card, SegmentedControl, Chip, Banner, CommandBar
from ..preview import PreviewCanvas
from .. import tokens  # add near the top of the file if not present

class IconExportPage(ttk.Frame):
    """
    Main page: preview hero, fit mode, sizes chips, export/apply.
    The App injects callbacks for open/save/apply and exposes state via 'model'.
    """
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.model = app.model  # shared state

        # Layout: left preview (hero), right controls
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(2, weight=1)

        GUTTER = tokens.SPACING                  # outer margin on both sides
        HALF_GUTTER = max(1, GUTTER // 2)        # inner gutter between the two columns
        OUTER_PADX = (GUTTER, GUTTER)

        # Command bar wrapped in a rounded Card + spacing below
        cmd_card = Card(self)
        cmd_card.grid(row=0, column=0, columnspan=2, sticky="ew",
                    padx=OUTER_PADX, pady=(0, 8))
        cmd = CommandBar(cmd_card)
        cmd.pack(fill=tk.X)

        ttk.Button(cmd, text="Open", command=app.action_open).pack(side=tk.LEFT, padx=4)
        ttk.Button(cmd, text="Export ICO", command=self._export).pack(side=tk.LEFT, padx=4)

        # --- Banner area
        self.banner_area = ttk.Frame(self)
        self.banner_area.grid(row=3, column=0, columnspan=2, sticky="ew",
                            padx=OUTER_PADX, pady=(6, 0))


        # --- Preview Card
        left_card = Card(self)
        left_card.grid(row=2, column=0, sticky="nsew",
                    padx=(OUTER_PADX[0], HALF_GUTTER))
        left_card.columnconfigure(0, weight=1)
        left_card.rowconfigure(0, weight=1)

        self.preview = PreviewCanvas(left_card, self._get_square_for_preview, self.app.is_light_ui)
        self.preview.grid(row=0, column=0, sticky="nsew")

        # Hook crop interactions to app handlers
        self.preview.bind("<MouseWheel>", self._on_wheel)
        self.preview.bind("<Button-4>", lambda e: self._on_wheel(_mkdelta(e, +120)))
        self.preview.bind("<Button-5>", lambda e: self._on_wheel(_mkdelta(e, -120)))
        self.preview.bind("<ButtonPress-1>", self._on_drag_start)
        self.preview.bind("<B1-Motion>", self._on_drag_move)
        self.preview.bind("<ButtonRelease-1>", self._on_drag_end)

        # --- Controls Card
        right_card = Card(self)
        right_card.grid(row=2, column=1, sticky="nsew",
                    padx=(HALF_GUTTER, OUTER_PADX[1]))

        # Fit mode segmented
        row = ttk.Frame(right_card)
        row.pack(fill=tk.X, pady=(0,6))
        ttk.Label(row, text="Fit to square").pack(anchor="w", pady=(0,4))
        self.fit_mode = self.model.fit_mode  # StringVar
        self.segment = SegmentedControl(row, self.fit_mode,
                                        [("Pad", "pad"), ("Crop", "crop"), ("Stretch", "stretch")],
                                        command=self._on_fit_changed)
        self.segment.pack(fill=tk.X)

        # Pad color sub-panel (contextual)
        # self.pad_row = ttk.Frame(right_card)
        # self.pad_row.pack(fill=tk.X, pady=(6,6))
        # ttk.Label(self.pad_row, text="Pad color").pack(side=tk.LEFT)
        # self.pad_color_btn = ttk.Button(self.pad_row, text="Choose…", command=self._choose_pad_color)
        # self.pad_color_btn.pack(side=tk.LEFT, padx=6)
        # self._update_pad_row_state()

        # Sizes chips
        sizes_frame = ttk.Frame(right_card)
        sizes_frame.pack(fill=tk.X, pady=(8,6))
        top = ttk.Frame(sizes_frame)
        top.pack(fill=tk.X)
        ttk.Label(top, text="Icon sizes").pack(side=tk.LEFT)
        ttk.Button(top, text="All", width=6, command=lambda: self._toggle_all_sizes(True)).pack(side=tk.RIGHT, padx=(4,0))
        ttk.Button(top, text="None", width=6, command=lambda: self._toggle_all_sizes(False)).pack(side=tk.RIGHT)

        grid = ttk.Frame(sizes_frame)
        grid.pack(fill=tk.X, pady=(6,0))
        self.size_vars = {n: tk.IntVar(value=1) for n in DEFAULT_SIZES}
        cols = 4
        for i, n in enumerate(DEFAULT_SIZES):
            chip = Chip(grid, f"{n}", self.size_vars[n])
            chip.grid(row=i // cols, column=i % cols, padx=4, pady=4, sticky="w")

        custom_row = ttk.Frame(sizes_frame)
        custom_row.pack(fill=tk.X, pady=(6,0))
        ttk.Label(custom_row, text="Custom (comma/space)").pack(side=tk.LEFT)
        self.custom_sizes_str = tk.StringVar()
        ttk.Entry(custom_row, textvariable=self.custom_sizes_str, width=26).pack(side=tk.LEFT, padx=(6, 0))

        # Output paths
        out_frame = ttk.Frame(right_card)
        out_frame.pack(fill=tk.X, pady=(8,6))
        ttk.Button(out_frame, text="Save as…", command=self._choose_output).pack(side=tk.LEFT)
        ttk.Label(out_frame, textvariable=self.model.output_path, width=32).pack(side=tk.LEFT, padx=6)

        # Status
        self.status_var = tk.StringVar(value="")
        ttk.Label(right_card, textvariable=self.status_var).pack(anchor="w", pady=(8,0))

    # ---- App state integration
    def _get_square_for_preview(self):
        img = self.model.loaded_img
        if img is None:
            return None
        if self.fit_mode.get() == "crop":
            return make_square(img, mode="crop",
                               crop_center=(self.model.crop_cx, self.model.crop_cy),
                               crop_zoom=self.model.crop_zoom)
        elif self.fit_mode.get() == "pad":
            return make_square(img, mode="pad", pad_rgba=self.model.pad_color)
        else:
            return make_square(img, mode="stretch")

    # ---- Event handlers
    def _on_fit_changed(self):
        self._update_pad_row_state()
        self.preview.refresh()

    def _update_pad_row_state(self):
        """Enable/disable the Pad color sub-panel based on the current fit mode."""
        is_pad = self.fit_mode.get() == "pad"
        # try:
            # ttk state API
            # if is_pad:
                # self.pad_color_btn.state(["!disabled"])
            # else:
                # self.pad_color_btn.state(["disabled"])
        # except Exception:
            # Fallback for older Tk builds
            # self.pad_color_btn.configure(state=("normal" if is_pad else "disabled"))

    def _choose_pad_color(self):
        rgb, _ = colorchooser.askcolor(title="Pad color")
        if rgb is None:
            return
        # a = self.model.pad_color[3]
        # self.model.pad_color = (int(rgb[0]), int(rgb[1]), int(rgb[2]), a)
        self.preview.refresh()

    def _toggle_all_sizes(self, state=True):
        for v in self.size_vars.values():
            v.set(1 if state else 0)

    def _choose_output(self):
        suggested = self.model.output_path.get().strip()
        initdir = self.app.get_last_dir("save_ico") or (os.path.dirname(suggested) if suggested else None)
        initialfile = os.path.basename(suggested) if suggested else ""
        path = filedialog.asksaveasfilename(
            title="Save ICO",
            defaultextension=".ico",
            filetypes=[("Windows icon (.ico)", "*.ico")],
            initialdir=initdir,
            initialfile=initialfile
        )
        if path:
            self.model.output_path.set(path)
            try:
                self.app.set_last_dir("save_ico", os.path.dirname(path))
            except Exception:
                pass

    def _reveal_in_explorer(self, path: str):
        import os, subprocess
        try:
            p = os.path.normpath(path)
            if os.path.isfile(p):
                subprocess.Popen(["explorer", "/select,", p])
            else:
                # Fallback: open the directory itself
                folder = p if os.path.isdir(p) else os.path.dirname(p)
                if folder:
                    os.startfile(folder)
        except Exception as e:
            messagebox.showerror("Open Folder", f"Could not open Explorer:\n{e}")


    # ---- Export / Apply
    def _gather_sizes(self):
        picked = [n for n, v in self.size_vars.items() if v.get() == 1]
        custom = parse_custom_sizes(self.custom_sizes_str.get())
        return sorted(set(picked + custom))

    def _export(self):
        if self.model.loaded_img is None:
            self.app.toast("Open an image first.")
            return
        sizes = self._gather_sizes()
        if not sizes:
            self.app.toast("Select at least one size.")
            return
        out = self.model.output_path.get().strip()
        if not out:
            self.app.toast("Choose where to save the .ico file.")
            return

        # Pre-warn about upscaling
        try:
            sq = self._get_square_for_preview()
            if sq and sq.size[0] < max(sizes):
                self.app.toast("Warning: source smaller than largest size (will upscale).", duration_ms=4000)
        except Exception:
            pass

        def worker():
            try:
                create_multi_resolution_ico(
                    input_png_path=self.model.input_path.get(),
                    output_ico_path=out,
                    sizes=sizes,
                    fit_mode=self.fit_mode.get(),
                    # pad_rgba=self.model.pad_color if self.fit_mode.get() == "pad" else (0,0,0,0),
                    crop_center=(self.model.crop_cx, self.model.crop_cy) if self.fit_mode.get() == "crop" else None,
                    crop_zoom=self.model.crop_zoom if self.fit_mode.get() == "crop" else 1.0,
                )
            except Exception as e:
                self.after(0, lambda: self._show_banner("error", f"Export failed: {e}"))
                return

            # define a local callback that uses the closed-over 'out' and 'self'
            def _on_success():
                banner = self._show_banner("info", f"Saved: {os.path.basename(out)}")
                banner.add_action("Open Folder", lambda p=out: self._reveal_in_explorer(p))

            self.after(0, _on_success)

        threading.Thread(target=worker, daemon=True).start()

    # ---- Crop interactions (delegated to model)
    def _on_wheel(self, event):
        if self.fit_mode.get() != "crop" or self.model.loaded_img is None:
            return
        direction = 1 if getattr(event, "delta", 0) > 0 else -1
        factor = 1.1 if direction > 0 else (1/1.1)
        new_zoom = max(1.0, min(20.0, self.model.crop_zoom * factor))
        if new_zoom == self.model.crop_zoom:
            return

        w, h = self.model.loaded_img.size
        base = min(w, h)
        old_side = base / self.model.crop_zoom
        new_side = base / new_zoom

        cx_canvas = self.preview._preview_w / 2.0
        cy_canvas = self.preview._preview_h / 2.0
        mx = getattr(event, "x", cx_canvas)
        my = getattr(event, "y", cy_canvas)
        dx = mx - cx_canvas
        dy = my - cy_canvas

        img_x = self.model.crop_cx + dx * (old_side / self.preview._preview_side)
        img_y = self.model.crop_cy + dy * (old_side / self.preview._preview_side)

        self.model.crop_cx = img_x - dx * (new_side / self.preview._preview_side)
        self.model.crop_cy = img_y - dy * (new_side / self.preview._preview_side)
        self._clamp_center()
        self.model.crop_zoom = new_zoom
        self.preview.refresh()

    def _on_drag_start(self, event):
        if self.fit_mode.get() != "crop" or self.model.loaded_img is None:
            return
        self.model._drag_last = (event.x, event.y)

    def _on_drag_move(self, event):
        if self.fit_mode.get() != "crop" or self.model.loaded_img is None or self.model._drag_last is None:
            return
        dx = event.x - self.model._drag_last[0]
        dy = event.y - self.model._drag_last[1]
        self.model._drag_last = (event.x, event.y)

        side = self._current_crop_side()
        px_to_img = side / float(self.preview._preview_side)

        self.model.crop_cx -= dx * px_to_img
        self.model.crop_cy -= dy * px_to_img
        self._clamp_center()
        self.preview.refresh()

    def _on_drag_end(self, _):
        self.model._drag_last = None

    def _clamp_center(self):
        w, h = self.model.loaded_img.size
        side = self._current_crop_side()
        half = side / 2
        self.model.crop_cx = min(max(self.model.crop_cx, half), w - half)
        self.model.crop_cy = min(max(self.model.crop_cy, half), h - half)

    def _current_crop_side(self):
        w, h = self.model.loaded_img.size
        base = min(w, h)
        return max(1, int(round(base / max(1.0, self.model.crop_zoom))))

    # ---- Open helper used by App
    def open_path(self, path: str):
        try:
            # Probe animation
            is_anim = False
            try:
                _probe = Image.open(path)
                is_anim = bool(getattr(_probe, "is_animated", False))
                _probe.close()
            except Exception:
                pass

            self.model.loaded_img = load_image_as_rgba(path)
            w, h = self.model.loaded_img.size
            self.model.crop_zoom = 1.0
            self.model.crop_cx = w / 2
            self.model.crop_cy = h / 2
            self.model.input_path.set(path)
            self.model.output_path.set(os.path.splitext(path)[0] + ".ico")
            # keep last-dir for open-image in sync even when using DnD or Recent
            try:
                self.app.set_last_dir("open_image", os.path.dirname(path))
            except Exception:
                pass

            self.preview.refresh()
            if is_anim:
                self._show_banner("info", "Animated image detected — using the first frame.")
            else:
                self._clear_banners()

            # Persist to recents (covers DnD/Recent-open paths)
            self.app._add_recent(path)

        except Exception as e:
            messagebox.showerror("Open image failed", f"Could not open image:\n{e}")


    # ---- Banners
    def _clear_banners(self):
        for w in list(self.banner_area.children.values()):
            try:
                w.destroy()
            except Exception:
                pass

    def _show_banner(self, kind: str, text: str):
        # Clear any previous banner(s) for a clean, non-stacking UX
        self._clear_banners()
        b = Banner(self.banner_area, kind, text, on_close=self._clear_banners)
        b.pack(fill=tk.X, pady=(0, 0))
        return b

def _mkdelta(event, delta):
    class E: pass
    e = E()
    e.delta = delta
    e.x, e.y = event.x, event.y
    return e
