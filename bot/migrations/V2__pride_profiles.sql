-- Revision Version: V2
-- Revises: V1
-- Creation Date: 2024-06-16 17:49:08.154360+00:00 UTC
-- Reason: pride_profiles

-- This is an replacement table for the old profiles table
CREATE TABLE IF NOT EXISTS pride_profiles (
    id SERIAL PRIMARY KEY,
    user_id BIGINT,
    name TEXT,
    pronouns TEXT,
    gender_identity TEXT,
    sexual_orientation TEXT,
    romantic_orientation TEXT,
    views INT DEFAULT 0
);

CREATE INDEX IF NOT EXISTS pride_profiles_name_idx ON pride_profiles (name);
CREATE INDEX IF NOT EXISTS pride_profiles_name_trgm_idx ON pride_profiles USING GIN (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS pride_profiles_name_lower_idx ON pride_profiles (LOWER(name));
CREATE UNIQUE INDEX IF NOT EXISTS pride_profiles_user_idx ON pride_profiles (user_id);

INSERT INTO pride_profiles (SELECT id, user_id, name, pronouns, gender_identity, sexual_orientation, romantic_orientation, views FROM profiles);