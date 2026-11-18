import re
import html

def sanitize_text(text: str, max_length: int = 1000) -> str:
    """Sanitize arbitrary user text to prevent injection or malicious inputs."""
    if not text:
        return ""
    text = text.strip()[:max_length]
    # Escape dangerous HTML characters
    escaped = html.escape(text)
    # Remove control characters
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", escaped)
    return cleaned

def sanitize_query(query: str, max_length: int = 250) -> str:
    """Normalize and sanitize a natural language search query."""
    if not query:
        return ""
    # Strip dangerous shell characters or invalid SQL characters
    clean = re.sub(r"[\"\'`;\\]", " ", query)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean[:max_length]
