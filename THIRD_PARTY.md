# Third-Party Attributions

This project (pIcon) is MIT-licensed. It uses the following third-party components.

---

## Core runtime dependencies (bundled)

- **Pillow** — HPND (PIL license)  
  https://python-pillow.org

- **sv_ttk (Sun Valley ttk theme)** — MIT  
  https://github.com/rdbende/Sun-Valley-ttk-theme

- **pywinstyles** — MIT (Windows only)  
  https://github.com/Akascape/pywinstyles

- **Tkinter** — Python standard library (PSF license)  
  https://docs.python.org/3/library/tkinter.html

- **pi-heif (Python bindings to libheif)** — MIT  
  https://github.com/strukturag/pi-heif  
  **Note on transitive libraries:** pi-heif uses **libheif** (LGPL-3.0-or-later) and codec libraries under their own licenses.  
  - **libheif** — LGPL-3.0-or-later — https://github.com/strukturag/libheif  
  - Codec backends (e.g., libde265, aom, etc.) may be included depending on the wheel/build. Check the wheel’s bundled DLLs and upstream licenses.  

  **LGPL guidance (if you distribute HEIC support):**  
  - Prefer a **one-folder** PyInstaller build so the LGPL DLLs remain as separate files users can replace (“relink”) to comply with LGPL.  
  - Ship the corresponding **license texts** and provide a link to **source code** for the LGPL libraries you bundle (e.g., libheif).  
  - If you instead use a **one-file** build, be aware it unpacks to a temp dir at runtime; satisfying “user relinking” may be less straightforward. Consider switching to one-folder when distributing HEIC.

- **tkinterdnd2** — MIT (adds drag & drop)  
  https://github.com/pmgagne/tkinterdnd2

---

## Build-time tools (not bundled with the app)

- **PyInstaller** — GPL (with exception permitting distribution of frozen apps under any license)  
  https://www.pyinstaller.org  
  PyInstaller is used only to produce the executable. The GPL exception allows distributing your frozen application without subjecting your code to the GPL.

---

## System assets / fonts

- **Segoe UI / Segoe UI Variable** — Microsoft system fonts.  
  Used as **system-provided** fonts only; they are **not redistributed** in this project.

---

## Notes

- When distributing with optional HEIC support, include the appropriate **license files** for any LGPL/GPL/BSD libraries that come with the pi-heif wheel, and provide source locations for those libraries as required by their licenses.
