from typing import Optional, Tuple


def parse_bp(bp_text: Optional[str]) -> Optional[Tuple[int, int]]:
    if not bp_text:
        return None
    try:
        if "/" in bp_text:
            s, d = bp_text.split("/", 1)
            return int(s.strip()), int(d.strip())
        parts = bp_text.split()
        if len(parts) == 2:
            return int(parts[0]), int(parts[1])
    except Exception:
        return None
    return None
