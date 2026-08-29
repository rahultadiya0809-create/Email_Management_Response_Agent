"""
Unit tests for the Priority Scoring Engine.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.priority_engine import PriorityEngine


class TestPriorityEngine:
    """Tests for the PriorityEngine class."""

    def setup_method(self):
        self.engine = PriorityEngine()

    def test_high_priority_urgent_email(self):
        """Test that urgent emails with strong signals get high priority."""
        email_data = {
            "from": "professor@university.edu",
            "subject": "URGENT: Submit assignment by deadline today",
            "body": "This is critical. Submit your assignment immediately before the deadline.",
        }
        classification = {"category": "urgent", "confidence": 0.95}

        result = self.engine.calculate_priority(email_data, classification)
        assert result["score"] >= 0.65
        assert result["level"] in ("CRITICAL", "HIGH")

    def test_low_priority_promotional(self):
        """Test that promotional emails get low priority."""
        email_data = {
            "from": "noreply@shop.com",
            "subject": "50% off sale!",
            "body": "Buy now and save. Limited time offer.",
        }
        classification = {"category": "promotional", "confidence": 0.9}

        result = self.engine.calculate_priority(email_data, classification)
        assert result["score"] < 0.5
        assert result["level"] in ("LOW", "MEDIUM")

    def test_priority_result_fields(self):
        """Test that priority result contains all required fields."""
        email_data = {
            "from": "test@example.com",
            "subject": "Test email",
            "body": "This is a test.",
        }
        classification = {"category": "informational", "confidence": 0.7}

        result = self.engine.calculate_priority(email_data, classification)
        assert "score" in result
        assert "level" in result
        assert "level_info" in result
        assert "components" in result
        assert "deadlines" in result
        assert 0 <= result["score"] <= 1
        assert result["level"] in ("CRITICAL", "HIGH", "MEDIUM", "LOW")

    def test_known_contact_boost(self):
        """Test that known contacts get a sender score boost."""
        self.engine.add_known_contact("boss@company.com", 0.95)

        email_data = {
            "from": "Boss <boss@company.com>",
            "subject": "Review needed",
            "body": "Please review this document.",
        }
        classification = {"category": "informational", "confidence": 0.6}

        result = self.engine.calculate_priority(email_data, classification)
        assert result["components"]["sender_score"] == 0.95

    def test_keyword_score(self):
        """Test keyword scoring for urgency terms."""
        text = "URGENT: deadline today, action required immediately"
        score = self.engine._get_keyword_score(text)
        assert score >= 0.5

    def test_empty_text_handling(self):
        """Test handling of empty text in keyword scoring."""
        assert self.engine._get_keyword_score("") == 0.2
        assert self.engine._get_keyword_score(None) == 0.2
