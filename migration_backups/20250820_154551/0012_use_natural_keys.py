from django.db import migrations, models

def ensure_primary_keys_not_null(apps, schema_editor):
    """
    Ensure that the fields we want to use as primary keys are not null
    """
    Locality = apps.get_model('butterflies', 'Locality')
    Initials = apps.get_model('butterflies', 'Initials')
    Specimen = apps.get_model('butterflies', 'Specimen')
    
    # Generate values for any null locality codes
    for locality in Locality.objects.filter(localityCode__isnull=True):
        locality.localityCode = f"LOC-{Locality.objects.count() + 1:04d}"
        locality.save()
        
    # Generate values for any null initials
    for initial in Initials.objects.filter(initials__isnull=True):
        initial.initials = f"INI-{Initials.objects.count() + 1:02d}"
        initial.save()
        
    # Generate values for any null catalog numbers
    for specimen in Specimen.objects.filter(catalogNumber__isnull=True):
        year = specimen.year or 'XXXX'
        locality_code = specimen.locality.localityCode if specimen.locality else 'XXXX'
        specimen_number = specimen.specimenNumber or f'SP{Specimen.objects.count()+1:04d}'
        specimen.catalogNumber = f"{year}-{locality_code}-{specimen_number}"
        specimen.save()


class Migration(migrations.Migration):

    dependencies = [
        ('butterflies', '0011_alter_initials_initials_alter_initials_name_and_more'),
    ]

    operations = [
        # First, ensure all primary key fields have values
        migrations.RunPython(ensure_primary_keys_not_null),
        
        # Update Locality model to use localityCode as primary key
        migrations.AlterField(
            model_name='locality',
            name='localityCode',
            field=models.CharField(help_text='Unique code for locality (primary key)', max_length=100, primary_key=True, serialize=False),
        ),
        
        # Update Initials model to use initials as primary key
        migrations.AlterField(
            model_name='initials',
            name='initials',
            field=models.CharField(help_text='Initials (primary key)', max_length=10, primary_key=True, serialize=False),
        ),
        
        # Update Specimen model to use catalogNumber as primary key
        migrations.AlterField(
            model_name='specimen',
            name='catalogNumber',
            field=models.CharField(help_text='Auto-generated: year-localityCode-specimenNumber (nnnn). Primary key for specimen.', max_length=100, primary_key=True, serialize=False),
        ),
    ]
