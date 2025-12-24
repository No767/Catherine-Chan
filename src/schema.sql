-- Move the creation of this extension to here to reduce brittleness during initialization 
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE IF NOT EXISTS pride_profiles (
    id BIGINT PRIMARY KEY,
    name TEXT,
    pronouns TEXT,
    gender_identity TEXT,
    sexual_orientation TEXT,
    romantic_orientation TEXT,
    views INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS pronouns_test_examples (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    owner_id BIGINT,
    content TEXT NOT NULL,
    approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

CREATE INDEX IF NOT EXISTS pride_profiles_name_idx ON pride_profiles (name);
CREATE INDEX IF NOT EXISTS pride_profiles_name_lower_idx ON pride_profiles (LOWER(name));
CREATE INDEX IF NOT EXISTS pride_profiles_name_trgm_idx ON pride_profiles USING GIN (name gin_trgm_ops);