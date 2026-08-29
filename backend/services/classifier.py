"""
Email Classification Service.

Trains and uses a TF-IDF + Logistic Regression model to classify
emails into categories: urgent, informational, promotional.
"""

import os
import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline

from config import Config
from services.preprocessor import preprocessor


class EmailClassifier:
    """
    ML-based email classifier using TF-IDF features and Logistic Regression.

    Categories:
    - urgent: Time-sensitive, requires immediate action
    - informational: General updates, newsletters, FYI messages
    - promotional: Marketing, offers, advertisements
    """

    CATEGORIES = ["urgent", "informational", "promotional"]

    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.pipeline = None
        self._load_model()

    def _load_model(self):
        """Load a previously trained model if it exists."""
        if (
            os.path.exists(Config.MODEL_PATH)
            and os.path.exists(Config.VECTORIZER_PATH)
        ):
            try:
                self.model = joblib.load(Config.MODEL_PATH)
                self.vectorizer = joblib.load(Config.VECTORIZER_PATH)
                print("Loaded trained classification model.")
            except Exception as e:
                print(f"Error loading model: {e}")
                self.model = None
                self.vectorizer = None

    def train(self, data_path=None):
        """
        Train the classifier on labeled email data.

        Args:
            data_path: Path to a CSV file with columns 'text' and 'category'.

        Returns:
            dict: Training results including accuracy and classification report.
        """
        if data_path is None:
            data_path = os.path.join(
                os.path.dirname(__file__), "..", "training", "sample_data.csv"
            )

        # Load training data
        df = pd.read_csv(data_path)
        if "text" not in df.columns or "category" not in df.columns:
            raise ValueError("CSV must have 'text' and 'category' columns.")

        # Preprocess all texts
        df["cleaned_text"] = df["text"].apply(preprocessor.clean_email)

        X = df["cleaned_text"]
        y = df["category"]

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Build TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),   # Unigrams and bigrams
            min_df=2,
            max_df=0.95,
            sublinear_tf=True,
        )

        # Transform training data
        X_train_tfidf = self.vectorizer.fit_transform(X_train)
        X_test_tfidf = self.vectorizer.transform(X_test)

        # Train Logistic Regression
        self.model = LogisticRegression(
            max_iter=1000,
            C=1.0,
            class_weight="balanced",  # Handle class imbalance
            random_state=42,
        )
        self.model.fit(X_train_tfidf, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test_tfidf)
        accuracy = self.model.score(X_test_tfidf, y_test)
        report = classification_report(y_test, y_pred, output_dict=True)

        # Cross-validation
        cv_scores = cross_val_score(
            self.model, X_train_tfidf, y_train, cv=5, scoring="accuracy"
        )

        # Save model
        self.save_model()

        return {
            "accuracy": accuracy,
            "cv_mean_accuracy": cv_scores.mean(),
            "cv_std": cv_scores.std(),
            "classification_report": report,
        }

    def classify(self, text):
        """
        Classify a single email text.

        Args:
            text: Raw or cleaned email text.

        Returns:
            dict: Classification result with category, confidence, and all probabilities.
        """
        if self.model is None or self.vectorizer is None:
            # Return a rule-based fallback if no model is trained
            return self._rule_based_classify(text)

        # Clean and vectorize
        cleaned = preprocessor.clean_email(text)
        text_tfidf = self.vectorizer.transform([cleaned])

        # Predict
        category = self.model.predict(text_tfidf)[0]
        probabilities = self.model.predict_proba(text_tfidf)[0]

        # Build probability dict
        prob_dict = {}
        for i, cat in enumerate(self.model.classes_):
            prob_dict[cat] = round(float(probabilities[i]), 4)

        return {
            "category": category,
            "confidence": round(float(max(probabilities)), 4),
            "probabilities": prob_dict,
        }

    def _rule_based_classify(self, text):
        """
        Fallback rule-based classification when no ML model is available.

        Args:
            text: Email text to classify.

        Returns:
            dict: Classification result.
        """
        text_lower = text.lower() if text else ""

        # Check for urgent indicators
        urgent_keywords = [
            "urgent", "asap", "immediately", "deadline", "critical",
            "action required", "time-sensitive", "emergency", "due today",
        ]
        urgent_score = sum(1 for kw in urgent_keywords if kw in text_lower)

        # Check for promotional indicators
        promo_keywords = [
            "unsubscribe", "offer", "discount", "sale", "deal",
            "limited time", "buy now", "free trial", "promotion",
            "special offer", "click here", "shop now", "% off",
        ]
        promo_score = sum(1 for kw in promo_keywords if kw in text_lower)

        if urgent_score >= 2:
            category = "urgent"
            confidence = min(0.5 + urgent_score * 0.1, 0.9)
        elif promo_score >= 2:
            category = "promotional"
            confidence = min(0.5 + promo_score * 0.1, 0.9)
        else:
            category = "informational"
            confidence = 0.6

        return {
            "category": category,
            "confidence": confidence,
            "probabilities": {
                "urgent": confidence if category == "urgent" else 0.1,
                "informational": confidence if category == "informational" else 0.1,
                "promotional": confidence if category == "promotional" else 0.1,
            },
        }

    def save_model(self):
        """Save the trained model and vectorizer to disk."""
        if self.model and self.vectorizer:
            os.makedirs(os.path.dirname(Config.MODEL_PATH), exist_ok=True)
            joblib.dump(self.model, Config.MODEL_PATH)
            joblib.dump(self.vectorizer, Config.VECTORIZER_PATH)
            print(f"Model saved to {Config.MODEL_PATH}")

    def is_trained(self):
        """Check if a trained model is loaded."""
        return self.model is not None and self.vectorizer is not None


# Singleton instance
email_classifier = EmailClassifier()
