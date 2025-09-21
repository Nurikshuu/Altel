from googleapiclient.discovery import build
import pandas as pd


def fetch_comments(api_key: str, video_id: str, max_results: int = 100) -> pd.DataFrame:
    """
    Получает комментарии с YouTube видео по API.
    Возвращает DataFrame с колонками author, text, published_at, platform.
    """
    youtube = build("youtube", "v3", developerKey=api_key)
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        textFormat="plainText",
        maxResults=min(max_results, 100),
    )
    response = request.execute()

    rows = []
    for item in response.get("items", []):
        snippet = item["snippet"]["topLevelComment"]["snippet"]
        rows.append(
            {
                "author": snippet.get("authorDisplayName", ""),
                "text": snippet.get("textDisplay", ""),
                "published_at": snippet.get("publishedAt", ""),
                "platform": "youtube",
            }
        )

    return pd.DataFrame(rows)
