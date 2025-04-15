from sqlalchemy import Column, String, LargeBinary, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Waitlist(Base):
    __tablename__ = "waitlist"

    trackId = Column("trackId", Integer, primary_key=True)
    status = Column("status", Integer)


class Music(Base):
    __tablename__ = "music"

    trackId = Column("trackId", Integer, primary_key=True)
    trackName = Column("trackName", String(100))
    artisteId = Column("artisteId", Integer)
    artisteName = Column("artisteName", String(100))
    coverImageUrl = Column("coverImageUrl", String(200))
    musicKey = Column("musicKey", String(11))
    musicBuffer = Column("musicBuffer", LargeBinary)