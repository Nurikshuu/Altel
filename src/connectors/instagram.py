import pandas as pd
import instaloader


def fetch_comments(shortcode: str, username: str, password: str, max_count: int = 100) -> pd.DataFrame:
    """
    Получает комментарии из Instagram поста с помощью Instaloader.
    Требуется действительный аккаунт (username/password).
    """
    loader = instaloader.Instaloader()
    loader.login(username, password)

    post = instaloader.Post.from_shortcode(loader.context, shortcode)
    rows = []

    for i, comment in enumerate(post.get_comments()):
        if i >= max_count:
            break
        rows.append(
            {
                "author": comment.owner.username if comment.owner else "",
                "text": comment.text or "",
                "published_at": comment.created_at_utc.isoformat(),
                "platform": "instagram",
            }
        )

    return pd.DataFrame(rows)
