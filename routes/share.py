from flask import Blueprint, request, render_template
from services.nlp_service import analyze_sentiment
from services.emotion_service import detect_emotion
from models.database import save_share, get_community_shares

share_bp = Blueprint('share', __name__)

ADVICE = {
    ("positive", "work"):          "You're thriving at work! Keep that momentum going.",
    ("positive", "health"):        "Great to hear you're feeling well. Keep taking care of yourself.",
    ("positive", "relationships"): "Positive connections fuel everything. Cherish them.",
    ("positive", "finance"):       "Financial confidence is empowering. Stay consistent.",
    ("positive", "mental_health"): "You're in a good headspace. Acknowledge that win.",
    ("positive", "other"):         "Things seem to be going well. Hold onto that energy.",
    ("neutral",  "work"):          "Work feels balanced right now - a good time to plan ahead.",
    ("neutral",  "health"):        "Steady is good. Small habits compound into big results.",
    ("neutral",  "relationships"): "Neutral can mean stable. Sometimes that is exactly what is needed.",
    ("neutral",  "finance"):       "A calm moment financially - good time to review your goals.",
    ("neutral",  "mental_health"): "You're holding steady. Be gentle with yourself.",
    ("neutral",  "other"):         "Things feel even - use this calm to reflect.",
    ("negative", "work"):          "Work stress is real. Try breaking things into smaller steps today.",
    ("negative", "health"):        "Your health matters most. Please talk to someone you trust.",
    ("negative", "relationships"): "Relationships can be hard. It is okay to take space and breathe.",
    ("negative", "finance"):       "Financial pressure is heavy. One small step at a time helps.",
    ("negative", "mental_health"): "You are not alone in this. Reaching out takes courage - well done.",
    ("negative", "other"):         "Hard moments pass. You reached out, and that matters.",
}


@share_bp.route('/share', methods=['GET'])
def share():
    recent = get_community_shares(limit=6)
    return render_template('share.html', recent=recent)


@share_bp.route('/share', methods=['POST'])
def share_submit():
    name     = request.form.get('name', 'Anonymous').strip() or 'Anonymous'
    category = request.form.get('category', 'other')
    mood     = request.form.get('mood', 'okay')
    raw_text = request.form.get('text', '').strip()

    if not raw_text:
        return render_template('share.html',
                               error="Please write something before submitting.",
                               recent=get_community_shares(limit=6))

    # ── Analysis ───────────────────────────────────────────────────
    sentiment = analyze_sentiment(raw_text)
    emotion   = detect_emotion(sentiment)
    result    = {**sentiment, **emotion}

    # ── Save to DB ─────────────────────────────────────────────────
    try:
        save_share(
            name=name,
            category=category,
            mood=mood,
            text=raw_text,
            sentiment_score=sentiment["confidence"] / 100,
            sentiment=sentiment["label"],
        )
    except Exception:
        pass

    advice = ADVICE.get(
        (sentiment["label"], category),
        "Thank you for sharing. Your feelings are valid."
    )

    return render_template('share.html',
        submitted=True,
        name=name,
        category=category,
        mood=mood,
        raw_text=raw_text,
        result=result,
        advice=advice,
        recent=get_community_shares(limit=6)
    )