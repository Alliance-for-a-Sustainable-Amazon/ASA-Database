# Generated migration to add performance indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('butterflies', '0006_alter_specimen_specimennumber'),
    ]

    operations = [
        # Add indexes for commonly filtered fields
        migrations.AlterField(
            model_name='specimen',
            name='year',
            field=models.CharField(blank=True, help_text='Dropdown/typeable: 1900-2050.', max_length=4, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='specimen',
            name='month',
            field=models.CharField(blank=True, help_text='Dropdown/typeable.', max_length=10, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='specimen',
            name='specimenNumber',
            field=models.CharField(blank=True, default=None, help_text='Manual entry. Can have duplicates across different locations.', max_length=100, null=True, db_index=True),
        ),
    ]
