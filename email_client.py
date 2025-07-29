import os
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
CLIENT_SECRET_PATH = "secrets/client_secret.json"
TOKEN_PATH = "secrets/token.json"

class GmailClient:
    def __init__(self):
        self.service = self.authenticate()

    def authenticate(self):
        creds = None
        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(TOKEN_PATH, "w") as token:
                token.write(creds.to_json())
        return build("gmail", "v1", credentials=creds)

    def send_email(self, sender: str, recipient: str, subject: str, body: str):
        message = MIMEText(body, "html")
        message["to"] = recipient
        message["from"] = "DsCubed Recruitment Team <recruitment@dscubed.org.au>"
        message["subject"] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        body = {"raw": raw}
        sent = self.service.users().messages().send(userId="me", body=body).execute()
        print(f"✅ Email sent! Message ID: {sent['id']}")