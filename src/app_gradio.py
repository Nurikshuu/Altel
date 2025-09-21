import io
import os
import gradio as gr
import pandas as pd
from dotenv import load_dotenv

from src.connectors.youtube import fetch_comments as yt_fetch
from src.connectors.facebook import fetch_comments as fb_fetch
from src.connectors.instagram import fetch_comments as ig_fetch

from src.pipelines import run_pipeline
from src.responder import generate_reply
from src.utils import (
    detect_platform,
    extract_youtube_video_id,
    extract_facebook_object_id,
    extract_instagram_shortcode,
)

# Загружаем переменные окружения
load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
IG_USERNAME = os.getenv("IG_USERNAME", "")
IG_PASSWORD = os.getenv("IG_PASSWORD", "")
MAX_COMMENTS = int(os.getenv("MAX_COMMENTS", "100"))


def analyze(platform: str, url: str):
    """
    Основная функция анализа комментариев.
    Определяет платформу, загружает комментарии, классифицирует и генерирует ответы.
    """
    try:
        if platform == "auto":
            platform = detect_platform(url)

        if platform == "youtube":
            vid = extract_youtube_video_id(url)
            if not vid:
                return None, "❌ Не удалось извлечь ID видео YouTube.", None
            df = yt_fetch(YOUTUBE_API_KEY, vid, MAX_COMMENTS)

        elif platform == "facebook":
            if not FACEBOOK_ACCESS_TOKEN:
                return None, "⚠ Требуется FACEBOOK_ACCESS_TOKEN в .env", None
            obj = extract_facebook_object_id(url)
            if not obj:
                return None, "❌ Неверная ссылка Facebook.", None
            df = fb_fetch(FACEBOOK_ACCESS_TOKEN, obj, MAX_COMMENTS)

        elif platform == "instagram":
            if not (IG_USERNAME and IG_PASSWORD):
                return None, "⚠ Требуются IG_USERNAME и IG_PASSWORD в .env", None
            sc = extract_instagram_shortcode(url)
            if not sc:
                return None, "❌ Неверная ссылка Instagram.", None
            df = ig_fetch(sc, IG_USERNAME, IG_PASSWORD, MAX_COMMENTS)

        else:
            return None, "❌ Неизвестная платформа.", None

        if df is None or df.empty:
            return None, "Комментариев не найдено.", None

        # Обрабатываем данные пайплайном
        df = run_pipeline(df)

        # Формируем предпросмотр и динамические ответы
        preview_rows = []
        for _, row in df.head(5).iterrows():
            reply_text = generate_reply(row["text"], row["language"])
            preview_rows.append(
                {
                    "text": row["text"][:140],
                    "тип": row["тип"],
                    "тональность": row["тональность"],
                    "toxicity": round(float(row["toxicity"]), 2),
                    "reply": reply_text,
                }
            )
        preview_df = pd.DataFrame(preview_rows)

        # Создаём Excel-отчёт
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="report")
        output.seek(0)

        return preview_df, "✅ Готово", ("report.xlsx", output)

    except Exception as e:
        return None, f"Ошибка: {e}", None


# --- Gradio UI ---
with gr.Blocks(title="Social AI Moderator") as demo:
    gr.Markdown("# 📊 Social AI Moderator — YouTube / Facebook / Instagram")
    with gr.Row():
        platform = gr.Dropdown(
            ["auto", "youtube", "facebook", "instagram"],
            value="auto",
            label="Платформа"
        )
        url = gr.Textbox(label="Ссылка на пост/видео")
        run_btn = gr.Button("Анализировать")

    status = gr.Markdown()
    table = gr.Dataframe(
        headers=["text", "тип", "тональность", "toxicity", "reply"],
        interactive=False
    )
    file = gr.File(label="Скачать отчёт (xlsx)")

    def _run(platform, url):
        table_df, msg, file_tuple = analyze(platform, url)
        file_obj = None
        if file_tuple:
            name, bio = file_tuple
            file_obj = gr.File.update(value=(name, bio))
        return table_df, msg, file_obj

    run_btn.click(_run, inputs=[platform, url], outputs=[table, status, file])

if __name__ == "__main__":
    demo.launch(share=True, server_port=7860)
  # share=True создаёт публичную ссылку
