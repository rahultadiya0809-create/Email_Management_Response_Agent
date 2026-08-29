"""
Telegram Notification Service.

Sends real-time push notifications to Telegram when high-priority
emails are detected.
"""

import requests
from config import Config


class NotificationService:
    """
    Sends alerts via the Telegram Bot API for high-priority emails.

    Setup:
    1. Create a bot via @BotFather on Telegram
    2. Get the bot token and your chat ID
    3. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env
    """

    TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}"

    # Priority level emoji mapping
    PRIORITY_EMOJI = {
        "CRITICAL": "🚨",
        "HIGH": "🔴",
        "MEDIUM": "🟡",
        "LOW": "🟢",
    }

    def __init__(self):
        self.bot_token = Config.TELEGRAM_BOT_TOKEN
        self.chat_id = Config.TELEGRAM_CHAT_ID

    def send_email_alert(self, email_data, classification, priority):
        """
        Send a Telegram notification for a high-priority email.

        Args:
            email_data: Dict with email metadata (from, subject, snippet).
            classification: Dict with category and confidence.
            priority: Dict with score and level from priority engine.

        Returns:
            bool: True if the notification was sent successfully.
        """
        if not self.is_configured():
            return False

        # Only notify for HIGH and CRITICAL priority
        level = priority.get("level", "LOW")
        if level not in ("CRITICAL", "HIGH"):
            return False

        message = self._format_alert(email_data, classification, priority)
        return self._send_telegram_message(message)

    def _format_alert(self, email_data, classification, priority):
        """
        Format the email data into a readable Telegram message.

        Args:
            email_data: Email metadata.
            classification: Classification result.
            priority: Priority result.

        Returns:
            str: Formatted message string.
        """
        level = priority.get("level", "MEDIUM")
        emoji = self.PRIORITY_EMOJI.get(level, "📧")
        score = priority.get("score", 0)
        category = classification.get("category", "unknown")

        sender = email_data.get("from", "Unknown")
        subject = email_data.get("subject", "(No Subject)")
        snippet = email_data.get("snippet", "")

        # Truncate snippet
        if len(snippet) > 200:
            snippet = snippet[:200] + "..."

        deadlines = priority.get("deadlines", [])
        deadline_text = (
            f"\n⏰ *Deadlines detected:* {', '.join(deadlines)}"
            if deadlines
            else ""
        )

        message = (
            f"{emoji} *{level} Priority Email*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📬 *From:* {sender}\n"
            f"📋 *Subject:* {subject}\n"
            f"🏷️ *Category:* {category.title()}\n"
            f"📊 *Priority Score:* {score:.0%}\n"
            f"{deadline_text}\n\n"
            f"💬 *Preview:*\n{snippet}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"_Open the dashboard to review and respond._"
        )

        return message

    def _send_telegram_message(self, message):
        """
        Send a message via the Telegram Bot API.

        Args:
            message: The message text to send.

        Returns:
            bool: True if successful.
        """
        try:
            url = f"{self.TELEGRAM_API_BASE.format(token=self.bot_token)}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True,
            }

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            result = response.json()
            return result.get("ok", False)

        except Exception as e:
            print(f"Telegram notification error: {e}")
            return False

    def send_daily_digest(self, email_summary):
        """
        Send a daily digest summary of email activity.

        Args:
            email_summary: Dict with counts by category and priority.

        Returns:
            bool: True if sent successfully.
        """
        if not self.is_configured():
            return False

        total = email_summary.get("total", 0)
        urgent = email_summary.get("urgent", 0)
        informational = email_summary.get("informational", 0)
        promotional = email_summary.get("promotional", 0)
        high_priority = email_summary.get("high_priority", 0)

        message = (
            "📊 *Daily Email Digest*\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"📬 Total Emails: *{total}*\n\n"
            f"🔴 Urgent: *{urgent}*\n"
            f"ℹ️ Informational: *{informational}*\n"
            f"📢 Promotional: *{promotional}*\n\n"
            f"⚡ High Priority: *{high_priority}*\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "_Open the dashboard for details._"
        )

        return self._send_telegram_message(message)

    def send_test_notification(self):
        """
        Send a test notification to verify the Telegram setup.

        Returns:
            bool: True if the test message was sent.
        """
        if not self.is_configured():
            return False

        message = (
            "✅ *Email Agent Connected!*\n\n"
            "Your Email Management Agent is now linked to this chat. "
            "You'll receive notifications for high-priority emails here."
        )
        return self._send_telegram_message(message)

    def is_configured(self):
        """Check if Telegram bot is properly configured."""
        return bool(self.bot_token) and bool(self.chat_id)

    def reconfigure(self, bot_token, chat_id):
        """
        Update Telegram bot configuration.

        Args:
            bot_token: New Telegram bot token.
            chat_id: New Telegram chat ID.
        """
        self.bot_token = bot_token
        self.chat_id = chat_id


# Singleton instance
notification_service = NotificationService()
