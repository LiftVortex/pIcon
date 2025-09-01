import os
from typing import Iterable, Optional, Tuple
from PIL import Image, ImageOps, ImageDraw, UnidentifiedImageError

# Optional HEIC/HEIF
try:
    import pi_heif  # type: ignore
except Exception:
    pi_heif = None  # type: ignore

RGBA = Tuple[int, int, int, int]

def load_image_as_rgba(path: str) -> Image.Image:
    """
    Open common image formats and return an RGBA image.
    - Uses pi-heif for .heic/.heif if available
    - Applies EXIF orientation
    - If animated (GIF/WEBP), uses the first frame
    """
    lower = path.lower()
    img = None

    if lower.endswith((".heic", ".heif")) and pi_heif is not None:
        img = _open_heif_as_pil(path)
    else:
        try:
            img = Image.open(path)
        except UnidentifiedImageError:
            if pi_heif is not None:
                img = _open_heif_as_pil(path)
            else:
                raise

    try:
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass

    if getattr(img, "is_animated", False):
        try:
            img.seek(0)
        except Exception:
            pass

    if img.mode != "RGBA":
        img = img.convert("RGBA")
    return img

def make_square(img: Image.Image, mode: str = "pad",
                pad_rgba: RGBA = (0, 0, 0, 0),
                crop_center: Optional[Tuple[float, float]] = None,
                crop_zoom: float = 1.0) -> Image.Image:
    """
    Returns a square version of img.
    - pad: centers on square RGBA canvas
    - crop: crops a square area; if crop_center/zoom provided, uses them
    - stretch: non-uniformly resizes to square
    """
    w, h = img.size
    if w == h and mode != "crop":
        return img

    if mode == "crop":
        cx = (w / 2) if (crop_center is None) else float(crop_center[0])
        cy = (h / 2) if (crop_center is None) else float(crop_center[1])
        zoom = max(1.0, float(crop_zoom) if crop_zoom else 1.0)

        base_side = min(w, h)
        crop_side = max(1, int(round(base_side / zoom)))
        half = crop_side / 2

        cx = min(max(cx, half), w - half)
        cy = min(max(cy, half), h - half)

        left = int(round(cx - half))
        top = int(round(cy - half))
        return img.crop((left, top, left + crop_side, top + crop_side))

    if mode == "stretch":
        side = max(w, h)
        return img.resize((side, side), Image.Resampling.LANCZOS)

    # pad
    side = max(w, h)
    canvas = Image.new("RGBA", (side, side), pad_rgba)
    canvas.paste(img, ((side - w) // 2, (side - h) // 2))
    return canvas

def create_multi_resolution_ico(input_png_path: str,
                                output_ico_path: str,
                                sizes: Iterable[int],
                                fit_mode: str = "pad",
                                pad_rgba: RGBA = (0, 0, 0, 0),
                                crop_center: Optional[Tuple[float, float]] = None,
                                crop_zoom: float = 1.0) -> None:
    """
    Safe, reusable function. Writes a multi-size .ico file.
    """
    sizes = sorted(set(int(s) for s in sizes))
    if not sizes:
        raise ValueError("No icon sizes specified.")
    if not os.path.isfile(input_png_path):
        raise FileNotFoundError(f"Input file not found: {input_png_path}")

    base = load_image_as_rgba(input_png_path)
    square = make_square(base, mode=fit_mode, pad_rgba=pad_rgba,
                         crop_center=crop_center, crop_zoom=crop_zoom)

    max_req = max(sizes)
    if square.width < max_req:
        square = square.resize((max_req, max_req), Image.Resampling.LANCZOS)

    size_pairs = [(n, n) for n in sizes]
    square.save(output_ico_path, format="ICO", sizes=size_pairs)

def _open_heif_as_pil(path: str) -> Image.Image:
    """Open a HEIC/HEIF image using pi-heif and return a PIL Image with ICC/EXIF when available."""
    if pi_heif is None:
        raise RuntimeError("HEIF/HEIC support requires 'pi-heif' (pip install pi-heif).")

    heif = pi_heif.read_heif(path)
    img = Image.frombytes(
        heif.mode, heif.size, heif.data, "raw", heif.mode, heif.stride
    )
    try:
        if getattr(heif, "color_profile", None) and "data" in heif.color_profile:
            img.info["icc_profile"] = heif.color_profile["data"]
        for md in getattr(heif, "metadata", []) or []:
            if md.get("type") == "Exif" and "data" in md:
                img.info["exif"] = md["data"]
                break
    except Exception:
        pass
    return img
