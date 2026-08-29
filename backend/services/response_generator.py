"""
AI Response Generation Service.

Uses Google Gemini API to generate context-aware, professional
draft replies for classified emails.
"""

import google.generativeai as genai
from config import Config


class ResponseGenerator:
    """
    Generates AI-drafted email replies using Google Gemini API.
    Includes prompt engineering for professional, category-appropriate responses.
    """

    # Category-specific prompt instructions
    CATEGORY_PROMPTS = {
        "urgent": (
            "This is an URGENT email requiring immediate attention. "
            "Draft a prompt, professional reply that acknowledges the urgency, "
            "addresses the key points directly, and commits to a timeline or action."
        ),
        "informational": (
            "This is an informational email (update, notification, or FYI). "
            "Draft a brief, polite acknowledgment. Keep it concise — "
            "confirm receipt and mention any follow-up if needed."
        ),
        "promotional": (
            "This is a promotional/marketing email. "
            "Draft a polite but brief response if a reply is needed, "
            "or suggest that no reply is necessary."
        ),
    }

    def __init__(self):
        self.model = None
        self._initialize()

    def _initialize(self):
        """Initialize the Gemini API client."""
        if Config.GEMINI_API_KEY:
            try:
                genai.configure(api_key=Config.GEMINI_API_KEY)
                for model_name in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]:
                    try:
                        self.model = genai.GenerativeModel(model_name)
                        break
                    except Exception:
                        continue
                if self.model:
                    print("Gemini API initialized successfully.")
                else:
                    print("Could not initialize Gemini model.")
            except Exception as e:
                print(f"Error initializing Gemini API: {e}")
                self.model = None

    def generate_draft_reply(self, email_data, classification):
        """
        Generate an AI-drafted reply for an email.

        Args:
            email_data: Dict with 'from', 'subject', 'body', etc.
            classification: Dict with 'category' and 'confidence'.

        Returns:
            dict: Generated reply with 'draft_text', 'category_context',
                  and 'suggestions'.
        """
        category = classification.get("category", "informational")

        # Build the prompt
        prompt = self._build_prompt(email_data, category)

        # Try Gemini API first
        if self.model:
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=500,
                        top_p=0.9,
                    ),
                )
                draft_text = response.text.strip()

                return {
                    "draft_text": draft_text,
                    "category": category,
                    "generated_by": "gemini",
                    "editable": True,
                    "suggestions": self._get_suggestions(category),
                }

            except Exception as e:
                print(f"Gemini API error: {e}")

        # Fallback: template-based reply
        return self._template_reply(email_data, category)

    def _build_prompt(self, email_data, category):
        """
        Build a structured prompt for the LLM.

        Args:
            email_data: Email metadata and content.
            category: The email's classified category.

        Returns:
            str: The full prompt string.
        """
        sender = email_data.get("from", "the sender")
        subject = email_data.get("subject", "")
        body = email_data.get("body", "")

        # Truncate body if too long
        if len(body) > 2000:
            body = body[:2000] + "... [truncated]"

        category_instruction = self.CATEGORY_PROMPTS.get(
            category,
            "Draft a professional reply to this email.",
        )

        prompt = f"""You are an AI email assistant. Draft a professional reply to the following email.

INSTRUCTIONS:
{category_instruction}

RULES:
- Write ONLY the reply body (no subject line, no greeting header like "Subject: ...")
- Start with an appropriate greeting (e.g., "Hi [Name],")
- Keep the tone professional but warm
- Be concise — aim for 3-6 sentences
- Do NOT include placeholder text like [Your Name] — just end naturally
- Do NOT add email signatures

ORIGINAL EMAIL:
From: {sender}
Subject: {subject}
Body:
{body}

DRAFT REPLY:"""

        return prompt

    def _template_reply(self, email_data, category):
        """
        Generate a template-based reply when the AI API is unavailable.

        Args:
            email_data: Email metadata.
            category: Email category.

        Returns:
            dict: Template reply result.
        """
        sender_name = email_data.get("from", "").split("<")[0].strip()
        if not sender_name or "@" in sender_name:
            sender_name = "there"

        templates = {
            "urgent": (
                f"Hi {sender_name},\n\n"
                "Thank you for flagging this. I've noted the urgency and "
                "will address this as a priority. I'll get back to you with "
                "a detailed response shortly.\n\n"
                "Best regards"
            ),
            "informational": (
                f"Hi {sender_name},\n\n"
                "Thank you for the update. I've reviewed the information "
                "and will follow up if I have any questions.\n\n"
                "Best regards"
            ),
            "promotional": (
                f"Hi {sender_name},\n\n"
                "Thank you for reaching out. I've noted the details "
                "and will review them when convenient.\n\n"
                "Best regards"
            ),
        }

        draft_text = templates.get(category, templates["informational"])

        return {
            "draft_text": draft_text,
            "category": category,
            "generated_by": "template",
            "editable": True,
            "suggestions": self._get_suggestions(category),
        }

    def _get_suggestions(self, category):
        """
        Provide action suggestions based on the email category.

        Args:
            category: The email category.

        Returns:
            list: Suggested actions.
        """
        suggestions = {
            "urgent": [
                "Consider replying within the hour",
                "Check if any deadlines mentioned need calendar entries",
                "Flag for follow-up if action items are pending",
            ],
            "informational": [
                "Archive after reading if no action needed",
                "Star if you need to reference this later",
                "Forward to relevant team members if applicable",
            ],
            "promotional": [
                "Consider unsubscribing if not relevant",
                "No reply needed for most promotional emails",
                "Archive or delete to keep inbox clean",
            ],
        }
        return suggestions.get(category, suggestions["informational"])

    def is_available(self):
        """Check if the AI response generator is configured and ready."""
        return self.model is not None

    def reconfigure(self, api_key):
        """
        Reconfigure the Gemini API with a new key.

        Args:
            api_key: New Gemini API key.

        Returns:
            bool: True if reconfiguration succeeded.
        """
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-2.0-flash")
            return True
        except Exception as e:
            print(f"Error reconfiguring Gemini: {e}")
            return False


# Singleton instance
response_generator = ResponseGenerator()
