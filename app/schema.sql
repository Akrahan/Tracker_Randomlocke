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

CREATE UNIQUE INDEX IF NOT EXISTS uq_encounters_primer_encuentro
    ON encounters (run_id, route) WHERE event_type IN ('captura', 'fallo');

CREATE TABLE IF NOT EXISTS species (
    id    INTEGER PRIMARY KEY,
    name  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_species_nombre
    ON species (lower(name) text_pattern_ops);

CREATE TABLE IF NOT EXISTS party (
    run_id    BIGINT   NOT NULL REFERENCES runs (id),
    route     TEXT     NOT NULL,
    position  SMALLINT NOT NULL CHECK (position BETWEEN 1 AND 6),
    PRIMARY KEY (run_id, route),
    UNIQUE (run_id, position)
);

CREATE TABLE IF NOT EXISTS types (
    id          SMALLINT PRIMARY KEY,
    identifier  TEXT NOT NULL,
    name        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS species_types (
    species_id  INTEGER  NOT NULL REFERENCES species (id),
    type_id     SMALLINT NOT NULL REFERENCES types (id),
    slot        SMALLINT NOT NULL CHECK (slot IN (1, 2)),
    PRIMARY KEY (species_id, slot)
);
