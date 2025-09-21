from transformers import pipeline

# Загружаем генеративную модель (лёгкая, чтобы шла даже на CPU)
# Можно заменить на более мощную, например "google/mt5-small" для мультиязычности
generator = pipeline("text2text-generation", model="facebook/blenderbot-400M-distill")


def generate_reply(comment_text: str, lang: str) -> str:
    """
    Генерация динамического ответа на комментарий.
    Язык определяется автоматически и влияет на стиль подсказки.
    """
    if lang == "kk":
        prompt = f"Жауап бер қазақ тілінде, қысқа әрі сыпайы түрде: {comment_text}"
    elif lang == "ru":
        prompt = f"Ответь на русском языке, вежливо и профессионально: {comment_text}"
    else:
        prompt = f"Answer in English politely and helpfully: {comment_text}"

    output = generator(prompt, max_length=80, num_return_sequences=1)
    return output[0]["generated_text"]
