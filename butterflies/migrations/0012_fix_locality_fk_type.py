from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('butterflies', '0011_alter_initials_initials_alter_initials_name_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            # Fix the foreign key relationship between specimen and locality tables
            """
            -- First, ensure all locality references are valid (if needed, update specimens with invalid references)
            UPDATE "specimenTable"
            SET locality_id = NULL
            WHERE locality_id IS NOT NULL AND NOT EXISTS (
                SELECT 1 FROM "localityTable" WHERE "localityCode" = CAST(locality_id AS VARCHAR)
            );
            
            -- Create a temporary column for the correct data type
            ALTER TABLE "specimenTable" 
            ADD COLUMN locality_id_new VARCHAR(100) REFERENCES "localityTable"("localityCode") ON DELETE SET NULL;
            
            -- Copy data, converting from integer to string if needed
            UPDATE "specimenTable"
            SET locality_id_new = CAST(locality_id AS VARCHAR)
            WHERE locality_id IS NOT NULL;
            
            -- Drop the original foreign key constraint
            ALTER TABLE "specimenTable" DROP CONSTRAINT IF EXISTS specimenTable_locality_id_fkey;
            
            -- Drop the original column
            ALTER TABLE "specimenTable" DROP COLUMN locality_id;
            
            -- Rename the new column to the original name
            ALTER TABLE "specimenTable" RENAME COLUMN locality_id_new TO locality_id;
            """,
            # Rollback SQL - reverse the changes if needed
            """
            -- This would restore the integer column, but data might be lost
            ALTER TABLE "specimenTable" 
            ADD COLUMN locality_id_old INTEGER;
            
            -- Try to convert back strings that are numeric
            UPDATE "specimenTable"
            SET locality_id_old = CAST(locality_id AS INTEGER)
            WHERE locality_id ~ '^[0-9]+$';
            
            -- Drop the string column
            ALTER TABLE "specimenTable" DROP COLUMN locality_id;
            
            -- Rename the integer column back
            ALTER TABLE "specimenTable" RENAME COLUMN locality_id_old TO locality_id;
            
            -- Re-add the foreign key constraint if possible
            -- This might fail if the data types still don't match
            """
        ),
    ]
