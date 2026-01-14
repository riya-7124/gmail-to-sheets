# Gmail to Sheets Automation

**Author**: RIYA MAHESHWARI

## Overview
This project automates the process of reading incoming emails from a Gmail account and logging them into a Google Sheet. It uses OAuth 2.0 for secure authentication and ensures that no email is processed twice.

## High-Level Architecture


+-------------+      (1) Auth &       +----------------+
|   Gmail     | <--- Fetch Unread --- |                |
|    API      |      Messages         |  Python Script |
+-------------+                       |  (src/main.py) |
       |                              +----------------+
       | (2) JSON Response                    |
       v                                      | (3) Check State (Duplicates)
+-------------+                               v
| Email       |                       +----------------+
| Parser      | --------------------> |   state.json   |
+-------------+                       +----------------+
       |                                      |
       | (4) Clean Data                       | (5) Append Row
       v                                      v
+-------------+                       +----------------+
|   Google    | --- Write Data -----> |     Google     |
| Sheets API  |                       |     Sheets     |
+-------------+                       +----------------+

## High-Level Architecture

+-----------+           (1) Auth &           +-----------------+
|   Gmail   | <--- Fetch Unread ------------ |  Python Script  |
|    API    |           Messages             |  (src/main.py)  |
+-----------+                                +-----------------+
      |                                            |
      | (2) JSON Response                          |
      v                                            | (3) Check State 
+-----------+                                      v    (Duplicates)
|   Email   |                                 +------------+
|  Parser   | ------------------------------> | state.json |
+-----------+                                 +------------+
      |                                            |
      | (4) Clean Data                             |  (5) Append Row
      v                                            v
+------------+                               +-----------------+
|   Google   | ----(6) Write Data ---------> |  Google Sheet   |
| Sheets API |                               +-----------------+
+------------+                                     |
                                                   |
                  (7) Finalize:                    |
           Mark as Read & Update state.json <------+

## Project Structure

gmail-to-sheets/
├── src/
│   ├── main.py            # Entry point
│   ├── gmail_service.py   # Gmail API wrapper
│   ├── sheets_service.py  # Sheets API wrapper
│   └── email_parser.py    # Content extraction logic
├── credentials/           # credentials.json is stored here
├── proof/                 # Screenshots and Video proof
├── config.py              # Configuration (Sheet ID, scopes)
├── requirements.txt       # Dependencies
└── state.json             # Local database of processed IDs


## Setup Instructions

### 1. Prerequisites
- Python 3 installed.
- A Google Cloud Project with **Gmail API** and **Google Sheets API** enabled.

### 2. Credentials
1.  Go to the Google Cloud Console.
2.  Create an **OAuth 2.0 Client ID** (Application Type: Desktop App).
3.  Download the JSON file.
4.  Rename it to `credentials.json`.
5.  Place it in the `credentials/` folder.
    *   *Warning*: Never commit this file. It is ignored by `.gitignore`.

### 3. Installation

# Install dependencies
pip install -r requirements.txt


### 4. Configuration
Open `config.py` and replace `SPREADSHEET_ID` with the ID of your target Google Sheet.
*(You can find the ID in the URL of your Google Sheet: docs.google.com/spreadsheets/d/**ID_HERE**/edit)*

### 5. Running

python src/main.py

- On the first run, a browser window will open for you to log in to your Google Account.
- Grant the requested permissions.

## Design & Implementation Details

### OAuth Flow
We use **OAuth 2.0** for authorization. The `gmail_service.py` handles the flow:
1.  Checks for `token.json`.
2.  If missing/expired, initiates the `InstalledAppFlow` using `credentials.json`.
3.  Opens a local server port to capture the callback.
4.  Saves the valid `token.json` for future runs.
*Note*: `token.json` is also ignored by `.gitignore`.

### Duplicate Prevention Logic
Using a **Dual-Layer Strategy** to ensure zero duplicates:

1.  **Primary Filter (API Level)**: We query the Gmail API specifically for `q='is:unread in:inbox'`. This ensures we primarily only see new mail.
2.  **Secondary Safety Net (Local State)**:
    - We maintain a `state.json` file that functions as a lightweight local database.
    - Before processing *any* email, we check if its unique `id` exists in `state.json`.
    - If it exists, we skip it (even if it was marked unread).
    - After successful processing (appending to Sheets), we add the ID to `state.json` and mark the message as READ in Gmail.

### State Persistence
**Why a JSON file?**
We chose a local `state.json` file because:
-   **Simplicity**: It doesn't require setting up an external database (SQL/NoSQL).
-   **Portability**: It keeps the project self-contained.
-   **Performance**: For personal inbox automation, the volume of data is small enough that a JSON list is performant and reliable.

## Challenges & Limitations

### Challenge: Handling Multipart Emails
Emails come in various structures (Plain text, HTML, Multipart).
*   **Solution**: I implemented a priority parser in `email_parser.py`. It first looks for a `text/plain` part. If not found, it falls back to `text/html` and uses `BeautifulSoup` to strip tags and extract clean text. This ensures we always get readable content.

### Challenge: Google Sheets API 403 Permission Denied
During initial testing, the script failed to append data despite successful authentication.
*  **Solution**:This was identified as a permission mismatch. The authenticated Gmail account did not have `Editor` access to the specific spreadsheet. I resolved this by sharing the Google Sheet with the target email address and ensuring the user was added to the `Test Users` list in the Google Cloud Console.

### Limitations
1.  **Local State Concurrency**: If two instances of the script ran exactly at the same time, they might race on writing `state.json`. (Not an issue for this single-user use case).
2.  **Attachment Handling**: The current script only extracts text body; attachments are ignored.
3.  **Manual Sharing Requirement**: The solution cannot automatically grant itself access to a private Google Sheet, the user must manually ensure the spreadsheet is shared with the authenticated account.

## Proof of Execution
See the `proof/` directory for:
-   `inbox_screenshot.png`: Showing unread emails.
-   `sheets_screenshot.png`: Showing appended data.
-   `consent_screen.png`: Showing OAuth flow.
-   `gmail-to-sheets demo.mp4`: Short video explaining the project.