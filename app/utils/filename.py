import re

INVALID_CHARS_PATTERN = r'[<>:"/\\|?*]'


def sanitize_filename(name: str, replacement: str = "_") -> str:
    sanitized = re.sub(INVALID_CHARS_PATTERN, replacement, name).strip()
    sanitized = re.sub(r"\s+", " ", sanitized)
    return sanitized.rstrip(".") or "video"
