pIcon — Third‑Party Licenses (bundle)

This folder contains license texts for all direct and optional dependencies used by pIcon.

Covered components
------------------
Required (installed per requirements.txt):
- Pillow — HPND (PIL license)
- sv_ttk — MIT
- pywinstyles — CC0 1.0 Universal (Public Domain Dedication)
- tkinterdnd2 — MIT (wrapper), bundling tkdnd binaries which are Public Domain per upstream
- Tkinter — Python stdlib (PSF) + Tcl/Tk license (for the underlying GUI toolkit)
- Python runtime — PSF 2.0 license

Optional (enable extra functionality if installed):
- pi-heif — MIT; the wheels bundle libheif (LGPL-3.0) and codec libs (e.g., libde265, LGPL-3.0)
- libheif — LGPL-3.0 (copy included here)
- libde265 — LGPL-3.0 (covered by LGPL-3.0 copy here)

How to use
----------
Keep this folder with your source distribution and ship it alongside the packaged EXE.
If you remove optional features (e.g., HEIF support), you may remove the corresponding files.

Sources
-------
See each file header for the source URL used.
