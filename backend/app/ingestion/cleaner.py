import re
from typing import Dict, Any, Tuple, Optional

def clean_string(val: Any) -> str:
    if val is None:
        return ""
    text = str(val).strip()
    return re.sub(r"\s+", " ", text)

def clean_price(val: Any) -> float:
    if val is None or val == "":
        return 0.0
    if isinstance(val, (int, float)):
        return max(0.0, float(val))
    # Remove currency symbols (₹, $, commas)
    clean_str = re.sub(r"[^\d.]", "", str(val))
    try:
        return max(0.0, float(clean_str)) if clean_str else 0.0
    except ValueError:
        return 0.0

def clean_rating(val: Any) -> float:
    try:
        r = float(val)
        return max(1.0, min(5.0, round(r + 1e-9, 1)))
    except (ValueError, TypeError):
        return 4.0

def clean_specifications(raw_specs: Any) -> Dict[str, Any]:
    """Clean and normalize category specifications."""
    if not isinstance(raw_specs, dict):
        return {}
    cleaned = {}
    for k, v in raw_specs.items():
        key = clean_string(k).lower().replace(" ", "_")
        if isinstance(v, (int, float, bool)):
            cleaned[key] = v
        else:
            cleaned[key] = clean_string(v)
    return cleaned
