# Generated manually on 2025-08-18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('butterflies', '0018_alter_specimen_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='specimen',
            name='uploaded_iNaturalist',
        ),
    ]
