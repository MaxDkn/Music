CREATE TABLE waitlist (
    "trackId" INTEGER PRIMARY KEY,
    "status" INTEGER
);

CREATE TABLE music (
    "trackId" INTEGER PRIMARY KEY,
    "trackName" VARCHAR(100),
    "artistId" INTEGER,
    "artistName" VARCHAR(100),
    "coverImageUrl" VARCHAR(200),
    "musicKey" VARCHAR(11),
    "musicBuffer" BYTEA
);
