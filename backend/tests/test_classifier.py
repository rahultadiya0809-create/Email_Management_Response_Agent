"""
Unit tests for the Email Classifier service.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.classifier import EmailClassifier


class TestEmailClassifier:
    """Tests for the EmailClassifier class."""

    def setup_method(self):
        self.classifier = EmailClassifier()

    def test_rule_based_urgent(self):
        """Test rule-based fallback classifies urgent emails."""
        text = "URGENT: Action required immediately. This is critical and time-sensitive."
        result = self.classifier._rule_based_classify(text)
        assert result["category"] == "urgent"
        assert result["confidence"] > 0.5

    def test_rule_based_promotional(self):
        """Test rule-based fallback classifies promotional emails."""
        text = "FLASH SALE! 50% discount on all items. Shop now and save big. Unsubscribe link below."
        result = self.classifier._rule_based_classify(text)
        assert result["category"] == "promotional"
        assert result["confidence"] > 0.5

    def test_rule_based_informational(self):
        """Test rule-based fallback classifies informational emails."""
        text = "Here are the meeting notes from today's standup discussion."
        result = self.classifier._rule_based_classify(text)
        assert result["category"] == "informational"

    def test_classify_returns_required_fields(self):
        """Test that classify returns all required fields."""
        text = "Please review this document at your earliest convenience."
        result = self.classifier.classify(text)
        assert "category" in result
        assert "confidence" in result
        assert "probabilities" in result
        assert result["category"] in ["urgent", "informational", "promotional"]

    def test_classify_empty_text(self):
        """Test classification of empty text."""
        result = self.classifier.classify("")
        assert "category" in result
        assert result["category"] in ["urgent", "informational", "promotional"]
