CREATE TABLE IF NOT EXISTS catherine_users (
    id BIGINT PRIMARY KEY,
    created_at timestamp WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

ALTER TABLE profiles ADD COLUMN user_id BIGINT REFERENCES catherine_users (id) ON DELETE CASCADE ON UPDATE NO ACTION;
CREATE UNIQUE INDEX IF NOT EXISTS profiles_user_idx ON profiles (user_id);


CREATE TABLE IF NOT EXISTS pronouns_examples (
    id SERIAL PRIMARY KEY,
    sentence TEXT,
    created_at timestamp WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc'),
    approved BOOLEAN DEFAULT FALSE,
    user_id BIGINT REFERENCES catherine_users (id) ON DELETE NO ACTION ON UPDATE NO ACTION
);

CREATE INDEX IF NOT EXISTS pronouns_examples_user_idx ON pronouns_examples (user_id);