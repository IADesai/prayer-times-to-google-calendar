from googleapiclient.discovery import build
from googleapiclient.http import BatchHttpRequest
from google.oauth2.credentials import Credentials
import os

# Path to credentials.json (ensure it's in the same directory as the script)
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

def authenticate():
    """
    Authenticate and return a Google Calendar API service instance.
    """
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, ['https://www.googleapis.com/auth/calendar'])
    else:
        from google_auth_oauthlib.flow import InstalledAppFlow
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/calendar'])
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def delete_all_events(calendar_id='primary'):
    """
    Delete all events from a specified calendar using batch requests.
    """
    service = authenticate()
    events_result = service.events().list(calendarId=calendar_id).execute()
    events = events_result.get('items', [])

    if not events:
        print("No events found.")
        return

    # Callback for batch requests
    def callback(request_id, response, exception):
        if exception:
            print(f"Failed to delete an event: {exception}")

    # Create a batch request
    batch = service.new_batch_http_request(callback=callback)
    print(f"Found {len(events)} events to delete...")

    for event in events:
        batch.add(service.events().delete(calendarId=calendar_id, eventId=event['id']))

    # Execute the batch request
    batch.execute()
    print("All events deleted successfully.")

if __name__ == '__main__':
    # Replace 'your-calendar-id' with the actual calendar ID if it's not the primary calendar
    calendar_id = "1a4a4046ea518584fe2a3a0dc2dcffc889427489a999182a13214a1c2c5d830c@group.calendar.google.com"
    delete_all_events(calendar_id)
