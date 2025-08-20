from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    """
    This migration fixes the foreign key relationships after changing the primary keys to natural keys.
    It updates the foreign key fields in the Specimen model to be string-based to match the new primary key types.
    """

    dependencies = [
        ('butterflies', '0020_merge_20250820_1541'),
    ]

    operations = [
        # Step 1: First remove the old integer-based foreign key relationships
        migrations.RemoveField(
            model_name='specimen',
            name='georeferencedBy',
        ),
        migrations.RemoveField(
            model_name='specimen',
            name='identifiedBy',
        ),
        migrations.RemoveField(
            model_name='specimen',
            name='locality',
        ),
        migrations.RemoveField(
            model_name='specimen',
            name='recordedBy',
        ),
        
        # Step 2: Re-create the foreign keys with string-based to_field
        migrations.AddField(
            model_name='specimen',
            name='georeferencedBy',
            field=models.ForeignKey(
                help_text='Dropdown: initials from Initials table.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='georeferenced_specimens',
                to='butterflies.initials',
                to_field='initials'
            ),
        ),
        migrations.AddField(
            model_name='specimen',
            name='identifiedBy',
            field=models.ForeignKey(
                help_text='Dropdown: initials from Initials table.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='identified_specimens',
                to='butterflies.initials',
                to_field='initials'
            ),
        ),
        migrations.AddField(
            model_name='specimen',
            name='locality',
            field=models.ForeignKey(
                help_text='Dropdown: localityCode from Locality table.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='butterflies.locality',
                to_field='localityCode'
            ),
        ),
        migrations.AddField(
            model_name='specimen',
            name='recordedBy',
            field=models.ForeignKey(
                help_text='Dropdown: initials from Initials table.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='butterflies.initials',
                to_field='initials'
            ),
        ),
    ]
