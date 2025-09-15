import os
import shutil
from datetime import datetime

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ---------- CONFIG ----------
SQLITE_DB_PATH = 'db.sqlite3'  # Path to your SQLite3 DB
BACKUP_FILENAME = f'db_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sqlite3'
SERVICE_ACCOUNT_FILE = 'credentials/service-account.json'
SHARED_DRIVE_ID = '0ADUE7KR7YsqxUk9PVA'  # Your Shared Drive ID
FOLDER_NAME = 'django_backup'  # Folder inside the Shared Drive

# ---------- STEP 1: Copy DB to temporary backup file ----------
shutil.copy(SQLITE_DB_PATH, BACKUP_FILENAME)
print(f'Copied database to {BACKUP_FILENAME}')

# ---------- STEP 2: Authenticate ----------
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/drive']
)
service = build('drive', 'v3', credentials=creds)

# ---------- STEP 3: Find folder inside Shared Drive ----------
results = (
    service.files()
    .list(
        q=f"name='{FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder'",
        corpora='drive',
        driveId=SHARED_DRIVE_ID,
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
        fields='files(id, name)',
    )
    .execute()
)

folders = results.get('files', [])

# If folder not found, create it
if not folders:
    print(f"Folder '{FOLDER_NAME}' not found. Creating it...")
    folder_metadata = {
        'name': FOLDER_NAME,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [SHARED_DRIVE_ID],  # Create inside the Shared Drive
    }
    folder = (
        service.files()
        .create(body=folder_metadata, supportsAllDrives=True, fields='id, name')
        .execute()
    )
    folder_id = folder['id']
    print(f"Created folder '{FOLDER_NAME}' with ID {folder_id}")
else:
    folder_id = folders[0]['id']
    print(f"Found folder '{FOLDER_NAME}' with ID {folder_id}")

# ---------- STEP 4: Upload backup ----------
file_metadata = {'name': BACKUP_FILENAME, 'parents': [folder_id]}

media = MediaFileUpload(BACKUP_FILENAME, mimetype='application/x-sqlite3')

file = (
    service.files()
    .create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink',
        supportsAllDrives=True,
    )
    .execute()
)

print(f'Backup uploaded! File ID: {file["id"]}')
print(f'View in Drive: https://drive.google.com/file/d/{file["id"]}/view?usp=drivesdk')

# ---------- STEP 5: Cleanup ----------
os.remove(BACKUP_FILENAME)
print('Temporary backup file removed locally.')
