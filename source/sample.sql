CREATE TABLE IF NOT EXISTS images(
    id uuid PRIMARY KEY,
    created_at BIGINT,
    texture bytea,
    hash_name TEXT
);