"""Gmail OAuth - fixed for Windows."""
import os
import sys
import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]

CREDENTIALS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "credentials.json")
TOKEN_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token.json")
PORT = 8095
REDIRECT_URI = f"http://localhost:{PORT}/"

auth_code = None
server_done = threading.Event()


class AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        query = parse_qs(urlparse(self.path).query)
        if "code" in query:
            auth_code = query["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            html = "<html><body style='font-family:Arial;text-align:center;padding:50px;background:#1a1a2e;color:#fff'>"
            html += "<h1 style='color:#4ade80'>Authentication Successful!</h1>"
            html += "<p>You can close this tab and go back to your Email Agent app.</p>"
            html += "</body></html>"
            self.wfile.write(html.encode())
        else:
            error = query.get("error", ["unknown"])[0]
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(f"<html><body><h1>Error: {error}</h1></body></html>".encode())
        server_done.set()

    def log_message(self, format, *args):
        pass


def main():
    global auth_code

    # Check existing token
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        if creds and creds.valid:
            print("ALREADY_AUTHENTICATED")
            return
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_PATH, "w") as f:
                f.write(creds.to_json())
            print("TOKEN_REFRESHED")
            return

    if not os.path.exists(CREDENTIALS_PATH):
        print("ERROR: credentials.json not found!")
        sys.exit(1)

    # Create flow
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_PATH,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    auth_url, state = flow.authorization_url(access_type="offline", prompt="consent")

    # Save URL to file
    url_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "auth_url.txt")
    with open(url_file, "w") as f:
        f.write(auth_url)
    print(f"AUTH_URL_SAVED to auth_url.txt")

    # Start HTTP server FIRST
    server = HTTPServer(("localhost", PORT), AuthHandler)
    server.timeout = 300
    print(f"Server listening on port {PORT}")

    # Open browser using Python webbrowser module (works on Windows)
    print("Opening browser...")
    webbrowser.open(auth_url)

    # Wait for callback (5 min timeout)
    print("Waiting for Google sign-in... (5 min timeout)")
    server.handle_request()
    server.server_close()

    if auth_code:
        print(f"Got auth code, exchanging for token...")
        try:
            flow.fetch_token(code=auth_code)
            creds = flow.credentials
            with open(TOKEN_PATH, "w") as f:
                f.write(creds.to_json())
            print("SUCCESS! token.json saved!")
        except Exception as e:
            print(f"Token exchange failed: {e}")
            sys.exit(1)
    else:
        print("FAILED: No auth code received.")
        sys.exit(1)


if __name__ == "__main__":
    main()
