from typing import List

DEFAULT_SIZES: List[int] = [16, 24, 32, 48, 64, 96, 128, 192, 256]

def parse_custom_sizes(s: str) -> List[int]:
    """
    Parse comma/space-separated integers into a sorted unique list.
    Filters out values < 16 or > 1024 (ICO typically <= 256, but headroom allowed).
    """
    if not s or not s.strip():
        return []
    parts = [p.strip() for p in s.replace(",", " ").split()]
    out = []
    for p in parts:
        if not p.isdigit():
            continue
        v = int(p)
        if 16 <= v <= 1024:
            out.append(v)
    return sorted(set(out))
