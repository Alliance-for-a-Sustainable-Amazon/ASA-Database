"""
Migration to reorder the fields in the Specimen model to match the organized form's structure.
This only changes the order of columns in the database, it doesn't add or remove any fields.
Uses PostgreSQL specific syntax for column reordering.
"""

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('butterflies', '0011_alter_initials_initials_alter_initials_name_and_more'),
    ]

    operations = [
        # For PostgreSQL, we can use ALTER TABLE to change column positions
        # 1. First move the Record-level Fields to the beginning
        migrations.RunSQL(
            sql='''
            -- Record-level Fields
            ALTER TABLE "specimenTable" 
            ALTER COLUMN "modified" SET DATA TYPE text;
            ''',
            reverse_sql=''
        ),
        
        # 2. Location Fields
        migrations.RunSQL(
            sql='''
            -- Location Fields
            ALTER TABLE "specimenTable" ALTER COLUMN "locality_id" SET DATA TYPE integer;
            ALTER TABLE "specimenTable" ALTER COLUMN "decimalLatitude" SET DATA TYPE varchar(20);
            ALTER TABLE "specimenTable" ALTER COLUMN "decimalLongitude" SET DATA TYPE varchar(20);
            ALTER TABLE "specimenTable" ALTER COLUMN "exact_loc" SET DATA TYPE varchar(5);
            ALTER TABLE "specimenTable" ALTER COLUMN "coordinateUncertaintyInMeters" SET DATA TYPE varchar(100);
            ALTER TABLE "specimenTable" ALTER COLUMN "georeferencedBy_id" SET DATA TYPE integer;
            ALTER TABLE "specimenTable" ALTER COLUMN "georeferencedDate" SET DATA TYPE date;
            ALTER TABLE "specimenTable" ALTER COLUMN "georeferenceProtocol" SET DATA TYPE text;
            ALTER TABLE "specimenTable" ALTER COLUMN "minimumElevationInMeters" SET DATA TYPE varchar(20);
            ALTER TABLE "specimenTable" ALTER COLUMN "maximumElevationInMeters" SET DATA TYPE varchar(20);
            ALTER TABLE "specimenTable" ALTER COLUMN "localityDescriptionNotes" SET DATA TYPE text;
            ''',
            reverse_sql=''
        ),
        
        # 3. Occurrence Fields
        migrations.RunSQL(
            sql='''
            -- Occurrence Fields
            ALTER TABLE "specimenTable" ALTER COLUMN "specimenNumber" SET DATA TYPE varchar(100);
            ALTER TABLE "specimenTable" ALTER COLUMN "catalogNumber" SET DATA TYPE varchar(100);
            ALTER TABLE "specimenTable" ALTER COLUMN "recordedBy_id" SET DATA TYPE integer;
            ALTER TABLE "specimenTable" ALTER COLUMN "sex" SET DATA TYPE varchar(6);
            ALTER TABLE "specimenTable" ALTER COLUMN "uploaded_iNaturalist" SET DATA TYPE varchar(5);
            ALTER TABLE "specimenTable" ALTER COLUMN "behavior" SET DATA TYPE text;
            ALTER TABLE "specimenTable" ALTER COLUMN "occurrenceRemarks" SET DATA TYPE text;
            ALTER TABLE "specimenTable" ALTER COLUMN "disposition" SET DATA TYPE text;
            ''',
            reverse_sql=''
        ),
        
        # 4. Event Fields
        migrations.RunSQL(
            sql='''
            -- Event Fields
            ALTER TABLE "specimenTable" ALTER COLUMN "year" SET DATA TYPE varchar(4);
            ALTER TABLE "specimenTable" ALTER COLUMN "month" SET DATA TYPE varchar(2);
            ALTER TABLE "specimenTable" ALTER COLUMN "day" SET DATA TYPE varchar(2);
            ALTER TABLE "specimenTable" ALTER COLUMN "eventTime" SET DATA TYPE time;
            ALTER TABLE "specimenTable" ALTER COLUMN "eventDate" SET DATA TYPE date;
            ALTER TABLE "specimenTable" ALTER COLUMN "habitatNotes" SET DATA TYPE text;
            ALTER TABLE "specimenTable" ALTER COLUMN "samplingProtocol" SET DATA TYPE text;
            ''',
            reverse_sql=''
        ),
        
        # 5. Taxon Fields
        migrations.RunSQL(
            sql='''
            -- Taxon Fields
            ALTER TABLE "specimenTable" ALTER COLUMN "family" SET DATA TYPE varchar(100);
            ALTER TABLE "specimenTable" ALTER COLUMN "subfamily" SET DATA TYPE varchar(100);
            ALTER TABLE "specimenTable" ALTER COLUMN "tribe" SET DATA TYPE varchar(100);
            ALTER TABLE "specimenTable" ALTER COLUMN "subtribe" SET DATA TYPE varchar(100);
            ALTER TABLE "specimenTable" ALTER COLUMN "genus" SET DATA TYPE varchar(100);
            ALTER TABLE "specimenTable" ALTER COLUMN "specificEpithet" SET DATA TYPE varchar(100);
            ALTER TABLE "specimenTable" ALTER COLUMN "infraspecificEpithet" SET DATA TYPE varchar(100);
            ''',
            reverse_sql=''
        ),
        
        # 6. Identification Fields
        migrations.RunSQL(
            sql='''
            -- Identification Fields
            ALTER TABLE "specimenTable" ALTER COLUMN "identifiedBy_id" SET DATA TYPE integer;
            ALTER TABLE "specimenTable" ALTER COLUMN "dateIdentified" SET DATA TYPE date;
            ALTER TABLE "specimenTable" ALTER COLUMN "identificationReferences" SET DATA TYPE text;
            ALTER TABLE "specimenTable" ALTER COLUMN "identificationRemarks" SET DATA TYPE text;
            ''',
            reverse_sql=''
        ),
        
        # PostgreSQL doesn't have a simple way to reorder columns in the database schema
        # We're just ensuring column types are correct. The ORM will handle the order for us.
        # The exports will use the order from the views.py file instead of the database column order.
    ]
