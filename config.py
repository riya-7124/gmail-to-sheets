import os

# Scopes required for the application
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/spreadsheets'
]

# File Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials', 'credentials.json')
TOKEN_FILE = os.path.join(BASE_DIR, 'token.json')
STATE_FILE = os.path.join(BASE_DIR, 'state.json')

# User Configuration - REPLACE THIS WITH YOUR SHEET ID
SPREADSHEET_ID = '1bcFXOvcySRN2jgdOuT2zT6bYnGcrlNKFxonk7XRgoPg' 
