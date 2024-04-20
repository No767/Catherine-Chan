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