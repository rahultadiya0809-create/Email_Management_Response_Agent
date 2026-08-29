"""
Database module for the Email Management Agent.

Uses SQLite for local development. Provides CRUD operations
for emails, classifications, draft replies, and contacts.
"""

import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager

from config import Config


class Database:
    """SQLite database manager for the Email Management Agent."""

    def __init__(self, db_path=None):
        self.db_path = db_path or Config.DATABASE_PATH
        self._init_db()

    def _init_db(self):
        """Create database tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Emails table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emails (
                    id TEXT PRIMARY KEY,
                    thread_id TEXT,
                    sender TEXT NOT NULL,
                    recipient TEXT,
                    subject TEXT,
                    snippet TEXT,
                    body TEXT,
                    date TEXT,
                    labels TEXT,
                    is_read INTEGER DEFAULT 0,
                    category TEXT,
                    category_confidence REAL,
                    priority_score REAL,
                    priority_level TEXT,
                    priority_components TEXT,
                    deadlines TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Draft replies table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS draft_replies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email_id TEXT NOT NULL,
                    draft_text TEXT NOT NULL,
                    generated_by TEXT DEFAULT 'gemini',
                    category TEXT,
                    status TEXT DEFAULT 'draft',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (email_id) REFERENCES emails(id)
                )
            """)

            # Known contacts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT,
                    importance REAL DEFAULT 0.5,
                    interaction_count INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Email activity log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email_id TEXT,
                    action TEXT NOT NULL,
                    details TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    @contextmanager
    def _get_connection(self):
        """Get a database connection as a context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    # ─── Email Operations ──────────────────────────────────────────

    def save_email(self, email_data, classification=None, priority=None):
        """
        Save or update an email record.

        Args:
            email_data: Dict with email fields.
            classification: Optional classification result.
            priority: Optional priority result.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            category = classification.get("category") if classification else None
            confidence = classification.get("confidence") if classification else None
            p_score = priority.get("score") if priority else None
            p_level = priority.get("level") if priority else None
            p_components = (
                json.dumps(priority.get("components")) if priority else None
            )
            deadlines = (
                json.dumps(priority.get("deadlines")) if priority else None
            )

            cursor.execute("""
                INSERT OR REPLACE INTO emails
                (id, thread_id, sender, recipient, subject, snippet, body, date,
                 labels, is_read, category, category_confidence, priority_score,
                 priority_level, priority_components, deadlines, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                email_data.get("id"),
                email_data.get("thread_id"),
                email_data.get("from"),
                email_data.get("to"),
                email_data.get("subject"),
                email_data.get("snippet"),
                email_data.get("body"),
                email_data.get("date"),
                json.dumps(email_data.get("labels", [])),
                1 if email_data.get("is_read") else 0,
                category,
                confidence,
                p_score,
                p_level,
                p_components,
                deadlines,
                datetime.utcnow().isoformat(),
            ))

            conn.commit()

    def get_emails(self, limit=50, offset=0, category=None, priority_level=None):
        """
        Fetch emails with optional filters.

        Args:
            limit: Max number of emails to return.
            offset: Pagination offset.
            category: Filter by category.
            priority_level: Filter by priority level.

        Returns:
            list: List of email dicts.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM emails WHERE 1=1"
            params = []

            if category:
                query += " AND category = ?"
                params.append(category)
            if priority_level:
                query += " AND priority_level = ?"
                params.append(priority_level)

            query += " ORDER BY priority_score DESC, date DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [self._row_to_dict(row) for row in rows]

    def get_email(self, email_id):
        """
        Get a single email by ID.

        Args:
            email_id: The email ID.

        Returns:
            dict or None: Email data.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM emails WHERE id = ?", (email_id,))
            row = cursor.fetchone()
            return self._row_to_dict(row) if row else None

    # ─── Draft Reply Operations ────────────────────────────────────

    def save_draft_reply(self, email_id, draft_text, generated_by="gemini", category=None):
        """Save a draft reply for an email."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO draft_replies (email_id, draft_text, generated_by, category)
                VALUES (?, ?, ?, ?)
            """, (email_id, draft_text, generated_by, category))
            conn.commit()
            return cursor.lastrowid

    def get_draft_reply(self, email_id):
        """Get the latest draft reply for an email."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM draft_replies
                WHERE email_id = ?
                ORDER BY created_at DESC LIMIT 1
            """, (email_id,))
            row = cursor.fetchone()
            return self._row_to_dict(row) if row else None

    def update_draft_status(self, draft_id, status):
        """Update draft reply status (draft/approved/sent/discarded)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE draft_replies
                SET status = ?, updated_at = ?
                WHERE id = ?
            """, (status, datetime.utcnow().isoformat(), draft_id))
            conn.commit()

    # ─── Contact Operations ────────────────────────────────────────

    def save_contact(self, email, name=None, importance=0.5):
        """Add or update a known contact."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO contacts (email, name, importance)
                VALUES (?, ?, ?)
                ON CONFLICT(email) DO UPDATE SET
                    name = COALESCE(?, name),
                    importance = ?,
                    interaction_count = interaction_count + 1
            """, (email, name, importance, name, importance))
            conn.commit()

    def get_contacts(self):
        """Get all known contacts."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts ORDER BY importance DESC")
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]

    # ─── Settings Operations ───────────────────────────────────────

    def get_setting(self, key, default=None):
        """Get a setting value."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row["value"] if row else default

    def set_setting(self, key, value):
        """Set a setting value."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
            """, (key, value, datetime.utcnow().isoformat()))
            conn.commit()

    # ─── Statistics ────────────────────────────────────────────────

    def get_stats(self):
        """Get email statistics for the dashboard."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            # Total emails
            cursor.execute("SELECT COUNT(*) as count FROM emails")
            stats["total_emails"] = cursor.fetchone()["count"]

            # By category
            cursor.execute("""
                SELECT category, COUNT(*) as count
                FROM emails
                WHERE category IS NOT NULL
                GROUP BY category
            """)
            stats["by_category"] = {
                row["category"]: row["count"] for row in cursor.fetchall()
            }

            # By priority
            cursor.execute("""
                SELECT priority_level, COUNT(*) as count
                FROM emails
                WHERE priority_level IS NOT NULL
                GROUP BY priority_level
            """)
            stats["by_priority"] = {
                row["priority_level"]: row["count"] for row in cursor.fetchall()
            }

            # Unread count
            cursor.execute("SELECT COUNT(*) as count FROM emails WHERE is_read = 0")
            stats["unread"] = cursor.fetchone()["count"]

            # Draft replies pending
            cursor.execute(
                "SELECT COUNT(*) as count FROM draft_replies WHERE status = 'draft'"
            )
            stats["pending_drafts"] = cursor.fetchone()["count"]

            return stats

    # ─── Activity Log ──────────────────────────────────────────────

    def log_activity(self, email_id, action, details=None):
        """Log an activity (classify, reply, archive, etc.)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO activity_log (email_id, action, details)
                VALUES (?, ?, ?)
            """, (email_id, action, details))
            conn.commit()

    def get_recent_activity(self, limit=20):
        """Get recent activity log entries."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM activity_log
                ORDER BY created_at DESC LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]

    # ─── Helpers ───────────────────────────────────────────────────

    def _row_to_dict(self, row):
        """Convert a sqlite3.Row to a plain dictionary."""
        if row is None:
            return None
        d = dict(row)
        # Parse JSON fields
        for key in ("labels", "priority_components", "deadlines"):
            if key in d and d[key]:
                try:
                    d[key] = json.loads(d[key])
                except (json.JSONDecodeError, TypeError):
                    pass
        return d


# Singleton instance
db = Database()




