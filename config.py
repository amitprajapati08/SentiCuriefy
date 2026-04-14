# config.py
import os

class Config:
    # Database
    DB_PATH = os.getenv("DB_PATH", "sentiment_history.db")

    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "sentricureify-dev-key-change-in-prod")
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    # Sentiment thresholds
    POSITIVE_THRESHOLD = 0.6
    NEGATIVE_THRESHOLD = 0.4

    # History limit
    HISTORY_LIMIT = 150