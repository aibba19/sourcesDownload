from urllib.parse import urlparse

VALID_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "youtu.be",
    "www.youtu.be",
}


def is_supported_youtube_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except ValueError:
        return False

    return parsed.scheme in {"http", "https"} and parsed.netloc.lower() in VALID_HOSTS
