import os
import pandas as pd
from django.core.management.base import BaseCommand
from butterflies.models import Specimen, Locality, Initials

class Command(BaseCommand):
    help = "Export Specimen, Locality, Initials tables to Excel files"

    def handle(self, *args, **kwargs):
        export_dir = "db_exports"
        os.makedirs(export_dir, exist_ok=True)

        tables = [
            ("Specimen", Specimen),
            ("Locality", Locality),
            ("Initials", Initials),
        ]
        for name, model in tables:
            df = pd.DataFrame(list(model.objects.all().values()))
            file_path = os.path.join(export_dir, f"{name.lower()}_backup.xlsx")
            df.to_excel(file_path, index=False)
            self.stdout.write(self.style.SUCCESS(f"Exported {name} to {file_path}"))
            # Remove file after export (if uploaded)
            # Actual removal is handled after upload in upload_to_gdrive
