import os
import time
import logging
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline
from functools import lru_cache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Model config ──────────────────────────────────────────────────
# cardiffnlp is trained on 124M tweets — perfect for comments/reviews
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

# Ensemble weights: how much we trust each model
# Transformer = deep learned context, VADER = fast lexicon signal
TRANSFORMER_WEIGHT = 0.70
VADER_WEIGHT       = 0.30

# ── Load once at startup, NOT per request ─────────────────────────
# This is critical for performance — loading takes ~2s, inference is ~50ms
_transformer = None
_vader = SentimentIntensityAnalyzer()

def _load_transformer():
    global _transformer
    if _transformer is None:
        logger.info(f"Loading transformer model: {MODEL_NAME}")
        start = time.time()
        _transformer = pipeline(
            task="text-classification",
            model=MODEL_NAME,
            return_all_scores=True,   # gives us all 3 class probabilities
            truncation=True,
            max_length=512
        )
        logger.info(f"Model loaded in {time.time() - start:.1f}s")
    return _transformer


# ── Label normalization ───────────────────────────────────────────
# cardiffnlp returns: LABEL_0=negative, LABEL_1=neutral, LABEL_2=positive
LABEL_MAP = {
    "LABEL_0": "negative",
    "LABEL_1": "neutral",
    "LABEL_2": "positive",
    # Some model versions return these directly
    "negative": "negative",
    "neutral":  "neutral",
    "positive": "positive",
}


def _vader_to_probs(text):
    """
    Convert VADER compound score to a 3-class probability distribution.
    VADER gives: compound in [-1, 1]
    We map it to neg/neu/pos probabilities to blend with transformer output.
    """
    scores = _vader.polarity_scores(text)
    total = scores["neg"] + scores["neu"] + scores["pos"]
    if total == 0:
        return {"negative": 0.33, "neutral": 0.34, "positive": 0.33}
    return {
        "negative": scores["neg"] / total,
        "neutral":  scores["neu"] / total,
        "positive": scores["pos"] / total,
    }


def _transformer_to_probs(text):
    """
    Run transformer inference and normalize labels.
    Returns: {"negative": float, "neutral": float, "positive": float}
    """
    model = _load_transformer()
    raw = model(text)[0]   # list of {"label": ..., "score": ...}
    return {
        LABEL_MAP.get(item["label"], item["label"]): item["score"]
        for item in raw
    }


def _blend(t_probs, v_probs):
    """
    Weighted ensemble: 70% transformer + 30% VADER.
    Returns blended probabilities and the winning label.
    """
    blended = {}
    for label in ["negative", "neutral", "positive"]:
        blended[label] = round(
            TRANSFORMER_WEIGHT * t_probs.get(label, 0)
            + VADER_WEIGHT     * v_probs.get(label, 0),
            4
        )
    winner = max(blended, key=blended.get)
    confidence = round(blended[winner] * 100, 1)
    return winner, confidence, blended


def _confidence_to_grade(confidence):
    """Human-readable confidence level for the UI."""
    if confidence >= 85:
        return "very high"
    elif confidence >= 70:
        return "high"
    elif confidence >= 55:
        return "moderate"
    else:
        return "low"


# ── Public API ────────────────────────────────────────────────────

def analyze_sentiment(text: str) -> dict:
    """
    Main entry point. Takes raw text, returns rich analysis dict.

    Returns:
        {
            "label":        "positive" | "negative" | "neutral",
            "confidence":   87.3,           # percentage 0-100
            "grade":        "very high",
            "probabilities": {
                "positive": 0.873,
                "neutral":  0.089,
                "negative": 0.038
            },
            "vader_compound": 0.72,         # raw VADER for reference
            "model_used":    "ensemble",
            "word_count":    12,
            "char_count":    68,
        }
    """
    if not text or not text.strip():
        return {"error": "Empty text provided"}

    text = text.strip()

    # Run both models
    t_probs = _transformer_to_probs(text)
    v_probs = _vader_to_probs(text)
    vader_raw = _vader.polarity_scores(text)

    # Blend
    label, confidence, blended = _blend(t_probs, v_probs)

    return {
        "label":          label,
        "confidence":     confidence,
        "grade":          _confidence_to_grade(confidence),
        "probabilities":  blended,
        "vader_compound": round(vader_raw["compound"], 4),
        "model_used":     "ensemble (transformer 70% + VADER 30%)",
        "word_count":     len(text.split()),
        "char_count":     len(text),
    }


def analyze_batch(texts: list) -> list:
    """
    Analyze a list of texts. Used for CSV batch feature (Phase 2).
    Returns list of result dicts.
    """
    return [analyze_sentiment(t) for t in texts]
