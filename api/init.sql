CREATE TABLE music (
    MusicId SERIAL PRIMARY KEY,
    Titre VARCHAR(255),
    Artiste VARCHAR(255),
    CoverImageBuffer BYTEA,
    MusicBuffer BYTEA
);