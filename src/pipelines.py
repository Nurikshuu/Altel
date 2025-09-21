from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from langdetect import detect
import torch
import pandas as pd

# Загружаем модели один раз
sentiment = pipeline("sentiment-analysis", model="cardiffnlp/twitter-xlm-roberta-base-sentiment")
zeroshot = pipeline("zero-shot-classification", model="joeddav/xlm-roberta-large-xnli")
_tox_tok = AutoTokenizer.from_pretrained("unitary/toxic-bert")
_tox_mod = AutoModelForSequenceClassification.from_pretrained("unitary/toxic-bert")

LABELS_TYPE = ["вопрос", "отзыв", "жалоба", "благодарность"]


def detect_lang_safe(text: str) -> str:
    try:
        lang = detect(text)
        return lang if lang in ("ru", "kk") else "mixed"
    except Exception:
        return "mixed"


def toxicity_score(text: str) -> float:
    inputs = _tox_tok(text, return_tensors="pt", truncation=True, max_length=256)
    with torch.no_grad():
        outputs = _tox_mod(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)
        return float(probs[0][1].item())  # 1 = токсичный


def classify_sentiment(text: str) -> str:
    label = sentiment(text[:512])[0]["label"]
    mapping = {"Positive": "позитивная", "Neutral": "нейтральная", "Negative": "негативная"}
    return mapping.get(label, "нейтральная")


def classify_type(text: str) -> str:
    result = zeroshot(text, candidate_labels=LABELS_TYPE, multi_label=False)
    return result["labels"][0]


def run_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    df["language"] = df["text"].apply(detect_lang_safe)
    df["toxicity"] = df["text"].apply(toxicity_score)
    df["is_toxic"] = df["toxicity"].apply(lambda x: x > 0.5)
    df["тональность"] = df["text"].apply(classify_sentiment)
    df["тип"] = df["text"].apply(classify_type)
    return df
