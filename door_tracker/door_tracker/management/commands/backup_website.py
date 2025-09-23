import os
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import connection
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from door_tracker import settings


class Command(BaseCommand):
    help = 'Back up SQLite3 database to Shared Drive'

    def handle(self, *args, **options):
        # ---------- CONFIG ----------
        BACKUP_FILENAME = (
            f'db_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sqlite3'
        )
        SERVICE_ACCOUNT_FILE = os.path.join(
            os.getcwd(), 'credentials/service-account.json'
        )

        SHARED_DRIVE_ID = settings.BACKUP_SHARED_DRIVE_ID
        FOLDER_NAME = settings.BACKUP_FOLDER_NAME

        # ---------- STEP 1: Copy DB ----------
        with connection.cursor() as cursor:
            cursor.execute(f"VACUUM INTO '{BACKUP_FILENAME}'")
        self.stdout.write(f'Copied database to {BACKUP_FILENAME}')

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
            self.stdout.write(f"Folder '{FOLDER_NAME}' not found. Creating it...")
            folder_metadata = {
                'name': FOLDER_NAME,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [SHARED_DRIVE_ID],
            }
            folder = (
                service.files()
                .create(body=folder_metadata, supportsAllDrives=True, fields='id, name')
                .execute()
            )
            folder_id = folder['id']
            self.stdout.write(f"Created folder '{FOLDER_NAME}' with ID {folder_id}")
        else:
            folder_id = folders[0]['id']
            self.stdout.write(f"Found folder '{FOLDER_NAME}' with ID {folder_id}")

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

        self.stdout.write(f'Backup uploaded! File ID: {file["id"]}')
        self.stdout.write(
            f'View in Drive: https://drive.google.com/file/d/{file["id"]}/view?usp=drivesdk'
        )

        # ---------- STEP 5: Cleanup ----------
        os.remove(BACKUP_FILENAME)
        self.stdout.write('Temporary backup file removed locally.')
