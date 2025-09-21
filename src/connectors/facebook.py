import requests
import pandas as pd

GRAPH = "https://graph.facebook.com/v18.0"


def fetch_comments(access_token: str, object_url_or_id: str, limit: int = 100) -> pd.DataFrame:
    """
    Получает комментарии из Facebook Graph API.
    Требуется действительный access token и ID поста или URL.
    """
    params = {
        "access_token": access_token,
        "fields": "from,message,created_time",
        "limit": min(limit, 100),
    }
    url = f"{GRAPH}/{object_url_or_id}/comments"

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()

    rows = []
    for item in data.get("data", []):
        rows.append(
            {
                "author": (item.get("from") or {}).get("name", ""),
                "text": item.get("message", ""),
                "published_at": item.get("created_time", ""),
                "platform": "facebook",
            }
        )

    return pd.DataFrame(rows)
