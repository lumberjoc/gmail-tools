import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the email address of the sender you want to delete emails from
sender_emails = input("Enter sender emails (separated by comma): ").split(",")

# If modifying the scopes, delete the token.pickle file.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_credentials():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def delete_emails():
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    
    total_emails_moved = 0
    
    for sender_email in sender_emails:
        query = f"from:{sender_email.strip()}"
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])
        
        if not messages:
            print(f'No matching emails found for sender email: {sender_email}')
            continue
        
        print(f'Moving {len(messages)} emails from sender: {sender_email.strip()} to trash...')
        
        batch = service.new_batch_http_request()
        
        for message in messages:
            message_id = message['id']
            batch.add(service.users().messages().modify(userId='me', id=message_id, body={'removeLabelIds': ['INBOX'], 'addLabelIds': ['TRASH']}))
        
        batch.execute()
        
        total_emails_moved += len(messages)
    
    print(f'Total emails moved to trash: {total_emails_moved}')

delete_emails()


