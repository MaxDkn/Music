from sqlalchemy.orm import Session
from . import models


def create_music_entry(db: Session, trackId: int, trackName: str, artisteId: int, artisteName: str, coverImageUrl: str, musicKey: str, musicBuffer: bytes):
    music = db.query(models.Music).filter(models.Music.trackId == trackId).first()
    if music:
        return music
    music_entry = models.Music(
        trackId=trackId,
        trackName=trackName,
        artisteId=artisteId,
        artisteName=artisteName,
        coverImageUrl=coverImageUrl,
        musicKey=musicKey,
        musicBuffer=musicBuffer
    )
    db.add(music_entry)
    db.commit()
    db.refresh(music_entry)
    return music_entry


def add_waitlist_entry(db: Session, track_id: int, status: int):
    waitlist_entry = models.Waitlist(
        trackId=track_id,
        status=status
    )
    db.add(waitlist_entry)
    db.commit()
    db.refresh(waitlist_entry)
    return waitlist_entry


def modify_status(db: Session, track_id: int, status: int):
    waitlist_entry = db.query(models.Waitlist).filter(models.Waitlist.trackId == track_id).first()
    if waitlist_entry:
        waitlist_entry.status = status
        db.commit()
        db.refresh(waitlist_entry)
        return waitlist_entry
    return None
