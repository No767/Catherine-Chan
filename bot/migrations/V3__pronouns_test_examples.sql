-- Revision Version: V3
-- Revises: V2
-- Creation Date: 2024-09-25 03:52:04.644936+00:00 UTC
-- Reason: pronouns_test_examples

CREATE TABLE IF NOT EXISTS pronouns_test_examples (
    id SERIAL PRIMARY KEY,
    owner_id BIGINT,
    content TEXT NOT NULL,
    approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

-- Same thing with the pride profiles. There isn't much data to justify copying
INSERT INTO pronouns_test_examples (SELECT id, user_id, sentence, approved, created_at FROM pronouns_examples);