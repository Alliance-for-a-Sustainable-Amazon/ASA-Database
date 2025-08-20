from django.db import migrations

class Migration(migrations.Migration):
    """
    This migration fixes the type mismatch between integer foreign keys and string primary keys
    by modifying the database directly with SQL commands.
    """

    dependencies = [
        ('butterflies', '0012_use_natural_keys'),
    ]

    operations = [
        # Execute raw SQL to fix the foreign key issue
        migrations.RunSQL(
            sql="""
            -- Step 1: Create temporary columns to store the original foreign key values
            ALTER TABLE "specimenTable" ADD COLUMN temp_locality_id INTEGER;
            ALTER TABLE "specimenTable" ADD COLUMN temp_recordedBy_id INTEGER;
            ALTER TABLE "specimenTable" ADD COLUMN temp_identifiedBy_id INTEGER;
            ALTER TABLE "specimenTable" ADD COLUMN temp_georeferencedBy_id INTEGER;
            
            -- Step 2: Copy values from original foreign key columns
            UPDATE "specimenTable" 
            SET 
                temp_locality_id = locality_id,
                temp_recordedBy_id = "recordedBy_id",
                temp_identifiedBy_id = "identifiedBy_id",
                temp_georeferencedBy_id = "georeferencedBy_id";
                
            -- Step 3: Drop the original foreign key constraints
            ALTER TABLE "specimenTable" DROP CONSTRAINT IF EXISTS "specimenTable_locality_id_fkey";
            ALTER TABLE "specimenTable" DROP CONSTRAINT IF EXISTS "specimenTable_recordedBy_id_fkey";
            ALTER TABLE "specimenTable" DROP CONSTRAINT IF EXISTS "specimenTable_identifiedBy_id_fkey";
            ALTER TABLE "specimenTable" DROP CONSTRAINT IF EXISTS "specimenTable_georeferencedBy_id_fkey";
            
            -- Step 4: Alter the foreign key columns to be text-based
            ALTER TABLE "specimenTable" DROP COLUMN "locality_id";
            ALTER TABLE "specimenTable" ADD COLUMN "locality_id" VARCHAR(100);
            
            ALTER TABLE "specimenTable" DROP COLUMN "recordedBy_id";
            ALTER TABLE "specimenTable" ADD COLUMN "recordedBy_id" VARCHAR(10);
            
            ALTER TABLE "specimenTable" DROP COLUMN "identifiedBy_id";
            ALTER TABLE "specimenTable" ADD COLUMN "identifiedBy_id" VARCHAR(10);
            
            ALTER TABLE "specimenTable" DROP COLUMN "georeferencedBy_id";
            ALTER TABLE "specimenTable" ADD COLUMN "georeferencedBy_id" VARCHAR(10);
            
            -- Step 5: Update the text-based foreign key columns with values from the related tables
            UPDATE "specimenTable" s
            SET "locality_id" = l."localityCode"
            FROM "localityTable" l
            WHERE s.temp_locality_id = l.id;
            
            UPDATE "specimenTable" s
            SET "recordedBy_id" = i."initials"
            FROM "initialsTable" i
            WHERE s.temp_recordedBy_id = i.id;
            
            UPDATE "specimenTable" s
            SET "identifiedBy_id" = i."initials"
            FROM "initialsTable" i
            WHERE s.temp_identifiedBy_id = i.id;
            
            UPDATE "specimenTable" s
            SET "georeferencedBy_id" = i."initials"
            FROM "initialsTable" i
            WHERE s.temp_georeferencedBy_id = i.id;
            
            -- Step 6: Add the foreign key constraints back
            ALTER TABLE "specimenTable" 
            ADD CONSTRAINT "specimenTable_locality_id_fkey" 
            FOREIGN KEY ("locality_id") REFERENCES "localityTable" ("localityCode");
            
            ALTER TABLE "specimenTable" 
            ADD CONSTRAINT "specimenTable_recordedBy_id_fkey"
            FOREIGN KEY ("recordedBy_id") REFERENCES "initialsTable" ("initials");
            
            ALTER TABLE "specimenTable" 
            ADD CONSTRAINT "specimenTable_identifiedBy_id_fkey"
            FOREIGN KEY ("identifiedBy_id") REFERENCES "initialsTable" ("initials");
            
            ALTER TABLE "specimenTable" 
            ADD CONSTRAINT "specimenTable_georeferencedBy_id_fkey"
            FOREIGN KEY ("georeferencedBy_id") REFERENCES "initialsTable" ("initials");
            
            -- Step 7: Drop the temporary columns
            ALTER TABLE "specimenTable" DROP COLUMN temp_locality_id;
            ALTER TABLE "specimenTable" DROP COLUMN temp_recordedBy_id;
            ALTER TABLE "specimenTable" DROP COLUMN temp_identifiedBy_id;
            ALTER TABLE "specimenTable" DROP COLUMN temp_georeferencedBy_id;
            """,
            reverse_sql="""
            -- This is for rolling back the migration if needed
            -- It's complex to reverse this operation, so we'll just warn
            SELECT 'Warning: Cannot automatically reverse this migration. Manual intervention required.';
            """
        ),
    ]
