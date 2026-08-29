"""
Priority Scoring Engine.

Combines ML classifier confidence with rule-based signals (sender
importance, urgency keywords, deadline detection) to produce a
composite priority score for each email.
"""

import re
from services.preprocessor import preprocessor
from config import Config


class PriorityEngine:
    """
    Hybrid priority scoring engine.

    Formula:
        priority = W1 × classifier_confidence + W2 × sender_score + W3 × keyword_score

    Priority Levels:
        CRITICAL: score >= 0.85
        HIGH:     score >= 0.65
        MEDIUM:   score >= 0.40
        LOW:      score < 0.40
    """

    PRIORITY_LEVELS = {
        "CRITICAL": {"min_score": 0.85, "color": "#ef4444", "icon": "🔴"},
        "HIGH":     {"min_score": 0.65, "color": "#f97316", "icon": "🟠"},
        "MEDIUM":   {"min_score": 0.40, "color": "#eab308", "icon": "🟡"},
        "LOW":      {"min_score": 0.00, "color": "#22c55e", "icon": "🟢"},
    }

    # Known important sender patterns (can be extended via settings)
    IMPORTANT_SENDER_PATTERNS = [
        r"(?i)\.edu$",        # Educational institutions
        r"(?i)\.gov$",        # Government
        r"(?i)boss",
        r"(?i)manager",
        r"(?i)director",
        r"(?i)professor",
        r"(?i)prof\.",
        r"(?i)dean",
        r"(?i)hod",
        r"(?i)principal",
    ]

    # Keywords that boost priority
    HIGH_PRIORITY_KEYWORDS = [
        "urgent", "asap", "immediately", "critical", "emergency",
        "action required", "time-sensitive", "deadline today",
        "respond immediately", "final notice", "overdue",
    ]

    MEDIUM_PRIORITY_KEYWORDS = [
        "important", "deadline", "reminder", "follow up", "follow-up",
        "due", "expiring", "meeting", "interview", "review",
        "submission", "assignment", "exam", "project",
    ]

    def __init__(self):
        self.known_contacts = {}  # email -> importance score

    def calculate_priority(self, email_data, classification):
        """
        Calculate the composite priority score for an email.

        Args:
            email_data: Dict with 'from', 'subject', 'body', etc.
            classification: Dict with 'category' and 'confidence' from classifier.

        Returns:
            dict: Priority result with score, level, and component breakdown.
        """
        # Component 1: Classifier confidence (weighted by category)
        classifier_score = self._get_classifier_score(classification)

        # Component 2: Sender importance
        sender_score = self._get_sender_score(email_data.get("from", ""))

        # Component 3: Keyword / content urgency
        text = f"{email_data.get('subject', '')} {email_data.get('body', '')}"
        keyword_score = self._get_keyword_score(text)

        # Composite score
        composite = (
            Config.CLASSIFIER_WEIGHT * classifier_score
            + Config.SENDER_WEIGHT * sender_score
            + Config.KEYWORD_WEIGHT * keyword_score
        )

        # Clamp to [0, 1]
        composite = max(0.0, min(1.0, composite))

        # Determine level
        level = self._score_to_level(composite)

        # Extract deadlines for extra context
        deadlines = preprocessor.extract_deadlines(text)

        return {
            "score": round(composite, 4),
            "level": level,
            "level_info": self.PRIORITY_LEVELS[level],
            "components": {
                "classifier_score": round(classifier_score, 4),
                "sender_score": round(sender_score, 4),
                "keyword_score": round(keyword_score, 4),
            },
            "deadlines": deadlines,
        }

    def _get_classifier_score(self, classification):
        """
        Convert classifier output to a priority-relevant score.
        Urgent emails get a boost; promotional gets penalized.
        """
        category = classification.get("category", "informational")
        confidence = classification.get("confidence", 0.5)

        if category == "urgent":
            return confidence * 1.0  # Full weight
        elif category == "informational":
            return confidence * 0.5  # Half weight
        elif category == "promotional":
            return confidence * 0.1  # Very low weight
        return 0.5

    def _get_sender_score(self, sender):
        """
        Score the sender's importance.

        Args:
            sender: The sender's email/name string (e.g., "John <john@example.com>").

        Returns:
            float: Score between 0 and 1.
        """
        if not sender:
            return 0.3

        sender_lower = sender.lower()

        # Check known contacts
        for email, score in self.known_contacts.items():
            if email in sender_lower:
                return score

        # Check important patterns
        for pattern in self.IMPORTANT_SENDER_PATTERNS:
            if re.search(pattern, sender_lower):
                return 0.9

        # Unknown first-time sender gets a moderate score
        return 0.4

    def _get_keyword_score(self, text):
        """
        Score based on urgency keywords found in the text.

        Args:
            text: Email subject + body text.

        Returns:
            float: Score between 0 and 1.
        """
        if not text:
            return 0.2

        text_lower = text.lower()

        # High priority keywords
        high_count = sum(
            1 for kw in self.HIGH_PRIORITY_KEYWORDS if kw in text_lower
        )

        # Medium priority keywords
        medium_count = sum(
            1 for kw in self.MEDIUM_PRIORITY_KEYWORDS if kw in text_lower
        )

        # Weighted score
        score = min(1.0, high_count * 0.25 + medium_count * 0.1)

        return score

    def _score_to_level(self, score):
        """Convert a numeric score to a priority level string."""
        if score >= 0.85:
            return "CRITICAL"
        elif score >= 0.65:
            return "HIGH"
        elif score >= 0.40:
            return "MEDIUM"
        else:
            return "LOW"

    def add_known_contact(self, email, importance=0.8):
        """
        Add a known contact with a custom importance score.

        Args:
            email: Contact email address.
            importance: Score between 0 and 1.
        """
        self.known_contacts[email.lower()] = importance

    def remove_known_contact(self, email):
        """Remove a contact from the known contacts list."""
        self.known_contacts.pop(email.lower(), None)


# Singleton instance
priority_engine = PriorityEngine()
