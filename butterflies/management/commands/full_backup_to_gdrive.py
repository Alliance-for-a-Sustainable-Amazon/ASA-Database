import os
import subprocess
from django.core.management.base import BaseCommand
from django.conf import settings
from butterflies.management.commands.export_tables_to_excel import Command as ExportExcelCommand
from butterflies.utils.upload_to_gdrive import upload_file_to_gdrive

class Command(BaseCommand):
    help = "Backup Postgres DB, export tables to Excel, and upload all to Google Drive."

    def handle(self, *args, **kwargs):
        # 1. Backup Postgres DB
        backup_filename = f"asa_postgres_backup_$(date +%Y%m%d_%H%M%S).sql"
        backup_cmd = [
            "bash", "backup_postgres.sh"
        ]
        self.stdout.write("[DEBUG] Backing up PostgreSQL database...")
        subprocess.run(backup_cmd, check=True)
        self.stdout.write(self.style.SUCCESS("[DEBUG] Postgres backup complete."))

        # 2. Export tables to Excel
        self.stdout.write("[DEBUG] Exporting tables to Excel...")
        export_excel_cmd = ExportExcelCommand()
        export_excel_cmd.handle()
        self.stdout.write(self.style.SUCCESS("[DEBUG] Excel export complete."))

        # 3. Upload all files to Google Drive
        credentials_json = os.environ.get("GOOGLE_DRIVE_CREDENTIALS_JSON")
        folder_id = os.environ.get("GOOGLE_DRIVE_FOLDER_ID")
        if not credentials_json or not folder_id:
            self.stdout.write(self.style.WARNING("[DEBUG] Google Drive credentials or folder ID not set. Skipping upload."))
            return
        self.stdout.write("[DEBUG] Uploading backup files to Google Drive...")
        # Upload Postgres backup (cleanup handled in upload_to_gdrive)
        for file in os.listdir('.'):
            if file.startswith('asa_postgres_backup_') and file.endswith('.sql'):
                upload_file_to_gdrive(file, folder_id, credentials_json)
                self.stdout.write(self.style.SUCCESS(f"[DEBUG] Uploaded {file} to Google Drive (old backups cleaned and local file deleted)."))
        # Upload Excel files (cleanup handled in upload_to_gdrive)
        export_dir = "db_exports"
        for file in os.listdir(export_dir):
            if file.endswith('.xlsx'):
                upload_file_to_gdrive(os.path.join(export_dir, file), folder_id, credentials_json)
                self.stdout.write(self.style.SUCCESS(f"[DEBUG] Uploaded {file} to Google Drive (local file deleted)."))
        self.stdout.write(self.style.SUCCESS("[DEBUG] All backup files uploaded to Google Drive and removed locally."))
