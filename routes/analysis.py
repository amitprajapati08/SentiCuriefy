from flask import Blueprint, request, render_template, jsonify, session
from services.nlp_service import analyze_sentiment
from services.emotion_service import detect_emotion
from models.database import add_to_history, get_user_history

analysis_bp = Blueprint("analysis", __name__)


@analysis_bp.route("/predict", methods=["GET", "POST"])
def predict():
    user_id  = session.get("user_id")
    history  = get_user_history(user_id, limit=10) if user_id else []

    if request.method == "GET":
        return render_template("predict.html", history=history)

    if request.is_json:
        text = request.json.get("text", "")
    else:
        text = request.form.get("text", "")

    if not text.strip():
        return render_template("predict.html",
                               error="Please enter some text.", history=history)

    sentiment = analyze_sentiment(text)
    emotion   = detect_emotion(sentiment)
    result    = {**sentiment, **emotion, "original_text": text}

    try:
        add_to_history(
            text=text,
            sentiment_score=sentiment["confidence"] / 100,
            sentiment=sentiment["label"],
            emotion=emotion["primary_emotion"],
            user_id=user_id,
        )
        # Refresh history after save
        if user_id:
            history = get_user_history(user_id, limit=10)
    except Exception:
        pass

    return render_template("predict.html", result=result, history=history)


@analysis_bp.route("/api/analyze", methods=["POST"])
def api_analyze():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    if not text.strip():
        return jsonify({"error": "text field required"}), 400
    sentiment = analyze_sentiment(text)
    emotion   = detect_emotion(sentiment)
    return jsonify({**sentiment, **emotion, "text": text})