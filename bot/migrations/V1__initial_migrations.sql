-- Revision Version: V1
-- Revises: V0
-- Creation Date: 2024-05-20 19:06:40.005347 UTC
-- Reason: initial_migrations

-- Remove tonetags feature from the database
DROP TABLE IF EXISTS tonetags CASCADE;
DROP TABLE IF EXISTS tonetags_lookup CASCADE;

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

CREATE TABLE IF NOT EXISTS catherine_users (
    id BIGINT PRIMARY KEY,
    created_at timestamp WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

CREATE TABLE IF NOT EXISTS pronouns_examples (
    id SERIAL PRIMARY KEY,
    sentence TEXT,
    created_at timestamp WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc'),
    approved BOOLEAN DEFAULT FALSE,
    user_id BIGINT REFERENCES catherine_users (id) ON DELETE NO ACTION ON UPDATE NO ACTION
);

CREATE INDEX IF NOT EXISTS pronouns_examples_user_idx ON pronouns_examples (user_id);

DROP TABLE IF EXISTS blacklist;

CREATE TABLE IF NOT EXISTS blacklist (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT,
    entity_id BIGINT,
    UNIQUE (entity_id)
);

CREATE INDEX IF NOT EXISTS blacklist_guild_id_idx ON blacklist (guild_id);
CREATE INDEX IF NOT EXISTS blacklist_entity_id_idx ON blacklist (entity_id);
