import base64
from bs4 import BeautifulSoup
import email

def clean_body(html_content):
    """
    Converts HTML content to plain text.
    """
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    # Get text and strip extra whitespace
    text = soup.get_text(separator=' ', strip=True)
    return text

def parse_email(message):
    """
    Parses a Gmail API message resource into a dictionary.
    """
    payload = message.get('payload', {})
    headers = payload.get('headers', [])
    
    # Extract headers
    headers_dict = {h['name'].lower(): h['value'] for h in headers}
    sender = headers_dict.get('from', 'Unknown')
    subject = headers_dict.get('subject', 'No Subject')
    date = headers_dict.get('date', 'Unknown Date')
    
    # Extract Body
    body = ""
    parts = payload.get('parts', [])
    
    data = None
    
    # Strategy: Look for plain text first, then HTML
    if not parts:
        # Simple message (no parts)
        data = payload.get('body', {}).get('data')
    else:
        # Check for plain text part
        for part in parts:
            if part.get('mimeType') == 'text/plain':
                data = part.get('body', {}).get('data')
                break
        
        # If no plain text, look for HTML
        if not data:
            for part in parts:
                if part.get('mimeType') == 'text/html':
                    data = part.get('body', {}).get('data')
                    break
                    
    if data:
        # Decode base64url
        try:
            decoded_bytes = base64.urlsafe_b64decode(data.encode('UTF-8'))
            body_content = decoded_bytes.decode('UTF-8')
            # Clean up if it was HTML
            # Note: We run clean_body anyway to be safe, or we could detect if we grabbed the HTML part
            body = clean_body(body_content)
        except Exception as e:
            print(f"Error decoding body: {e}")
            body = "(Error decoding body)"
            
    return {
        "id": message.get('id'),
        "from": sender,
        "subject": subject,
        "date": date,
        "content": body
    }
