from google_auth_oauthlib.flow import InstalledAppFlow
from apiclient.discovery import build
from apiclient.http import MediaIoBaseDownload, MediaFileUpload
import pickle
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('mode', type=str)
parser.add_argument('file_name', type=str)
parser.add_argument('output_file', type=str)
args = parser.parse_args()


# OAuth
credentials = None
try:
    with open("credentials.pkl", 'rb') as f:
        credentials = pickle.load(f)
except:
    pass
if not credentials:
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/drive'])
    credentials = flow.run_console()
with open("credentials.pkl", 'wb') as f:
    pickle.dump(credentials, f)

# Get google drive service
service = build('drive', 'v3', credentials=credentials)

if args.mode == 'upload':
    media = MediaFileUpload(args.file_name, resumable=True)
    file = service.files().create(body={'name': args.output_file}, media_body=media, fields='id').execute()
if args.mode == 'download':
    # Search files from file name
    files = service.files().list(q="name contains '%s'" % args.file_name).execute()

    # Download file
    for f in files['files']:
        if f['mimeType'] == 'application/vnd.google-apps.folder':
            # Skip folder
            continue
        if f['mimeType'].startswith('application/vnd.google-apps'):
            # Get Google Docs file type to pdf
            request = service.files().export_media(fileId=f['id'], mimeType='application/pdf')
        else:
            # Get Other format file to original file
            request = service.files().get_media(fileId=f['id'])
        buffer = open(args.output_file, 'wb')
        downloader = MediaIoBaseDownload(buffer, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))
        buffer.close()
