from typing import Dict, List, Set


def merge_unique(*lists: List[List[str]]) -> List[str]:
    seen: Set[str] = set()
    out: List[str] = []
    for lst in lists:
        for item in lst:
            key = item.strip().lower()
            if key not in seen:
                seen.add(key)
                out.append(item)
    return out


def clamp(val: float, low: float, high: float) -> float:
    return max(low, min(high, val))


def round_nearest(x: float, base: float = 5.0) -> float:
    return base * round(x / base)
