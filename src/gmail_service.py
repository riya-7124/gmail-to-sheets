import os
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import sys

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class GmailService:
    def __init__(self):
        self.creds = None
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Authenticates using OAuth 2.0"""
        if os.path.exists(config.TOKEN_FILE):
            self.creds = Credentials.from_authorized_user_file(config.TOKEN_FILE, config.SCOPES)
        
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing token: {e}")
                    self.creds = None # Force re-auth
            
            if not self.creds:
                if not os.path.exists(config.CREDENTIALS_FILE):
                    raise FileNotFoundError(f"Credentials file not found at {config.CREDENTIALS_FILE}. Please follow README setup.")
                    
                flow = InstalledAppFlow.from_client_secrets_file(
                    config.CREDENTIALS_FILE, config.SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(config.TOKEN_FILE, 'w') as token:
                token.write(self.creds.to_json())

        self.service = build('gmail', 'v1', credentials=self.creds)

    def fetch_unread_messages(self):
        """Fetches list of unread messages from Inbox."""
        try:
            # q='is:unread in:inbox' filters API side
            results = self.service.users().messages().list(userId='me', q='is:unread in:inbox').execute()
            messages = results.get('messages', [])
            return messages
        except Exception as e:
            print(f"An error occurred fetching messages: {e}")
            return []

    def get_message_detail(self, message_id):
        """Gets full message detail by ID"""
        try:
            message = self.service.users().messages().get(userId='me', id=message_id).execute()
            return message
        except Exception as e:
            print(f"An error occurred getting message detail {message_id}: {e}")
            return None

    def mark_as_read(self, message_id):
        """Removes the UNREAD label from a message"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            print(f"Marked message {message_id} as read.")
        except Exception as e:
            print(f"An error occurred marking message as read: {e}")
