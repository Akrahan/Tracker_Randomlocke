CREATE TABLE IF NOT EXISTS runs (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS encounters (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id      BIGINT NOT NULL REFERENCES runs (id),
    event_type  TEXT NOT NULL CHECK (event_type IN ('captura', 'fallo', 'muerte')),
    route       TEXT NOT NULL,
    species     TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    details     JSONB
);

CREATE INDEX IF NOT EXISTS idx_encounters_run_id ON encounters (run_id);
