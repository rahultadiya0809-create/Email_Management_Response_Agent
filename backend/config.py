"""
Configuration module for the Email Management Agent backend.
Loads environment variables and provides centralized settings.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    HOST = os.getenv("FLASK_HOST", "127.0.0.1")
    PORT = int(os.getenv("FLASK_PORT", 5000))

    # Database
    DATABASE_PATH = os.getenv(
        "DATABASE_PATH",
        os.path.join(os.path.dirname(__file__), "email_agent.db"),
    )

    # Gmail API
    GMAIL_CREDENTIALS_PATH = os.getenv(
        "GMAIL_CREDENTIALS_PATH",
        os.path.join(os.path.dirname(__file__), "credentials.json"),
    )
    GMAIL_TOKEN_PATH = os.getenv(
        "GMAIL_TOKEN_PATH",
        os.path.join(os.path.dirname(__file__), "token.json"),
    )
    GMAIL_SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.modify",
    ]

    # Google Gemini API
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    # Telegram Notifications
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

    # Classification Model
    MODEL_PATH = os.getenv(
        "MODEL_PATH",
        os.path.join(os.path.dirname(__file__), "training", "trained_model.pkl"),
    )
    VECTORIZER_PATH = os.getenv(
        "VECTORIZER_PATH",
        os.path.join(os.path.dirname(__file__), "training", "tfidf_vectorizer.pkl"),
    )

    # Priority Scoring Weights
    CLASSIFIER_WEIGHT = float(os.getenv("CLASSIFIER_WEIGHT", "0.6"))
    SENDER_WEIGHT = float(os.getenv("SENDER_WEIGHT", "0.2"))
    KEYWORD_WEIGHT = float(os.getenv("KEYWORD_WEIGHT", "0.2"))

    # Frontend URL (for CORS)
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
