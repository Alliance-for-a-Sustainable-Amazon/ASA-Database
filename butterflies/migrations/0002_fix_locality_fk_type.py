"""
Migration to fix locality foreign key field types.
This migration is designed to run even when previous migrations have problems.
It has minimal dependencies and can be applied to a fresh database to ensure proper field types.
"""

from django.db import migrations, models
import django.db.models.deletion


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
        # Run SQL to verify and fix the locality table if needed
        migrations.RunSQL(
            sql="""
            -- Check if locality table exists and create it if not
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.tables 
                              WHERE table_name = 'butterflies_locality') THEN
                    -- Create locality table
                    CREATE TABLE IF NOT EXISTS butterflies_locality (
                        id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                        locality VARCHAR(255) UNIQUE NOT NULL,
                        country VARCHAR(255),
                        state VARCHAR(255),
                        region VARCHAR(255),
                        coordinates VARCHAR(255)
                    );
                END IF;
                
                -- Ensure the specimen table exists
                IF NOT EXISTS (SELECT 1 FROM information_schema.tables 
                              WHERE table_name = 'butterflies_specimen') THEN
                    -- Create minimal specimen table if it doesn't exist
                    CREATE TABLE IF NOT EXISTS butterflies_specimen (
                        id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                        catalognumber VARCHAR(255),
                        locality_id BIGINT
                    );
                END IF;
                
                -- Ensure the locality_id column exists and has the right type
                IF EXISTS (SELECT 1 FROM information_schema.columns 
                           WHERE table_name = 'butterflies_specimen' AND column_name = 'locality_id') THEN
                    -- Column exists, ensure it has the right type
                    ALTER TABLE butterflies_specimen 
                    ALTER COLUMN locality_id TYPE bigint USING locality_id::bigint;
                ELSE
                    -- Column doesn't exist, create it
                    ALTER TABLE butterflies_specimen 
                    ADD COLUMN locality_id bigint;
                END IF;
                
                -- Ensure foreign key constraint exists if possible
                BEGIN
                    ALTER TABLE butterflies_specimen
                    ADD CONSTRAINT fk_specimen_locality
                    FOREIGN KEY (locality_id)
                    REFERENCES butterflies_locality(id);
                EXCEPTION
                    WHEN others THEN
                        -- Constraint might already exist or tables might not be ready
                        RAISE NOTICE 'Could not add foreign key constraint: %', SQLERRM;
                END;
            END
            $$;
            """,
            reverse_sql="""
            -- No specific reverse operations needed
            SELECT 1;
            """
        ),
    ]
