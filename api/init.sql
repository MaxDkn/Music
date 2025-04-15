CREATE TABLE waitlist (
    "trackId" INTEGER PRIMARY KEY,
    "status" INTEGER
);

CREATE TABLE music (
    "trackId" INTEGER PRIMARY KEY,
    "trackName" VARCHAR(100),
    "artisteId" INTEGER,
    "artisteName" VARCHAR(100),
    "coverImageUrl" VARCHAR(200),
    "MusicKey" VARCHAR(11),
    "MusicBuffer" BYTEA
);
