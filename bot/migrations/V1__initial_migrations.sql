-- Revision Version: V1
-- Revises: V0
-- Creation Date: 2024-05-20 19:06:40.005347 UTC
-- Reason: initial_migrations

-- These migrations are intended to continue from the previous migrations
CREATE TABLE IF NOT EXISTS catherine_users (
    id BIGINT PRIMARY KEY,
    created_at timestamp WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

CREATE TABLE IF NOT EXISTS profiles (
    id SERIAL PRIMARY KEY,
    views INT DEFAULT 0,
    name VARCHAR(50),
    pronouns VARCHAR(50),
    gender_identity VARCHAR(50),
    sexual_orientation VARCHAR(50),
    romantic_orientation VARCHAR(50),
    user_id BIGINT REFERENCES catherine_users (id) ON DELETE CASCADE ON UPDATE NO ACTION
);

CREATE INDEX IF NOT EXISTS profiles_name_idx ON profiles (name);
CREATE INDEX IF NOT EXISTS profiles_name_trgm_idx ON profiles USING GIN (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS profiles_name_lower_idx ON profiles (LOWER(name));
CREATE UNIQUE INDEX IF NOT EXISTS profiles_user_idx ON profiles (user_id);


CREATE TABLE IF NOT EXISTS pronouns_examples (
    id SERIAL PRIMARY KEY,
    sentence TEXT,
    created_at timestamp WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc'),
    approved BOOLEAN DEFAULT FALSE,
    user_id BIGINT REFERENCES catherine_users (id) ON DELETE NO ACTION ON UPDATE NO ACTION
);

CREATE INDEX IF NOT EXISTS pronouns_examples_user_idx ON pronouns_examples (user_id);

-- Keeping the tonetags for consistency with previous migrations
CREATE TABLE IF NOT EXISTS tonetags (
    id SERIAL PRIMARY KEY,
    indicator VARCHAR(255),
    definition TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc'),
    author_id BIGINT REFERENCES catherine_users (id) ON DELETE CASCADE ON UPDATE NO ACTION
);

CREATE TABLE IF NOT EXISTS tonetags_lookup (
    id SERIAL PRIMARY KEY,
    indicator VARCHAR (255),
    author_id BIGINT,
    tonetags_id INTEGER REFERENCES tonetags (id) ON DELETE CASCADE ON UPDATE NO ACTION
);

CREATE INDEX IF NOT EXISTS tonetags_indicator_idx ON tonetags (indicator);
CREATE INDEX IF NOT EXISTS tonetags_indicator_trgm_idx ON tonetags USING GIN (indicator gin_trgm_ops);
CREATE INDEX IF NOT EXISTS tonetags_indicator_lower_idx ON tonetags (LOWER(indicator));
CREATE UNIQUE INDEX IF NOT EXISTS tonetags_uniq_idx ON tonetags (LOWER(indicator), author_id);

CREATE INDEX IF NOT EXISTS tonetags_lookup_indicator_idx ON tonetags_lookup (indicator);
CREATE INDEX IF NOT EXISTS tonetags_lookup_indicator_trgm_idx ON tonetags_lookup USING GIN (indicator gin_trgm_ops);
CREATE INDEX IF NOT EXISTS tonetags_lookup_indicator_lower_idx ON tonetags_lookup (LOWER(indicator));
CREATE UNIQUE INDEX IF NOT EXISTS tonetags_lookup_uniq_idx ON tonetags_lookup (LOWER(indicator), author_id);
