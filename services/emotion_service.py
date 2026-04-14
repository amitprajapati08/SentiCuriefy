"""
Emotion service — maps sentiment analysis output to human emotions.
Uses both the final label AND probability distribution for nuance.
"""

# Primary emotion map — what each label most likely signals
LABEL_TO_EMOTIONS = {
    "positive": ["joy", "trust", "anticipation"],
    "neutral":  ["calm", "curiosity", "contemplation"],
    "negative": ["frustration", "sadness", "anger"],
}

# Intensity bands — confidence shapes the emotion word we choose
INTENSITY_MAP = {
    "positive": {
        "very high": "excitement",
        "high":      "happiness",
        "moderate":  "satisfaction",
        "low":       "mild positivity",
    },
    "neutral": {
        "very high": "objectivity",
        "high":      "calmness",
        "moderate":  "ambivalence",
        "low":       "uncertainty",
    },
    "negative": {
        "very high": "strong dissatisfaction",
        "high":      "frustration",
        "moderate":  "disappointment",
        "low":       "mild concern",
    },
}

# Emoji map for UI display
EMOTION_EMOJI = {
    "excitement":              "🔥",
    "happiness":               "😊",
    "satisfaction":            "👍",
    "mild positivity":         "🙂",
    "objectivity":             "📊",
    "calmness":                "😌",
    "ambivalence":             "😐",
    "uncertainty":             "🤔",
    "strong dissatisfaction":  "😤",
    "frustration":             "😠",
    "disappointment":          "😞",
    "mild concern":            "😕",
}


def detect_emotion(sentiment_result: dict) -> dict:
    """
    Takes the output of nlp_service.analyze_sentiment() and returns
    a richer emotion analysis.

    Returns:
        {
            "primary_emotion": "happiness",
            "emoji":           "😊",
            "emotion_tags":    ["joy", "trust", "anticipation"],
            "tone":            "warm and enthusiastic",
        }
    """
    label      = sentiment_result.get("label", "neutral")
    grade      = sentiment_result.get("grade", "moderate")
    probs      = sentiment_result.get("probabilities", {})

    primary_emotion = INTENSITY_MAP.get(label, {}).get(grade, label)
    emotion_tags    = LABEL_TO_EMOTIONS.get(label, ["calm"])
    emoji           = EMOTION_EMOJI.get(primary_emotion, "💬")

    # Detect mixed signal: if 2nd highest prob is > 0.30, flag it
    sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
    mixed = False
    mixed_note = ""
    if len(sorted_probs) >= 2 and sorted_probs[1][1] > 0.30:
        mixed = True
        mixed_note = (
            f"Mixed signal detected — strong {sorted_probs[1][0]} undertone "
            f"({round(sorted_probs[1][1]*100, 1)}%)"
        )

    tone = _build_tone(label, grade, mixed)

    return {
        "primary_emotion": primary_emotion,
        "emoji":           emoji,
        "emotion_tags":    emotion_tags,
        "tone":            tone,
        "mixed_signal":    mixed,
        "mixed_note":      mixed_note,
    }


def _build_tone(label, grade, mixed):
    base = {
        ("positive", "very high"): "enthusiastic and confident",
        ("positive", "high"):      "warm and positive",
        ("positive", "moderate"):  "generally positive",
        ("positive", "low"):       "slightly positive",
        ("neutral",  "very high"): "factual and objective",
        ("neutral",  "high"):      "balanced and calm",
        ("neutral",  "moderate"):  "somewhat neutral",
        ("neutral",  "low"):       "unclear tone",
        ("negative", "very high"): "strongly critical",
        ("negative", "high"):      "frustrated or disappointed",
        ("negative", "moderate"):  "mildly negative",
        ("negative", "low"):       "slightly concerned",
    }.get((label, grade), "neutral tone")

    if mixed:
        base += " with mixed undertones"
    return base
