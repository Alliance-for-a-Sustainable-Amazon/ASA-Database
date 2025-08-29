import os
import tempfile
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_file_to_gdrive(file_path, folder_id, credentials_json=None):
    import datetime
    print(f"[DEBUG] Starting upload for {file_path} at {datetime.datetime.now()}")
    if credentials_json is None:
        json_value = os.environ.get('GOOGLE_DRIVE_CREDENTIALS_JSON_VALUE')
        if not json_value:
            print("[ERROR] Google Drive credentials JSON value not found in environment variable.")
            raise RuntimeError('Google Drive credentials JSON value not found in environment variable.')
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json') as tmp:
            tmp.write(json_value)
            credentials_json = tmp.name
    creds = service_account.Credentials.from_service_account_file(credentials_json, scopes=['https://www.googleapis.com/auth/drive.file'])
    service = build('drive', 'v3', credentials=creds)
    file_metadata = {'name': os.path.basename(file_path), 'parents': [folder_id]}
    media = MediaFileUpload(file_path, resumable=True)
    uploaded_file = service.files().create(body=file_metadata, media_body=media, fields='id, name, createdTime').execute()
    print(f"[DEBUG] Uploaded {file_path} to Google Drive as {uploaded_file.get('name')} (ID: {uploaded_file.get('id')})")

    # Retention logic: keep only the latest 3 backups by createdTime
    query_pg = f"'{folder_id}' in parents and name contains 'asa_postgres_backup_' and mimeType != 'application/vnd.google-apps.folder'"
    results_pg = service.files().list(q=query_pg, fields="files(id, name, createdTime)", orderBy="createdTime desc").execute()
    files_pg = results_pg.get('files', [])
    files_pg_sorted = sorted(files_pg, key=lambda x: x['createdTime'], reverse=True)
    print(f"[DEBUG] Found {len(files_pg_sorted)} Postgres backups in Google Drive. Keeping latest 3.")
    for f in files_pg_sorted[3:]:
        print(f"[DEBUG] Deleting old backup {f['name']} (ID: {f['id']})")
        service.files().delete(fileId=f['id']).execute()

    excel_names = ['specimen_backup.xlsx', 'locality_backup.xlsx', 'initials_backup.xlsx']
    for excel_name in excel_names:
        query_excel = f"'{folder_id}' in parents and name = '{excel_name}' and mimeType != 'application/vnd.google-apps.folder'"
        results_excel = service.files().list(q=query_excel, fields="files(id, name, createdTime)", orderBy="createdTime desc").execute()
        files_excel = results_excel.get('files', [])
        files_excel_sorted = sorted(files_excel, key=lambda x: x['createdTime'], reverse=True)
        print(f"[DEBUG] Found {len(files_excel_sorted)} {excel_name} backups in Google Drive. Keeping latest 3.")
        for f in files_excel_sorted[3:]:
            print(f"[DEBUG] Deleting old backup {f['name']} (ID: {f['id']})")
            service.files().delete(fileId=f['id']).execute()

    # Clean up temp file if used
    if 'tmp' in locals():
        print(f"[DEBUG] Removing temp credentials file {tmp.name}")
        os.remove(tmp.name)

    # Remove local backup file after upload
    try:
        os.remove(file_path)
        print(f"[DEBUG] Removed local backup file {file_path}")
    except Exception as e:
        print(f"[WARNING] Could not remove local backup file {file_path}: {e}")

    return uploaded_file.get('id')
