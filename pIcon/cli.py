import sys
from .core.sizes import DEFAULT_SIZES, parse_custom_sizes
from .core.images import create_multi_resolution_ico

def _cli(args):
    import argparse
    p = argparse.ArgumentParser(description="Create a multi-resolution Windows .ico from an image (PNG/JPG/GIF/WEBP first frame/HEIC via pi-heif).")
    p.add_argument("input_png", help="Path to input image")
    p.add_argument("output_ico", help="Path to output .ico")
    p.add_argument("--sizes", default=",".join(map(str, DEFAULT_SIZES)),
                   help="Comma/space-separated sizes (e.g., 16,24,32,48,64,96,128,192,256)")
    p.add_argument("--fit", choices=["pad", "crop", "stretch"], default="pad")
    p.add_argument("--padrgb", default="0,0,0,0",
                   help="Pad RGBA color, e.g., 0,0,0,0 (transparent)")
    ns = p.parse_args(args)

    sizes = parse_custom_sizes(ns.sizes)
    if not sizes:
        print("No valid sizes provided.", file=sys.stderr)
        sys.exit(1)

    try:
        rgba = tuple(int(x) for x in ns.padrgb.split(","))
        if len(rgba) != 4:
            raise ValueError
    except Exception:
        print("padrgb must be R,G,B,A", file=sys.stderr)
        sys.exit(1)

    try:
        create_multi_resolution_ico(ns.input_png, ns.output_ico, sizes, fit_mode=ns.fit, pad_rgba=rgba)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    print(f"Saved {ns.output_ico}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        _cli(sys.argv[2:])
    else:
        from .ui.app import main
        main()
