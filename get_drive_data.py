from google_auth_oauthlib.flow import InstalledAppFlow
from apiclient.discovery import build


# OAuth
flow = InstalledAppFlow.from_client_secrets_file(
    'client_secret.json',
    scopes=['https://www.googleapis.com/auth/drive'])
credentials = flow.run_console()


# execute
service = build('drive', 'v3', credentials=credentials)
print(service.files().list().execute())