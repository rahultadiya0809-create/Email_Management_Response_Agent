"""
Email Management and Response Agent — Flask Backend

Main application file with REST API endpoints for:
- Gmail OAuth authentication
- Email fetching, classification, and prioritization
- AI draft reply generation
- Reply approval and sending
- Dashboard statistics
- Settings management
"""

import os
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
from flask import Flask, request, jsonify, redirect, session
from flask_cors import CORS

from config import Config
from models.database import db
from services.gmail_service import gmail_service
from services.preprocessor import preprocessor
from services.classifier import email_classifier
from services.priority_engine import priority_engine
from services.response_generator import response_generator
from services.notification import notification_service


# ─── App Initialization ──────────────────────────────────────────

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

CORS(app, resources={r"/api/*": {"origins": Config.FRONTEND_URL}})


# ─── Health Check ─────────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "services": {
            "gmail": gmail_service.is_authenticated(),
            "classifier": email_classifier.is_trained(),
            "gemini": response_generator.is_available(),
            "telegram": notification_service.is_configured(),
        },
    })


# ─── Authentication ──────────────────────────────────────────────

@app.route("/api/auth/status", methods=["GET"])
def auth_status():
    """Check Gmail authentication status."""
    return jsonify({
        "authenticated": gmail_service.is_authenticated(),
    })


@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    """
    Check if already authenticated (existing token).
    If yes, return success. If no, return needs_auth=true.
    """
    try:
        # Try to authenticate with existing token
        if os.path.exists(Config.GMAIL_TOKEN_PATH):
            gmail_service.authenticate()
            if gmail_service.is_authenticated():
                return jsonify({
                    "success": True,
                    "message": "Already authenticated.",
                })

        return jsonify({
            "success": False,
            "needs_auth": True,
            "message": "Authentication required.",
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "needs_auth": True,
            "error": str(e),
        })


@app.route("/api/auth/url", methods=["POST"])
def auth_get_url():
    """
    Generate and return the Google OAuth authorization URL.
    The frontend opens this in a popup window.
    """
    try:
        data = request.get_json() or {}
        email = data.get("email", "")

        if not os.path.exists(Config.GMAIL_CREDENTIALS_PATH):
            return jsonify({
                "success": False,
                "error": "Gmail credentials not found. Place credentials.json in the backend/ directory.",
            }), 400

        from google_auth_oauthlib.flow import Flow

        flow = Flow.from_client_secrets_file(
            Config.GMAIL_CREDENTIALS_PATH,
            scopes=Config.GMAIL_SCOPES,
            redirect_uri="http://localhost:5000/api/auth/callback",
        )

        auth_url, state = flow.authorization_url(
            access_type="offline",
            prompt="consent",
            login_hint=email if email else None,
        )

        # Store state in session for verification
        session["oauth_state"] = state

        return jsonify({
            "success": True,
            "auth_url": auth_url,
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
        }), 500


@app.route("/api/auth/callback")
def auth_callback():
    """
    Handle the OAuth callback from Google.
    Exchanges the authorization code for tokens, saves them,
    and returns an HTML page that auto-closes the popup.
    """
    try:
        code = request.args.get("code")
        error = request.args.get("error")

        if error:
            return f"""
            <html>
            <body style="font-family: 'Inter', sans-serif; display:flex; align-items:center;
                         justify-content:center; min-height:100vh; background:#f8f9fc; color:#1a1d2e; text-align:center;">
                <div>
                    <h2 style="color:#e11d48;">Authentication Failed</h2>
                    <p style="color:#5a6178;">Error: {error}</p>
                    <p style="color:#8d94a8;">You can close this window.</p>
                </div>
            </body>
            </html>
            """, 400

        if not code:
            return "Missing authorization code.", 400

        from google_auth_oauthlib.flow import Flow

        flow = Flow.from_client_secrets_file(
            Config.GMAIL_CREDENTIALS_PATH,
            scopes=Config.GMAIL_SCOPES,
            redirect_uri="http://localhost:5000/api/auth/callback",
        )

        flow.fetch_token(code=code)
        creds = flow.credentials

        # Save the token
        with open(Config.GMAIL_TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())

        # Initialize the gmail service
        gmail_service.creds = creds
        from googleapiclient.discovery import build
        gmail_service.service = build("gmail", "v1", credentials=creds)

        # Return HTML that notifies the opener and closes the popup
        return """
        <html>
        <body style="font-family: 'Inter', sans-serif; display:flex; align-items:center;
                     justify-content:center; min-height:100vh; background:#f8f9fc; color:#1a1d2e; text-align:center;">
            <div>
                <div style="font-size:3rem; margin-bottom:16px;">✅</div>
                <h2 style="color:#059669; margin-bottom:8px;">Signed In Successfully!</h2>
                <p style="color:#5a6178;">This window will close automatically...</p>
            </div>
            <script>
                if (window.opener) {
                    window.opener.postMessage({ type: 'GOOGLE_AUTH_SUCCESS' }, '*');
                }
                setTimeout(function() { window.close(); }, 1500);
            </script>
        </body>
        </html>
        """
    except Exception as e:
        return f"""
        <html>
        <body style="font-family: 'Inter', sans-serif; display:flex; align-items:center;
                     justify-content:center; min-height:100vh; background:#f8f9fc; color:#e11d48; text-align:center;">
            <div>
                <h2>Authentication Error</h2>
                <p style="color:#5a6178;">{str(e)}</p>
                <p style="color:#8d94a8;">You can close this window and try again.</p>
            </div>
        </body>
        </html>
        """, 500


@app.route("/api/auth/logout", methods=["POST"])
def auth_logout():
    """
    Log out by removing the stored Gmail token.
    This forces re-authentication on next login.
    """
    try:
        # Remove the token file
        if os.path.exists(Config.GMAIL_TOKEN_PATH):
            os.remove(Config.GMAIL_TOKEN_PATH)

        # Reset the gmail service state
        gmail_service.creds = None
        gmail_service.service = None

        return jsonify({
            "success": True,
            "message": "Logged out successfully.",
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
        }), 500


# ─── Email Endpoints ─────────────────────────────────────────────

@app.route("/api/emails", methods=["GET"])
def get_emails():
    """
    Fetch, classify, and prioritize inbox emails.

    Query params:
        max_results (int): Number of emails to fetch (default: 20)
        category (str): Filter by category
        priority (str): Filter by priority level
        source (str): 'gmail' to fetch fresh, 'db' for cached (default: 'db')
    """
    max_results = request.args.get("max_results", 20, type=int)
    category = request.args.get("category")
    priority_level = request.args.get("priority")
    source = request.args.get("source", "db")

    if source == "gmail":
        # Fetch fresh from Gmail and process
        if not gmail_service.is_authenticated():
            return jsonify({"error": "Not authenticated with Gmail"}), 401

        raw_emails = gmail_service.fetch_emails(max_results=max_results)
        processed_emails = []

        for email_data in raw_emails:
            # Classify
            text = f"{email_data.get('subject', '')} {email_data.get('body', '')}"
            classification = email_classifier.classify(text)

            # Prioritize
            priority = priority_engine.calculate_priority(email_data, classification)

            # Save to DB
            db.save_email(email_data, classification, priority)

            # Send notification if high priority
            notification_service.send_email_alert(
                email_data, classification, priority
            )

            # Log activity
            db.log_activity(email_data["id"], "classified", classification["category"])

            # Build response object
            processed = {
                **email_data,
                "classification": classification,
                "priority": priority,
            }
            processed_emails.append(processed)

        return jsonify({
            "emails": processed_emails,
            "total": len(processed_emails),
            "source": "gmail",
        })

    else:
        # Return cached emails from DB
        emails = db.get_emails(
            limit=max_results,
            category=category,
            priority_level=priority_level,
        )
        return jsonify({
            "emails": emails,
            "total": len(emails),
            "source": "database",
        })


@app.route("/api/emails/<email_id>", methods=["GET"])
def get_email(email_id):
    """Get a single email by ID with full details."""
    # Check DB first
    email = db.get_email(email_id)

    if not email and gmail_service.is_authenticated():
        # Fetch from Gmail
        email_data = gmail_service.get_email_detail(email_id)
        if email_data:
            text = f"{email_data.get('subject', '')} {email_data.get('body', '')}"
            classification = email_classifier.classify(text)
            priority = priority_engine.calculate_priority(email_data, classification)
            db.save_email(email_data, classification, priority)
            email = {
                **email_data,
                "classification": classification,
                "priority": priority,
            }

    if not email:
        return jsonify({"error": "Email not found"}), 404

    return jsonify(email)


@app.route("/api/emails/<email_id>/classify", methods=["POST"])
def classify_email(email_id):
    """Classify a specific email."""
    email = db.get_email(email_id)
    if not email:
        return jsonify({"error": "Email not found"}), 404

    text = f"{email.get('subject', '')} {email.get('body', '')}"
    classification = email_classifier.classify(text)
    priority = priority_engine.calculate_priority(email, classification)

    # Update DB
    db.save_email(email, classification, priority)
    db.log_activity(email_id, "reclassified", classification["category"])

    return jsonify({
        "classification": classification,
        "priority": priority,
    })


# ─── Draft Reply Endpoints ───────────────────────────────────────

@app.route("/api/emails/<email_id>/draft-reply", methods=["GET"])
def generate_draft_reply(email_id):
    """Generate an AI draft reply for an email."""
    # Check for existing draft
    existing_draft = db.get_draft_reply(email_id)
    if existing_draft and existing_draft.get("status") == "draft":
        return jsonify(existing_draft)

    # Get the email
    email = db.get_email(email_id)
    if not email:
        return jsonify({"error": "Email not found"}), 404

    # Get classification
    text = f"{email.get('subject', '')} {email.get('body', '')}"
    classification = email_classifier.classify(text)

    # Generate reply
    result = response_generator.generate_draft_reply(email, classification)

    # Save draft
    draft_id = db.save_draft_reply(
        email_id,
        result["draft_text"],
        result["generated_by"],
        result["category"],
    )
    db.log_activity(email_id, "draft_generated", result["generated_by"])

    result["id"] = draft_id
    result["email_id"] = email_id
    result["status"] = "draft"

    return jsonify(result)


@app.route("/api/emails/<email_id>/draft-reply", methods=["PUT"])
def update_draft_reply(email_id):
    """Update (edit) a draft reply."""
    data = request.get_json()
    if not data or "draft_text" not in data:
        return jsonify({"error": "draft_text is required"}), 400

    # Save updated draft
    draft_id = db.save_draft_reply(
        email_id,
        data["draft_text"],
        "user_edited",
    )
    db.log_activity(email_id, "draft_edited")

    return jsonify({
        "id": draft_id,
        "email_id": email_id,
        "draft_text": data["draft_text"],
        "status": "draft",
    })


@app.route("/api/emails/<email_id>/send-reply", methods=["POST"])
def send_reply(email_id):
    """Approve and send a draft reply via Gmail."""
    data = request.get_json()
    reply_text = data.get("reply_text") if data else None

    if not reply_text:
        # Use the latest draft
        draft = db.get_draft_reply(email_id)
        if draft:
            reply_text = draft.get("draft_text")

    if not reply_text:
        return jsonify({"error": "No reply text provided"}), 400

    if not gmail_service.is_authenticated():
        return jsonify({"error": "Not authenticated with Gmail"}), 401

    # Send via Gmail
    result = gmail_service.send_reply(email_id, reply_text)

    if result:
        # Update draft status
        draft = db.get_draft_reply(email_id)
        if draft:
            db.update_draft_status(draft["id"], "sent")
        db.log_activity(email_id, "reply_sent")

        return jsonify({
            "success": True,
            "message": "Reply sent successfully.",
            "sent_message_id": result.get("id"),
        })
    else:
        return jsonify({
            "success": False,
            "error": "Failed to send reply via Gmail.",
        }), 500


@app.route("/api/emails/<email_id>/archive", methods=["POST"])
def archive_email(email_id):
    """Archive an email."""
    if not gmail_service.is_authenticated():
        return jsonify({"error": "Not authenticated with Gmail"}), 401

    success = gmail_service.archive_email(email_id)
    if success:
        db.log_activity(email_id, "archived")
        return jsonify({"success": True, "message": "Email archived."})
    else:
        return jsonify({"success": False, "error": "Failed to archive."}), 500


# ─── Statistics ───────────────────────────────────────────────────

@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get dashboard statistics."""
    stats = db.get_stats()
    return jsonify(stats)


@app.route("/api/activity", methods=["GET"])
def get_activity():
    """Get recent activity log."""
    limit = request.args.get("limit", 20, type=int)
    activity = db.get_recent_activity(limit=limit)
    return jsonify({"activity": activity})


# ─── Settings ─────────────────────────────────────────────────────

@app.route("/api/settings", methods=["GET"])
def get_settings():
    """Get current application settings."""
    return jsonify({
        "gemini_configured": response_generator.is_available(),
        "telegram_configured": notification_service.is_configured(),
        "gmail_authenticated": gmail_service.is_authenticated(),
        "classifier_trained": email_classifier.is_trained(),
        "classifier_weight": Config.CLASSIFIER_WEIGHT,
        "sender_weight": Config.SENDER_WEIGHT,
        "keyword_weight": Config.KEYWORD_WEIGHT,
    })


@app.route("/api/settings", methods=["PUT"])
def update_settings():
    """Update application settings."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    updated = []

    # Update Gemini API key
    if "gemini_api_key" in data:
        success = response_generator.reconfigure(data["gemini_api_key"])
        if success:
            db.set_setting("gemini_api_key", data["gemini_api_key"])
            updated.append("gemini_api_key")

    # Update Telegram settings
    if "telegram_bot_token" in data and "telegram_chat_id" in data:
        notification_service.reconfigure(
            data["telegram_bot_token"],
            data["telegram_chat_id"],
        )
        db.set_setting("telegram_bot_token", data["telegram_bot_token"])
        db.set_setting("telegram_chat_id", data["telegram_chat_id"])
        updated.append("telegram")

    # Add known contacts
    if "contacts" in data:
        for contact in data["contacts"]:
            db.save_contact(
                contact["email"],
                contact.get("name"),
                contact.get("importance", 0.8),
            )
            priority_engine.add_known_contact(
                contact["email"],
                contact.get("importance", 0.8),
            )
        updated.append("contacts")

    return jsonify({
        "success": True,
        "updated": updated,
    })


# ─── Classifier Training ─────────────────────────────────────────

@app.route("/api/classifier/train", methods=["POST"])
def train_classifier():
    """Train the email classifier with the sample data."""
    try:
        results = email_classifier.train()
        return jsonify({
            "success": True,
            "accuracy": results["accuracy"],
            "cv_mean_accuracy": results["cv_mean_accuracy"],
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
        }), 500


@app.route("/api/classifier/status", methods=["GET"])
def classifier_status():
    """Check if the classifier is trained and ready."""
    return jsonify({
        "trained": email_classifier.is_trained(),
    })


# ─── Notification Test ────────────────────────────────────────────

@app.route("/api/notifications/test", methods=["POST"])
def test_notification():
    """Send a test Telegram notification."""
    success = notification_service.send_test_notification()
    return jsonify({
        "success": success,
        "configured": notification_service.is_configured(),
    })


# ─── Run Server ──────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  EMAIL MANAGEMENT AND RESPONSE AGENT")
    print("  Backend Server")
    print("=" * 60)
    print(f"\n  Server: http://{Config.HOST}:{Config.PORT}")
    print(f"  Frontend: {Config.FRONTEND_URL}")
    print(f"  Gmail: {'[OK] Authenticated' if gmail_service.is_authenticated() else '[NO] Not authenticated'}")
    print(f"  Classifier: {'[OK] Trained' if email_classifier.is_trained() else '[!!] Not trained (using rule-based fallback)'}")
    print(f"  Gemini: {'[OK] Configured' if response_generator.is_available() else '[!!] Not configured (using templates)'}")
    print(f"  Telegram: {'[OK] Configured' if notification_service.is_configured() else '[!!] Not configured'}")
    print(f"\n{'=' * 60}\n")

    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
    )
