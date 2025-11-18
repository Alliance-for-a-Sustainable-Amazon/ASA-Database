# Generated migration to add indexes for sorting performance

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('butterflies', '0008_alter_specimen_month_alter_specimen_specimennumber_and_more'),
    ]

    operations = [
        # Add index on eventDate for efficient sorting
        migrations.AlterField(
            model_name='specimen',
            name='eventDate',
            field=models.DateField(blank=True, null=True, db_index=True, help_text='Date of the event or collection.'),
        ),
        # Add composite index for (eventDate DESC, eventTime DESC) - optimal for report_table sorting
        migrations.AddIndex(
            model_name='specimen',
            index=models.Index(fields=['-eventDate', '-eventTime'], name='specimen_event_idx'),
        ),
        # Add index on catalogNumber for faster lookups
        migrations.AddIndex(
            model_name='specimen',
            index=models.Index(fields=['catalogNumber'], name='specimen_catalog_idx'),
        ),
    ]
