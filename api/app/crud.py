from sqlalchemy.orm import Session
from . import models

def create_music_entry(db: Session, titre: str, artiste: str, cover: bytes, music: bytes):
    music_entry = models.Index(
        Titre=titre,
        Artiste=artiste,
        CoverImageBuffer=cover,
        MusicBuffer=music
    )
    db.add(music_entry)
    db.commit()
    db.refresh(music_entry)
    return music_entry
