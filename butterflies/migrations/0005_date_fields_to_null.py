from django.db import migrations, models

def clear_date_fields(apps, schema_editor):
    """
    Clear all date fields to avoid conversion errors
    """
    Specimen = apps.get_model('butterflies', 'Specimen')
    for specimen in Specimen.objects.all():
        specimen.eventDate = None
        specimen.georeferencedDate = None
        specimen.dateIdentified = None
        specimen.save()

class Migration(migrations.Migration):
    dependencies = [
        ('butterflies', '0004_alter_specimen_exact_loc'),  # Update this to your latest migration before our date changes
    ]

    operations = [
        # First clear all date fields to avoid conversion issues
        migrations.RunPython(clear_date_fields, migrations.RunPython.noop),
        
        # Then change the field types
        migrations.AlterField(
            model_name='specimen',
            name='eventDate',
            field=models.DateField(blank=True, help_text='Date of the event or collection.', null=True),
        ),
        migrations.AlterField(
            model_name='specimen',
            name='georeferencedDate',
            field=models.DateField(blank=True, help_text='Date of georeferencing.', null=True),
        ),
        migrations.AlterField(
            model_name='specimen',
            name='dateIdentified',
            field=models.DateField(blank=True, help_text='Date of identification.', null=True),
        ),
    ]
