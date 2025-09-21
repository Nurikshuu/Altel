import re
from typing import Optional
from urllib.parse import urlparse, parse_qs

# Поддерживаемые домены
YOUTUBE_HOSTS = {"www.youtube.com", "youtube.com", "youtu.be", "m.youtube.com"}
FACEBOOK_HOSTS = {"www.facebook.com", "facebook.com", "m.facebook.com"}
INSTAGRAM_HOSTS = {"www.instagram.com", "instagram.com"}


def extract_youtube_video_id(url: str) -> Optional[str]:
    """
    Извлекает ID видео из полной ссылки YouTube (поддержка watch, youtu.be, shorts, live, embed).
    """
    try:
        u = urlparse(url)
        host = u.netloc.lower()
        if host not in YOUTUBE_HOSTS:
            return None
        if host == "youtu.be":
            return u.path.lstrip("/") or None
        if u.path == "/watch":
            return parse_qs(u.query).get("v", [None])[0]
        parts = [p for p in u.path.split("/") if p]
        return parts[-1] if parts else None
    except Exception:
        return None


def extract_facebook_object_id(url: str) -> Optional[str]:
    """
    Возвращает URL или ID объекта Facebook.
    Для упрощения возвращаем исходный URL — Graph API сам разрешит его в ID.
    """
    u = urlparse(url)
    if u.netloc.lower() not in FACEBOOK_HOSTS:
        return None
    return url


def extract_instagram_shortcode(url: str) -> Optional[str]:
    """
    Извлекает shortcode поста Instagram из ссылки (поддержка /p/, /reel/, /tv/).
    """
    u = urlparse(url)
    if u.netloc.lower() not in INSTAGRAM_HOSTS:
        return None
    parts = [p for p in u.path.split("/") if p]
    if len(parts) >= 2:
        return parts[1]
    return None


def detect_platform(url: str) -> str:
    """
    Определяет платформу по домену URL: youtube, facebook, instagram или unknown.
    """
    host = urlparse(url).netloc.lower()
    if any(h in host for h in YOUTUBE_HOSTS):
        return "youtube"
    if any(h in host for h in FACEBOOK_HOSTS):
        return "facebook"
    if any(h in host for h in INSTAGRAM_HOSTS):
        return "instagram"
    return "unknown"
