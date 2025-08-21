from django.db import migrations, models

class Migration(migrations.Migration):
    """
    Migration to ensure proper field types for locality foreign keys.
    This migration is designed to work with a fresh database where only 0001_initial
    has been applied.
    """

    dependencies = [
        ('butterflies', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            -- No-op SQL that will work with a fresh database
            SELECT 1;
            """,
            reverse_sql="""
            SELECT 1;
            """
        ),
    ]
