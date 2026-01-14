import os
import sys
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class SheetsService:
    def __init__(self):
        self.creds = None
        self.service = None
        self.authenticate()

    def authenticate(self):
        """
        reuses the same credentials because scopes are combined in config.py
        But we need to load them similarly.
        """
        if os.path.exists(config.TOKEN_FILE):
             self.creds = Credentials.from_authorized_user_file(config.TOKEN_FILE, config.SCOPES)
        else:
            raise FileNotFoundError("Token file not found. Authorization typically happens via GmailService first or Main orchestrator.")

        self.service = build('sheets', 'v4', credentials=self.creds)

    def append_row(self, values):
        """Apends a single row to the sheet."""
        if not config.SPREADSHEET_ID or config.SPREADSHEET_ID == 'YOUR_SPREADSHEET_ID_HERE':
            print("Error: SPREADSHEET_ID is not configured in config.py")
            return

        body = {
            'values': [values]
        }
        
        try:
            result = self.service.spreadsheets().values().append(
                spreadsheetId=config.SPREADSHEET_ID,
                range='Sheet1!A1', # Appends to the end of data in Sheet1
                valueInputOption='RAW',
                body=body
            ).execute()
            print(f"Appended row: {result.get('updates').get('updatedRange')}")
        except Exception as e:
            print(f"Error appending row to sheets: {e}")

    def ensure_header(self):
        """Checks if the first row is empty and adds headers if needed."""
        if not config.SPREADSHEET_ID or config.SPREADSHEET_ID == 'YOUR_SPREADSHEET_ID_HERE':
            return

        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=config.SPREADSHEET_ID,
                range='Sheet1!A1:D1'
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                header = ["From", "Subject", "Date", "Content"]
                self.append_row(header)
                print("Added Helper Headers to new Sheet.")
        except Exception as e:
            print(f"Error checking headers: {e}")
