import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the email address of the sender you want to move emails from
sender_email = input("Enter sender email: ")

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

def move_emails_to_trash():
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    
    query = f"from:{sender_email}"
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    
    if not messages:
        print('No matching emails found.')
        return
    
    print(f'Moving {len(messages)} emails to trash...')
    
    batch = service.new_batch_http_request()

    for message in messages:
        message_id = message['id']
        batch.add(service.users().messages().modify(userId='me', id=message_id, body={'removeLabelIds': ['INBOX'], 'addLabelIds': ['TRASH']}))
    
    batch.execute()
    
    print('Emails moved to trash successfully.')

move_emails_to_trash()
