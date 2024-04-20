CREATE TABLE IF NOT EXISTS profiles (
    id SERIAL PRIMARY KEY,
    views INT DEFAULT 0,
    name VARCHAR(50),
    pronouns VARCHAR(50),
    gender_identity VARCHAR(50),
    sexual_orientation VARCHAR(50),
    romantic_orientation VARCHAR(50)
);

-- Trigram indexes for GIN indexes to work properly
CREATE INDEX IF NOT EXISTS profiles_name_idx ON profiles (name);
CREATE INDEX IF NOT EXISTS profiles_name_trgm_idx ON profiles USING GIN (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS profiles_name_lower_idx ON profiles (LOWER(name));