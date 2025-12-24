-- FYI: Google Gemini wrote this for me, just for migration purposes

DO $$ 
DECLARE
    -- Variable to hold the name of the new identity sequence
    seq_name TEXT;
    max_id BIGINT;
BEGIN
    ----------------------------------------------------------------
    -- STEP 1: CLEANUP (Safe to run even if previous run failed)
    ----------------------------------------------------------------
    
    -- Drop the old default 'nextval(...)' if it still exists
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = 'pronouns_test_examples' AND column_name = 'id' AND column_default IS NOT NULL
    ) THEN
        ALTER TABLE public.pronouns_test_examples ALTER COLUMN id DROP DEFAULT;
    END IF;

    -- Drop the old SERIAL sequence explicitly
    DROP SEQUENCE IF EXISTS public.pronouns_test_examples_id_seq;

    ----------------------------------------------------------------
    -- STEP 2: CONVERT TO IDENTITY
    ----------------------------------------------------------------
    
    -- Only add identity if it's not already an identity column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = 'pronouns_test_examples' AND column_name = 'id' AND is_identity = 'YES'
    ) THEN
        ALTER TABLE public.pronouns_test_examples 
        ALTER COLUMN id 
        ADD GENERATED ALWAYS AS IDENTITY;
    END IF;

    ----------------------------------------------------------------
    -- STEP 3: SYNC VALUES (The step that failed previously)
    ----------------------------------------------------------------

    -- 1. Find the sequence name explicitly using the schema
    seq_name := pg_get_serial_sequence('public.pronouns_test_examples', 'id');

    -- 2. Validate we found it
    IF seq_name IS NULL THEN
        RAISE EXCEPTION 'Could not find the new identity sequence. Ensure the table is in the public schema.';
    END IF;

    -- 3. Get the current highest ID (safe for empty tables)
    SELECT COALESCE(MAX(id), 0) + 1 INTO max_id FROM public.pronouns_test_examples;

    -- 4. Apply the fix
    PERFORM setval(seq_name, max_id, false);
    
    RAISE NOTICE 'Migration Successful: Sequence % synced to %', seq_name, max_id;
END $$;