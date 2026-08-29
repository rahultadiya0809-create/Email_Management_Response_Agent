"""
Gmail API Integration Service.

Handles OAuth 2.0 authentication, email fetching, sending replies,
and archiving via the Gmail API.
"""

import os
import base64
import json
from email.mime.text import MIMEText
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config import Config


class GmailService:
    """Service class for Gmail API operations."""

    def __init__(self):
        self.creds = None
        self.service = None

    def authenticate(self, login_hint=""):
        """
        Authenticate with Gmail API using OAuth 2.0.

        First checks for an existing token. If not found or expired,
        initiates the OAuth flow using credentials.json.

        Args:
            login_hint: Optional email address to pre-fill in the Google
                        sign-in page.

        Returns:
            bool: True if authentication succeeded.
        """
        # Check for existing token
        if os.path.exists(Config.GMAIL_TOKEN_PATH):
            self.creds = Credentials.from_authorized_user_file(
                Config.GMAIL_TOKEN_PATH, Config.GMAIL_SCOPES
            )

        # If no valid credentials, authenticate
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(Config.GMAIL_CREDENTIALS_PATH):
                    raise FileNotFoundError(
                        f"Gmail credentials not found at {Config.GMAIL_CREDENTIALS_PATH}. "
                        "Download credentials.json from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    Config.GMAIL_CREDENTIALS_PATH, Config.GMAIL_SCOPES
                )
                # Pass login_hint so Google pre-fills the email address
                kwargs = {}
                if login_hint:
                    kwargs["login_hint"] = login_hint
                self.creds = flow.run_local_server(port=0, **kwargs)

            # Save the token for future runs
            with open(Config.GMAIL_TOKEN_PATH, "w") as token_file:
                token_file.write(self.creds.to_json())

        self.service = build("gmail", "v1", credentials=self.creds)
        return True

    def _ensure_service(self):
        """Ensure the Gmail API service is initialized."""
        if not self.service:
            self.authenticate()

    def fetch_emails(self, max_results=20, label="INBOX", query=""):
        """
        Fetch emails from the user's mailbox.

        Args:
            max_results: Maximum number of emails to fetch.
            label: Gmail label to filter by (e.g., 'INBOX', 'SPAM').
            query: Optional Gmail search query string.

        Returns:
            list: List of email dictionaries with metadata and body.
        """
        self._ensure_service()

        try:
            # Build the request
            request_params = {
                "userId": "me",
                "maxResults": max_results,
                "labelIds": [label],
            }
            if query:
                request_params["q"] = query

            results = self.service.users().messages().list(**request_params).execute()
            messages = results.get("messages", [])

            emails = []
            for msg in messages:
                email_data = self.get_email_detail(msg["id"])
                if email_data:
                    emails.append(email_data)

            return emails

        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []

    def get_email_detail(self, email_id):
        """
        Get full details of a single email.

        Args:
            email_id: The Gmail message ID.

        Returns:
            dict: Email data including headers, body, labels, and snippet.
        """
        self._ensure_service()

        try:
            message = (
                self.service.users()
                .messages()
                .get(userId="me", id=email_id, format="full")
                .execute()
            )

            headers = message.get("payload", {}).get("headers", [])
            header_dict = {}
            for header in headers:
                name = header["name"].lower()
                if name in ("from", "to", "subject", "date", "message-id"):
                    header_dict[name] = header["value"]

            # Extract body
            body = self._extract_body(message.get("payload", {}))

            # Parse date
            date_str = header_dict.get("date", "")
            try:
                # Try common date formats
                parsed_date = datetime.strptime(
                    date_str.split(" (")[0].strip(),
                    "%a, %d %b %Y %H:%M:%S %z",
                )
                date_iso = parsed_date.isoformat()
            except (ValueError, IndexError):
                date_iso = date_str

            return {
                "id": email_id,
                "thread_id": message.get("threadId", ""),
                "from": header_dict.get("from", "Unknown"),
                "to": header_dict.get("to", ""),
                "subject": header_dict.get("subject", "(No Subject)"),
                "date": date_iso,
                "snippet": message.get("snippet", ""),
                "body": body,
                "labels": message.get("labelIds", []),
                "is_read": "UNREAD" not in message.get("labelIds", []),
                "message_id": header_dict.get("message-id", ""),
            }

        except Exception as e:
            print(f"Error fetching email {email_id}: {e}")
            return None

    def _extract_body(self, payload):
        """
        Recursively extract the email body from the payload.
        Handles multipart emails, preferring plain text over HTML.

        Args:
            payload: The Gmail message payload.

        Returns:
            str: The decoded email body text.
        """
        body = ""

        if "body" in payload and payload["body"].get("data"):
            body = base64.urlsafe_b64decode(payload["body"]["data"]).decode(
                "utf-8", errors="replace"
            )
        elif "parts" in payload:
            # Prefer text/plain, fall back to text/html
            plain_text = ""
            html_text = ""
            for part in payload["parts"]:
                mime_type = part.get("mimeType", "")
                if mime_type == "text/plain" and part.get("body", {}).get("data"):
                    plain_text = base64.urlsafe_b64decode(
                        part["body"]["data"]
                    ).decode("utf-8", errors="replace")
                elif mime_type == "text/html" and part.get("body", {}).get("data"):
                    html_text = base64.urlsafe_b64decode(
                        part["body"]["data"]
                    ).decode("utf-8", errors="replace")
                elif "parts" in part:
                    # Nested multipart
                    body = self._extract_body(part)

            body = plain_text or html_text or body

        return body

    def send_reply(self, email_id, reply_text):
        """
        Send a reply to a specific email.

        Args:
            email_id: The original email's Gmail message ID.
            reply_text: The reply body text.

        Returns:
            dict: The sent message data, or None on failure.
        """
        self._ensure_service()

        try:
            # Get the original message for threading
            original = (
                self.service.users()
                .messages()
                .get(userId="me", id=email_id, format="metadata")
                .execute()
            )

            headers = original.get("payload", {}).get("headers", [])
            header_dict = {h["name"].lower(): h["value"] for h in headers}

            # Build the reply
            reply_to = header_dict.get("reply-to", header_dict.get("from", ""))
            subject = header_dict.get("subject", "")
            if not subject.lower().startswith("re:"):
                subject = f"Re: {subject}"

            message = MIMEText(reply_text)
            message["to"] = reply_to
            message["subject"] = subject
            message["In-Reply-To"] = header_dict.get("message-id", "")
            message["References"] = header_dict.get("message-id", "")

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

            sent_message = (
                self.service.users()
                .messages()
                .send(
                    userId="me",
                    body={
                        "raw": raw,
                        "threadId": original.get("threadId", ""),
                    },
                )
                .execute()
            )

            return sent_message

        except Exception as e:
            print(f"Error sending reply: {e}")
            return None

    def archive_email(self, email_id):
        """
        Archive an email by removing the INBOX label.

        Args:
            email_id: The Gmail message ID.

        Returns:
            bool: True if successful.
        """
        self._ensure_service()

        try:
            self.service.users().messages().modify(
                userId="me",
                id=email_id,
                body={"removeLabelIds": ["INBOX"]},
            ).execute()
            return True

        except Exception as e:
            print(f"Error archiving email {email_id}: {e}")
            return False

    def mark_as_read(self, email_id):
        """
        Mark an email as read by removing the UNREAD label.

        Args:
            email_id: The Gmail message ID.

        Returns:
            bool: True if successful.
        """
        self._ensure_service()

        try:
            self.service.users().messages().modify(
                userId="me",
                id=email_id,
                body={"removeLabelIds": ["UNREAD"]},
            ).execute()
            return True

        except Exception as e:
            print(f"Error marking email as read: {e}")
            return False

    def get_spam_emails(self, max_results=10):
        """
        Fetch emails marked as spam by Gmail's built-in filter.

        Args:
            max_results: Maximum number of spam emails to fetch.

        Returns:
            list: List of spam email dictionaries.
        """
        return self.fetch_emails(max_results=max_results, label="SPAM")

    def is_authenticated(self):
        """Check if the service is authenticated and ready."""
        return self.service is not None and self.creds is not None and self.creds.valid


# Singleton instance
gmail_service = GmailService()
