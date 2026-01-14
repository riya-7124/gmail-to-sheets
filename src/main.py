import os
import json
import sys
from gmail_service import GmailService
from sheets_service import SheetsService
from email_parser import parse_email

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Force UTF-8 encoding for Windows console output
sys.stdout.reconfigure(encoding='utf-8')

def load_state():
    """Loads the list of processed message IDs from state.json"""
    if os.path.exists(config.STATE_FILE):
        try:
            with open(config.STATE_FILE, 'r') as f:
                return set(json.load(f))
        except Exception as e:
            print(f"Warning: Could not load state file: {e}. Starting fresh.")
            return set()
    return set()

def save_state(processed_ids):
    """Saves the list of processed message IDs to state.json"""
    try:
        with open(config.STATE_FILE, 'w') as f:
            json.dump(list(processed_ids), f)
    except Exception as e:
        print(f"Error saving state: {e}")

def main():
    print("--- Gmail to Sheets Automation ---")
    
    # 1. Authenticate Services
    print("Authenticating with Gmail...")
    gmail = GmailService()
    
    print("Authenticating with Google Sheets...")
    try:
        sheets = SheetsService()
    except FileNotFoundError:
        print("Sheets Auth failed. Re-run after Gmail auth completes creating token.json")
        return

    # 2. Ensure Sheet Header
    sheets.ensure_header()

    # 3. Load State
    processed_ids = load_state()
    print(f"Loaded state: {len(processed_ids)} emails previously processed.")

    # 4. Fetch Unread Emails
    print("Fetching unread emails from Inbox...")
    messages = gmail.fetch_unread_messages()
    
    if not messages:
        print("No new unread emails found.")
        return

    print(f"Found {len(messages)} unread emails. Processing...")
    
    new_processed_count = 0

    # 5. Process Each Email
    for msg in messages:
        msg_id = msg['id']
        
        # Duplicate Prevention Check:
        # Check 1: API filter 'is:unread' (Already done in fetch)
        # Check 2: Local State check (Safety net)
        if msg_id in processed_ids:
            print(f"Skipping duplicate (State-checked): {msg_id}")
            continue

        full_msg = gmail.get_message_detail(msg_id)
        if not full_msg:
            continue

        parsed_data = parse_email(full_msg)
        
        # Prepare row data
        row = [
            parsed_data['from'],
            parsed_data['subject'],
            parsed_data['date'],
            parsed_data['content']
        ]

        # Append to Sheet
        print(f"Appending email: {parsed_data['subject'][:30]}...")
        sheets.append_row(row)
        
        # Update State
        processed_ids.add(msg_id)
        new_processed_count += 1
        
        # Mark as Read
        gmail.mark_as_read(msg_id)

    # 6. Save State
    if new_processed_count > 0:
        save_state(processed_ids)
        print(f"Successfully processed {new_processed_count} new emails.")
    else:
        print("No new emails processed (duplicates skipped).")

if __name__ == "__main__":
    main()
