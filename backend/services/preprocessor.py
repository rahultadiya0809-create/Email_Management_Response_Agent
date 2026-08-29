"""
Email Preprocessing Service.

Cleans raw email content by stripping HTML, removing signatures,
tokenizing text, detecting language, and extracting entities.
"""

import re
import html

from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download required NLTK data (runs once)
try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", quiet=True)

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords", quiet=True)


class EmailPreprocessor:
    """Preprocesses raw email content for classification and analysis."""

    # Common email signature indicators
    SIGNATURE_PATTERNS = [
        r"--\s*\n",                            # Standard delimiter
        r"(?i)^sent from my ",                 # Mobile signatures
        r"(?i)^best regards",
        r"(?i)^kind regards",
        r"(?i)^sincerely",
        r"(?i)^thanks and regards",
        r"(?i)^thank you",
        r"(?i)^cheers",
        r"(?i)^regards,",
        r"(?i)^warm regards",
    ]

    # Quoted reply patterns
    QUOTE_PATTERNS = [
        r"(?m)^>.*$",                          # Standard quoting
        r"(?m)^On .+ wrote:$",                 # Gmail quoted header
        r"(?i)-----\s*original message\s*-----", # Outlook style
        r"(?i)from:.*sent:.*to:.*subject:",    # Outlook forwarded header
    ]

    # Urgency keywords for feature extraction
    URGENCY_KEYWORDS = [
        "urgent", "asap", "immediately", "deadline", "critical",
        "important", "priority", "time-sensitive", "action required",
        "respond immediately", "due today", "overdue", "reminder",
        "final notice", "last chance", "expiring", "emergency",
    ]

    # Deadline-related regex patterns
    DEADLINE_PATTERNS = [
        r"(?i)by\s+(\w+\s+\d{1,2}(?:st|nd|rd|th)?(?:\s*,?\s*\d{4})?)",
        r"(?i)before\s+(\w+\s+\d{1,2}(?:st|nd|rd|th)?)",
        r"(?i)due\s+(?:on\s+)?(\w+\s+\d{1,2}(?:st|nd|rd|th)?(?:\s*,?\s*\d{4})?)",
        r"(?i)deadline[:\s]+(\w+\s+\d{1,2}(?:st|nd|rd|th)?(?:\s*,?\s*\d{4})?)",
        r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b",
    ]

    def __init__(self):
        self.stop_words = set(stopwords.words("english"))

    def clean_email(self, raw_text):
        """
        Full cleaning pipeline for raw email content.

        Steps:
        1. Strip HTML tags
        2. Decode HTML entities
        3. Remove email signatures
        4. Remove quoted replies
        5. Remove URLs
        6. Normalize whitespace

        Args:
            raw_text: Raw email body (may contain HTML).

        Returns:
            str: Cleaned plain text.
        """
        if not raw_text:
            return ""

        text = raw_text

        # Step 1: Strip HTML
        text = self._strip_html(text)

        # Step 2: Decode HTML entities
        text = html.unescape(text)

        # Step 3: Remove signatures
        text = self._remove_signatures(text)

        # Step 4: Remove quoted replies
        text = self._remove_quotes(text)

        # Step 5: Remove URLs
        text = re.sub(r"https?://\S+", "", text)
        text = re.sub(r"www\.\S+", "", text)

        # Step 6: Remove email addresses from body
        text = re.sub(r"\S+@\S+\.\S+", "", text)

        # Step 7: Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def _strip_html(self, text):
        """Remove HTML tags and extract text content."""
        if "<" in text and ">" in text:
            soup = BeautifulSoup(text, "html.parser")
            # Remove script and style elements
            for element in soup(["script", "style", "head"]):
                element.decompose()
            return soup.get_text(separator=" ")
        return text

    def _remove_signatures(self, text):
        """Remove email signatures from the text."""
        for pattern in self.SIGNATURE_PATTERNS:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                text = text[: match.start()]
        return text

    def _remove_quotes(self, text):
        """Remove quoted/forwarded content from replies."""
        for pattern in self.QUOTE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                text = text[: match.start()]
        return text

    def tokenize(self, text):
        """
        Tokenize text into words, removing stopwords and short tokens.

        Args:
            text: Cleaned text string.

        Returns:
            list: List of meaningful tokens.
        """
        if not text:
            return []

        tokens = word_tokenize(text.lower())
        # Keep only alphabetic tokens, remove stopwords, min length 2
        filtered = [
            token for token in tokens
            if token.isalpha()
            and token not in self.stop_words
            and len(token) > 2
        ]
        return filtered

    def detect_language(self, text):
        """
        Detect the language of the text.

        Args:
            text: Text to detect language of.

        Returns:
            str: Language code (e.g., 'en', 'hi', 'es').
        """
        try:
            from langdetect import detect
            return detect(text) if text.strip() else "en"
        except Exception:
            return "en"

    def extract_urgency_keywords(self, text):
        """
        Find urgency-related keywords in the text.

        Args:
            text: Cleaned email text.

        Returns:
            list: Found urgency keywords.
        """
        if not text:
            return []

        text_lower = text.lower()
        found = [kw for kw in self.URGENCY_KEYWORDS if kw in text_lower]
        return found

    def extract_deadlines(self, text):
        """
        Extract potential deadline dates from the text.

        Args:
            text: Cleaned email text.

        Returns:
            list: Extracted deadline strings.
        """
        if not text:
            return []

        deadlines = []
        for pattern in self.DEADLINE_PATTERNS:
            matches = re.findall(pattern, text)
            deadlines.extend(matches)

        return list(set(deadlines))

    def get_text_features(self, text):
        """
        Extract all features from text for classification and prioritization.

        Args:
            text: Raw or cleaned email text.

        Returns:
            dict: Feature dictionary with cleaned text, tokens, language,
                  urgency keywords, and deadlines.
        """
        cleaned = self.clean_email(text)
        return {
            "cleaned_text": cleaned,
            "tokens": self.tokenize(cleaned),
            "language": self.detect_language(cleaned),
            "urgency_keywords": self.extract_urgency_keywords(cleaned),
            "deadlines": self.extract_deadlines(cleaned),
            "word_count": len(cleaned.split()),
        }


# Singleton instance
preprocessor = EmailPreprocessor()
