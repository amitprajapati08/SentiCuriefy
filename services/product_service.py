# services/product_service.py
"""
Product/e-commerce sentiment analysis.
Takes multiple reviews, returns per-review + per-aspect breakdown.
"""
from services.nlp_service import analyze_sentiment

# ── Aspect keyword map ────────────────────────────────────────────
# Each aspect maps to keywords we scan for in each review
ASPECTS = {
    "quality":  ["quality", "build", "material", "durable", "sturdy",
                 "cheap", "flimsy", "broke", "excellent", "poor", "solid"],
    "price":    ["price", "cost", "worth", "value", "expensive", "cheap",
                 "affordable", "overpriced", "money", "budget"],
    "delivery": ["delivery", "shipping", "arrived", "package", "fast",
                 "slow", "delayed", "courier", "dispatch", "late", "quick"],
    "support":  ["support", "service", "helpdesk", "refund", "return",
                 "customer", "response", "staff", "team", "reply"],
    "design":   ["design", "look", "appearance", "color", "style",
                 "aesthetic", "beautiful", "ugly", "sleek", "compact"],
}

ASPECT_EMOJI = {
    "quality":  "🔧",
    "price":    "💰",
    "delivery": "📦",
    "support":  "🎧",
    "design":   "🎨",
}


def _detect_aspects(text: str) -> list:
    """Return list of aspects mentioned in this review."""
    text_lower = text.lower()
    found = []
    for aspect, keywords in ASPECTS.items():
        if any(kw in text_lower for kw in keywords):
            found.append(aspect)
    return found if found else ["general"]


def _star_rating(confidence: float, label: str) -> float:
    """Convert sentiment to a 1-5 star rating."""
    if label == "positive":
        return round(3.0 + (confidence / 100) * 2.0, 1)   # 3.0 - 5.0
    elif label == "neutral":
        return round(2.5 + (confidence / 100) * 0.5, 1)   # 2.5 - 3.0
    else:
        return round(2.5 - (confidence / 100) * 1.5, 1)   # 1.0 - 2.5


def _verdict(pos_pct: float, avg_stars: float) -> dict:
    """Generate a buy/skip/consider verdict with reasoning."""
    if pos_pct >= 70 and avg_stars >= 4.0:
        return {
            "label":   "Recommended",
            "icon":    "✅",
            "color":   "success",
            "reason":  f"{pos_pct:.0f}% positive reviews with avg {avg_stars} stars."
        }
    elif pos_pct <= 35 or avg_stars <= 2.5:
        return {
            "label":   "Not Recommended",
            "icon":    "❌",
            "color":   "danger",
            "reason":  f"Only {pos_pct:.0f}% positive reviews. Consider alternatives."
        }
    else:
        return {
            "label":   "Mixed Reviews",
            "icon":    "⚠️",
            "color":   "warning",
            "reason":  f"{pos_pct:.0f}% positive — check aspects before buying."
        }


def analyze_product_reviews(reviews_text: str) -> dict:
    """
    Main entry point.

    Args:
        reviews_text: raw string with one review per line

    Returns:
        {
          "reviews":        [ per-review analysis dicts ],
          "total":          int,
          "aspect_scores":  { aspect: {pos, neu, neg, count} },
          "overall_label":  "positive"|"neutral"|"negative",
          "avg_stars":      float,
          "pos_pct":        float,
          "verdict":        { label, icon, color, reason },
          "highlights":     { best, worst },
        }
    """
    # Split and clean — one review per line, skip blanks
    lines = [l.strip() for l in reviews_text.strip().splitlines() if l.strip()]

    if not lines:
        return {"error": "No reviews found. Enter one review per line."}

    # ── Analyze each review ───────────────────────────────────────
    analyzed = []
    for i, text in enumerate(lines, 1):
        s = analyze_sentiment(text)
        aspects = _detect_aspects(text)
        stars = _star_rating(s["confidence"], s["label"])
        analyzed.append({
            "index":      i,
            "text":       text,
            "label":      s["label"],
            "confidence": s["confidence"],
            "stars":      stars,
            "aspects":    aspects,
            "probabilities": s["probabilities"],
        })

    # ── Aspect breakdown ──────────────────────────────────────────
    aspect_scores = {a: {"positive": 0, "neutral": 0,
                         "negative": 0, "count": 0}
                     for a in list(ASPECTS.keys()) + ["general"]}

    for r in analyzed:
        for aspect in r["aspects"]:
            if aspect in aspect_scores:
                aspect_scores[aspect][r["label"]] += 1
                aspect_scores[aspect]["count"] += 1

    # Remove aspects with zero mentions
    aspect_scores = {k: v for k, v in aspect_scores.items() if v["count"] > 0}

    # Add percentage and emoji to each aspect
    for asp, data in aspect_scores.items():
        total = data["count"]
        data["pos_pct"] = round(data["positive"] / total * 100) if total else 0
        data["neg_pct"] = round(data["negative"] / total * 100) if total else 0
        data["neu_pct"] = round(data["neutral"]  / total * 100) if total else 0
        data["emoji"]   = ASPECT_EMOJI.get(asp, "📊")

    # ── Overall stats ─────────────────────────────────────────────
    total     = len(analyzed)
    pos_count = sum(1 for r in analyzed if r["label"] == "positive")
    neg_count = sum(1 for r in analyzed if r["label"] == "negative")
    neu_count = sum(1 for r in analyzed if r["label"] == "neutral")
    pos_pct   = round(pos_count / total * 100, 1)
    avg_stars = round(sum(r["stars"] for r in analyzed) / total, 1)

    # Overall label = whichever has the most
    counts = {"positive": pos_count, "neutral": neu_count, "negative": neg_count}
    overall_label = max(counts, key=counts.get)

    # ── Highlights ────────────────────────────────────────────────
    positives = [r for r in analyzed if r["label"] == "positive"]
    negatives = [r for r in analyzed if r["label"] == "negative"]

    best  = max(positives, key=lambda r: r["confidence"])["text"] if positives else None
    worst = max(negatives, key=lambda r: r["confidence"])["text"] if negatives else None

    return {
        "reviews":       analyzed,
        "total":         total,
        "pos_count":     pos_count,
        "neg_count":     neg_count,
        "neu_count":     neu_count,
        "pos_pct":       pos_pct,
        "neg_pct":       round(neg_count / total * 100, 1),
        "neu_pct":       round(neu_count / total * 100, 1),
        "aspect_scores": aspect_scores,
        "overall_label": overall_label,
        "avg_stars":     avg_stars,
        "verdict":       _verdict(pos_pct, avg_stars),
        "highlights":    {"best": best, "worst": worst},
    }
