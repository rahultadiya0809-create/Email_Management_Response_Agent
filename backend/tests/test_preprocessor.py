"""
Unit tests for the Email Preprocessor service.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.preprocessor import EmailPreprocessor


class TestEmailPreprocessor:
    """Tests for the EmailPreprocessor class."""

    def setup_method(self):
        self.preprocessor = EmailPreprocessor()

    def test_clean_plain_text(self):
        """Test cleaning plain text email."""
        text = "Hello John,\n\nPlease review the attached document.\n\nBest regards,\nJane"
        cleaned = self.preprocessor.clean_email(text)
        assert "Hello John" in cleaned
        assert "review" in cleaned
        # Signature should be removed
        assert "Best regards" not in cleaned

    def test_clean_html_email(self):
        """Test stripping HTML tags from email."""
        html = "<html><body><p>Hello <b>World</b></p><script>alert('x')</script></body></html>"
        cleaned = self.preprocessor.clean_email(html)
        assert "Hello" in cleaned
        assert "World" in cleaned
        assert "<" not in cleaned
        assert "script" not in cleaned

    def test_remove_urls(self):
        """Test URL removal."""
        text = "Check this out: https://example.com/page and www.test.com"
        cleaned = self.preprocessor.clean_email(text)
        assert "https://" not in cleaned
        assert "www." not in cleaned

    def test_tokenize(self):
        """Test tokenization with stopword removal."""
        text = "The urgent meeting is scheduled for today"
        tokens = self.preprocessor.tokenize(text)
        assert "urgent" in tokens
        assert "meeting" in tokens
        assert "the" not in tokens  # Stopword
        assert "is" not in tokens   # Stopword

    def test_extract_urgency_keywords(self):
        """Test urgency keyword extraction."""
        text = "URGENT: Please respond immediately to this critical matter."
        keywords = self.preprocessor.extract_urgency_keywords(text)
        assert "urgent" in keywords
        assert "immediately" in keywords
        assert "critical" in keywords

    def test_extract_deadlines(self):
        """Test deadline detection."""
        text = "Please submit by August 15, 2026. The deadline is 12/31/2026."
        deadlines = self.preprocessor.extract_deadlines(text)
        assert len(deadlines) >= 1

    def test_empty_input(self):
        """Test handling of empty input."""
        assert self.preprocessor.clean_email("") == ""
        assert self.preprocessor.clean_email(None) == ""
        assert self.preprocessor.tokenize("") == []
        assert self.preprocessor.extract_urgency_keywords("") == []

    def test_get_text_features(self):
        """Test full feature extraction pipeline."""
        text = "URGENT: Meeting deadline is tomorrow August 20th!"
        features = self.preprocessor.get_text_features(text)
        assert "cleaned_text" in features
        assert "tokens" in features
        assert "language" in features
        assert "urgency_keywords" in features
        assert "deadlines" in features
        assert "word_count" in features
        assert features["word_count"] > 0
