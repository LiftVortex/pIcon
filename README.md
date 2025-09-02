# pIcon

A Windows desktop app that converts images (PNG/JPG/GIF/WEBP/HEIC/HEIF) into **multi-resolution `.ico`** files. It features a live preview with **Pad/Crop/Stretch** fit modes, size **chips** (16–256) plus custom sizes, a refined Win11-style UI (rounded cards, Mica/Acrylic backdrop), **dark/light themes**, and a simple CLI.

<img width="1208" height="821" alt="pIcon-UI" src="https://github.com/user-attachments/assets/aebf9e17-b078-4b84-8157-4f53b8000284" />

---

## Features

- **Formats:** PNG, JPG/JPEG, GIF/WEBP (first frame), BMP, TIFF, ICO
- **Pipeline:** EXIF orientation handled, normalized to RGBA, safe upscaling when needed
- **Fit modes:**  
  - **Pad**
  - **Crop** (interactive pan + wheel zoom)  
  - **Stretch**
- **Icon sizes:** one-click **chips** for 16–256 + custom field; **All / None**
- **Preview:** large hero preview with checkerboard that follows theme
- **Feedback:** non-blocking **toasts** + inline **banners**
- **UX polish:** rounded cards, soft depth, Win11 Mica/Acrylic backdrop
- **Theme:** Auto light/dark + manual toggle; bold color variants
- **Persistence:** “Recent files” list and **per-dialog last folder** memory
- **Keyboard shortcuts:**
  - **Ctrl+O** Open image
  - **Ctrl+S** Export ICO
  - **Ctrl+Shift+S** Save As…
  - **R** Reset crop
  - **+ / -** Zoom (when cropping)
  - **Arrow keys** Pan crop
  - **F11** Toggle maximize
  - **Ctrl+1 / Ctrl+2 / Ctrl+3** Pad / Crop / Stretch
  - **Alt+Up / Alt+Down** Navigate left-nav
- **CLI**: quick icon creation from terminal

---

## Install (dev)

```powershell
python -m venv .venv
. .\.venv\Scripts\activate
pip install -r requirements.txt
# Optional extras:
pip install pi-heif tkinterdnd2
```

- `pi-heif` enables **HEIC/HEIF** decoding.
- `tkinterdnd2` enables **drag & drop** (the app works without it).

---

## Run (GUI)

### From VS Code or terminal
```powershell
python run_app.py
```

### As a module (if you added `pIcon/__main__.py`)
```powershell
python -m pIcon
```

---

## Run (CLI)

```powershell
python -m pIcon.cli INPUT.png OUTPUT.ico ^
  --sizes 16,24,32,48,64,96,128,192,256 ^
  --fit pad ^
  --padrgb 0,0,0,0
```

**Args (parity with the original CLI):**
- positional: `input_png` `output_ico`
- `--sizes` comma/space list (valid 16–1024; Windows typically uses ≤256)
- `--fit` one of `pad|crop|stretch` (CLI crop uses centered crop)
- `--padrgb` `R,G,B,A` (e.g., `0,0,0,0` for transparent)

---

## Build (PyInstaller)

This repo includes a **one-file** spec that outputs a single portable EXE.

1) Install PyInstaller
```powershell
pip install pyinstaller
```

2) Clean & build (PowerShell)
```powershell
Remove-Item -Recurse -Force .\build, .\dist -ErrorAction SilentlyContinue
pyinstaller -y --clean pIcon_win11.spec
```

3) Run the packaged app:
```
dist\pIcon.exe
```

**Notes**
- The spec builds from `run_app.py` to keep package-relative imports valid.
- It bundles Pillow plugins, `sv_ttk`, and (if installed) `pi_heif` binaries automatically.
- If you prefer a **one-folder** build (easier debugging), use the earlier COLLECT-based spec or a CLI command instead.

---

## Customization

### Backdrop material (titlebar/window)
Open `pIcon/ui/theme.py` and set:
```python
BACKDROP_MODE = "mica"   # options: "mica" | "acrylic" | "dark" | "normal"
```
> Full “transparent” is not reliable with Tk; we map it to **acrylic** for stability.

### Color palette
Open `pIcon/ui/tokens.py`. Set:
```python
CURRENT_VARIANT = "cyberpunk"  # or "vaporwave" | "future_dusk" | "sunset_pop" | "midnight_lime"
```
Adjust any hex values you like.

### App icon (titlebar/taskbar)
Place an `.ico` at `pIcon/ui/app.ico` (multi-size recommended: 16–256).  
The app also has a PNG fallback from embedded assets.

---

## Troubleshooting

- **“attempted relative import with no known parent package”**  
  Always launch the GUI via `run_app.py` (or `python -m pIcon`). The spec already uses `run_app.py`.

- **No HEIC support**  
  Install `pi-heif`:
  ```powershell
  pip install pi-heif
  ```

- **Drag & drop missing**  
  Install `tkinterdnd2` (optional). If not present, DnD affordances are hidden; everything else works.

- **SmartScreen warning**  
  Unsigned EXEs may show a Windows warning. If you have a code-signing cert:
  ```powershell
  signtool sign /fd SHA256 /tr http://timestamp.sectigo.com /td SHA256 /a dist\pIcon.exe
  ```

- **Backdrop not visible / controls disappear**  
  Avoid `"transparent"` on Tk. Use `"mica"` or `"acrylic"`.

---

## Project layout (high level)

```
pIcon/
  core/
    images.py         # load/fit/export pipeline (EXIF, HEIC via pi_heif)
    sizes.py          # defaults & parsing
  ui/
    tokens.py         # design tokens (colors, radii, spacing)
    theme.py          # theme/backdrop; font scaling; system theme
    components.py     # Card, SegmentedControl, Chip, Banner, CommandBar, Nav
    preview.py        # PreviewCanvas (checkerboard + crop/zoom/pan)
    pages/
      page_icon_export.py   # main export page
      page_advanced.py      # metadata form (placeholder-ready)
      page_recent.py        # recent files
      page_settings.py      # theme/scaling settings
  cli.py              # CLI entry
run_app.py            # GUI entry (used by PyInstaller spec)
```

---

## License

This project is MIT-licensed. Dependencies are permissive:
- Tkinter (stdlib), Pillow (HPND), `sv_ttk` (MIT), `pywinstyles` (MIT)  
- Optional: `pi-heif` (MIT), `tkinterdnd2` (MIT)

If you add an optional Qt/PySide6 variant, note **PySide6 is LGPL** (dynamic linking and relinking must be allowed). The default Tkinter UI has **no LGPL obligations**.

---

## Tested

Windows 10 / 11, Python 3.10–3.12.  
If you hit an environment-specific quirk, feel free to file an issue with your Python & Windows build info.
