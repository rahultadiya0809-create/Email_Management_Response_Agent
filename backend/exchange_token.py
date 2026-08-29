"""Exchange an auth code for a token. Pass the full redirect URL as argument."""
import sys
import os
import json

from google_auth_oauthlib.flow import Flow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]

CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "credentials.json")
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "token.json")
REDIRECT_URI = "http://localhost:8095/"

if len(sys.argv) < 2:
    print("Usage: python exchange_token.py <auth_code>")
    exit(1)

auth_code = sys.argv[1]
print(f"Exchanging auth code: {auth_code[:20]}...")

flow = Flow.from_client_secrets_file(
    CREDENTIALS_PATH,
    scopes=SCOPES,
    redirect_uri=REDIRECT_URI,
)

flow.fetch_token(code=auth_code)
creds = flow.credentials

with open(TOKEN_PATH, "w") as f:
    f.write(creds.to_json())

print("SUCCESS! token.json saved!")
